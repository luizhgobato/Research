#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# VARREDURA COMPLETA — quais métricas identificam ação barata (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pergunta do usuário: "quais as melhores métricas para identificar uma ação barata, com base
# em backtest". Sem exemplo dado, sem hipótese minha escolhida a dedo — TODAS as métricas que
# a base permite calcular, todos os pares, ranqueadas pelo mesmo critério.
#
# O QUE ESTE SCRIPT FAZ DE DIFERENTE DOS OUTROS TRÊS:
#   backtest_multiplos.py  → 5 múltiplos escolhidos a dedo
#   backtest_ranking.py    → réguas de ordenação, por grupo de motor
#   backtest_criterios.py  → combinações que EU escolhi testar (P/L×ROE etc.)
#   este                   → varredura cega: 14 métricas isoladas + os 91 pares possíveis,
#                            mais um TESTE DE PERMUTAÇÃO que mede quanto spread uma métrica
#                            SEM NENHUMA INFORMAÇÃO produziria nesta amostra.
#
# ⚠️⚠️ POR QUE O TESTE DE PERMUTAÇÃO É A PARTE MAIS IMPORTANTE DAQUI, e não um detalhe:
# testar 105 combinações em 5 transições anuais e depois anunciar "a melhor deu +25 p.p." é
# quase garantia de estar medindo sorte. Com amostra deste tamanho, a MELHOR de 105 métricas
# aleatórias também dá um número alto — e se o vencedor real não se separar dessa distribuição,
# ele não é conhecimento, é o maior ruído de um conjunto de ruídos. O teste embaralha os
# retornos DENTRO de cada ano (preservando o efeito do ano, destruindo só a ligação
# métrica→retorno), refaz a varredura inteira e guarda o melhor spread. Repetido N vezes, dá a
# régua: quanto precisa render para valer alguma coisa.
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import random
import statistics as st
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

_bt = (RAIZ / 'scripts/backtest_multiplos.py').read_text()
BT = {'__file__': str(RAIZ / 'scripts/backtest_multiplos.py')}
exec(_bt[:_bt.index('# ── AS MÉTRICAS DA CORRIDA ──')], BT)
H, ANOS, num, retorno, QUEBRA = BT['H'], BT['ANOS'], BT['num'], BT['retorno'], BT['QUEBRA']

_mt = (RAIZ / 'scripts/motor_teto.py').read_text()
MT = {}
exec(_mt[:_mt.index('def carregar()')], MT)
MOTOR = MT['MOTOR']
DEFENSIVOS = ('FIN', 'UTIL')

N_PERMUTACOES = 400
random.seed(20260913)          # resultado reproduzível — sem seed, cada rodada conta outra história


def _papeis(D):
    """Ações implícitas = lucro ÷ LPA. Mesma identidade usada em backtest_multiplos.py."""
    l, lpa = num(D, 'lucrolin'), num(D, 'lpa')
    if not l or not lpa or lpa == 0:
        return None
    n = l / lpa
    return abs(n) if n else None


