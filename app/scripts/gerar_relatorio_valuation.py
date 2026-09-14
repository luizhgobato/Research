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
import json
import statistics as st, re
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


# ══════════════════════════════════════════════════════════════════════════════════════════
# A REGRA DO RELATÓRIO — o que cada um tem que mostrar, e por quê
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pedido do usuário: "nos relatórios das empresas eu quero ver o cálculo de múltiplo e a regra
# que adotamos para cada empresa, e também um detalhamento do LPA projetado considerando 3
# cenários — deixe essa regra bem estabelecida para o momento de gerar cada relatório. Além
# disso quero uma análise qualitativa da empresa".
#
# A regra, fixada aqui para todo relatório gerado a partir de 14/09/2026:
#
#  1 · REGRA DO MÚLTIPLO. O relatório declara, nesta ordem: (a) qual método decide e POR QUE
#      esse e não outro — a razão é do NEGÓCIO, não estatística; (b) a ÂNCORA (a mediana do
#      próprio múltiplo na janela 2021→) e o AJUSTE DE ROE que a corrige, cada um com seu
#      número; (c) o múltiplo final e a conta completa até o preço justo.
#      ⚠️ ATUALIZADO EM 14/09/2026: antes eram "as duas metades, a própria série e a dos
#      pares". O múltiplo do setor saiu da conta por decisão do usuário — a mediana do
#      segmento mistura empresas com rentabilidade e risco diferentes, e quem passa a trazer
#      essa informação é o ROE da própria empresa contra a própria média.
#
#  2 · LPA EM TRÊS CENÁRIOS. Um número só de LPA esconde que ele é uma projeção. Os três
#      cenários usam a MESMA base e variam só o crescimento:
#        · CONSERVADOR — crescimento ZERO. A empresa repete o que acabou de fazer. É o piso
#          defensável sem premissa nenhuma: não supõe deterioração, só ausência de avanço.
#        · BASE — a taxa que o motor usa (ou o lucro declarado no relatório, quando existe).
#        · OTIMISTA — a taxa do base vezes 1,5, limitada ao CRESC_CAP de 25%.
#      O fator 1,5 é PREMISSA DECLARADA, não calibração: com 6 anos de série não há amostra
#      para calibrar dispersão de crescimento, e fingir que há seria o superajuste que o teste
#      de permutação existe para denunciar (mesma prateleira do juro real de 5,5%, seção 25.3).
#      Cada cenário mostra também o PREÇO JUSTO correspondente, que é o que decide.
#
#  3 · ANÁLISE QUALITATIVA. Duas origens, sempre separadas e rotuladas:
#        · A TESE ESCRITA, quando o relatório tem — análise com data e fontes declaradas.
#        · A LEITURA DERIVADA DOS DADOS, gerada aqui: rentabilidade, alavancagem,
#          consistência do lucro, sustentabilidade do dividendo e quebra de série. São fatos
#          do HIST_SEED traduzidos para frase, e o rótulo diz isso — nunca se passa por
#          análise fundamentalista escrita por alguém.
#      ⚠️ O que NÃO se faz: inventar tese para empresa sem relatório. Dezenove das trinta e
#      três não têm análise escrita; elas recebem a leitura derivada e um aviso de que a tese
#      está pendente, não um texto plausível gerado do nada.

CRESC_OTIMISTA = 1.5     # multiplicador do cenário otimista sobre a taxa base — ver regra 2

