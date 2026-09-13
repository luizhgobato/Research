#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# A MARGEM DE SEGURANÇA PREDIZ RETORNO? — teste de ponta a ponta do preço-teto (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Esta é a pergunta que decide se o motor de preço-teto serve para alguma coisa:
#
#     Quando o preço estava ABAIXO do teto, o retorno dos 12 meses seguintes foi maior?
#
# Os outros backtests testam MÚLTIPLOS e RÉGUAS DE ORDENAÇÃO. Nenhum testa o teto de verdade —
# o número em reais que sai de `motor_teto.py` depois da mediana de métodos, do Ke variável,
# do ajuste de convicção e da margem que escala com ela. `backtest_multiplos.py` usa um PROXY
# grosseiro (mediana do próprio P/L ou P/VP), declarado como tal no comentário dele.
#
# ⚠️ RECONSTRUÇÃO PONTO NO TEMPO — a parte que torna o teste honesto. O motor calcula o teto de
# HOJE lendo a série inteira. Rodá-lo assim sobre 2023 usaria dado de 2024-2026 para decidir se
# 2023 estava barato: olhar o futuro, e o resultado sairia bom por construção. Em vez disso a
# base é TRUNCADA a cada ano — `H_ate(2023)` contém só 2021-2023 — e o motor roda sobre ela sem
# saber que 2024 existe. É o mesmo motor, os mesmos métodos, a mesma mediana; muda só o que ele
# enxerga.
#
# ⚠️ O QUE CONTINUA ANACRÔNICO, e não dá para corrigir: as premissas (IPCA 4,44%, juro real
# normalizado 5,5%, prêmio 5,0 p.p., g = IPCA+2%) são as de hoje, aplicadas a 2023. Elas movem
# o NÍVEL de todos os tetos em bloco, não a ordem entre eles — então o teste de ORDENAÇÃO
# (margem alta rende mais que margem baixa?) sobrevive; o teste de NÍVEL ("margem positiva é
# sinal de compra?") fica com essa ressalva, e ela está impressa junto do resultado.
#
# ⚠️ AMOSTRA: o motor precisa de 2-3 anos de série, e o HIST_SEED começa em 2021. Sobram três
# reconstruções (2023, 2024, 2025) e três retornos futuros. É pouco até para os padrões já
# baixos deste projeto — por isso o teste roda também o CONTRAFACTUAL: as mesmas observações,
# ordenadas pelos critérios validados, para comparar maçã com maçã.
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import random
import statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

_bm = (RAIZ / 'scripts/backtest_metricas.py').read_text()
BM = {'__file__': str(RAIZ / 'scripts/backtest_metricas.py')}
exec(_bm[:_bm.index("def varrer(")], BM)
H, ANOS, num, retorno = BM['H'], BM['ANOS'], BM['num'], BM['retorno']
MOTOR, DEFENSIVOS, _t_anual, metricas = BM['MOTOR'], BM['DEFENSIVOS'], BM['_t_anual'], BM['metricas']

# Motor completo, não só o dicionário MOTOR: precisamos de calcular(), pl_setorial() e do
# H_GLOBAL que o motor NAV usa para ler a investida.
MT = {}
_src = (RAIZ / 'scripts/motor_teto.py').read_text()
exec(_src[:_src.index("if __name__ == '__main__':")], MT)

ANOS_TESTE = [2023, 2024, 2025]
DEBUG = False
random.seed(20260913)


def H_ate(ano):
    """Base truncada: só os exercícios até `ano`. É o que o motor teria visto naquela data."""
    # ⚠️ CHAVE INTEIRA, não string. `backtest_multiplos.py` carrega o HIST_SEED via json e as
    # chaves de ano viram STRING ("2026"); `motor_teto.carregar()` faz int() e usa INTEIRO.
    # O motor faz aritmética com o ano (y-1, anos consecutivos), então string estoura — e na
    # primeira versão deste script o `except Exception` engolia o erro e devolvia zero
    # observações sem dizer por quê. A conversão é aqui, uma vez, no ponto de fronteira.
    out = {}
    for t, A in H.items():
        sub = {int(y): d for y, d in A.items() if int(y) <= ano}
        if sub:
            out[t] = sub
    return out


