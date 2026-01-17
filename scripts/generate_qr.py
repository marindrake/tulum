from PIL import Image, ImageDraw
import qrcode
import os

BASE = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE, 'assets')
if not os.path.isdir(ASSETS):
    os.makedirs(ASSETS, exist_ok=True)

name = 'Tulum Dessert & Snacks'
phones = ['+1 514-937-7754', '+1 514-638-8399']
address = '7070 Henri Julien Ave, Montreal, Quebec H2S 3A3, Canada'
hours = '8:00 AM - 6:00 PM, Todos los días'
website = ''

# Generate vCard with both phone numbers
phone_lines = '\n'.join([f'TEL;TYPE=WORK,VOICE:{p}' for p in phones])
vcard = f'''BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{name}
{phone_lines}
ADR;TYPE=WORK:;;{address}
NOTE:{hours}
END:VCARD
'''

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
qr.add_data(vcard)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

# attempt to open logo
logo_path = os.path.join(ASSETS, 'logo.PNG')
if not os.path.exists(logo_path):
    logo_path = os.path.join(ASSETS, 'logo.png')

if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path).convert('RGBA')
        # resize logo to fit into QR (about 20% width)
        qr_w, qr_h = img.size
        logo_size = int(qr_w * 0.2)
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        # make circular white background
        bg = Image.new('RGBA', (logo_size, logo_size), (255,255,255,0))
        draw = ImageDraw.Draw(bg)
        draw.ellipse((0,0,logo_size,logo_size), fill=(255,255,255,255))
        # paste logo centered on bg
        lx = (logo_size - logo.width)//2
        ly = (logo_size - logo.height)//2
        bg.paste(logo, (lx, ly), logo)
        # composite onto QR
        pos = ((qr_w - logo_size)//2, (qr_h - logo_size)//2)
        img.paste(bg, pos, bg)
    except Exception as e:
        print('Error processing logo:', e)

out_webp = os.path.join(ASSETS, 'qr_contact.webp')
out_png = os.path.join(ASSETS, 'qr_contact.png')
img.save(out_png, format='PNG')
img.save(out_webp, format='WEBP', quality=90)
print('Saved', out_png, out_webp)
