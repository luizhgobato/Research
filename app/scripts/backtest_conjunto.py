#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# QUAL O MELHOR CONJUNTO DE INDICADORES — não a melhor métrica (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Correção de rumo pedida pelo usuário: "eu não falei em um critério único e você tornou isso
# como verdade. Para definir uma empresa barata podemos ter uma série de indicadores".
#
# Ele está certo, e não é só preferência — é estatística. Indicador solto carrega o ruído
# específico daquela conta (o lucro de UM ano, a receita de UM ano). Vários indicadores
# medindo a mesma coisa por caminhos diferentes cancelam parte desse ruído e mantêm o sinal
# comum. É a mesma lógica que o motor de preço-teto já usa desde a seção 19 — mediana de N
# métodos em vez de um método só — aplicada agora ao lado do RANKING.
#
# DUAS ABORDAGENS, e a diferença entre elas é a diferença entre ciência e pesca:
#
#   1. CONJUNTOS PRÉ-ESPECIFICADOS — definidos por raciocínio ANTES de ver o resultado, cada
#      um com uma tese declarada. Testar estes é confirmar hipótese. O p-valor individual vale.
#
#   2. BUSCA EXAUSTIVA nos 560 trios possíveis — encontra o melhor, mas o melhor de 560 numa
#      amostra de 5 anos é quase certamente sorte. Entra aqui só como CONTRASTE, medido contra
#      o teste de permutação, para mostrar quanto o vencedor da pesca vale (spoiler: pouco).
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import random
import statistics as st
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

_bm = (RAIZ / 'scripts/backtest_metricas.py').read_text()
BM = {'__file__': str(RAIZ / 'scripts/backtest_metricas.py')}
exec(_bm[:_bm.index("def varrer(")], BM)
H, ANOS, observar, metricas = BM['H'], BM['ANOS'], BM['observar'], BM['metricas']
MOTOR, DEFENSIVOS, _t_anual = BM['MOTOR'], BM['DEFENSIVOS'], BM['_t_anual']

N_PERM = 300
random.seed(20260913)


def avaliar_conjunto(obs, nomes, rets=None, min_presentes=None):
    """Percentil médio de N indicadores dentro do ano; metade de cima contra metade de baixo.

    `min_presentes` permite avaliar uma empresa que não tem TODOS os indicadores — sem isso,
    um indicador com cobertura ruim (ROIC existe em 39 de 76 observações) derruba o conjunto
    inteiro para o tamanho do pior membro. Usa a média dos percentis disponíveis, desde que
    haja pelo menos `min_presentes`. É a mesma decisão que o motor de preço-teto toma ao rodar
    "os métodos aplicáveis" em vez de exigir todos.
    """
    if min_presentes is None:
        min_presentes = max(2, len(nomes) - 1)
    acima, abaixo, por_ano = [], [], {}
    for a in ANOS[:-1]:
        do_ano = [(t, mm, (rets[(ay, t)] if rets else r))
                  for (ay, t, mm, r) in obs if ay == a]
        if len(do_ano) < 6:
            continue
        pct = {}
        for nome in nomes:
            com = [x for x in do_ano if nome in x[1]]
            if len(com) < 4:
                continue
            ordem = sorted(com, key=lambda x: -x[1][nome])
            for i, row in enumerate(ordem):
                pct.setdefault(row[0], []).append(i / (len(ordem) - 1))
        elegiveis = [x for x in do_ano if len(pct.get(x[0], [])) >= min_presentes]
        if len(elegiveis) < 6:
            continue
        ranked = sorted(elegiveis, key=lambda x: st.mean(pct[x[0]]))
        meio = len(ranked) // 2
        ac = [x[2] for x in ranked[:meio]]
        ab = [x[2] for x in ranked[meio:]]
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


# ── 1 · CONJUNTOS PRÉ-ESPECIFICADOS ──────────────────────────────────────────────────────
# Cada um tem uma tese. Nenhum foi escolhido depois de ver o resultado.
CONJUNTOS = {
    'VALOR PURO (4 réguas de preço)': (
        ['L/P', 'Receita/Preco', 'EBITDA/EV', 'VP/P'],
        'Quatro formas de perguntar "pago pouco pelo quê?": lucro, receita, geração de caixa e '
        'patrimônio. Se as quatro concordam, a empresa está barata por qualquer régua — e não '
        'por um artefato contábil de uma delas.'),
    'VALOR + QUALIDADE': (
        ['L/P', 'Receita/Preco', 'EBITDA/EV', 'VP/P', 'ROE'],
        'O valor puro mais o filtro que separa barato-bom de barato-quebrado.'),
    'VALOR + QUALIDADE + RISCO': (
        ['L/P', 'Receita/Preco', 'EBITDA/EV', 'VP/P', 'ROE', 'Baixa alavancagem'],
        'Acrescenta solvência. Testa se o filtro de risco custa retorno.'),
    'MAGIC FORMULA (Greenblatt)': (
        ['EBIT/EV', 'ROIC'],
        'O clássico: barato pelo operacional + retorno sobre capital. Referência externa — '
        'existe fora deste projeto e não foi calibrado nele.'),
    'VALOR + CRESCIMENTO': (
        ['L/P', 'Receita/Preco', 'Cresc. lucro'],
        'Barato que ainda cresce, em vez de barato que encolhe (armadilha de valor).'),
    'DUPLA VENCEDORA ISOLADA': (
        ['L/P', 'Receita/Preco'],
        'As duas melhores individuais, para saber se o conjunto maior ganha delas.'),
    'TUDO (10 indicadores)': (
        ['L/P', 'Receita/Preco', 'EBITDA/EV', 'VP/P', 'DY', 'ROE', 'ROIC',
         'Margem liq.', 'Baixa alavancagem', 'Cresc. lucro'],
        'Joga tudo junto. Se diluir, mostra que indicador ruim contamina o conjunto.'),
}


