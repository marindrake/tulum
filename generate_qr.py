#!/usr/bin/env python3
"""Genera un QR (vCard) y lo guarda en assets/qr_contact.webp.

Uso: `py -m pip install qrcode[pil] Pillow` si no está instalado.
Luego: `py generate_qr.py`
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode

ASSETS = Path('assets')
ASSETS.mkdir(exist_ok=True)

# Datos ficticios para vCard
vcard = (
    'BEGIN:VCARD\n'
    'VERSION:3.0\n'
    'FN:Tulum Dessert & Snacks\n'
    'ORG:Tulum Dessert & Snacks\n'
    'TEL;TYPE=CELL:+5219980000000\n'
    'EMAIL:info@tulum.example\n'
    'ADR:;;Calle Principal 123;Tulum;;;Mexico\n'
    'URL:https://tulum.example\n'
    'END:VCARD'
)

def make_placeholder_logo(size=200):
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    # Circle background
    draw.ellipse((0,0,size,size), fill=(226,85,43,255))
    # Letter T
    try:
        font = ImageFont.truetype('arial.ttf', int(size*0.5))
    except Exception:
        font = ImageFont.load_default()
    w, h = font.getsize('T') if hasattr(font, 'getsize') else (size//2, size//2)
    draw.text(((size-w)/2,(size-h)/2-10),'T',fill='white',font=font)
    return img

def generate_qr(vcard_text, out_path: Path):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
    qr.add_data(vcard_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white').convert('RGBA')
    # Add logo: look for several filename variants
    candidates = ['logo.png', 'logo.PNG', 'logo.webp', 'logo.jpg', 'logo.jpeg', 'logo.JPG']
    logo = None
    for c in candidates:
        p = ASSETS / c
        if p.exists():
            logo = Image.open(p).convert('RGBA')
            break
    if logo is None:
        logo = make_placeholder_logo(size=img.size[0]//4)

    # Prepare logo: crop to square, resize, and add circular white background for contrast
    w0, h0 = logo.size
    side = min(w0, h0)
    left = (w0 - side)//2
    top = (h0 - side)//2
    logo = logo.crop((left, top, left+side, top+side))

    # target logo size relative to QR
    logo_size = img.size[0] // 4
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    # Create circular background slightly larger than logo for legibility
    pad = max(8, logo_size // 8)
    bg_size = logo_size + pad*2
    bg = Image.new('RGBA', (bg_size, bg_size), (255,255,255,0))
    draw = ImageDraw.Draw(bg)
    draw.ellipse((0,0,bg_size-1,bg_size-1), fill=(255,255,255,255))

    # Composite logo onto bg (centered)
    bg.paste(logo, (pad, pad), logo)

    # Paste bg onto QR
    pos = ((img.size[0] - bg_size)//2, (img.size[1] - bg_size)//2)
    img.paste(bg, pos, bg)
    # Save as WebP
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format='WEBP', quality=90)
    print('QR guardado en', out_path)

if __name__ == '__main__':
    out = ASSETS / 'qr_contact.webp'
    generate_qr(vcard, out)