# POR QUE ESTE MÉTODO E NÃO OUTRO, por grupo. A razão é sempre do NEGÓCIO — o que a
# contabilidade daquele setor distorce —, nunca "o backtest gostou mais".
REGRA_METODO = {
    'SHOP': ('P/FFO',
             'Shopping registra o imóvel a CUSTO e o deprecia como se ele se desgastasse. Só '
             'que shopping bem administrado não perde valor, ganha — e o peso dessa depreciação '
             'depende de política contábil (a ALOS3 deprecia 29% do EBITDA, a MULT3 6%, porque '
             'a MULT3 usa valor justo). Lucro líquido de shopping mede contabilidade junto com '
             'operação. FFO = lucro + depreciação devolve a despesa que não sai caixa.'),
    'CICL': ('EV/EBITDA sobre a média do ciclo',
             'Cíclica de commodity tem lucro de UM ano que é fundo ou pico, nunca capacidade '
             'normal — a KLBN11 saiu com LPA de R$ 0,09 no fundo da celulose. Multiplicar isso '
             'por um múltiplo trata ano ruim como normalidade. O EBITDA médio de seis anos '
             'atravessa o ciclo, e o EV inclui a dívida, que em cíclica alavancada é metade '
             'da história.'),
    'NAV':  ('Paridade com a investida',
             'O "lucro" de uma holding é equivalência patrimonial: ele herda o ciclo da '
             'controlada amplificado. A BRAP4 teve lucro caindo de R$ 8,1 bi para R$ 0,6 bi '
             'acompanhando o minério, e nenhum múltiplo sobre esse lucro descreve o valor de '
             'uma participação na Vale. A razão entre os dois preços mede o desconto de '
             'holding que o mercado de fato pratica.'),
    'FIN':  ('P/L', 'Banco ganha no spread de crédito e o lucro é a medida direta disso. '
             'EV não se aplica: o passivo é a matéria-prima (depósito), não alavancagem.'),
    'SEG':  ('P/L', 'Seguradora ganha na subscrição e no float, e o lucro captura os dois. '
             'Como em banco, EV/EBITDA não se aplica — a provisão técnica é insumo, não dívida. '
             'A separação entre pares de banco e de seguradora, feita em 13/09/2026, deixou '
             'de afetar o preço justo em 14/09 — o múltiplo do setor saiu da conta —, mas '
             'segue valendo para o fallback de quem não tem série própria utilizável.'),
}
REGRA_PADRAO = ('P/L',
                'Caso geral: o lucro é a medida do que o negócio entrega ao acionista, e o '
                'P/L é o preço que o mercado paga por ele. Os múltiplos de EV entram só onde '
                'a dívida financia o ativo operacional e distorce a comparação por lucro.')


def faixa_do_multiplo(t, A, chave, M, mult):
    """(p25, p75) do múltiplo da PRÓPRIA empresa, recentrados no múltiplo aplicado.

    ⚠️ 14/09/2026 — POR QUE OS CENÁRIOS PASSARAM A MOVER O MÚLTIPLO TAMBÉM.
    Pedido do usuário: "os cenários conservador, base e otimista estão muito próximos um do
    outro... dois centavos de diferença entre um e outro não faz diferença, precisamos ser
    mais agressivos". Ele está certo, e o defeito era estrutural: os três cenários variavam
    SÓ o crescimento do fundamento e mantinham o múltiplo fixo. Na ALOS3 isso dava R$ 27,91 ·
    R$ 30,07 · R$ 31,29 — uma amplitude de 12%, que é menos que a oscilação de um mês.

    Só que preço justo = fundamento × múltiplo, e são DUAS variáveis. Um cenário pessimista
    de verdade é o que supõe as duas piorando juntas: a empresa cresce menos E o mercado paga
    menos por esse resultado. É assim que o mercado se move de fato — múltiplo comprime
    justamente quando o resultado decepciona.

    As pontas NÃO são inventadas: são o percentil 25 e 75 do múltiplo que a PRÓPRIA empresa
    já negociou, a mesma faixa que o motor publica na coluna Preço Justo. Recentradas no
    múltiplo aplicado pela mesma `recentrar` do motor, para o base cair exatamente no meio.
    """
    serie = {
        'P/FFO': lambda: [v for _y, v in M['serie_pffo'](t, A)] if 'serie_pffo' in M else None,
        'P/VP': lambda: M['serie_pvp'](t, A),
        'EV/Receita': lambda: M['serie'](A, 'evEbitda'),
    }
    vals = None
    if chave in ('E/P', 'P/L'):
        val, _q = M['anos_validos'](A)
        vals = [v for y in val for v in (M['pl_ano'](t, A, y),) if v]
    elif chave == 'P/FFO':
        val, _q = M['anos_validos'](A)
        vals = [v for y in val for v in (M['pffo_ano'](t, A, y),) if v]
    elif chave == 'P/VP':
        vals = M['serie_pvp'](t, A)
    if not vals or len(vals) < 3:
        return None
    p25, p50, p75, _n = M['faixa_com_tendencia'](vals, truncar=False)
    p25, p75 = M['recentrar'](p25, p50, p75, mult)
    return (min(p25, mult), max(p75, mult))


