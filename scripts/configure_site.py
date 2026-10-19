#!/usr/bin/env python3
"""Set the public base URL for this static site. Python 3.9+, stdlib only."""

import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit, urlunsplit
import xml.etree.ElementTree as ET


TAG_RE = re.compile(r"<(?:link|meta)\b[^>]*>", re.I)
JSON_RE = re.compile(
    r'(<script\b[^>]*\btype\s*=\s*[\"\']application/ld\+json[\"\'][^>]*>)(.*?)(</script\s*>)',
    re.I | re.S,
)
DEFAULT_BASE = "https://henrychan0719.github.io/"


def attribute(tag, name):
    match = re.search(r"(?<![\w:-])" + re.escape(name) + r"\s*=\s*([\"\'])(.*?)\1", tag, re.I | re.S)
    return html.unescape(match.group(2)) if match else None


def set_attribute(tag, name, value):
    pattern = re.compile(r"((?<![\w:-])" + re.escape(name) + r"\s*=\s*)([\"\'])(.*?)\2", re.I | re.S)
    escaped = html.escape(value, quote=True)
    if pattern.search(tag):
        return pattern.sub(lambda match: match.group(1) + '"' + escaped + '"', tag, count=1)
    return re.sub(r"\s*/?>$", lambda match: ' ' + name + '="' + escaped + '"' + match.group(0), tag)


def normalize_base(value):
    parts = urlsplit(value.strip())
    host = parts.hostname or ""
    if (parts.scheme != "https" or not host or "." not in host or parts.username
            or parts.password or parts.query or parts.fragment or parts.port
            or not re.fullmatch(r"[A-Za-z0-9.-]+", host)):
        raise ValueError("請提供完整 HTTPS 網址，不含帳密、連接埠、查詢參數或 #，例如 https://example.com/。")
    if any(segment in (".", "..") for segment in parts.path.split("/")):
        raise ValueError("網址路徑不能包含 . 或 ..。")
    return urlunsplit(("https", host.lower(), parts.path.rstrip("/") + "/", "", ""))


def current_base(index_text):
    tags = TAG_RE.findall(index_text)
    for kind in ("canonical", "og:url"):
        for tag in tags:
            if kind == "canonical" and attribute(tag, "rel") == kind:
                value = attribute(tag, "href")
            elif kind == "og:url" and attribute(tag, "property") == kind:
                value = attribute(tag, "content")
            else:
                continue
            if value:
                return value.removesuffix("index.html").rstrip("/") + "/"
    return DEFAULT_BASE


def rebase_url(value, old_bases, new_base, allow_relative=False):
    """Rebase only this site's URLs, preserving external research/profile URLs."""
    for old_base in old_bases:
        if value == old_base.rstrip("/"):
            return new_base
        if value.startswith(old_base):
            return new_base + value[len(old_base):]
    parts = urlsplit(value)
    if allow_relative and not parts.scheme and not parts.netloc and not value.startswith("#"):
        return urljoin(new_base, value.lstrip("/"))
    return value


def update_json(value, old_bases, new_base):
    if isinstance(value, dict):
        return {key: update_json(item, old_bases, new_base) for key, item in value.items()}
    if isinstance(value, list):
        return [update_json(item, old_bases, new_base) for item in value]
    if isinstance(value, str):
        return rebase_url(value, old_bases, new_base)
    return value


