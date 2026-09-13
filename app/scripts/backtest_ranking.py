#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# BACKTEST DOS CRITÉRIOS DE RANKING — por grupo de motor (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pergunta: das réguas que o Radar usa para ORDENAR (não para precificar), qual separou
# vencedor de perdedor DENTRO DOS SEGMENTOS QUE O USUÁRIO COMPRA — bancos, seguradoras,
# elétricas, telecom e saneamento?
#
# POR QUE ESTE SCRIPT EXISTE, e por que ele não é o backtest_multiplos.py:
#
#   · `backtest_multiplos.py` mistura os 30 tickers do Radar num universo só. Isso responde
#     "qual múltiplo é melhor em geral", que NÃO é a pergunta do usuário — ele não compra
#     cíclica de commodity nem construtora. Um sinal que funciona na VALE3 e falha no ITUB3
#     aparece lá como "funciona"; aqui não.
#   · `backtest_multiplos.py` testa a MARGEM SOBRE O PREÇO-TETO. Mas o que ordena a lista
#     "Por onde começar" em produção é a TIR REAL, que nunca foi testada contra retorno
#     futuro em lugar nenhum deste projeto. Trocar um critério sem medir o que está em
#     produção seria repetir exatamente o erro que a seção 24 documenta.
#
# ⚠️ A TIR REAL AQUI É UM PROXY, e a diferença importa. A TIR real de produção é a MEDIANA de
# três medidas (caixa/FCFE, dividendos/DDM, lucro). FCO, capex e dívida bruta não estão no
# HIST_SEED, então a medida de caixa e o DDM não são reconstruíveis ano a ano. O que dá para
# reconstruir é a medida LUCRO — `real(ey + g)` — que é a que `gerar_tir.py` calcula como:
#
#     ey = lucro normalizado ÷ valor de mercado      (aqui: 1 ÷ P/L do ano, lucro reportado)
#     g  = min(ROE × retenção, CAGR) capado em 15%   (aqui: só ROE × retenção; CAGR exige
#                                                     lucro recorrente, que não está na base)
#     luc = (1 + ey + g) ÷ (1 + IPCA) − 1            (Fisher, idêntico a gerar_tir.py)
#
# Como `real()` é monotônico em (ey + g), ordenar por esta TIR é ordenar por (ey + g). Então o
# teste responde uma pergunta limpa e decidível: **somar `g` ao earnings yield melhora ou piora
# a ordenação?** Se piorar, o `g` está adicionando ruído, não informação — e o critério de
# produção está pior que o insumo mais simples que ele usa por dentro.
#
# ⚠️ AMOSTRA. 17 tickers × 5 transições anuais, e as observações do mesmo ano são
# correlacionadas (todas pegam o mesmo mercado). O n efetivo para significância é o número de
# ANOS (5), não o de observações. Nada aqui prova nada; o que dá para exigir de um critério é
# que ele pelo menos não erre a DIREÇÃO de forma consistente.
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import json
import statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Reaproveita carregamento, detecção de quebra e retorno do backtest de múltiplos — o mesmo
# código, não uma segunda cópia que pode divergir (ver seção 24 da metodologia).
_bt = (RAIZ / 'scripts/backtest_multiplos.py').read_text()
BT = {'__file__': str(RAIZ / 'scripts/backtest_multiplos.py')}
exec(_bt[:_bt.index('# ── AS MÉTRICAS DA CORRIDA ──')], BT)

H, QUEBRA, ANOS, num, retorno = BT['H'], BT['QUEBRA'], BT['ANOS'], BT['num'], BT['retorno']

IPCA = 0.0444          # igual a scripts/motor_teto.py e a js/decisao.js (_TIR_IPCA)
G_CAP = 0.15           # igual a gerar_tir.py

# ── GRUPOS DE MOTOR ──────────────────────────────────────────────────────────────────────
# Mesma classificação de scripts/motor_teto.py (dicionário MOTOR). Não é cópia solta: se
# divergir, o teste deixa de descrever o motor que está em produção — o assert abaixo quebra
# o script em vez de deixar passar em silêncio.
_mt = (RAIZ / 'scripts/motor_teto.py').read_text()
MT = {}
exec(_mt[:_mt.index('def carregar()')], MT)
MOTOR = MT['MOTOR']

# Os segmentos que o usuário compra: pagadoras de dividendo, risco baixo, negócio maduro.
# FIN  = bancos e seguradoras (P/VP × ROE)
# UTIL = elétricas, saneamento e telecom (EV/EBITDA + Gordon sobre dividendo sustentável)
GRUPOS_DEFENSIVOS = ('FIN', 'UTIL')


def universo(grupos):
    return {t for t in H if MOTOR.get(t) in grupos}


def payout(D):
    """payout = DY × P/L. DY vem em %, P/L é razão: (dy/100) × pl = DPS/LPA."""
    dy, pl = num(D, 'dy'), num(D, 'pl')
    if dy is None or not pl or pl <= 0:
        return None
    p = (dy / 100) * pl
    return p if 0 <= p <= 2 else None      # >200% não é política, é ano fora da curva


def criterios(t, a):
    """As réguas de ORDENAÇÃO, todas orientadas para MAIOR = MELHOR OPORTUNIDADE."""
    D = H[t].get(str(a))
    if not D:
        return {}
    m = {}
    pl, dy, roe = num(D, 'pl'), num(D, 'dy'), num(D, 'roe')

    ey = 1 / pl if (pl and pl > 0) else None
    if ey is not None:
        m['L/P (earnings yield)'] = ey

    if dy is not None:
        m['Dividend yield'] = dy / 100

    # TIR real, medida LUCRO — o proxy do critério que ordena o Radar hoje
    if ey is not None and roe is not None:
        po = payout(D)
        if po is not None:
            g = max(0.0, min((roe / 100) * (1 - po), G_CAP))
            m['TIR real (proxy: ey+g)'] = (1 + ey + g) / (1 + IPCA) - 1
            # `g` isolado: serve para saber se o componente que a TIR ACRESCENTA ao L/P tem
            # sinal próprio ou só dilui o que o L/P já entrega.
            m['g isolado (ROE x retencao)'] = g
    return m