def serie_do_multiplo(t, A, chave, M):
    """[{ano, multiplo, roe, fundamento}] — a série que o motor de fato usou, ano a ano.

    Pedido do usuário: "quero acrescentar o ROE e P/L histórico que está sendo utilizado,
    quebrado por ano". Até aqui o relatório dizia "o P/FFO mediano ao longo de 3 anos
    (8,13x)" e o leitor tinha que confiar. Agora ele vê os três anos, confere a mediana e
    enxerga se o múltiplo atual está acima ou abaixo do que a empresa costuma negociar.
    """
    val, q = M['anos_validos'](A)
    roe_hoje, pares_roe, metrica = M['serie_roe'](t, A)
    roe = dict(pares_roe)
    pap = M['papeis'](t, A)
    ff = dict(M['serie_ffo'](t, A)) if chave == 'P/FFO' else {}
    linhas, crus = [], []
    for y in val:
        d = A[y] or {}
        m = f_val = None
        if chave in ('E/P', 'P/L'):
            m = M['pl_ano'](t, A, y)
            f_val = (d.get('lucrolin') or 0) / 1e9
        elif chave == 'P/FFO':
            m = M['pffo_ano'](t, A, y)          # mesma conta do motor, não reimplementada
            f_val = (ff[y] / 1e9) if y in ff else None
        elif chave == 'P/VP':
            fm = M['fator_multiplo'](t, A)
            m = (d.get('pvp') or 0) / fm or None
            f_val = None
        if m is None:
            continue
        crus.append(m)
        linhas.append({
            'ano': str(y),
            'multiplo': f'{ptbr(f"{m:.2f}")}x',
            'roe': (f'{ptbr(f"{roe[y]:.1f}")}%' if y in roe else '—'),
            'fundamento': (f'R$ {ptbr(f"{f_val:.2f}")} bi' if f_val else '—'),
            'preco': (brl(d['preco']) if d.get('preco') else '—'),
        })
    # ⚠️ MEDIANA SOBRE OS VALORES CRUS, não sobre o que a tabela imprime. A primeira versão
    # relia as strings já arredondadas (6,40 · 9,08 · 8,14) e publicava 8,14x de mediana
    # enquanto o motor, sobre os mesmos anos sem arredondar, usa 8,13x. Dois números para a
    # mesma conta na mesma tela — o defeito que este projeto passou a semana inteira caçando.
    vals = crus
    rvals = [roe[y] for y in val if y in roe]
    return {
        'metrica': chave,
        'metricaRoe': metrica,
        'linhas': linhas,
        'mediana': (f'{ptbr(f"{st.median(vals):.2f}")}x' if vals else '—'),
        'roeMediano': (f'{ptbr(f"{st.median(rvals):.1f}")}%' if rvals else '—'),
        'roeHoje': (f'{ptbr(f"{roe_hoje:.1f}")}%' if roe_hoje else '—'),
        'quebra': (f'Série restrita a partir de {q} por QUEBRA DE SÉRIE — os anos anteriores '
                   f'descrevem outra empresa (evento societário) e não servem de âncora.'
                   if q else ''),
    }


