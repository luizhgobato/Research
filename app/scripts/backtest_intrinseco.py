#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# "QUANTO O MERCADO PAGA" vs "QUANTO A EMPRESA DEVERIA VALER" — qual prediz retorno? (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pergunta do usuário, e ela é a pergunta de fundo de todo o motor. Duas escolas:
#
#   RELATIVA  — o preço justo é o múltiplo que a PRÓPRIA empresa já negociou, aplicado ao
#               fundamento de hoje. Não projeta nada. É o que `motor_teto.py` faz hoje.
#               Aqui: mediana de E/P, P/VP e EV/Receita.
#
#   INTRÍNSECA — o preço justo é o valor presente do que a empresa vai gerar. Exige Ke, g e
#               uma trajetória de ROE. É o que o relatório da ALOS3 faz, e o que Gordon,
#               DDM e lucro residual fazem. Aqui: mediana de Gordon (ROE/Ke/g sobre o
#               patrimônio), lucro residual com fade de 10 anos, e Gordon sobre dividendo.
#
# Os dois já existem em motor_teto.py — o intrínseco saiu da composição em 13/09/2026 sem
# nunca ter sido medido CONTRA o relativo. Este script mede.
#
# ⚠️ RECONSTRUÇÃO PONTO NO TEMPO, igual a backtest_margem.py: a base é truncada a cada ano
# (H_ate(2023) só contém 2021-2023) e cada família roda sem saber que o futuro existe.
#
# ⚠️ ANACRONISMO QUE NÃO DÁ PARA CORRIGIR, e que pesa MAIS contra o intrínseco: as premissas
# (IPCA 4,44%, juro real normalizado 5,5%, prêmio 5,0 p.p., g = IPCA+2%) são as de hoje
# aplicadas a 2023. Elas movem o NÍVEL de todos os justos em bloco. O teste de ORDENAÇÃO
# sobrevive a isso; o de NÍVEL (porteira) fica com a ressalva impressa junto do resultado.
#
# ⚠️ AMOSTRA: 3 reconstruções (2023, 2024, 2025). É pouco. Por isso cada resultado sai com
# t-stat sobre os spreads ANUAIS e com teste de permutação.
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
MOTOR, DEFENSIVOS, _t_anual = BM['MOTOR'], BM['DEFENSIVOS'], BM['_t_anual']

MT = {}
_src = (RAIZ / 'scripts/motor_teto.py').read_text()
exec(_src[:_src.index("if __name__ == '__main__':")], MT)

ANOS_TESTE = [2023, 2024, 2025]
N_PERM = 2000
random.seed(20260913)


def H_ate(ano):
    out = {}
    for t, A in H.items():
        sub = {int(y): d for y, d in A.items() if int(y) <= ano}
        if sub:
            out[t] = sub
    return out


def _med(vals):
    vals = [v for v in vals if v and v > 0]
    return st.median(vals) if vals else None


def justo_relativo(t, A):
    """Só múltiplo da própria empresa. Nenhuma premissa de futuro.

    Devolve (mediana dos justos, PISO da faixa). O piso — menor p25 entre os métodos — é o que
    a produção usa como teto de compra desde 13/09/2026, e é uma porteira bem mais estreita que
    a mediana. Testar os dois separa "a família relativa funciona?" de "o CORTE certo é o piso?".
    """
    out, los = [], []
    for f in (lambda: MT['teto_ep'](t, A, pl_setor=None),
              lambda: MT['teto_pvp'](t, A),
              lambda: MT['teto_ev_receita'](t, A)):
        try:
            r = f()
        except Exception:
            r = None
        if r and r.get('justo'):
            out.append(r['justo'])
            fx = r.get('faixa')
            los.append(fx[0] if (fx and fx[0] and fx[0] > 0) else r['justo'])
    return _med(out), (min(los) if los else None)


def justo_intrinseco(t, A):
    """Valor presente do que a empresa gera. Precisa de Ke, g e trajetória de ROE."""
    out = []
    try:
        val, _q = MT['anos_validos'](A)
        roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
        roe = MT['mediana_com_tendencia'](roes, limiar_abs=2.0)[0] if roes else None
        v = MT['vpa'](t, A)
        po, _n, _f = MT['payout_final'](t, A)
        ke, _det = MT['ke_empresa'](t, A)
        G = MT['G']
        if roe and v and v > 0 and po is not None:
            # A · Gordon sobre o patrimônio: vantagem competitiva ETERNA
            if ke > G and roe > G:
                out.append(v * (roe - G) / (ke - G))
            # B · Lucro residual com fade: vantagem some em 10 anos
            out.append(MT['rim_fade'](v, roe, ke, po, rt=(roe + ke) / 2))
    except Exception:
        pass
    # C · Gordon sobre dividendo (o "Bazin" do motor)
    try:
        r = MT['teto_bazin'](t, A)
        if r and r.get('justo'):
            out.append(r['justo'])
    except Exception:
        pass
    return _med(out)