def metricas(t, a):
    """TODAS as métricas calculáveis da base, orientadas para MAIOR = MELHOR OPORTUNIDADE.

    A orientação importa: se metade estivesse invertida, "acima da mediana" significaria coisas
    opostas e o ranking de vencedores misturaria sinal com sinal-trocado.
    """
    D = H[t].get(str(a))
    if not D:
        return {}
    m = {}
    pl, pvp = num(D, 'pl'), num(D, 'pvp')
    dy, ev = num(D, 'dy'), num(D, 'evEbitda')
    roe, roic = num(D, 'roe'), num(D, 'roic')
    mgl, mgb, mge = num(D, 'mgLiq'), num(D, 'mgBruta'), num(D, 'mgEbitda')
    de, dpl = num(D, 'divEbitda'), num(D, 'divPl')
    ebit, ebitda = num(D, 'ebit'), num(D, 'ebitda')
    rec, luc, preco = num(D, 'receita'), num(D, 'lucrolin'), num(D, 'preco')
    pap = _papeis(D)

    # ── PREÇO (value) ────────────────────────────────────────────────────────────────────
    if pl and pl > 0:
        m['L/P'] = 1 / pl
    if pvp and pvp > 0:
        m['VP/P'] = 1 / pvp
    if ev and ev > 0:
        m['EBITDA/EV'] = 1 / ev
        if ebit and ebitda and ebitda > 0:
            m['EBIT/EV'] = ebit / (ev * ebitda)
    if dy is not None:
        m['DY'] = dy / 100
    if rec and preco and pap:
        m['Receita/Preco'] = rec / (preco * pap)      # sales yield

    # ── QUALIDADE ────────────────────────────────────────────────────────────────────────
    if roe is not None:
        m['ROE'] = roe
    if roic is not None:
        m['ROIC'] = roic
    if mgl is not None:
        m['Margem liq.'] = mgl
    if mgb is not None:
        m['Margem bruta'] = mgb
    if mge is not None:
        m['Margem EBITDA'] = mge

    # ── RISCO / ESTRUTURA DE CAPITAL (invertidos: menos dívida = melhor) ─────────────────
    if de is not None:
        m['Baixa alavancagem'] = -de
    if dpl is not None:
        m['Baixa div./PL'] = -dpl

    # ── FATORES CLÁSSICOS que o projeto nunca testou ─────────────────────────────────────
    # MOMENTUM 12m: retorno de preço do ano anterior. Um dos fatores mais replicados da
    # literatura e nunca medido aqui. Descarta quando há quebra entre os dois anos — a série
    # de preço do Partnr não é reexpressa retroativamente (ver comentário em retorno()).
    ant = H[t].get(str(a - 1))
    if ant and not any(y in QUEBRA.get(t, []) for y in (a - 1, a)):
        p0, p1 = num(ant, 'preco'), preco
        if p0 and p1 and p0 > 0:
            m['Momentum 12m'] = (p1 - p0) / p0
    # TAMANHO: o prêmio de small cap. Invertido — menor empresa no topo.
    if preco and pap:
        m['Tamanho (menor)'] = -(preco * pap)
    # CRESCIMENTO do lucro realizado
    if ant:
        l0 = num(ant, 'lucrolin')
        if l0 and luc and l0 > 0:
            m['Cresc. lucro'] = (luc - l0) / l0
    return m


def observar(tickers):
    obs = []
    for a in ANOS[:-1]:
        for t in sorted(tickers):
            r = retorno(t, a)
            if r is None:
                continue
            mm = metricas(t, a)
            if mm:
                obs.append((a, t, mm, r))
    return obs


def _t_anual(sp):
    return (st.mean(sp) / (st.stdev(sp) / len(sp) ** .5)) if len(sp) > 2 and st.stdev(sp) else None


def avaliar(obs, chave, rets=None):
    """Spread mediana-acima menos mediana-abaixo, ano a ano. `chave` devolve o valor da métrica.

    `rets` permite injetar retornos embaralhados sem reconstruir `obs` — é o que o teste de
    permutação usa, e é por isso que a função recebe retorno por fora em vez de ler de dentro.
    """
    acima, abaixo, por_ano = [], [], {}
    for a in ANOS[:-1]:
        do_ano = [(chave(mm), (rets[(ay, t)] if rets else r))
                  for (ay, t, mm, r) in obs if ay == a and chave(mm) is not None]
        if len(do_ano) < 6:
            continue
        med = st.median(x[0] for x in do_ano)
        ac = [r for v, r in do_ano if v > med]
        ab = [r for v, r in do_ano if v <= med]
        if not ac or not ab:
            continue
        acima += ac
        abaixo += ab
        por_ano[a] = st.mean(ac) - st.mean(ab)
    if not por_ano:
        return None
    sp = list(por_ano.values())
    return dict(spread=st.mean(acima) - st.mean(abaixo), n=len(acima) + len(abaixo),
                pos=sum(1 for v in sp if v > 0), anos=len(sp), t=_t_anual(sp))


def chave_simples(nome):
    return lambda mm: mm.get(nome)


def chave_par(n1, n2, obs_ano_cache):
    """Rank composto: percentil médio dos dois sinais DENTRO do ano.

    Percentil e não valor bruto porque ROE (em %) e L/P (em fração) não somam — misturar
    unidades daria peso arbitrário ao que tem escala maior.
    """
    def k(mm):
        v1, v2 = mm.get(n1), mm.get(n2)
        if v1 is None or v2 is None:
            return None
        return (v1, v2)
    return k