def p_conjunto(obs, nomes, real, n_iter=N_PERM):
    por_ano = {}
    for (a, t, _mm, r) in obs:
        por_ano.setdefault(a, []).append((t, r))
    cont = 0
    for _ in range(n_iter):
        rets = {}
        for a, lst in por_ano.items():
            vals = [r for _t, r in lst]
            random.shuffle(vals)
            for (t, _r), v in zip(lst, vals):
                rets[(a, t)] = v
        r = avaliar_conjunto(obs, nomes, rets)
        if r and r['spread'] >= real:
            cont += 1
    return cont / n_iter


def rodar(tickers, titulo):
    obs = observar(tickers)
    print('\n' + '═' * 100)
    print(titulo)
    print('═' * 100)
    print(f'{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · '
          f'{len(set(o[0] for o in obs))} transições anuais')

    print('\n1 · CONJUNTOS PRÉ-ESPECIFICADOS (tese declarada antes do resultado)')
    print('-' * 100)
    print(f"{'Conjunto':<34}{'n':>5}{'spread':>10}{'t':>8}{'anos certos':>13}{'p':>9}")
    print('-' * 100)
    res = {}
    for nome, (membros, _tese) in CONJUNTOS.items():
        r = avaliar_conjunto(obs, membros)
        if not r:
            continue
        p = p_conjunto(obs, membros, r['spread'])
        res[nome] = (r, p)
        marca = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.10 else ''))
        anos = '%d de %d' % (r['pos'], r['anos'])
        tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
        print(f"{nome:<34}{r['n']:>5}{r['spread']*100:>9.1f}%{tt:>8}{anos:>13}{p:>9.3f} {marca}")

    print('\n2 · BUSCA EXAUSTIVA nos trios — CONTRASTE, não recomendação')
    print('-' * 100)
    nomes_todos = sorted({k for (_a, _t, mm, _r) in obs for k in mm})
    trios = {}
    for c in combinations(nomes_todos, 3):
        r = avaliar_conjunto(obs, list(c))
        if r:
            trios[' + '.join(c)] = r
    ordem = sorted(trios.items(), key=lambda kv: (-(kv[1]['pos'] / kv[1]['anos']), -kv[1]['spread']))
    print(f'  {len(trios)} trios testados. Cinco melhores por consistência:')
    for nome, r in ordem[:5]:
        anos = '%d de %d' % (r['pos'], r['anos'])
        tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
        print(f"    {nome:<58}{r['spread']*100:>8.1f}%{tt:>8}{anos:>13}")

    # Contrafactual da pesca: melhor de N trios com retorno embaralhado
    melhor_real = max(trios.values(), key=lambda r: r['spread'])['spread']
    por_ano = {}
    for (a, t, _mm, r) in obs:
        por_ano.setdefault(a, []).append((t, r))
    amostra = [list(c) for c in combinations(nomes_todos, 3)]
    random.shuffle(amostra)
    amostra = amostra[:120]          # subconjunto: 560 × 100 permutações não cabe no tempo
    melhores = []
    for _ in range(100):
        rets = {}
        for a, lst in por_ano.items():
            vals = [r for _t, r in lst]
            random.shuffle(vals)
            for (t, _r), v in zip(lst, vals):
                rets[(a, t)] = v
        sp = [avaliar_conjunto(obs, c, rets) for c in amostra]
        sp = [x['spread'] for x in sp if x]
        if sp:
            melhores.append(max(sp))
    melhores.sort()
    p50 = melhores[len(melhores) // 2]
    acima = sum(1 for d in melhores if d >= melhor_real) / len(melhores)
    print(f'\n  Melhor trio REAL: {melhor_real*100:+.1f} p.p.')
    print(f'  Melhor de 120 trios SEM informação: mediana {p50*100:+.1f} p.p.')
    print(f'  → o acaso bate o melhor real em {acima*100:.0f}% das rodadas'
          f'  ({"NÃO se distingue de sorte" if acima > 0.10 else "se separa"})')
    return res


if __name__ == '__main__':
    defensivos = {t for t in H if MOTOR.get(t) in DEFENSIVOS}
    rodar(defensivos, 'DEFENSIVOS (FIN + UTIL) — bancos, seguros, elétricas, telecom, saneamento')
    rodar(set(H), 'RADAR INTEIRO — 30 tickers')

    print('\n' + '═' * 100)
    print('AS TESES DOS CONJUNTOS')
    print('═' * 100)
    for nome, (membros, tese) in CONJUNTOS.items():
        print(f'\n  {nome}')
        print(f'    {" · ".join(membros)}')
        print(f'    {tese}')
