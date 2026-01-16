#!/usr/bin/env python3
"""
Convierte PROPUESTA_TULUM.md a PDF con formato profesional
"""

import markdown
import os
from pathlib import Path

# Leer el archivo Markdown
md_file = Path(__file__).parent.parent / 'PROPUESTA_TULUM.md'
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convertir Markdown a HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'nl2br'])

# CSS para el PDF
css = """
<style>
    @page {
        size: letter;
        margin: 1.5cm;
    }
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 210mm;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #e2552b;
        border-bottom: 3px solid #f6a623;
        padding-bottom: 10px;
        font-size: 28px;
    }
    h2 {
        color: #e2552b;
        margin-top: 30px;
        font-size: 22px;
    }
    h3 {
        color: #555;
        font-size: 18px;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        font-size: 14px;
    }
    th {
        background-color: #e2552b;
        color: white;
        padding: 12px;
        text-align: left;
    }
    td {
        border: 1px solid #ddd;
        padding: 10px;
    }
    tr:nth-child(even) {
        background-color: #f9f7f5;
    }
    ul, ol {
        margin: 15px 0;
    }
    li {
        margin: 8px 0;
    }
    hr {
        border: none;
        border-top: 2px solid #f6a623;
        margin: 30px 0;
    }
    .highlight {
        background-color: #fff3e0;
        padding: 15px;
        border-left: 4px solid #f6a623;
        margin: 20px 0;
    }
    blockquote {
        border-left: 4px solid #e2552b;
        margin: 20px 0;
        padding-left: 20px;
        color: #555;
        font-style: italic;
    }
</style>
"""

# HTML completo
html_full = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Propuesta - Tulum Dessert & Snacks</title>
    {css}
</head>
<body>
    {html_content}
</body>
</html>
"""

# Guardar HTML temporal
html_file = Path(__file__).parent.parent / 'PROPUESTA_TULUM.html'
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_full)

print(f"✅ HTML generado: {html_file}")

# Intentar convertir a PDF con weasyprint
try:
    from weasyprint import HTML
    pdf_file = Path(__file__).parent.parent / 'PROPUESTA_TULUM.pdf'
    HTML(string=html_full).write_pdf(pdf_file)
    print(f"✅ PDF generado: {pdf_file}")
except ImportError:
    print("⚠️  weasyprint no está instalado.")
    print("📄 Puedes abrir PROPUESTA_TULUM.html en tu navegador y usar 'Imprimir -> Guardar como PDF'")
    print("💡 O instala weasyprint: pip install weasyprint")
except Exception as e:
    print(f"⚠️  Error al generar PDF: {e}")
    print("📄 Abre PROPUESTA_TULUM.html en tu navegador y guarda como PDF")