def tetos_do_ano(ano):
    """Roda o motor inteiro sobre a base truncada e devolve {ticker: (teto, preco, margem)}."""
    Ht = H_ate(ano)
    MT['H_GLOBAL'] = Ht
    MT['PL_SETOR'].clear()
    try:
        MT['PL_SETOR'].update(MT['pl_setorial'](Ht))
    except Exception:
        pass
    out = {}
    for t, A in Ht.items():
        if ano not in A:
            continue
        preco = num(A[ano], 'preco')
        if not preco or preco <= 0:
            continue
        try:
            r = MT['calcular'](t, A)
        except Exception as e:
            if DEBUG:
                print(f'    [debug] {t} {ano}: {type(e).__name__}: {e}')
            continue
        # ⚠️ `calcular()` NÃO devolve o campo `teto` — devolve `justo` e `conv`. O teto é
        # derivado no __main__ do motor: justo × (1 − MARGEM[conv]), onde a margem escala com
        # a convicção (★★★ 10%, ★★ 15%, ★ 25%). Replicar aqui a mesma linha, lendo MARGEM do
        # próprio motor, em vez de reescrever o número — se a tabela mudar lá, muda aqui junto.
        if not r or r.get('recusa') or not r.get('justo'):
            continue
        teto = r['justo'] * (1 - MT['MARGEM'][r.get('conv', 1)])
        if not teto or teto <= 0:
            continue
        out[t] = dict(teto=teto, preco=preco, margem=teto / preco - 1,
                      conv=r.get('conv'), justo=r.get('justo'))
    return out


def coletar(tickers):
    """[(ano, ticker, margem, conviccao, retorno_futuro, metricas_do_ano)]"""
    obs = []
    for ano in ANOS_TESTE:
        tet = tetos_do_ano(ano)
        for t, d in tet.items():
            if t not in tickers:
                continue
            r = retorno(t, ano)
            if r is None:
                continue
            obs.append((ano, t, d['margem'], d['conv'], r, metricas(t, ano)))
    return obs


def _split(vals_rets):
    """Mediana-acima menos mediana-abaixo."""
    if len(vals_rets) < 4:
        return None
    med = st.median(v for v, _r in vals_rets)
    ac = [r for v, r in vals_rets if v > med]
    ab = [r for v, r in vals_rets if v <= med]
    if not ac or not ab:
        return None
    return st.mean(ac), st.mean(ab), len(ac) + len(ab)


def testar(obs, extrai, rotulo):
    acima, abaixo, por_ano = [], [], {}
    for ano in ANOS_TESTE:
        vr = [(extrai(o), o[4]) for o in obs if o[0] == ano and extrai(o) is not None]
        s = _split(vr)
        if not s:
            continue
        ac, ab, _n = s
        acima += [r for v, r in vr if v > st.median(x[0] for x in vr)]
        abaixo += [r for v, r in vr if v <= st.median(x[0] for x in vr)]
        por_ano[ano] = ac - ab
    if not por_ano:
        return None
    sp = list(por_ano.values())
    return dict(rotulo=rotulo, spread=st.mean(acima) - st.mean(abaixo),
                n=len(acima) + len(abaixo), pos=sum(1 for v in sp if v > 0),
                anos=len(sp), t=_t_anual(sp), por_ano=por_ano)


def linha(r):
    if not r:
        return
    tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
    anos = '%d de %d' % (r['pos'], r['anos'])
    print(f"  {r['rotulo']:<44}{r['n']:>5}{r['spread']*100:>9.1f}%{tt:>8}{anos:>10}")


