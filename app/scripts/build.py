# -*- coding: utf-8 -*-
"""Exporta uma cópia STANDALONE (CSS+JS embutidos) para exports/.

Uso:  python scripts/build.py
O arquivo principal é index.html (modular, carrega js/ e css/).
Este script só serve para gerar uma cópia portátil para compartilhar.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "exports" / "Analista Investimento standalone.html"

html = (ROOT / "index.html").read_text(encoding="utf-8")

# CSS inline
css = (ROOT / "css" / "styles.css").read_text(encoding="utf-8")
html = html.replace(
    '<link rel="stylesheet" href="css/styles.css">',
    "<style>\n" + css + "</style>",
)

# JS inline (mantém a ordem dos <script src>)
def inline_js(m):
    src = m.group(1)
    code = (ROOT / src).read_text(encoding="utf-8")
    return "<script>\n" + code + "</script>"

html = re.sub(r'<script src="([^"]+)"></script>', inline_js, html)

# Aviso de arquivo gerado
OUT.parent.mkdir(exist_ok=True)
html = html.replace(
    "<html lang=",
    "<!-- CÓPIA STANDALONE gerada por scripts/build.py — não editar. -->\n<html lang=",
    1,
)

OUT.write_text(html, encoding="utf-8", newline="\n")
print(f"OK: {OUT.name} ({len(html):,} bytes)")
