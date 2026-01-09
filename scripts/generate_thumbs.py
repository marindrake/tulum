from PIL import Image
import glob
import os

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
patterns = [os.path.join(ASSETS, 'thumb-*.webp')]
sizes = [64, 160, 320]

files = []
for p in patterns:
    files.extend(glob.glob(p))

if not files:
    print('No thumb files found in', ASSETS)
    raise SystemExit(1)

for f in files:
    name = os.path.splitext(os.path.basename(f))[0]  # thumb-trifle
    print('Processing', f)
    img = Image.open(f).convert('RGB')
    for w in sizes:
        out = os.path.join(ASSETS, f"{name}-{w}.webp")
        img2 = img.copy()
        h = int(img2.height * (w / img2.width))
        img2 = img2.resize((w, h), Image.Resampling.LANCZOS)
        img2.save(out, format='WEBP', quality=85)
        print('  saved', out)
print('Done')
