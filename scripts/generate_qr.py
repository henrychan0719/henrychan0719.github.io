"""Regenerate profile QR assets. Maintenance only: pip install reportlab pillow.

The website itself has no Python or package dependencies. No QR web service,
tracking redirect, network request, or data embedded beyond the destination URL.
"""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.graphics.barcode.qr import QrCodeWidget
from PIL import Image, ImageDraw

DESTINATIONS = {
    'google-scholar': 'https://scholar.google.com/citations?user=Gr3mhHUAAAAJ',
    'github': 'https://github.com/henrychan0719',
}

def main():
    out = Path(__file__).resolve().parents[1] / 'assets' / 'profiles'
    out.mkdir(parents=True, exist_ok=True)
    for name, url in DESTINATIONS.items():
        qr = QrCodeWidget(url, barLevel='M').qr
        qr.make()
        count = qr.getModuleCount()
        border, scale = 4, 16
        size = count + 2 * border
        cells = [(x + border, y + border) for y in range(count)
                 for x in range(count) if qr.isDark(y, x)]
        path = ''.join(f'M{x},{y}h1v1h-1z' for x, y in cells)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
               f'width="{size*scale}" height="{size*scale}" shape-rendering="crispEdges">'
               f'<title>{escape(url)}</title><rect width="{size}" height="{size}" fill="white"/>'
               f'<path fill="#111827" d="{path}"/></svg>')
        (out / f'{name}-qr.svg').write_text(svg, encoding='utf-8')
        image = Image.new('RGB', (size*scale, size*scale), 'white')
        draw = ImageDraw.Draw(image)
        for x, y in cells:
            draw.rectangle((x*scale, y*scale, (x+1)*scale-1, (y+1)*scale-1), fill='#111827')
        image.save(out / f'{name}-qr.png', optimize=True)
        print(f'{name}: {count} modules + 4-module quiet zone; PNG/SVG saved')
    (out / 'destinations.json').write_text(json.dumps(DESTINATIONS, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