def rodar(tickers, titulo):
    obs = coletar(tickers)
    print('\n' + '═' * 96)
    print(titulo)
    print('═' * 96)
    if not obs:
        print('  sem observações — o motor não produziu teto para nenhum ticker nestes anos')
        return
    print(f'{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · '
          f'{len(set(o[0] for o in obs))} anos reconstruídos ponto no tempo')

    # ── 1 · A REGRA QUE VOCÊ USA NA PRÁTICA ──────────────────────────────────────────────
    print('\n1 · A REGRA DE DECISÃO: preço abaixo do teto é sinal de compra?')
    print('-' * 96)
    abaixo_teto = [o[4] for o in obs if o[2] > 0]
    acima_teto = [o[4] for o in obs if o[2] <= 0]
    if abaixo_teto and acima_teto:
        print(f'  ABAIXO do teto (margem > 0) : retorno médio {st.mean(abaixo_teto)*100:6.1f}%  '
              f'(n={len(abaixo_teto)})')
        print(f'  ACIMA do teto  (margem ≤ 0) : retorno médio {st.mean(acima_teto)*100:6.1f}%  '
              f'(n={len(acima_teto)})')
        print(f'  diferença: {(st.mean(abaixo_teto)-st.mean(acima_teto))*100:+.1f} p.p.')
        print('  ⚠️ sujeito à ressalva do nível: as premissas de hoje aplicadas ao passado movem')
        print('     todos os tetos em bloco, e é o NÍVEL que decide quem fica acima ou abaixo.')
    else:
        print('  todas as observações caíram do mesmo lado do teto — regra não testável aqui')

    # ── 2 · ORDENAÇÃO: margem maior rende mais? (imune à ressalva do nível) ──────────────
    print('\n2 · ORDENAÇÃO — margem maior rende mais? (o nível não afeta a ordem)')
    print('-' * 96)
    print(f"  {'Critério':<44}{'n':>5}{'spread':>10}{'t':>8}{'anos ok':>10}")
    print('-' * 96)
    r_margem = testar(obs, lambda o: o[2], 'MARGEM SOBRE O TETO (o motor completo)')
    linha(r_margem)

    # ── 3 · CONTRAFACTUAL: os mesmos dados, pelos critérios validados ────────────────────
    for nome in ('L/P', 'Receita/Preco'):
        linha(testar(obs, lambda o, n=nome: o[5].get(n), f'{nome} (isolado)'))

    def trio(o):
        vs = [o[5].get(n) for n in ('L/P', 'Receita/Preco', 'Cresc. lucro')]
        return None if any(v is None for v in vs) else vs

    # trio precisa de percentil dentro do ano — calculado à parte
    acima, abaixo, por_ano = [], [], {}
    for ano in ANOS_TESTE:
        do_ano = [(o[1], trio(o), o[4]) for o in obs if o[0] == ano and trio(o) is not None]
        if len(do_ano) < 4:
            continue
        pct = {}
        for i in range(3):
            ordem = sorted(do_ano, key=lambda x: -x[1][i])
            for j, row in enumerate(ordem):
                pct.setdefault(row[0], []).append(j / max(1, len(ordem) - 1))
        ranked = sorted(do_ano, key=lambda x: st.mean(pct[x[0]]))
        meio = len(ranked) // 2
        ac = [x[2] for x in ranked[:meio]]
        ab = [x[2] for x in ranked[meio:]]
        if ac and ab:
            acima += ac
            abaixo += ab
            por_ano[ano] = st.mean(ac) - st.mean(ab)
    if por_ano:
        sp = list(por_ano.values())
        linha(dict(rotulo='TRIO VALIDADO (L/P+Receita/P+Cresc.)',
                   spread=st.mean(acima) - st.mean(abaixo), n=len(acima) + len(abaixo),
                   pos=sum(1 for v in sp if v > 0), anos=len(sp), t=_t_anual(sp)))

    # ── 4 · A CONVICÇÃO SIGNIFICA ALGO? ─────────────────────────────────────────────────
    print('\n4 · A CONVICÇÃO (★) separa teto bom de teto ruim?')
    print('-' * 96)
    por_conv = {}
    for o in obs:
        if o[3] is not None:
            por_conv.setdefault(o[3], []).append((o[2], o[4]))
    for c in sorted(por_conv, reverse=True):
        vr = por_conv[c]
        s = _split(vr)
        txt = f'spread margem {(s[0]-s[1])*100:+6.1f} p.p.' if s else 'amostra pequena'
        print(f'  convicção {c}★ : n={len(vr):>3}  retorno médio {st.mean(r for _v, r in vr)*100:6.1f}%   {txt}')
    print('  (se o teto ★★★ não ordena melhor que o ★, a convicção não está medindo confiança)')
    return obs


if __name__ == '__main__':
    defensivos = {t for t in H if MOTOR.get(t) in DEFENSIVOS}
    rodar(defensivos, 'DEFENSIVOS (FIN + UTIL) — bancos, seguros, elétricas, telecom, saneamento')
    rodar(set(H), 'RADAR INTEIRO')
