#!/usr/bin/env python3
"""
Descarga imágenes desde URLs listadas en `images.json` y las convierte a WebP optimizadas en la carpeta `assets/`.

Formato `images.json`:
{
  "hero.webp": "https://images.example.com/hero.jpg",
  "thumb-flan.webp": "https://images.example.com/flan.jpg",
  ...
}

Uso:
  python -m pip install -r requirements.txt
  python download_and_convert.py

El script crea `assets/` si no existe y sobrescribe archivos con el mismo nombre.
"""
import json
from pathlib import Path
import sys
import requests
from PIL import Image
from io import BytesIO

ASSETS_DIR = Path('assets')
IMAGES_JSON = Path('images.json')

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def download_image(url: str) -> Image.Image:
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert('RGB')

def save_webp(img: Image.Image, out_path: Path, quality: int = 85):
    ensure_dir(out_path.parent)
    img.save(out_path, format='WEBP', quality=quality, method=6)

def main():
    if not IMAGES_JSON.exists():
        print(f'ERROR: crea un archivo `images.json` en {Path.cwd()} con mapping nombre->url')
        print('Ejemplo: {"hero.webp":"https://images.example.com/hero.jpg"}')
        sys.exit(1)

    data = json.loads(IMAGES_JSON.read_text(encoding='utf-8'))
    ensure_dir(ASSETS_DIR)

    for name, url in data.items():
        out_path = ASSETS_DIR / name
        try:
            print(f'Descargando {url} ...')
            img = download_image(url)
            print(f'Convirtiendo y guardando {out_path} ...')
            save_webp(img, out_path, quality=85)
        except Exception as e:
            print(f'ERROR al procesar {url}: {e}')

    print('Proceso terminado. Revisa la carpeta assets/ para los WebP generados.')

if __name__ == '__main__':
    main()
