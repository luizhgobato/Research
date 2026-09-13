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
# ⚠️ A PÁGINA PUBLICADA. O GitHub Pages serve este arquivo na raiz do repositório, e até
# 13/09/2026 copiá-lo para lá era um `cp` manual documentado no README — que eu esqueci duas
# vezes seguidas. O resultado é a pior falha possível neste projeto: o app/ tem a correção, o
# commit está publicado, e o usuário continua vendo a versão antiga na tela, sem nada quebrar.
# Foi assim que a tooltip "Justo = mediana dos 2 métodos" sobreviveu a duas publicações depois
# de eu ter removido a mediana do motor. Passo manual em pipeline é passo que não existe.
PUBLICADA = ROOT.parent / "Analista Investimento.html"

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
PUBLICADA.write_text(html, encoding="utf-8", newline="\n")
print(f"OK: {OUT.name} ({len(html):,} bytes)")
print(f"OK: {PUBLICADA.name} — a página que o GitHub Pages serve")
