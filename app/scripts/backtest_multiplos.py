#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# CORRIDA DE MÚLTIPLOS — versão barata (30 tickers do Radar, 2021-2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pergunta: qual métrica de "barato" separou melhor vencedor de perdedor NAS EMPRESAS QUE O
# LUIZ ACOMPANHA? É a réplica em miniatura do horse race de Gray & Vogel.
#
# ⚠️ O QUE ESTE TESTE **NÃO** É:
#   · Não é o universo da B3 — são 30 empresas escolhidas A DEDO, e escolhidas HOJE.
#     Isso é VIÉS DE SOBREVIVÊNCIA na forma mais pura: nenhuma delas quebrou, saiu da bolsa
#     ou virou pó, porque se tivesse virado não estaria no Radar. O retorno médio da amostra
#     inteira é, por construção, otimista.
#   · 5 transições anuais (2021→22 … 2025→26) × 30 = no máximo 150 obs., e as observações do
#     mesmo ano são CORRELACIONADAS (todas pegam o mesmo mercado). O n efetivo é muito menor
#     que 150 — mais perto de 5 do que de 150 para efeito de significância.
#   · Não prova nada. Serve para uma coisa só: ver se o MEU motor de preço-teto é melhor ou
#     pior que um múltiplo simples nas empresas do Radar. Se ele perder aqui, perdeu.
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import json, re, statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# ── Carregar HIST_SEED do arquivo .js ────────────────────────────────────────────────────
txt = (RAIZ / 'data/historico.data.js').read_text()
bloco = txt[txt.index('const HIST_SEED = {') + len('const HIST_SEED = '):]
# corta no fechamento do objeto (primeira linha que é exatamente "};")
bloco = bloco[:bloco.index('\n};') + 2]
bloco = re.sub(r'//.*', '', bloco)                      # comentários
bloco = re.sub(r'([{,]\s*)(\w+)\s*:', r'\1"\2":', bloco)  # chaves sem aspas
bloco = re.sub(r',\s*([}\]])', r'\1', bloco)            # vírgula final
H = json.loads(bloco)
print(f"{len(H)} tickers carregados de historico.data.js\n")

ANOS = [2021, 2022, 2023, 2024, 2025, 2026]

# ── QUEBRAS DE SÉRIE — DETECTADAS, NÃO DIGITADAS ─────────────────────────────────────────
# Primeira versão deste script usava a lista fixa do motor_teto.py e produziu um retorno de
# +5.051% no IRBR3 em 2022→2023 (preço R$0,86 → R$44,30). Não foi retorno: foi GRUPAMENTO de
# ações. A lista do motor vinha de `ano_quebra`, que só detectava AUMENTO de ações (>25%) —
# incorporação, follow-on. Grupamento é o contrário: as ações DIMINUEM e o preço multiplica.
# O detector estava cego para metade dos casos, e essa metade é justamente a que explode o
# retorno em vez de amassar o múltiplo.
#
# Correção: a quantidade de ações está IMPLÍCITA no próprio dado — `lucrolin ÷ lpa`. Nenhuma
# chamada nova, e a detecção passa a ser MECÂNICA em vez de curada à mão: variação de mais de
# 25% PARA QUALQUER LADO marca quebra e descarta a transição.
LIM_QUEBRA = 0.25


def _acoes(t, a):
    D = H[t].get(str(a))
    if not D:
        return None
    lucro, lpa = num(D, 'lucrolin'), num(D, 'lpa')
    if not lucro or not lpa or lpa == 0:
        return None
    n = lucro / lpa
    return abs(n) if n else None


def _detectar_quebras():
    q = {}
    for t in H:
        for a in ANOS[1:]:
            n0, n1 = _acoes(t, a - 1), _acoes(t, a)
            if not n0 or not n1 or n0 <= 0:
                continue
            if abs(n1 - n0) / n0 > LIM_QUEBRA:
                q.setdefault(t, []).append(a)
    return q


QUEBRA = {}   # preenchido depois de num() existir (ver abaixo)


def num(d, k):
    v = d.get(k)
    return v if isinstance(v, (int, float)) and v == v else None


QUEBRA = _detectar_quebras()
_manual = {'ALOS3': [2022], 'AXIA3': [2022, 2025], 'FLRY3': [2023],
           'IRBR3': [2022], 'SAUD3': [2026], 'SBSP3': [2026], 'SHUL4': [2022]}
for _t, _as in _manual.items():                 # união com o que o motor já sabia
    QUEBRA[_t] = sorted(set(QUEBRA.get(_t, [])) | set(_as))