def comparacao_pares(t, A, M, H):
    """Tabela do ticker contra os pares do mesmo motor. Pedido do usuário: "sinto falta de
    comparação com os concorrentes".

    Compara o que É comparável: o múltiplo aplicado, a rentabilidade na MESMA definição
    (serie_roe, que em shopping usa FFO) e o tamanho. Não compara preço justo — cada empresa
    tem o seu e comparar dois números que saem de fundamentos diferentes não diz nada.
    """
    grupo = M['MOTOR'].get(t)
    if not grupo:
        return None
    tetos = json.loads((RAIZ / 'analise/tetos.json').read_text())
    linhas = []
    for o in sorted(H):
        if M['MOTOR'].get(o) != grupo:
            continue
        r = tetos.get(o) or {}
        mp = [m for m in r.get('metodos', []) if m.get('papel') == 'principal']
        if not mp:
            continue
        mm = re.findall(r'([\d.]+)x', mp[0].get('conta', ''))
        hoje, pares_roe, metrica = M['serie_roe'](o, H[o])
        co = H[o][max(H[o])]
        pap = M['papeis'](o, H[o])
        mg = co.get('mgLiq')
        de = co.get('divEbitda')
        pr = co.get('preco')
        roe_med_v = st.median([v for _y, v in pares_roe]) if pares_roe else None
        vm = (pr * pap / 1e9) if (pap and pr) else None
        linhas.append({
            # ⚠️ 'ativo', NÃO 'ticker'. A primeira versão usou 'ticker' e quebrou o próprio
            # gerador: `main` delimita cada relatório procurando a linha `"ticker": "XXX",`, e
            # as linhas desta tabela passaram a criar fronteiras FANTASMA dentro do objeto
            # valuation — o script via 16 relatórios onde há 14 e recusava a ALOS3 com
            # "valuation nao delimitado". Nome de chave em dado aninhado não pode colidir com
            # marcador estrutural.
            'ativo': o,
            'eu': o == t,
            'metodo': mp[0]['chave'],
            'multiplo': (f'{ptbr(mm[-1])}x' if mm else '—'),
            'roe': (f'{ptbr(f"{hoje:.1f}")}%' if hoje else '—'),
            'roeMed': (f'{ptbr(f"{roe_med_v:.1f}")}%' if roe_med_v is not None else '—'),
            'mgLiq': (f'{ptbr(f"{mg:.1f}")}%' if mg else '—'),
            'valorMercado': (f'R$ {ptbr(f"{vm:.1f}")} bi' if vm else '—'),
            'divEbitda': (f'{ptbr(f"{de:.2f}")}x' if de else '—'),
        })
    if len(linhas) < 2:
        return None
    return {'grupo': grupo, 'metricaRoe': metrica, 'linhas': linhas}


