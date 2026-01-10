import requests
from PIL import Image
import io
import os

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
os.makedirs(ASSETS, exist_ok=True)

# Try Wikimedia Commons first (more reliable), then fallback to loremflickr
urls = [
    'https://upload.wikimedia.org/wikipedia/commons/e/e9/March%C3%A9_Jean-Talon%2C_Montr%C3%A9al_2005-09-04.JPG',
    'https://loremflickr.com/1600/900/jean%20talon%20market,montreal',
    'https://loremflickr.com/1200/800/jean%20talon%20market,montreal'
]

out_base = os.path.join(ASSETS, 'hero-jeantalon')

img = None
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for u in urls:
    try:
        print('Downloading', u)
        r = requests.get(u, timeout=15, headers=headers)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert('RGB')
        break
    except Exception as e:
        print('Failed to download', u, e)

if img is None:
    raise SystemExit('Could not download hero image')

# Generate sizes
sizes = [(1600, '1600'), (1200, '1200'), (800, '800')]
for w, tag in sizes:
    h = int(img.height * (w / img.width))
    out = img.resize((w, h), Image.Resampling.LANCZOS)
    out_path = f"{out_base}-{tag}.webp"
    out.save(out_path, format='WEBP', quality=88)
    print('Saved', out_path)

# Also save a primary hero.webp (1200)
primary = f"{out_base}.webp"
img.resize((1200, int(img.height*(1200/img.width))), Image.Resampling.LANCZOS).save(primary, format='WEBP', quality=88)
print('Saved', primary)
