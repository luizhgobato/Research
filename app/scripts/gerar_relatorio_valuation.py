#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════════════════════════════
# ALINHA O VALUATION DOS 14 RELATÓRIOS EMBUTIDOS AO MOTOR — analise/tetos.json → index.html
# ══════════════════════════════════════════════════════════════════════════════════════════
# POR QUE EXISTE — o usuário abriu um relatório e leu, no bloco de valuation:
#
#     "Preço justo = média dos 2 métodos, ambos com g=5%. Preço teto = preço justo × 0,85."
#
# e respondeu: "aqui no tooltip aparece que você está fazendo mediana de dois métodos, eu já
# disse que não quero dessa forma — você precisa entender o que estou pedindo e implementar".
#
# Ele está certo e o erro era meu: eu tinha trocado o motor do RADAR para método único e
# deixado os RELATÓRIOS com o valuation antigo, escrito à mão em datas diferentes, cada um com
# sua própria média de métodos e sua própria margem de 15%. A mesma empresa mostrava uma conta
# na tabela e outra no relatório — que é exatamente a queixa que abriu esta linha de trabalho
# ("não faz sentido eu ter um valor no relatório e outro no radar").
#
# O QUE ESTE SCRIPT FAZ: reescreve, em cada relatório, o bloco `valuation`, o `precoTeto` do
# veredicto e o cabeçalho, a partir de analise/tetos.json. Uma fonte, dois lugares.
#
# ⚠️ O QUE ELE NÃO TOCA, de propósito: a PROSA do relatório (tese, riscos, gatilhos, bloco de
# descobertas). Aquilo é análise escrita com data e fonte declaradas; reescrever texto de
# análise a partir de um JSON seria inventar. Só os NÚMEROS de valuation são regenerados — e o
# `blocoCopiavel`, onde o rótulo "Preço-teto" é trocado pelo valor novo, porque ele é um
# resumo colável que sai do app e não pode carregar número contraditório.
import json, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TETOS = RAIZ / 'analise' / 'tetos.json'
HTML = RAIZ / 'index.html'


def brl(v):
    return f'R$ {v:,.2f}'.replace(',', '§').replace('.', ',').replace('§', '.')


def ptbr(t):
    return re.sub(r'(\d)\.(\d)', r'\1,\2', t)


def num_br(txt):
    if txt is None: return None
    m = re.search(r'-?\d[\d.]*,\d+|-?\d+[.,]?\d*', str(txt))
    if not m: return None
    v = m.group(0)
    v = re.sub(r'\.(?=\d{3}\b)', '', v).replace(',', '.')
    try: return float(v)
    except ValueError: return None


def bloco_valuation(t, r):
    """O novo `valuation`: UM método que decide, os outros como verificação declarada."""
    met = (r.get('metodos') or [{}])[0]
    justo = r['justo']
    verif = [m for m in (r.get('metodos') or [])[1:] if m.get('justo')]
    return {
        'criterio': met.get('chave') or '—',
        'metodos': [{'metodo': ptbr(met.get('conta') or met.get('motor') or ''),
                     'precoJusto': brl(justo)}],
        'origemMult': ptbr(met.get('origemMult') or ''),
        'precoJusto': brl(justo),
        # Sem prefixo "chave —": a conta já nomeia o múltiplo, e repetir dava
        # "E/P — E/P: P/L 14,54x" na tela.
        'verificacao': [{'metodo': ptbr(m.get('conta') or m.get('motor') or ''),
                         'precoJusto': brl(m['justo'])} for m in verif],
        'nota': (f'Método ÚNICO: {met.get("chave")}. O preço justo é o fundamento projetado '
                 f'multiplicado pelo múltiplo que a empresa deve negociar — não é média nem '
                 f'mediana de métodos diferentes. '
                 + (f'Os {len(verif)} método(s) de verificação abaixo são calculados para '
                    f'comparação e NÃO entram na conta. ' if verif else '')
                 + 'Mesmo número da coluna Preço Justo do Radar, gerado pela mesma fonte '
                   '(analise/tetos.json). Ver METODOLOGIA_ANALISE.md seção 31.'),
    }


def main():
    tetos = json.load(open(TETOS, encoding='utf-8'))
    s = HTML.read_text(encoding='utf-8')
    feitos, sem = [], []

    # ⚠️ DE TRÁS PARA A FRENTE. A primeira versão iterava do começo e reescrevia `s` dentro
    # do laço — os offsets das próximas correspondências, calculados sobre o texto ANTIGO,
    # apontavam para o lugar errado depois da primeira substituição, e o script alinhava
    # 1 relatório de 14 sem erro nenhum. Processar de trás para frente mantém válidos todos
    # os offsets ainda não usados.
    marcas = list(re.finditer(r'\n(\s*)"ticker": "([A-Z0-9]+)",\n', s))
    for i in range(len(marcas) - 1, -1, -1):
        m = marcas[i]
        t = m.group(2)
        r = tetos.get(t) or {}
        justo = r.get('justo')
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(s)
        bloco = s[m.start():fim]
        if '"valuation"' not in bloco:
            continue

        # ── 1 · o objeto `valuation` inteiro ──────────────────────────────────────────
        mv = re.search(r'(\n(\s*)"valuation": )\{.*?\n\2\}', bloco, re.S)
        if not mv:
            sem.append(f'{t} (valuation nao delimitado)'); continue
        ind = mv.group(2)
        if justo and justo > 0:
            obj = bloco_valuation(t, r)
        else:
            motivo = (r.get('nota') or 'sem motor aplicavel').split('||')[0].strip()
            obj = {'criterio': '—', 'metodos': [], 'origemMult': '', 'precoJusto': None,
                   'verificacao': [], 'nota': 'SEM PREÇO JUSTO. ' + motivo}
        txt = json.dumps(obj, ensure_ascii=False, indent=2)
        txt = '\n'.join((ind + l) if j else l for j, l in enumerate(txt.split('\n')))
        novo = bloco[:mv.start()] + mv.group(1) + txt + bloco[mv.end():]

        # ── 2 · `precoTeto` do veredicto e do cabecalho viram `precoJusto` ────────────
        alvo = brl(justo) if (justo and justo > 0) else '—'
        novo = re.sub(r'"precoTeto": "[^"]*"', f'"precoJusto": "{alvo}"', novo)

        # ── 3 · a margem do veredicto, recalculada contra a cotacao DO RELATORIO ──────
        # Nao contra a cotacao ao vivo: o relatorio e um retrato datado, e trocar so um dos
        # dois numeros faria a conta nao fechar dentro da propria pagina.
        mc = re.search(r'"cotacao": "([^"]*)"', novo)
        cot = num_br(mc.group(1)) if mc else None
        if cot and justo:
            mg = f'{(justo - cot) / justo * 100:+.1f}%'.replace('.', ',')
            novo = re.sub(r'"margem": "[^"]*"', f'"margem": "{mg}"', novo, count=1)

        # ── 4 · o bloco colavel nao pode sair do app com numero contraditorio ─────────
        if justo and justo > 0:
            novo = re.sub(r'Preço[- ][Tt]eto:? R\$ ?[\d.,]+', f'Preço justo: {alvo}', novo)
            novo = novo.replace('| Preço Teto |', '| Preço justo |')

        s = s[:m.start()] + novo + s[fim:]
        feitos.append(t)
    feitos.reverse()

    HTML.write_text(s, encoding='utf-8', newline='')
    print(f'{len(feitos)} relatórios alinhados ao motor: {", ".join(feitos)}')
    if sem:
        print('NÃO alterados: ' + ', '.join(sem))


if __name__ == '__main__':
    main()
