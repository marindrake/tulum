from PIL import Image, ImageDraw, ImageFont
import os

# Create a 32x32 favicon with a simple, bold design
size = 32
img = Image.new('RGB', (size, size), color='#FFFFFF')
draw = ImageDraw.Draw(img)

# Draw a circular background with gradient effect
for i in range(size//2):
    color_val = int(226 - (i * 20 / (size//2)))
    color = (max(color_val, 180), max(85 - i, 50), max(43 - i, 20))
    draw.ellipse([i, i, size-i-1, size-i-1], fill=color)

# Try to use a bold font, fall back to default if not available
try:
    # Try common Windows fonts
    font = ImageFont.truetype("arialbd.ttf", 22)
except:
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
    except:
        font = ImageFont.load_default()

# Draw the letter "T" in the center
text = "T"
# Get text size
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2 - 2

# Draw white text with shadow for better visibility
draw.text((x+1, y+1), text, fill='#8a2b10', font=font)
draw.text((x, y), text, fill='#FFFFFF', font=font)

# Save as favicon.ico
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'favicon.ico')
img.save(output_path, format='ICO', sizes=[(32, 32), (16, 16)])
print(f"Favicon creado: {output_path}")

# Also create a 180x180 for apple-touch-icon
apple_size = 180
apple_img = Image.new('RGB', (apple_size, apple_size), color='#FFFFFF')
apple_draw = ImageDraw.Draw(apple_img)

# Draw circular background
for i in range(apple_size//2):
    color_val = int(226 - (i * 20 / (apple_size//2)))
    color = (max(color_val, 180), max(85 - i, 50), max(43 - i, 20))
    apple_draw.ellipse([i, i, apple_size-i-1, apple_size-i-1], fill=color)

# Draw letter T
try:
    apple_font = ImageFont.truetype("arialbd.ttf", 120)
except:
    try:
        apple_font = ImageFont.truetype("Arial.ttf", 120)
    except:
        apple_font = ImageFont.load_default()

bbox = apple_draw.textbbox((0, 0), text, font=apple_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (apple_size - text_width) // 2
y = (apple_size - text_height) // 2 - 10

apple_draw.text((x+2, y+2), text, fill='#8a2b10', font=apple_font)
apple_draw.text((x, y), text, fill='#FFFFFF', font=apple_font)

apple_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'apple-touch-icon.png')
apple_img.save(apple_path, format='PNG')
print(f"Apple touch icon creado: {apple_path}")
