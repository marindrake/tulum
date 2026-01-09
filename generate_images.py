#!/usr/bin/env python3
"""
Generador simple de imágenes fotorealistas WebP para el prototipo.

Requisitos:
 - Tener un modelo de Stable Diffusion disponible en Hugging Face (p. ej. "runwayml/stable-diffusion-v1-5").
 - Definir la variable de entorno HF_TOKEN con tu token de Hugging Face.

Uso:
  pip install -r requirements.txt
  set HF_TOKEN=tu_token  # Windows PowerShell: $env:HF_TOKEN = "tu_token"
  python generate_images.py

El script genera las imágenes en `assets/` como WebP.
"""
import os
from pathlib import Path
from PIL import Image

def ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def save_webp(img, path: Path, quality=90):
    ensure_dir(path)
    img.save(path, format='WEBP', quality=quality)

def main():
    try:
        from diffusers import StableDiffusionPipeline
        import torch
    except Exception as e:
        print("Falta dependencias. Ejecuta: pip install -r requirements.txt")
        raise

    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        print('ERROR: define HF_TOKEN como variable de entorno con tu token de Hugging Face')
        return

    model_id = "runwayml/stable-diffusion-v1-5"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Cargando modelo {model_id} en {device} (esto puede tardar)...")
    pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=hf_token)
    pipe = pipe.to(device)

    assets = Path('assets')
    tasks = [
        {"name":"hero","prompt":"A photorealistic composition of tropical desserts on a wooden table with palm leaves in the background, soft natural light, shallow depth of field, vibrant colors, 16:9" ,"w":1600,"h":600, "out":"assets/hero.webp"},
        {"name":"thumb-flan","prompt":"Close-up photorealistic flan with coconut flakes and caramel sauce on a small plate, warm lighting, shallow depth of field","w":800,"h":600, "out":"assets/thumb-flan.webp"},
        {"name":"thumb-trifle","prompt":"Photorealistic dessert cup with fresh strawberries and whipped cream, studio lighting, appetizing composition","w":800,"h":600, "out":"assets/thumb-trifle.webp"},
        {"name":"thumb-roll","prompt":"Golden baked sweet roll filled with caramel and citrus, close up, soft warm light","w":800,"h":600, "out":"assets/thumb-roll.webp"},
        {"name":"gallery1","prompt":"Assorted Mexican desserts on a colorful plate, photorealistic, natural light","w":800,"h":600, "out":"assets/gallery1.webp"},
        {"name":"gallery2","prompt":"Fresh strawberries with cream in a small bowl, photorealistic, bright mood","w":800,"h":600, "out":"assets/gallery2.webp"},
        {"name":"gallery3","prompt":"Rolled pastry with sugar glaze on wooden board, photorealistic","w":800,"h":600, "out":"assets/gallery3.webp"},
        {"name":"gallery4","prompt":"Close up of small dessert bites on a plate, photorealistic, cozy lighting","w":800,"h":600, "out":"assets/gallery4.webp"},
    ]

    for t in tasks:
        outp = Path(t['out'])
        if outp.exists():
            print(f"Skipping existing {outp}")
            continue
        print(f"Generando {t['name']} -> {outp} ...")
        image = pipe(t['prompt'], width=t['w'], height=t['h']).images[0]
        if image.mode != 'RGB':
            image = image.convert('RGB')
        save_webp(image, outp, quality=90)
        print(f"Guardado {outp}")

    print("Todas las imágenes fueron generadas (o saltadas si ya existían).")

if __name__ == '__main__':
    main()