print("Quebras de série detectadas (ações implícitas = lucro ÷ LPA, ±25%):")
for _t in sorted(QUEBRA):
    print(f"   {_t}: {', '.join(map(str, QUEBRA[_t]))}")
print()


def retorno(t, a):
    """Retorno total de a → a+1: variação de preço + dividendo recebido no período."""
    A, B = H[t].get(str(a)), H[t].get(str(a + 1))
    if not A or not B:
        return None
    # JANELA DE UM ANO PARA CADA LADO. O IRBR3 mostrou por quê: o grupamento de ações
    # reapresentou o LPA de 2022 na base nova (−7,66 contra −0,54 de 2021), então a quebra é
    # detectada em 2022 — mas a série de PREÇOS do Partnr NÃO é ajustada retroativamente, e o
    # salto de R$0,86 para R$44,30 cai na transição 2022→2023, um ano DEPOIS. Descartar só o
    # ano da quebra deixava passar +5.051% de "retorno" que era só mudança de unidade.
    qs = QUEBRA.get(t, [])
    if any(y in qs for y in (a, a + 1)):
        return None
    p0, p1 = num(A, 'preco'), num(B, 'preco')
    if not p0 or not p1 or p0 <= 0:
        return None
    # DY do ano de chegada é dividendo/preço NAQUELE preço; o dividendo em R$ é dy×p1,
    # e o que interessa é quanto isso rende sobre o capital investido a p0.
    dy = num(B, 'dy') or 0
    return (p1 - p0) / p0 + (dy / 100) * p1 / p0


# ── AS MÉTRICAS DA CORRIDA ───────────────────────────────────────────────────────────────
# Todas orientadas para "MAIOR = MAIS BARATO", para o ranking ser comparável.
def metricas(t, a):
    D = H[t].get(str(a))
    if not D:
        return {}
    m = {}
    pl, pvp, ev, dy = num(D, 'pl'), num(D, 'pvp'), num(D, 'evEbitda'), num(D, 'dy')
    ebit, ebitda = num(D, 'ebit'), num(D, 'ebitda')
    if pl and pl > 0:
        m['L/P (earnings yield)'] = 1 / pl
    if pvp and pvp > 0:
        m['VP/P (book yield)'] = 1 / pvp
    if ev and ev > 0:
        m['EBITDA/EV'] = 1 / ev
        if ebit and ebitda and ebitda > 0:
            # EV = evEbitda × EBITDA  →  EBIT/EV = EBIT / (evEbitda × EBITDA)
            m['EBIT/EV'] = ebit / (ev * ebitda)
    if dy is not None:
        m['Dividend yield'] = dy / 100
    return m


# ── O MOTOR ATUAL, EM VERSÃO AUDITÁVEL NO PASSADO ────────────────────────────────────────
# Não dá para rodar o motor_teto.py de verdade retroativamente (ele usa dados de hoje). O que
# dá é reproduzir a ESPINHA DELE com informação disponível até o ano t, sem olhar o futuro:
#   · não-financeira → P/L mediano dos anos ANTERIORES a t × LPA de t
#   · financeira     → P/VP mediano dos anos ANTERIORES a t × VPA de t
# Exige ≥3 anos de história, então só existe a partir de 2024. É o mesmo princípio do motor
# ("múltiplo da própria série"), sem o Ke nem o Gordon.
FIN = {'ITUB3', 'BBSE3', 'CXSE3', 'BMEB4', 'BRSR6', 'PSSA3', 'SANB11',
       'BPAC11', 'IRBR3', 'ROXO34', 'SAUD3', 'ITSA4', 'BRAP4'}


def margem_motor(t, a):
    campo = 'pvp' if t in FIN else 'pl'
    hist = []
    for y in ANOS:
        if y >= a:
            break
        if y in QUEBRA.get(t, []):
            hist = []            # quebra apaga o passado: era outra empresa
            continue
        D = H[t].get(str(y))
        v = num(D, campo) if D else None
        if v and 0 < v < 60:
            hist.append(v)
    if len(hist) < 3:
        return None
    Da = H[t].get(str(a))
    atual, preco = (num(Da, campo) if Da else None), (num(Da, 'preco') if Da else None)
    if not atual or atual <= 0 or not preco:
        return None
    # múltiplo-alvo ÷ múltiplo praticado − 1 = margem sobre o preço de hoje
    return st.median(hist) / atual - 1


# ── EXECUÇÃO ─────────────────────────────────────────────────────────────────────────────
TICKERS = sorted(H)
NOMES = ['L/P (earnings yield)', 'VP/P (book yield)', 'EBIT/EV', 'EBITDA/EV',
         'Dividend yield', 'MOTOR (margem s/ teto)']