def coletar(tickers):
    """[(ano, ticker, margem_rel, margem_int, retorno)] — só linhas em que AMBOS existem."""
    obs = []
    for ano in ANOS_TESTE:
        Ht = H_ate(ano)
        MT['H_GLOBAL'] = Ht
        MT['PL_SETOR'].clear()
        try:
            MT['PL_SETOR'].update(MT['pl_setorial'](Ht))
        except Exception:
            pass
        for t, A in Ht.items():
            if t not in tickers or ano not in A:
                continue
            preco = num(A[ano], 'preco')
            r = retorno(t, ano)
            if not preco or preco <= 0 or r is None:
                continue
            jr, piso = justo_relativo(t, A)
            ji = justo_intrinseco(t, A)
            if not jr or not ji or not piso:
                continue
            # Margem de segurança na MESMA convenção do Radar: (justo − preço) ÷ justo.
            obs.append((ano, t, (jr - preco) / jr, (ji - preco) / ji, r, (piso - preco) / piso))
    return obs


def _spread_anual(obs, idx, regra):
    """regra='regua' → metade de cima vs metade de baixo. regra='porteira' → margem>0 vs <=0."""
    por_ano, acima, abaixo = {}, [], []
    for ano in ANOS_TESTE:
        linhas = [(o[idx], o[4]) for o in obs if o[0] == ano]
        if len(linhas) < 4:
            continue
        if regra == 'regua':
            med = st.median(v for v, _ in linhas)
            ac = [r for v, r in linhas if v > med]
            ab = [r for v, r in linhas if v <= med]
        else:
            ac = [r for v, r in linhas if v > 0]
            ab = [r for v, r in linhas if v <= 0]
        if not ac or not ab:
            continue
        acima += ac
        abaixo += ab
        por_ano[ano] = st.mean(ac) - st.mean(ab)
    if not por_ano:
        return None
    sp = list(por_ano.values())
    return dict(spread=st.mean(acima) - st.mean(abaixo), n=len(acima) + len(abaixo),
                mAc=st.mean(acima), mAb=st.mean(abaixo),
                pos=sum(1 for v in sp if v > 0), anos=len(sp), t=_t_anual(sp), por_ano=por_ano)


def p_permuta(obs, idx, regra, real):
    """Embaralha o RETORNO dentro de cada ano. Mede com que frequência o acaso bate o real."""
    por_ano = {}
    for o in obs:
        por_ano.setdefault(o[0], []).append(o)
    cont = 0
    for _ in range(N_PERM):
        emb = []
        for ano, lst in por_ano.items():
            rets = [o[4] for o in lst]
            random.shuffle(rets)
            emb += [(o[0], o[1], o[2], o[3], rr, o[5]) for o, rr in zip(lst, rets)]
        r = _spread_anual(emb, idx, regra)
        if r and r['spread'] >= real:
            cont += 1
    return cont / N_PERM


def rodar(tickers, titulo):
    obs = coletar(tickers)
    print('\n' + '═' * 98)
    print(titulo)
    print('═' * 98)
    if not obs:
        print('  sem observações')
        return
    print(f'{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · '
          f'{len(set(o[0] for o in obs))} anos · ambas as famílias calculáveis na mesma linha')

    for regra, rot in (('porteira', 'PORTEIRA — abaixo do justo rendeu mais que acima?'),
                       ('regua', 'RÉGUA — margem maior rendeu mais que margem menor?')):
        print(f'\n{rot}')
        print('-' * 98)
        print(f"{'Família':<44}{'n':>5}{'abaixo':>9}{'acima':>9}{'spread':>10}{'t':>8}{'anos':>7}{'p':>8}")
        print('-' * 98)
        for idx, nome in ((2, 'RELATIVA — mediana dos múltiplos'),
                          (5, 'RELATIVA — piso da faixa (teto de produção)'),
                          (3, 'INTRÍNSECA (Gordon + lucro residual + DDM)')):
            r = _spread_anual(obs, idx, regra)
            if not r:
                print(f'{nome:<44}    — sem split possível')
                continue
            p = p_permuta(obs, idx, regra, r['spread'])
            marca = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.10 else ''))
            tt = ('%+.2f' % r['t']) if r['t'] is not None else '—'
            print(f"{nome:<44}{r['n']:>5}{r['mAc']*100:>8.1f}%{r['mAb']*100:>8.1f}%"
                  f"{r['spread']*100:>9.1f}%{tt:>8}{('%d/%d' % (r['pos'], r['anos'])):>7}{p:>8.3f} {marca}")
            print(f"{'':<44}   por ano: " +
                  '  '.join(f'{a}: {v*100:+.1f}pp' for a, v in sorted(r['por_ano'].items())))

    # Quanto os dois discordam entre si — se dessem o mesmo número, a pergunta não existiria
    difs = [abs(o[2] - o[3]) for o in obs]
    print(f'\nDISCORDÂNCIA entre as duas famílias: mediana {st.median(difs)*100:.0f} p.p. de margem '
          f'(min {min(difs)*100:.0f} · max {max(difs)*100:.0f})')
    conc = sum(1 for o in obs if (o[2] > 0) == (o[3] > 0)) / len(obs)
    print(f'Concordam no VEREDICTO (barato/caro) em {conc*100:.0f}% das linhas')


if __name__ == '__main__':
    defensivos = {t for t in H if MOTOR.get(t) in DEFENSIVOS}
    rodar(defensivos, 'DEFENSIVOS (FIN + UTIL) — bancos, seguros, elétricas, telecom, saneamento')
    rodar(set(H), 'RADAR INTEIRO')