def cenarios_lpa(t, r, M, A):
    """Três cenários do FUNDAMENTO e o preço justo de cada um. Ver a regra 2 acima.

    ⚠️ O FUNDAMENTO NÃO É SEMPRE O LPA, e a conta até o preço justo não é sempre uma
    multiplicação. A primeira versão assumia "LPA × múltiplo" para todo mundo e produziu
    R$ 15,20 de preço justo para a ALOS3 no cenário conservador, contra R$ 27,39 no Radar —
    porque dividia o LUCRO por papéis num método que multiplica o FFO. Três famílias:

      P/L e P/FFO  → fundamento POR AÇÃO × múltiplo
      EV/EBITDA    → (múltiplo × EBITDA − dívida líquida) ÷ papéis
      Paridade     → preço justo da investida × a razão histórica

    Em EV/EBITDA e Paridade o cenário varia o fundamento (EBITDA, preço justo do pai) e o
    preço justo sai pela fórmula da família — não por multiplicação direta.
    """
    met = (r.get('metodos') or [{}])[0]
    chave = met.get('chave') or ''
    conta = met.get('conta') or ''
    grupo = M['MOTOR'].get(t)
    pap = M['papeis'](t, A)
    c = A[max(A)]

    m = re.search(r'×\s*(?:[A-Za-z/]+\s+)?([\d.,]+)x', conta)
    mult = float(m.group(1).replace(',', '.')) if m else None
    if chave == 'Paridade':
        m = re.search(r'×\s*paridade\s*([\d.,]+)', conta)
        mult = float(m.group(1).replace(',', '.')) if m else None
    if not mult:
        return None

    cap = M['CRESC_CAP']
    decl = M['LUCRO_2026_DECLARADO'].get(t)
    g_base, fonte_g = M['crescimento'](t, A, M['H_GLOBAL'])

    # ── qual fundamento, e como ele vira preço ────────────────────────────────────────────
    if chave == 'P/FFO':
        base_val = M['ffo_ano'](t, A, 2025) or M['ffo_ano'](t, A, max(A))
        rot_base = 'FFO do exercício de 2025'
        nome_fund = 'FFO por ação'
        preco = lambda v: (v / pap) * mult if pap else None
        por_acao = lambda v: v / pap if pap else None
    elif chave == 'EV/EBITDA':
        eb = M['serie'](A, 'ebitda')
        base_val = (sum(eb) / len(eb)) if (grupo == 'CICL' and eb) else c.get('ebitda')
        rot_base = ('EBITDA médio de %d anos do ciclo' % len(eb)) if (grupo == 'CICL' and eb) \
                   else 'EBITDA dos últimos 12 meses'
        nome_fund = 'EBITDA'
        dl = c.get('divliq') or 0
        preco = lambda v: (mult * v - dl) / pap if pap else None
        por_acao = lambda v: v / 1e9
    elif chave == 'Paridade':
        pai = M['PARENT'].get(t)
        rp = M['H_GLOBAL'] and pai and M['calcular'](pai, M['H_GLOBAL'][pai])
        base_val = rp.get('justo') if rp else None
        rot_base = f'preço justo de {pai}'
        nome_fund = f'preço justo de {pai}'
        preco = lambda v: v * mult
        por_acao = lambda v: v
    else:
        base_val, rot_base = M['base_projecao'](t, A)
        nome_fund = 'LPA'
        preco = lambda v: (v / pap) * mult if pap else None
        por_acao = lambda v: v / pap if pap else None

    if not base_val or base_val <= 0 or (chave != 'Paridade' and not pap):
        return None

    if decl and chave in ('E/P', 'P/L'):
        g_eff = (decl[0] / base_val - 1) * 100
        _d = decl[1]
        if len(_d) > 150:
            _d = _d[:150].rsplit(' ', 1)[0] + '…'
        premissa_base = f'lucro de 2026 declarado no relatório — {_d}'
    else:
        g_eff = g_base if g_base is not None else 0.0
        premissa_base = fonte_g or 'sem taxa utilizável na base'

    # ⚠️ EM CÍCLICA A SENSIBILIDADE É NO MÚLTIPLO, NÃO NO CRESCIMENTO. O método já usa o
    # EBITDA MÉDIO DE SEIS ANOS — um número que atravessa o ciclo de propósito —, então
    # aplicar taxa de crescimento sobre ele contradiz a escolha: seria projetar a média.
    # A primeira versão fez isso e produziu um cenário "base" ABAIXO do conservador na RANI3
    # (crescimento de −14,6%, que é a queda até o fundo do ciclo). O que varia aqui é o
    # múltiplo, entre o percentil 25 e o 75 da própria série — é o que o relatório da RANI3
    # já fazia à mão ("faixa sensibilizada de 5,0x a 6,0x").
    if chave == 'EV/EBITDA':
        decl_m = M['MULTIPLO_DECLARADO'].get(t)
        if decl_m and decl_m[0] == 'EV/EBITDA' and decl_m[2]:
            # faixa que o PRÓPRIO relatório sensibilizou — vence os percentis da série
            p25, p75 = decl_m[2]
            por_que = ('a faixa sensibilizada no relatório desta empresa', 'do relatório')
        else:
            mult_s = M['serie'](A, 'evEbitda')
            if len(mult_s) >= 4:
                p25, _p50, p75, _n = M['faixa_com_tendencia'](mult_s, limiar_rel=0.12)
            else:
                p25, p75 = (min(mult_s) if mult_s else mult), (max(mult_s) if mult_s else mult)
            por_que = ('o percentil 25 e o 75 da própria série', 'da própria série')
        # garante a ordem: um cenário otimista abaixo do base é sinal de faixa incoerente
        p25, p75 = min(p25, mult), max(p75, mult)
        trio = [('Conservador', p25, f'múltiplo de {ptbr(f"{p25:.2f}")}x — {por_que[0]}, '
                 f'ponta baixa: o ciclo comprime e o mercado paga menos pelo mesmo EBITDA'),
                ('Base', mult, f'o múltiplo que o preço justo usa ({ptbr(f"{mult:.2f}")}x)'),
                ('Otimista', p75, f'múltiplo de {ptbr(f"{p75:.2f}")}x — {por_que[0]}, '
                 f'ponta alta: o ciclo vira e o mercado paga o topo do que já pagou')]
        dl0 = c.get('divliq') or 0
        return {
            'multiplo': f'{ptbr(f"{mult:.2f}")}x',
            'fundamento': 'EBITDA (fixo)',
            'base': f'R$ {ptbr(f"{base_val/1e9:.2f}")} bi ({rot_base}) — NÃO é projetado: '
                    f'a média do ciclo já atravessa pico e fundo',
            'cenarios': [{'cenario': nome,
                          'crescimento': f'{ptbr(f"{mx:.2f}")}x',
                          'lpa': f'R$ {ptbr(f"{base_val/1e9:.2f}")} bi',
                          'precoJusto': brl((mx * base_val - dl0) / pap),
                          'premissa': prem} for nome, mx, prem in trio],
        }

    g_otim = max(-cap, min(g_eff * CRESC_OTIMISTA, cap)) if g_eff >= 0 else g_eff / CRESC_OTIMISTA
    # ⚠️ O CENÁRIO CONSERVADOR PASSA A ENCOLHER, não a ficar parado (14/09/2026).
    # "Crescimento zero" é o cenário em que nada dá errado — não é o pessimista, é o neutro.
    # O piso agora é a MESMA distância do base, para baixo: se o base cresce 7,7%, o
    # conservador encolhe 7,7%. Simétrico, declarado, e sem inventar taxa.
    g_cons = -abs(g_eff) if g_eff else 0.0
    faixa_m = faixa_do_multiplo(t, A, chave, M, mult)
    m_lo, m_hi = faixa_m if faixa_m else (mult, mult)
    nota_m = ('' if not faixa_m else
              f' e múltiplo de {ptbr(f"{m_lo:.2f}")}x (percentil 25 da própria série)')
    nota_M = ('' if not faixa_m else
              f' e múltiplo de {ptbr(f"{m_hi:.2f}")}x (percentil 75 da própria série)')
    linhas = [
        ('Conservador', g_cons, m_lo,
         (f'o fundamento ENCOLHE {ptbr(f"{abs(g_cons):.1f}")}% — a mesma distância do base, '
          f'para baixo' if g_cons else 'crescimento zero — não há taxa utilizável na base')
         + nota_m
         + '. As duas pontas pioram juntas, que é como o mercado se move de fato: múltiplo '
           'comprime justamente quando o resultado decepciona'),
        ('Base', g_eff, mult, premissa_base + f' e o múltiplo que o preço justo aplica '
                                             f'({ptbr(f"{mult:.2f}")}x)'),
        ('Otimista', g_otim, m_hi,
         f'a taxa do base vezes {CRESC_OTIMISTA:g}'.replace('.', ',') +
         f', limitada ao teto de {cap:.0f}%' + nota_M +
         '. Premissa declarada, não calibração — mas as duas pontas do múltiplo são a faixa '
         'que a empresa JÁ negociou, não número inventado'),
    ]
    fmt_f = (lambda v: brl(v)) if chave != 'EV/EBITDA' else (lambda v: f'R$ {ptbr(f"{v:.2f}")} bi')
    saida = []
    for nome, g, mx, prem in linhas:
        v = base_val * (1 + g / 100)
        pj = (v / pap) * mx if (chave != 'Paridade' and pap) else (v * mx)
        if pj is None:
            return None
        saida.append({'cenario': nome,
                      'crescimento': f'{g:+.1f}%'.replace('.', ','),
                      'multiplo': (f'{ptbr(f"{mx:.3f}")}' if chave == 'Paridade'
                                   else f'{ptbr(f"{mx:.2f}")}x'),
                      'lpa': fmt_f(por_acao(v)),
                      'precoJusto': brl(pj),
                      'premissa': prem})
    amp = None
    try:
        lo = min(base_val * (1 + g / 100) / pap * mx for _n, g, mx, _p in linhas)
        hi = max(base_val * (1 + g / 100) / pap * mx for _n, g, mx, _p in linhas)
        amp = f'{ptbr(f"{(hi/lo - 1)*100:.0f}")}%'
    except Exception:
        pass
    return {
        'multiplo': (f'{ptbr(f"{mult:.3f}")}' if chave == 'Paridade' else f'{ptbr(f"{mult:.2f}")}x'),
        'fundamento': nome_fund,
        'base': (f'R$ {ptbr(f"{base_val/1e9:.2f}")} bi ({rot_base})' if chave != 'Paridade'
                 else f'{brl(base_val)} ({rot_base})'),
        'amplitude': amp,
        'variaMultiplo': bool(faixa_m),
        'cenarios': saida,
    }


