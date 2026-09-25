#!/usr/bin/env python3
"""Extrai o JSON de app/index.html#reportsData para data/reports.json.

O projeto carteiras (luizhgobato/carteiras) busca esse arquivo ao vivo via
raw.githubusercontent.com no carregamento da página, pra mostrar o veredito/tese
de cada ticker dentro do dashboard de carteira sem precisar de cópia manual.

Rodar depois de qualquer edição em app/index.html que mude o conteúdo de
<script id="reportsData">, e commitar o data/reports.json resultante.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "app" / "index.html"
DEST = ROOT / "data" / "reports.json"

MARKER = '<script id="reportsData" type="application/json">'


def main():
    txt = SRC.read_text(encoding="utf-8")
    i = txt.index(MARKER)
    start = txt.index(">", i) + 1
    end = txt.index("</script>", start)
    raw = txt[start:end]

    data = json.loads(raw)  # valida antes de escrever

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(data)} tickers exportados para {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