obs = []   # (ano, ticker, {metrica: valor}, retorno)
for a in ANOS[:-1]:
    for t in TICKERS:
        r = retorno(t, a)
        if r is None:
            continue
        mm = metricas(t, a)
        mg = margem_motor(t, a)
        if mg is not None:
            mm['MOTOR (margem s/ teto)'] = mg
        if mm:
            obs.append((a, t, mm, r))

print(f"{len(obs)} observações válidas ({len(ANOS)-1} transições anuais)")
desc = sum(len(TICKERS) for _ in ANOS[:-1]) - len(obs)
print(f"{desc} descartadas por quebra de série ou dado ausente\n")


def spearman(pares):
    n = len(pares)
    if n < 4:
        return None
    def rank(v):
        o = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:                        # empates recebem rank médio
            j = i
            while j + 1 < n and v[o[j + 1]] == v[o[i]]:
                j += 1
            m = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[o[k]] = m
            i = j + 1
        return r
    x = rank([p[0] for p in pares]); y = rank([p[1] for p in pares])
    mx, my = st.mean(x), st.mean(y)
    num_ = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** .5
    return num_ / den if den else None


print("═" * 106)
print("CORRIDA DE MÚLTIPLOS — retorno total médio 12 meses à frente, por terço")
print("═" * 106)
print(f"{'Métrica':<26}{'n':>5}{'BARATO':>10}{'MEIO':>10}{'CARO':>10}{'spread':>10}"
      f"{'ρ':>8}{'spr.med':>10}{'t':>8}  {'anos c/ spread>0'}")
print("-" * 106)

linhas = []
for nome in NOMES:
    # ranking DENTRO DE CADA ANO (comparar 2021 com 2025 seria comparar mercados diferentes)
    tercos = {0: [], 1: [], 2: []}
    pares, por_ano = [], {}
    for a in ANOS[:-1]:
        do_ano = [(m[nome], r, t) for (ay, t, m, r) in obs if ay == a and nome in m]
        if len(do_ano) < 6:
            continue
        do_ano.sort(key=lambda x: -x[0])          # maior = mais barato = primeiro
        n = len(do_ano)
        c = n // 3
        grupos = [do_ano[:c], do_ano[c:n - c], do_ano[n - c:]]
        for g, lst in enumerate(grupos):
            tercos[g] += [x[1] for x in lst]
        pares += [(x[0], x[1]) for x in do_ano]
        if grupos[0] and grupos[2]:
            por_ano[a] = st.mean(x[1] for x in grupos[0]) - st.mean(x[1] for x in grupos[2])
    if not tercos[0]:
        continue
    # t de Student sobre os SPREADS ANUAIS. É o teste honesto: as observações dentro de um ano
    # não são independentes (todas pegam o mesmo mercado), então o n para significância é o
    # número de ANOS, não o de ações. Com 5 anos, nada aqui pode ser significativo — e mostrar
    # o t explícito é melhor que deixar o leitor achar que 125 observações são 125 graus de
    # liberdade. |t| > 2,78 seria 5% com 4 g.l.; nenhuma métrica chega perto.
    sp = list(por_ano.values())
    tstat = (st.mean(sp) / (st.stdev(sp) / len(sp) ** .5)) if len(sp) > 2 and st.stdev(sp) else None
    b, meio, c_ = (st.mean(tercos[0]), st.mean(tercos[1]) if tercos[1] else float('nan'),
                   st.mean(tercos[2]))
    mb, mc = st.median(tercos[0]), st.median(tercos[2])
    rho = spearman(pares)
    pos = sum(1 for v in por_ano.values() if v > 0)
    linhas.append((nome, len(pares), b, meio, c_, b - c_, rho, pos, len(por_ano), mb - mc))
    print(f"{nome:<26}{len(pares):>5}{b*100:>9.1f}%{meio*100:>9.1f}%{c_*100:>9.1f}%"
          f"{(b-c_)*100:>9.1f}%{(f'{rho:+.2f}' if rho is not None else '  —'):>8}"
          f"{(mb-mc)*100:>9.1f}%{(f'{tstat:+.2f}' if tstat is not None else '   —'):>8}"
          f"   {pos} de {len(por_ano)}")

base = st.mean(r for (_, _, _, r) in obs)
print("-" * 106)
medbase = st.median([r for (_, _, _, r) in obs])
print(f"{'BASELINE (comprar as 30)':<26}{len(obs):>5}{base*100:>9.1f}%"
      f"   (mediana {medbase*100:.1f}% — a média é puxada por poucos casos extremos)")
print("═" * 106)