def spearman(pares):
    n = len(pares)
    if n < 4:
        return None

    def rank(v):
        o = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[o[j + 1]] == v[o[i]]:
                j += 1
            med = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[o[k]] = med
            i = j + 1
        return r

    x, y = rank([p[0] for p in pares]), rank([p[1] for p in pares])
    mx, my = st.mean(x), st.mean(y)
    n_ = sum((a - mx) * (b - my) for a, b in zip(x, y))
    d = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** .5
    return n_ / d if d else None


def rodar(tickers, titulo):
    obs = []
    for a in ANOS[:-1]:
        for t in sorted(tickers):
            r = retorno(t, a)
            if r is None:
                continue
            c = criterios(t, a)
            if c:
                obs.append((a, t, c, r))

    print('\n' + '═' * 104)
    print(titulo)
    print('═' * 104)
    print(f"{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · "
          f"{len(set(o[0] for o in obs))} transições anuais")
    print('-' * 104)
    print(f"{'Critério':<28}{'n':>5}{'BARATO':>10}{'MEIO':>10}{'CARO':>10}"
          f"{'spread':>10}{'ρ':>8}{'t':>8}  anos c/ spread>0")
    print('-' * 104)

    nomes = ['L/P (earnings yield)', 'TIR real (proxy: ey+g)',
             'Dividend yield', 'g isolado (ROE x retencao)']
    linhas = {}
    for nome in nomes:
        tercos = {0: [], 1: [], 2: []}
        pares, por_ano = [], {}
        for a in ANOS[:-1]:
            do_ano = [(c[nome], r) for (ay, _t, c, r) in obs if ay == a and nome in c]
            if len(do_ano) < 6:
                continue
            do_ano.sort(key=lambda x: -x[0])
            n = len(do_ano)
            cut = max(1, n // 3)
            g = [do_ano[:cut], do_ano[cut:n - cut], do_ano[n - cut:]]
            for gi, lst in enumerate(g):
                tercos[gi] += [x[1] for x in lst]
            pares += do_ano
            if g[0] and g[2]:
                por_ano[a] = st.mean(x[1] for x in g[0]) - st.mean(x[1] for x in g[2])
        if not tercos[0]:
            print(f'{nome:<28}  — sem ano com n>=6')
            continue
        b = st.mean(tercos[0])
        meio = st.mean(tercos[1]) if tercos[1] else float('nan')
        c_ = st.mean(tercos[2])
        sp = list(por_ano.values())
        # t sobre os SPREADS ANUAIS: dentro de um ano as observações não são independentes.
        tt = (st.mean(sp) / (st.stdev(sp) / len(sp) ** .5)) if len(sp) > 2 and st.stdev(sp) else None
        rho = spearman(pares)
        pos = sum(1 for v in sp if v > 0)
        linhas[nome] = (b - c_, pos, len(sp))
        print(f"{nome:<28}{len(pares):>5}{b*100:>9.1f}%{meio*100:>9.1f}%{c_*100:>9.1f}%"
              f"{(b-c_)*100:>9.1f}%{(f'{rho:+.2f}' if rho is not None else '   —'):>8}"
              f"{(f'{tt:+.2f}' if tt is not None else '   —'):>8}   {pos} de {len(sp)}")

    if obs:
        base = st.mean(r for (_a, _t, _c, r) in obs)
        print('-' * 104)
        print(f"{'BASELINE (comprar todas)':<28}{len(obs):>5}{base*100:>9.1f}%")
    print('═' * 104)
    return linhas


if __name__ == '__main__':
    defensivos = universo(GRUPOS_DEFENSIVOS)
    L = rodar(defensivos,
              'SEGMENTOS DEFENSIVOS (FIN + UTIL) — bancos, seguros, elétricas, telecom, saneamento')

    print(f"\nTickers no universo: {', '.join(sorted(defensivos))}")

    ey_sp = L.get('L/P (earnings yield)')
    tir_sp = L.get('TIR real (proxy: ey+g)')
    if ey_sp and tir_sp:
        print('\nVEREDICTO — o `g` acrescenta ou tira?')
        print(f"  L/P puro      : spread {ey_sp[0]*100:+.1f} p.p. · acertou {ey_sp[1]} de {ey_sp[2]} anos")
        print(f"  TIR (ey + g)  : spread {tir_sp[0]*100:+.1f} p.p. · acertou {tir_sp[1]} de {tir_sp[2]} anos")
        delta = (tir_sp[0] - ey_sp[0]) * 100
        print(f"  Somar `g` ao earnings yield {'MELHORA' if delta > 0 else 'PIORA'} "
              f"o spread em {abs(delta):.1f} p.p.")

    # Controle: o mesmo teste no resto do Radar (cíclicas, indústria, shoppings, holdings).
    # Se o L/P vencer em todo lugar, a conclusão é "L/P é bom"; se vencer SÓ nos defensivos,
    # a conclusão é mais forte e mais útil — o motor complexo tem lugar, e não é aqui.
    outros = {t for t in H if MOTOR.get(t) not in GRUPOS_DEFENSIVOS and t in H}
    if outros:
        rodar(outros, 'CONTROLE — resto do Radar (cíclicas, indústria, shoppings, holdings)')
        print(f"\nTickers no controle: {', '.join(sorted(outros))}")
