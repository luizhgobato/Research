#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# BARATO CONTRA A PRÓPRIA HISTÓRIA, CONTRA OS PARES, OU A MÉDIA DOS DOIS? (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pergunta do usuário, no caso ALOS3: "se os pares negociam a 12-15x P/FFO esse deveria ser o
# múltiplo justo pra ela... deve ter uma média dos dois".
#
# É a escolha de ÂNCORA, e ela tem três opções legítimas:
#
#   PRÓPRIA  — o múltiplo que ESTA empresa já negociou. Captura o que ela tem de específico
#              (governança, alavancagem, qualidade do ativo), mas congela um desconto que
#              pode ser injusto e nunca deixa a empresa "sair" do próprio patamar.
#
#   PARES    — a mediana do múltiplo dos concorrentes HOJE. Enxerga re-rating e não herda o
#              passado da empresa, mas importa o preço de OUTRO negócio e trata desconto
#              estrutural (que pode ser merecido) como oportunidade.
#
#   MÉDIA    — metade de cada. A hipótese do usuário: o erro de uma compensa o da outra.
#
# Como as três viram um número comparável: preço = múltiplo × fundamento, então
# margem = múltiplo-alvo ÷ múltiplo-corrente − 1. Não precisa reconstruir o preço.
#
# ⚠️ PONTO NO TEMPO, igual aos outros: base truncada a cada ano (H_ate(2023) só vê 2021-2023).
# A âncora PRÓPRIA usa a mediana histórica até aquele ano; a de PARES usa o corte transversal
# daquele ano. Nenhuma enxerga o futuro.
#
# ⚠️ Pares = mesmo grupo de motor (FIN, UTIL, CICL, IND, SHOP, NAV), o ticker fora da própria
# mediana. Mínimo de 3 pares — SHOP tem 2 empresas e fica de fora, o que já diz algo sobre
# usar peer comp num setor de 3 listadas.
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import random
import statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MT = {}
_src = (RAIZ / 'scripts/motor_teto.py').read_text()
exec(_src[:_src.index("if __name__ == '__main__':")], MT)
_bm = (RAIZ / 'scripts/backtest_metricas.py').read_text()
BM = {'__file__': str(RAIZ / 'scripts/backtest_metricas.py')}
exec(_bm[:_bm.index("def varrer(")], BM)
H, ANOS, num, retorno = BM['H'], BM['ANOS'], BM['num'], BM['retorno']
MOTOR, DEFENSIVOS, _t_anual = BM['MOTOR'], BM['DEFENSIVOS'], BM['_t_anual']

ANOS_TESTE = [2023, 2024, 2025]
MIN_PARES = 3
N_PERM = 2000
random.seed(20260913)

# Múltiplos em que MENOR = mais barato. Todos vêm prontos da base.
METRICAS = ['pl', 'pvp', 'evEbitda']


def mult(t, ano, campo):
    d = H.get(t, {}).get(ano) or H.get(t, {}).get(str(ano))
    v = num(d, campo) if d else None
    return v if (v and 0 < v < 80) else None


def serie_ate(t, ano, campo):
    out = []
    for y in range(2015, ano + 1):
        v = mult(t, y, campo)
        if v: out.append(v)
    return out


def H_ate(ano):
    out = {}
    for t, A in H.items():
        sub = {int(y): d for y, d in A.items() if int(y) <= ano}
        if sub: out[t] = sub
    return out


def margem_motor(t, A, preco):
    """A âncora própria COMO O MOTOR FAZ: quebra de série, tendência, correção de units.

    A versão crua (mediana simples do campo `pl` da base) ignora tudo isso — e é justamente o
    que os filtros existem para consertar. Comparar peer comp contra a versão crua seria
    comparar o método deles contra uma caricatura do nosso.
    """
    vals = []
    for f in (lambda: MT['teto_ep'](t, A, pl_setor=None),
              lambda: MT['teto_pvp'](t, A),
              lambda: MT['teto_ev_receita'](t, A)):
        try: r = f()
        except Exception: r = None
        if r and r.get('justo') and r['justo'] > 0: vals.append(r['justo'])
    if not vals: return None
    return st.median(vals) / preco - 1