# ── ANO A ANO DO VENCEDOR E DO MOTOR ─────────────────────────────────────────────────────
if linhas:
    venc = max(linhas, key=lambda L: L[5])[0]
    print(f"\nSpread barato−caro ano a ano — {venc} vs MOTOR")
    print(f"{'ano':<7}{venc:>26}{'MOTOR':>26}")
    for a in ANOS[:-1]:
        saida = f"{a}→{a+1:<4}"
        for nome in (venc, 'MOTOR (margem s/ teto)'):
            do_ano = [(m[nome], r) for (ay, _, m, r) in obs if ay == a and nome in m]
            if len(do_ano) < 6:
                saida += f"{'—':>26}"
                continue
            do_ano.sort(key=lambda x: -x[0])
            c = len(do_ano) // 3
            s = st.mean(x[1] for x in do_ano[:c]) - st.mean(x[1] for x in do_ano[-c:])
            saida += f"{s*100:>25.1f}%"
        print(saida)

json.dump([{'ano': a, 'ticker': t, 'ret': r, **m} for (a, t, m, r) in obs],
          open(RAIZ / 'analise/backtest_multiplos.json', 'w'), indent=1)
print(f"\n{len(obs)} observações → analise/backtest_multiplos.json")


# ══════════════════════════════════════════════════════════════════════════════════════════
# COMBINAÇÃO — as duas métricas que sobreviveram, juntas
# ══════════════════════════════════════════════════════════════════════════════════════════
# L/P teve o maior spread MÉDIO (+8,8 p.p.) e o DY o maior spread MEDIANO (+13,5 p.p.).
# Perfis diferentes: o L/P captura lucro que a empresa GERA, o DY o caixa que ela ENTREGA.
# Uma empresa barata no lucro e mesquinha no dividendo (armadilha de valor) e uma generosa
# no dividendo mas cara no lucro (payout insustentável) são erros DIFERENTES — em tese um
# filtro corrige o outro.
#
# Como combinar sem inventar peso: RANK MÉDIO. Cada ação recebe o percentil dentro do ano em
# cada métrica e a nota é a média dos dois. Sem coeficiente escolhido por mim, sem calibração.
# É o mesmo espírito do Greenblatt (soma de dois ranks), que é a razão de ele ser difícil de
# superajustar.
print("\n" + "═" * 106)
print("COMBINAÇÃO — rank médio de L/P e Dividend yield")
print("═" * 106)

PAR = ['L/P (earnings yield)', 'Dividend yield']
tercos = {0: [], 1: [], 2: []}
por_ano = {}
for a in ANOS[:-1]:
    doano = [(t, m, r) for (ay, t, m, r) in obs if ay == a and all(k in m for k in PAR)]
    if len(doano) < 6:
        continue
    pcts = {}
    for k in PAR:
        ordem = sorted(doano, key=lambda x: -x[1][k])       # 1º = mais barato
        for i, (t, _, _) in enumerate(ordem):
            pcts.setdefault(t, []).append(i / (len(ordem) - 1))
    rank = sorted(doano, key=lambda x: st.mean(pcts[x[0]]))  # menor rank = mais barato
    n = len(rank); c = n // 3
    g = [rank[:c], rank[c:n - c], rank[n - c:]]
    for gi, lst in enumerate(g):
        tercos[gi] += [x[2] for x in lst]
    por_ano[a] = st.mean(x[2] for x in g[0]) - st.mean(x[2] for x in g[2])

if tercos[0]:
    b, meio, c_ = st.mean(tercos[0]), st.mean(tercos[1]), st.mean(tercos[2])
    mb, mc = st.median(tercos[0]), st.median(tercos[2])
    sp = list(por_ano.values())
    tt = st.mean(sp) / (st.stdev(sp) / len(sp) ** .5) if len(sp) > 2 and st.stdev(sp) else None
    print(f"{'Estratégia':<26}{'n':>5}{'BARATO':>10}{'MEIO':>10}{'CARO':>10}"
          f"{'spread':>10}{'spr.med':>10}{'t':>8}  anos c/ spread>0")
    print("-" * 106)
    print(f"{'L/P + DY (rank médio)':<26}{len(tercos[0])+len(tercos[1])+len(tercos[2]):>5}"
          f"{b*100:>9.1f}%{meio*100:>9.1f}%{c_*100:>9.1f}%{(b-c_)*100:>9.1f}%"
          f"{(mb-mc)*100:>9.1f}%{(f'{tt:+.2f}' if tt else '   —'):>8}"
          f"   {sum(1 for v in sp if v > 0)} de {len(sp)}")
    print("-" * 106)
    print("ano a ano:  " + "   ".join(f"{a}→{a+1}: {v*100:+.1f}%" for a, v in sorted(por_ano.items())))
    print("═" * 106)