def avaliar_par(obs, n1, n2, rets=None):
    acima, abaixo, por_ano = [], [], {}
    for a in ANOS[:-1]:
        do_ano = [(t, mm[n1], mm[n2], (rets[(ay, t)] if rets else r))
                  for (ay, t, mm, r) in obs if ay == a and n1 in mm and n2 in mm]
        if len(do_ano) < 6:
            continue
        pct = {}
        for idx in (1, 2):
            ordem = sorted(do_ano, key=lambda x: -x[idx])
            for i, row in enumerate(ordem):
                pct.setdefault(row[0], []).append(i / (len(ordem) - 1))
        ranked = sorted(do_ano, key=lambda x: st.mean(pct[x[0]]))
        meio = len(ranked) // 2
        ac = [x[3] for x in ranked[:meio]]
        ab = [x[3] for x in ranked[meio:]]
        if not ac or not ab:
            continue
        acima += ac
        abaixo += ab
        por_ano[a] = st.mean(ac) - st.mean(ab)
    if not por_ano:
        return None
    sp = list(por_ano.values())
    return dict(spread=st.mean(acima) - st.mean(abaixo), n=len(acima) + len(abaixo),
                pos=sum(1 for v in sp if v > 0), anos=len(sp), t=_t_anual(sp))


def varrer(obs, nomes, rets=None):
    res = {}
    for nome in nomes:
        r = avaliar(obs, chave_simples(nome), rets)
        if r:
            res[nome] = r
    for n1, n2 in combinations(nomes, 2):
        r = avaliar_par(obs, n1, n2, rets)
        if r:
            res[f'{n1} + {n2}'] = r
    return res


def permutacao(obs, nomes, n_iter=N_PERMUTACOES):
    """Distribuição do MELHOR spread quando a métrica não carrega informação nenhuma.

    Embaralha os retornos DENTRO de cada ano: o efeito do ano (todo mundo sobe em 2023) é
    preservado, e só a ligação métrica→retorno é destruída. É o contrafactual honesto.
    """
    por_ano = {}
    for (a, t, _mm, r) in obs:
        por_ano.setdefault(a, []).append((t, r))
    melhores = []
    for _ in range(n_iter):
        rets = {}
        for a, lst in por_ano.items():
            vals = [r for _t, r in lst]
            random.shuffle(vals)
            for (t, _r), v in zip(lst, vals):
                rets[(a, t)] = v
        res = varrer(obs, nomes, rets)
        if res:
            melhores.append(max(r['spread'] for r in res.values()))
    melhores.sort()
    return melhores


def rodar(tickers, titulo):
    obs = observar(tickers)
    nomes = sorted({k for (_a, _t, mm, _r) in obs for k in mm})
    print('\n' + '═' * 96)
    print(titulo)
    print('═' * 96)
    print(f'{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · '
          f'{len(set(o[0] for o in obs))} transições anuais · {len(nomes)} métricas')

    res = varrer(obs, nomes)
    simples = {k: v for k, v in res.items() if '+' not in k}
    pares = {k: v for k, v in res.items() if '+' in k}

    def tabela(d, titulo_sec, top=12):
        print(f'\n{titulo_sec}')
        print('-' * 96)
        print(f"{'Métrica':<38}{'n':>5}{'spread':>10}{'t':>8}{'anos certos':>14}")
        print('-' * 96)
        # Ordena por CONSISTÊNCIA primeiro (fração de anos certos), spread como desempate.
        # Spread médio alto com 2 de 5 anos é um ano bom carregando o resto — não é sinal.
        ordem = sorted(d.items(), key=lambda kv: (-(kv[1]['pos'] / kv[1]['anos']), -kv[1]['spread']))
        for nome, r in ordem[:top]:
            tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
            anos = '%d de %d' % (r['pos'], r['anos'])
            print(f"{nome:<38}{r['n']:>5}{r['spread']*100:>9.1f}%{tt:>8}{anos:>14}")
        return ordem

    ord_s = tabela(simples, 'MÉTRICAS ISOLADAS — ordenado por consistência (anos certos), depois spread')
    ord_p = tabela(pares, 'PARES (rank composto) — mesmo critério de ordenação')

    print(f'\nPIORES — sinais que erram a direção (candidatos a sair do motor)')
    print('-' * 96)
    for nome, r in sorted(simples.items(), key=lambda kv: kv[1]['spread'])[:5]:
        tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
        anos = '%d de %d' % (r['pos'], r['anos'])
        print(f"{nome:<38}{r['n']:>5}{r['spread']*100:>9.1f}%{tt:>8}{anos:>14}")

    # ── O CONTRAFACTUAL ──────────────────────────────────────────────────────────────────
    print(f'\nTESTE DE PERMUTAÇÃO — {N_PERMUTACOES} rodadas com retorno embaralhado dentro do ano')
    print('-' * 96)
    melhor_real = max(res.values(), key=lambda r: r['spread'])['spread']
    nome_real = max(res.items(), key=lambda kv: kv[1]['spread'])[0]
    dist = permutacao(obs, nomes)
    p50, p90, p95 = (dist[int(len(dist) * q)] for q in (.50, .90, .95))
    acima = sum(1 for d in dist if d >= melhor_real) / len(dist)
    print(f'  Testadas {len(res)} combinações ({len(simples)} isoladas + {len(pares)} pares).')
    print(f'  MELHOR REAL: {nome_real} → {melhor_real*100:+.1f} p.p.')
    print(f'  Melhor de {len(res)} métricas SEM informação (retorno embaralhado):')
    print(f'      mediana {p50*100:+.1f} p.p. · p90 {p90*100:+.1f} p.p. · p95 {p95*100:+.1f} p.p.')
    print(f'  → o acaso bate o melhor real em {acima*100:.1f}% das rodadas'
          f'  ({"NÃO se distingue de sorte" if acima > 0.10 else "se separa do acaso"})')
    return res, dist


