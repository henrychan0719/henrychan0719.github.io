#!/usr/bin/env python3
"""Validate a static site's local links and basic document integrity.

Usage: python scripts/validate_site.py [site-directory]
Uses only the Python standard library; it makes no network requests.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__"}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
# HTML permits these tags to end implicitly; do not report legal omissions.
OPTIONAL_END_TAGS = {
    "html", "head", "body", "li", "dt", "dd", "p", "rt", "rp",
    "optgroup", "option", "colgroup", "thead", "tbody", "tfoot",
    "tr", "td", "th",
}


@dataclass
class Reference:
    value: str
    line: int
    tag: str
    attribute: str


class Document(HTMLParser):
    def __init__(self, path: Path, report):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.report = report
        self.ids: set[str] = set()
        self.anchors: set[str] = set()
        self.references: list[Reference] = []
        self.stack: list[tuple[str, int]] = []
        self.json_ld: list[tuple[int, str]] = []
        self.json_parts: list[str] | None = None
        self.json_line = 0

    def problem(self, line: int, message: str):
        self.report(self.path, line, message)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        line = self.getpos()[0]
        identifier = attributes.get("id")
        if identifier is not None:
            if identifier in self.ids:
                self.problem(line, f"duplicate id: {identifier!r}")
            self.ids.add(identifier)
            self.anchors.add(identifier)
        if tag == "a" and attributes.get("name"):
            self.anchors.add(attributes["name"])

        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            # Empty src on a hidden image can be a deliberate lightbox placeholder.
            if value:
                self.references.append(Reference(value, line, tag, attribute))

        if attributes.get("target", "").lower() == "_blank":
            rel = set(attributes.get("rel", "").lower().split())
            if "noopener" not in rel:
                self.problem(line, 'target="_blank" needs rel="noopener"')

        if tag == "script" and attributes.get("type", "").lower() == "application/ld+json":
            self.json_parts = []
            self.json_line = line
        if tag not in VOID_TAGS:
            self.stack.append((tag, line))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        line = self.getpos()[0]
        if tag == "script" and self.json_parts is not None:
            self.json_ld.append((self.json_line, "".join(self.json_parts)))
            self.json_parts = None
        if tag in VOID_TAGS:
            self.problem(line, f"void element has a closing tag: </{tag}>")
            return
        matches = [i for i, item in enumerate(self.stack) if item[0] == tag]
        if not matches:
            if tag not in OPTIONAL_END_TAGS:
                self.problem(line, f"unmatched closing tag: </{tag}>")
            return
        index = matches[-1]
        for opened, opening_line in self.stack[index + 1:]:
            if opened not in OPTIONAL_END_TAGS:
                self.problem(line, f"</{tag}> closes before <{opened}> from line {opening_line}")
        del self.stack[index:]

    def handle_data(self, data):
        if self.json_parts is not None:
            self.json_parts.append(data)

    def finish(self):
        for tag, line in self.stack:
            if tag not in OPTIONAL_END_TAGS:
                self.problem(line, f"unclosed <{tag}> element")
        for line, raw in self.json_ld:
            try:
                json.loads(raw)
            except (json.JSONDecodeError, ValueError) as exc:
                self.problem(line, f"invalid JSON-LD: {exc}")


def included(path: Path, root: Path) -> bool:
    return not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)


def main() -> int:
    root = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: site directory does not exist: {root}")
        return 2

    problems: list[str] = []

    def report(path: Path, line: int, message: str):
        problems.append(f"{path.relative_to(root)}:{line}: {message}")

    html_paths = sorted(p for p in root.rglob("*.html") if included(p, root))
    if not html_paths:
        print(f"ERROR: no HTML files found in {root}")
        return 2
    documents: dict[Path, Document] = {}
    for path in html_paths:
        document = Document(path, report)
        try:
            document.feed(path.read_text(encoding="utf-8"))
            document.close()
            document.finish()
        except (OSError, UnicodeError, ValueError) as exc:
            report(path, 1, f"could not parse HTML: {exc}")
        documents[path.resolve()] = document

    checked_references = 0
    for path, document in documents.items():
        for reference in document.references:
            try:
                url = urlsplit(reference.value)
            except ValueError as exc:
                report(path, reference.line, f"invalid URL {reference.value!r}: {exc}")
                continue
            if url.scheme or url.netloc:
                continue
            decoded_path = unquote(url.path)
            if not decoded_path:
                target = path
            elif decoded_path.startswith("/"):
                target = (root / decoded_path.lstrip("/")).resolve()
            else:
                target = (path.parent / decoded_path).resolve()
            if not target.is_relative_to(root):
                report(path, reference.line, f"local URL leaves site directory: {reference.value!r}")
                continue
            if target.is_dir():
                target = target / "index.html"
            checked_references += 1
            if not target.is_file():
                report(path, reference.line, f"missing {reference.tag}[{reference.attribute}] target: {reference.value!r}")
                continue
            if url.fragment and target in documents:
                # Browser text fragments are not element IDs.
                fragment = unquote(url.fragment).split(":~:text=", 1)[0]
                if fragment and fragment not in documents[target].anchors:
                    report(path, reference.line, f"missing anchor: {reference.value!r}")

    svg_paths = sorted(p for p in root.rglob("*.svg") if included(p, root))
    for path in svg_paths:
        try:
            svg = ET.parse(path)
            if svg.getroot().tag.rsplit("}", 1)[-1] != "svg":
                report(path, 1, "root element is not <svg>")
        except (ET.ParseError, OSError) as exc:
            report(path, getattr(exc, "position", (1,))[0], f"invalid SVG XML: {exc}")

    if problems:
        print(f"FAIL: {len(problems)} issue(s)")
        for problem in problems:
            print(f"  {problem}")
        return 1
    json_count = sum(len(document.json_ld) for document in documents.values())
    print(
        f"PASS: {len(documents)} HTML pages, {checked_references} local references, "
        f"{len(svg_paths)} SVG files, and {json_count} JSON-LD blocks checked."
    )
    print("Checked duplicate IDs, page anchors, script/asset paths, element closure, and external-link rel attributes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
