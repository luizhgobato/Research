#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# SINCRONIZA O TOGGLE "MINHA CARTEIRA" DO RADAR COM AS TABELAS DE POSIÇÃO — 16/09/2026
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pedido do usuário: o toggle `data-carteira` do Radar (marca quais ações "são da carteira")
# desmarcava sozinho. Já tinha um fix de 14/09 (gravação por ticker, não por índice do DOM),
# mas o problema real continuava: a marcação vivia só no localStorage do navegador — some ao
# limpar dados do site, trocar de aparelho ou usar aba anônima. E o PADRÃO gravado no arquivo
# já estava desatualizado (ITUB3 e ALOS3 fora, quando deviam estar dentro).
#
# A fonte de verdade que o usuário pediu para usar: as tabelas "Carteira Luiz" e "Carteira
# Flavia" que já existem no site (tbody#luizPosBody / tbody#flaviaPosBody), NÃO a Redentia.
# Este script lê os tickers dessas duas tabelas, faz a união, e grava `data-carteira="true"`
# em cada linha do Radar que estiver na união — `"false"` no resto. Roda toda vez que alguém
# muda uma posição nas tabelas (compra/venda de ativo), então o Radar nunca mais fica preso a
# um toggle manual desmarcado sozinho.
#
# ⚠️ 25/09/2026 — ESTE SCRIPT É A ÚNICA COISA NO PROJETO INTEIRO QUE ESCREVE `data-carteira`.
# Até essa data o js/graficos.js do CLIENTE também escrevia — um checkbox clicável que gravava
# um snapshot no localStorage do navegador e o REAPLICAVA por cima do arquivo em toda carga de
# página. Duas fontes de verdade para o mesmo atributo, e o navegador vencia: quando este
# script marcava a GMAT3 como `true`, o snapshot antigo do usuário (de antes dela existir)
# desfazia a marca no instante seguinte, sem erro, sem aviso. Era exatamente esse zumbi que o
# usuário via como "a toggle não marca os ativos certos". O checkbox foi removido — o Radar
# agora só EXIBE o que este script calcula; não há mais nada além dele para desalinhar. Ver
# seção 45 da metodologia.
#
# LFTB11 (Tesouro Selic) é ignorado: é renda fixa, não existe linha correspondente no Radar
# (que só lista ações).
#
# Uso:  python3 scripts/atualizar_carteira_radar.py
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INDEX = RAIZ / 'index.html'
RADAR = RAIZ / 'data' / 'radar-rows.data.js'

IGNORAR = {'LFTB11.SA'}  # classes de ativo sem linha no Radar (renda fixa, ETF de RF etc.)


def tickers_da_tabela(html: str, tbody_id: str) -> set:
    m = re.search(r'<tbody id="' + tbody_id + r'"[^>]*>(.*?)</tbody>', html, re.S)
    if not m:
        raise SystemExit(f'tbody#{tbody_id} não encontrado em index.html — layout mudou?')
    return set(re.findall(r'data-ticker="([^"]+)"', m.group(1)))


def main():
    html = INDEX.read_text(encoding='utf-8')
    uniao = (tickers_da_tabela(html, 'luizPosBody') | tickers_da_tabela(html, 'flaviaPosBody')) - IGNORAR

    radar = RADAR.read_text(encoding='utf-8')
    mudancas = []

    def processa_linha(m):
        linha = m.group(0)
        tm = re.search(r'data-ticker="([^"]+)"', linha)
        cm = re.search(r'data-carteira="([^"]+)"', linha)
        if not tm or not cm:
            return linha
        ticker, atual = tm.group(1), cm.group(1)
        novo = 'true' if ticker in uniao else 'false'
        if atual != novo:
            mudancas.append((ticker, atual, novo))
            linha = linha.replace(f'data-carteira="{atual}"', f'data-carteira="{novo}"', 1)
        return linha

    radar2 = re.sub(r'<tr data-ticker="[^"]+".*?>', processa_linha, radar)

    if mudancas:
        RADAR.write_text(radar2, encoding='utf-8')
        print(f'OK: {len(mudancas)} ticker(s) atualizados em radar-rows.data.js:')
        for ticker, antes, depois in mudancas:
            print(f'  {ticker}: {antes} -> {depois}')
    else:
        print('Nada a atualizar — data-carteira já bate com as tabelas de posição.')

    print(f'\nCarteira consolidada (Luiz ∪ Flavia), {len(uniao)} ticker(s): {sorted(uniao)}')


if __name__ == '__main__':
    main()