def update_html(text, page_url, old_bases, new_base):
    found = set()

    def replace_tag(match):
        tag = match.group(0)
        rel = (attribute(tag, "rel") or "").lower()
        prop = (attribute(tag, "property") or attribute(tag, "name") or "").lower()
        if "canonical" in rel.split():
            found.add("canonical")
            return set_attribute(tag, "href", page_url)
        if prop == "og:url":
            found.add("og:url")
            return set_attribute(tag, "content", page_url)
        if prop in ("og:image", "og:image:url", "og:image:secure_url", "twitter:image", "twitter:image:src"):
            value = attribute(tag, "content")
            if value:
                return set_attribute(tag, "content", rebase_url(value, old_bases, new_base, True))
        return tag

    text = TAG_RE.sub(replace_tag, text)
    missing = []
    if "canonical" not in found:
        missing.append('  <link rel="canonical" href="' + html.escape(page_url, quote=True) + '" />')
    if "og:url" not in found:
        missing.append('  <meta property="og:url" content="' + html.escape(page_url, quote=True) + '" />')
    if missing:
        if not re.search(r"</head\s*>", text, re.I):
            raise ValueError("HTML 缺少 </head>，無法插入網址設定。")
        text = re.sub(r"</head\s*>", lambda match: "\n".join(missing) + "\n" + match.group(0), text, count=1, flags=re.I)

    def replace_json(match):
        data = json.loads(match.group(2))
        revised = update_json(data, old_bases, new_base)
        if revised == data:
            return match.group(0)
        # Keep literal </script> out of JSON-LD text, even if later content adds it.
        encoded = json.dumps(revised, ensure_ascii=False, indent=2).replace("</", "<\\/")
        return match.group(1) + "\n" + encoded + "\n  " + match.group(3)

    return JSON_RE.sub(replace_json, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="正式網站網址；GitHub 專案網站需包含 /repo/。")
    parser.add_argument("--site-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dry-run", action="store_true", help="列出將更新的檔案，不寫入。")
    cname = parser.add_mutually_exclusive_group()
    cname.add_argument("--write-cname", action="store_true", help="僅為 GitHub Pages 自訂網域寫入 CNAME。")
    cname.add_argument("--remove-cname", action="store_true", help="切回 github.io、pages.dev 或專案路徑時移除舊 CNAME。")
    args = parser.parse_args()
    try:
        base = normalize_base(args.base_url)
        root = args.site_dir.resolve()
        index = root / "index.html"
        old_base = current_base(index.read_text(encoding="utf-8"))
        old_bases = sorted({old_base, DEFAULT_BASE}, key=len, reverse=True)
        parts = urlsplit(base)
        if args.write_cname and (parts.path != "/" or parts.hostname.endswith((".github.io", ".pages.dev"))):
            raise ValueError("--write-cname 僅適用自訂網域的網站根目錄，例如 https://example.com/，不能用於 github.io、pages.dev 或 /repo/。")
        cname_path = root / "CNAME"
        if cname_path.exists() and not args.write_cname and not args.remove_cname:
            existing = cname_path.read_text(encoding="utf-8").strip()
            if existing != parts.hostname or parts.path != "/":
                raise ValueError("現有 CNAME 與新網址不符；自訂網域請加 --write-cname，否則加 --remove-cname。")

        # Prepare every change before writing, so invalid HTML/JSON fails early.
        changes = {}
        urls = []
        for path in sorted(root.glob("*.html")):
            page_url = base if path.name == "index.html" else urljoin(base, path.name)
            original = path.read_text(encoding="utf-8")
            revised = update_html(original, page_url, old_bases, base)
            if revised != original:
                changes[path] = revised
            if path.name != "404.html":
                urls.append(page_url)

        namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        ET.register_namespace("", namespace)
        sitemap = ET.Element("{" + namespace + "}urlset")
        for url in sorted(urls, key=lambda value: (value != base, value)):
            entry = ET.SubElement(sitemap, "{" + namespace + "}url")
            ET.SubElement(entry, "{" + namespace + "}loc").text = url
        ET.indent(sitemap, space="  ")
        changes[root / "sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(sitemap, encoding="unicode") + "\n"
        robots = root / "robots.txt"
        rules = robots.read_text(encoding="utf-8") if robots.exists() else "User-agent: *\nAllow: /\n"
        rules = "\n".join(line for line in rules.splitlines() if not line.strip().lower().startswith("sitemap:"))
        changes[robots] = rules.rstrip() + "\n\nSitemap: " + urljoin(base, "sitemap.xml") + "\n"
        if args.write_cname:
            changes[cname_path] = parts.hostname + "\n"
        changes = {path: value for path, value in changes.items()
                   if not path.exists() or path.read_text(encoding="utf-8") != value}
        for path, value in changes.items():
            print(("預計更新 " if args.dry_run else "更新 ") + str(path.relative_to(root)))
            if not args.dry_run:
                path.write_text(value, encoding="utf-8")
        if args.remove_cname and cname_path.exists():
            print("預計移除 CNAME" if args.dry_run else "移除 CNAME")
            if not args.dry_run:
                cname_path.unlink()
        print("網址：" + base)
        print("僅檢視，未寫入。" if args.dry_run else "本機檔案已設定；尚未上傳、部署或修改 DNS。")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