def coletar(tickers):
    """[(ano, ticker, propria_crua, pares, media, retorno, propria_motor, media_motor)]"""
    obs = []
    for ano in ANOS_TESTE:
        Ht = H_ate(ano)
        MT['H_GLOBAL'] = Ht
        MT['PL_SETOR'].clear()
        try: MT['PL_SETOR'].update(MT['pl_setorial'](Ht))
        except Exception: pass
        # corte transversal do ano, por grupo de motor
        porgrupo = {}
        for t in H:
            g = MOTOR.get(t)
            if not g: continue
            for c in METRICAS:
                v = mult(t, ano, c)
                if v: porgrupo.setdefault((g, c), []).append((t, v))
        for t in tickers:
            g = MOTOR.get(t)
            r = retorno(t, ano)
            if not g or r is None: continue
            rp, rq = [], []
            for c in METRICAS:
                atual = mult(t, ano, c)
                if not atual: continue
                hist = serie_ate(t, ano, c)
                if len(hist) >= 3:
                    rp.append(st.median(hist) / atual - 1)        # alvo próprio ÷ corrente
                pares = [v for (o, v) in porgrupo.get((g, c), []) if o != t]
                if len(pares) >= MIN_PARES:
                    rq.append(st.median(pares) / atual - 1)        # alvo dos pares ÷ corrente
            if not rp or not rq: continue
            mp, mq = st.median(rp), st.median(rq)
            preco = num(Ht.get(t, {}).get(ano) or {}, 'preco')
            mm = margem_motor(t, Ht[t], preco) if (t in Ht and preco) else None
            if mm is None: continue
            obs.append((ano, t, mp, mq, (mp + mq) / 2, r, mm, (mm + mq) / 2))
    return obs


def _spread(obs, idx, regra):
    por_ano, ac_t, ab_t = {}, [], []
    for ano in ANOS_TESTE:
        linhas = [(o[idx], o[5]) for o in obs if o[0] == ano]
        if len(linhas) < 4: continue
        if regra == 'regua':
            med = st.median(v for v, _ in linhas)
            ac = [r for v, r in linhas if v > med]; ab = [r for v, r in linhas if v <= med]
        else:
            ac = [r for v, r in linhas if v > 0]; ab = [r for v, r in linhas if v <= 0]
        if not ac or not ab: continue
        ac_t += ac; ab_t += ab
        por_ano[ano] = st.mean(ac) - st.mean(ab)
    if not por_ano: return None
    sp = list(por_ano.values())
    return dict(spread=st.mean(ac_t) - st.mean(ab_t), n=len(ac_t) + len(ab_t),
                mAc=st.mean(ac_t), mAb=st.mean(ab_t), pos=sum(1 for v in sp if v > 0),
                anos=len(sp), t=_t_anual(sp), por_ano=por_ano)


def p_perm(obs, idx, regra, real):
    por = {}
    for o in obs: por.setdefault(o[0], []).append(o)
    cont = 0
    for _ in range(N_PERM):
        emb = []
        for _a, lst in por.items():
            rets = [o[5] for o in lst]; random.shuffle(rets)
            emb += [(o[0], o[1], o[2], o[3], o[4], rr, o[6], o[7]) for o, rr in zip(lst, rets)]
        r = _spread(emb, idx, regra)
        if r and r['spread'] >= real: cont += 1
    return cont / N_PERM


def rodar(tickers, titulo):
    obs = coletar(tickers)
    print('\n' + '═' * 96); print(titulo); print('═' * 96)
    if not obs: print('  sem observações'); return
    print(f'{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · '
          f'{len(set(o[0] for o in obs))} anos')
    for regra, rot in (('regua', 'RÉGUA — margem maior rendeu mais?'),
                       ('porteira', 'PORTEIRA — margem positiva rendeu mais?')):
        print(f'\n{rot}'); print('-' * 96)
        print(f"{'Âncora':<30}{'n':>5}{'abaixo':>9}{'acima':>9}{'spread':>10}{'t':>8}{'anos':>7}{'p':>8}")
        print('-' * 96)
        for idx, nome in ((6, 'PRÓPRIA — motor de produção'), (2, 'PRÓPRIA — mediana crua'),
                          (3, 'PARES do setor'), (7, 'MÉDIA motor + pares'), (4, 'MÉDIA crua + pares')):
            r = _spread(obs, idx, regra)
            if not r: print(f'{nome:<30}   — sem split'); continue
            p = p_perm(obs, idx, regra, r['spread'])
            marca = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.10 else ''))
            tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
            print(f"{nome:<30}{r['n']:>5}{r['mAc']*100:>8.1f}%{r['mAb']*100:>8.1f}%"
                  f"{r['spread']*100:>9.1f}%{tt:>8}{('%d/%d'%(r['pos'],r['anos'])):>7}{p:>8.3f} {marca}")
            print(f"{'':<30}   " + '  '.join(f'{a}: {v*100:+.1f}pp' for a, v in sorted(r['por_ano'].items())))
    cor = sum(1 for o in obs if (o[6] > 0) == (o[3] > 0)) / len(obs)
    print(f'\nPrópria e pares concordam no veredicto barato/caro em {cor*100:.0f}% das linhas')


if __name__ == '__main__':
    rodar({t for t in H if MOTOR.get(t) in DEFENSIVOS}, 'DEFENSIVOS (FIN + UTIL)')
    rodar(set(H), 'RADAR INTEIRO')