def leitura_qualitativa(t, M, A):
    """Leitura derivada dos DADOS — nunca se passa por tese escrita. Ver a regra 3 acima."""
    c = A[max(A)]
    pontos = []
    val, q = M['anos_validos'](A)

    roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
    if roes:
        med = sorted(roes)[len(roes) // 2]
        if med >= 20:
            pontos.append(f'Rentabilidade ALTA: ROE mediano de {med:.1f}% em {len(roes)} '
                          f'exercícios. Retorno sobre capital nesse patamar costuma indicar '
                          f'vantagem competitiva ou alavancagem — vale distinguir qual.')
        elif med >= 12:
            pontos.append(f'Rentabilidade razoável: ROE mediano de {med:.1f}%.')
        else:
            pontos.append(f'⚠️ Rentabilidade BAIXA: ROE mediano de {med:.1f}% em {len(roes)} '
                          f'exercícios — abaixo do custo de capital de boa parte do mercado.')
        if len(roes) >= 4:
            recente, antigo = roes[-2:], roes[:2]
            d = sum(recente)/len(recente) - sum(antigo)/len(antigo)
            if abs(d) >= 3:
                pontos.append(f'ROE em {"MELHORA" if d > 0 else "DETERIORAÇÃO"} de '
                              f'{abs(d):.1f} p.p. entre o início e o fim da série.')

    dl, eb = c.get('divliq'), c.get('ebitda')
    if dl is not None and eb and eb > 0:
        x = dl / eb
        if x < 0:
            pontos.append(f'CAIXA LÍQUIDO: a empresa tem mais caixa que dívida ({x:.1f}x EBITDA).')
        elif x <= 2:
            pontos.append(f'Alavancagem confortável: {x:.1f}x EBITDA.')
        elif x <= 3.5:
            pontos.append(f'Alavancagem moderada: {x:.1f}x EBITDA — acompanhar.')
        else:
            pontos.append(f'⚠️ Alavancagem ALTA: {x:.1f}x EBITDA. Dívida desse tamanho consome '
                          f'o resultado no juro e limita a distribuição.')
    elif M['MOTOR'].get(t) in ('FIN', 'SEG'):
        pontos.append('Alavancagem não se aplica: em banco e seguradora o passivo é a '
                      'matéria-prima do negócio, não dívida.')

    lucros = [(y, A[y].get('lucrolin')) for y in val if A[y].get('lucrolin') is not None]
    neg = [y for y, v in lucros if v <= 0]
    if neg:
        pontos.append(f'⚠️ PREJUÍZO em {len(neg)} exercício(s) da série ({", ".join(map(str, neg))}). '
                      f'Múltiplo sobre lucro não descreve empresa que já deu prejuízo na janela.')
    elif len(lucros) >= 4:
        vals = [v for _, v in lucros]
        if all(b >= a * 0.95 for a, b in zip(vals, vals[1:])):
            pontos.append(f'Lucro CRESCENTE ou estável em todos os {len(vals)} exercícios da série.')

    po, npo, pf = M['payout_final'](t, A, M['H_GLOBAL'])
    if po is not None:
        if po >= 0.95:
            pontos.append(f'⚠️ Payout de {po*100:.0f}%: distribui praticamente todo o lucro. '
                          f'Sobra pouco para reinvestir, e o dividendo fica sem folga.')
        elif po >= 0.6:
            pontos.append(f'Payout alto ({po*100:.0f}%) — perfil de renda, crescimento limitado '
                          f'pela retenção baixa.')
        elif po <= 0.25:
            pontos.append(f'Payout baixo ({po*100:.0f}%): retém para crescer. O retorno tem que '
                          f'vir da valorização, não do dividendo.')

    if q:
        pontos.append(f'⚠️ QUEBRA DE SÉRIE em {q}: houve evento societário, e os exercícios '
                      f'anteriores descrevem uma empresa com outra base acionária. Toda média '
                      f'histórica desta linha usa só os anos a partir dali.')
    # vírgula decimal em tudo — a leitura fica ao lado de uma tabela toda em formato brasileiro
    return [ptbr(x) for x in pontos]


def bloco_valuation(t, r, M=None, A=None):
    """O novo `valuation`: UM método que decide, os outros como verificação declarada."""
    met = (r.get('metodos') or [{}])[0]
    justo = r['justo']
    verif = [m for m in (r.get('metodos') or [])[1:] if m.get('justo')]
    grupo = M['MOTOR'].get(t) if M else None
    nome_regra, porque = REGRA_METODO.get(grupo, REGRA_PADRAO)
    return {
        'regraMetodo': nome_regra,
        'regraPorque': porque,
        'regraGrupo': grupo or '—',
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
        # ── Blocos novos de 14/09/2026, todos pedidos pelo usuário ────────────────────────
        # `serieMultiplo` — "acrescentar o ROE e P/L histórico que está sendo utilizado,
        #                    quebrado por ano"
        # `pares`         — "sinto falta de comparação com os concorrentes"
        # Ficam em chaves próprias e o renderizador testa a presença: relatório gerado antes
        # desta versão simplesmente não mostra os blocos, em vez de quebrar.
        'serieMultiplo': (serie_do_multiplo(t, A, met.get('chave'), M)
                          if (M and A and met.get('chave')) else None),
        'pares': (comparacao_pares(t, A, M, M['H_GLOBAL']) if (M and A and M.get('H_GLOBAL'))
                  else None),
    }


def main(alvos=None):
    tetos = json.load(open(TETOS, encoding='utf-8'))
    src = (RAIZ / 'scripts/motor_teto.py').read_text(encoding='utf-8')
    M = {}
    exec(src[:src.index('if __name__')], M)
    H = M['carregar']()
    M['H_GLOBAL'] = H
    M['PL_SETOR'].update(M['pl_setorial'](H))
    M['MULT_PARES'].update(M['multiplos_pares'](H))
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
        if alvos and t not in alvos:
            continue
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
            obj = bloco_valuation(t, r, M, H.get(t))
            cen = cenarios_lpa(t, r, M, H[t]) if t in H else None
            if cen:
                obj['cenariosLpa'] = cen
            if t in H:
                obj['leituraDados'] = leitura_qualitativa(t, M, H[t])
        else:
            motivo = (r.get('nota') or 'sem motor aplicavel').split('||')[0].strip()
            obj = {'criterio': '—', 'metodos': [], 'origemMult': '', 'precoJusto': None,
                   'verificacao': [], 'nota': 'SEM PREÇO JUSTO. ' + motivo}
        txt = json.dumps(obj, ensure_ascii=False, indent=2)
        txt = '\n'.join((ind + l) if j else l for j, l in enumerate(txt.split('\n')))
        novo = bloco[:mv.start()] + mv.group(1) + txt + bloco[mv.end():]

        # ── 2 · `precoTeto` do veredicto e do cabecalho viram `precoJusto` ────────────
        alvo = brl(justo) if (justo and justo > 0) else '—'
        # ⚠️ A SEGUNDA REGEX É A QUE FALTAVA (14/09/2026). A primeira converte o campo ANTIGO
        # `precoTeto`; quem já tinha sido convertido numa rodada anterior ficava com o
        # `precoJusto` CONGELADO do dia da conversão. Na ALOS3 o cabeçalho anunciava R$ 31,53
        # enquanto o card do veredicto, gerado nesta mesma passada, dizia R$ 30,07 — dois
        # preços justos diferentes na mesma tela, a três centímetros um do outro.
        novo = re.sub(r'"precoTeto": "[^"]*"', f'"precoJusto": "{alvo}"', novo)
        # ⚠️ ANCORADO NO RECUO DO NÍVEL DE TOPO, e com count=1. A primeira versão usava
        # `^` com re.M e recuo livre — e reescreveu TODOS os "precoJusto" do arquivo,
        # inclusive os de dentro do array de cenários: conservador, base e otimista saíram
        # os três com R$ 30,07, cada um com o seu múltiplo e o seu FFO ao lado, sem que a
        # multiplicação fechasse. Só o campo do nível de topo do relatório pode ser tocado.
        ind_rel = m.group(1)
        novo = re.sub(r'\n' + ind_rel + r'"precoJusto": "[^"]*"',
                      f'\n{ind_rel}"precoJusto": "{alvo}"', novo, count=1)

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


# ⚠️ FILTRO POR TICKER — 14/09/2026. O usuário pediu para evoluir o modelo do relatório em
# UMA empresa antes de replicar: "faça essas alterações somente na Allos, depois
# replicaremos para as demais até acharmos o melhor modelo". Sem o filtro, rodar o gerador
# reescreveria os 14 de uma vez e não haveria como comparar o modelo novo com o antigo lado
# a lado. `python3 scripts/gerar_relatorio_valuation.py ALOS3` regenera só ela.
if __name__ == '__main__':
    import sys
    main([a.upper() for a in sys.argv[1:]] or None)