# ── P-VALOR INDIVIDUAL, PARA MÉTRICA COM HIPÓTESE PRÉVIA ─────────────────────────────────
# O teste de permutação acima pergunta "o MELHOR de 136 se separa do acaso?" — a pergunta certa
# para quem varreu tudo e escolheu o vencedor depois. Mas ela é severa demais para uma métrica
# que NÃO foi descoberta aqui: L/P e receita/preço são fatores de valor com décadas de
# literatura fora deste dataset, então testá-los é confirmação de hipótese prévia, não pesca.
# Para esses, o contrafactual certo é a distribuição da PRÓPRIA métrica sob retorno embaralhado,
# sem o "melhor de N". Os dois números respondem perguntas diferentes e os dois estão aqui.
def p_individual(obs, nomes_teste, n_iter=N_PERMUTACOES):
    por_ano = {}
    for (a, t, _mm, r) in obs:
        por_ano.setdefault(a, []).append((t, r))
    reais = {}
    for nome in nomes_teste:
        r = avaliar(obs, chave_simples(nome)) if '+' not in nome else \
            avaliar_par(obs, *nome.split(' + '))
        if r:
            reais[nome] = r['spread']
    cont = {k: 0 for k in reais}
    for _ in range(n_iter):
        rets = {}
        for a, lst in por_ano.items():
            vals = [r for _t, r in lst]
            random.shuffle(vals)
            for (t, _r), v in zip(lst, vals):
                rets[(a, t)] = v
        for nome in reais:
            r = avaliar(obs, chave_simples(nome), rets) if '+' not in nome else \
                avaliar_par(obs, *nome.split(' + '), rets=rets)
            if r and r['spread'] >= reais[nome]:
                cont[nome] += 1
    print('\nP-VALOR INDIVIDUAL — métricas com hipótese prévia (fator de valor consagrado)')
    print('-' * 96)
    print(f"{'Métrica':<38}{'spread real':>13}{'p (acaso >= real)':>20}")
    print('-' * 96)
    for nome in sorted(reais, key=lambda k: cont[k]):
        p = cont[nome] / n_iter
        marca = ' ***' if p < 0.01 else (' **' if p < 0.05 else (' *' if p < 0.10 else ''))
        print(f"{nome:<38}{reais[nome]*100:>12.1f}%{p:>19.3f}{marca}")
    print('  *** p<0,01   ** p<0,05   * p<0,10 — com 5 anos, mesmo p baixo é indício, não prova')


A_PRIORI = ['L/P', 'Receita/Preco', 'DY', 'VP/P', 'ROE', 'L/P + Receita/Preco', 'L/P + ROE']

if __name__ == '__main__':
    defensivos = {t for t in H if MOTOR.get(t) in DEFENSIVOS}
    rodar(defensivos, 'DEFENSIVOS (FIN + UTIL) — bancos, seguros, elétricas, telecom, saneamento')
    p_individual(observar(defensivos), A_PRIORI)
    rodar(set(H), 'RADAR INTEIRO — 30 tickers, para contraste')
    p_individual(observar(set(H)), A_PRIORI)
