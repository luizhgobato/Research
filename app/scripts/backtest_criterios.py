#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# QUAIS CRITÉRIOS DIZEM QUE ESTÁ BARATA — teste de COMBINAÇÕES (13/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pergunta do usuário, literal: "uma empresa com P/L baixo e ROE alto, ela subiu na cotação
# nos anos seguintes ou não? Quais critérios podemos colocar no motor que dirão se ela está
# barata agora, mas com base em critérios validados?"
#
# Os dois backtests anteriores respondem outra coisa:
#   · backtest_multiplos.py  → qual MÚLTIPLO isolado separa vencedor de perdedor
#   · backtest_ranking.py    → qual régua ORDENA melhor a fila, por grupo de motor
# Nenhum dos dois testa CONDIÇÃO COMBINADA, que é como a decisão é tomada na prática: ninguém
# compra por P/L baixo sozinho — compra por P/L baixo E empresa que presta.
#
# Este script testa três coisas:
#   A · SINAIS ISOLADOS, incluindo os de QUALIDADE (ROE, margem, alavancagem, crescimento),
#       que nunca tinham sido medidos contra retorno — só os de preço tinham.
#   B · 2x2 CONDICIONAL: corta o universo do ano pela MEDIANA de um sinal de preço e pela
#       mediana de um sinal de qualidade, e compara os quatro quadrantes. É a resposta direta
#       à pergunta: o quadrante "barato E bom" rendeu mais que "barato E ruim"?
#   C · RANK COMPOSTO: soma dos percentis de dois sinais, contra o melhor sinal sozinho.
#       Só entra no motor o que BATER o sinal isolado — combinar por combinar adiciona
#       parâmetro sem adicionar informação, e parâmetro a mais com n deste tamanho é
#       superajuste garantido.
#
# ⚠️⚠️ O TETO DESTA ANÁLISE, e ele é duro: são 30 tickers e 5 transições anuais, porque o
# único preço por exercício disponível é o do HIST_SEED. A chave de API do MCP Partnr desta
# sessão não tem escopo de cotação histórica (@quotes/post/eod), então NÃO DÁ para montar o
# universo de 300+ papéis × 10 anos que o item #1 do punch-list pede — não por esforço, por
# permissão. Num 2x2 sobram ~3 a 5 empresas por quadrante por ano. Isso é anedota organizada,
# não evidência. O que o teste consegue fazer é DESQUALIFICAR: um critério que erra a direção
# consistentemente aqui não merece entrar no motor. Confirmar, ele não consegue.
#
# Fonte: data/historico.data.js (MCP Partnr, B3/CVM). Nenhuma chamada de rede.
import statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

_bt = (RAIZ / 'scripts/backtest_multiplos.py').read_text()
BT = {'__file__': str(RAIZ / 'scripts/backtest_multiplos.py')}
exec(_bt[:_bt.index('# ── AS MÉTRICAS DA CORRIDA ──')], BT)
H, ANOS, num, retorno = BT['H'], BT['ANOS'], BT['num'], BT['retorno']

_mt = (RAIZ / 'scripts/motor_teto.py').read_text()
MT = {}
exec(_mt[:_mt.index('def carregar()')], MT)
MOTOR = MT['MOTOR']
DEFENSIVOS = ('FIN', 'UTIL')


# ── OS SINAIS ────────────────────────────────────────────────────────────────────────────
# Todos orientados para MAIOR = MELHOR, para que "acima da mediana" signifique a mesma coisa
# em todos eles e os quadrantes do 2x2 não troquem de lado sem avisar.
def sinais(t, a):
    D = H[t].get(str(a))
    if not D:
        return {}
    s = {}
    pl, pvp, dy = num(D, 'pl'), num(D, 'pvp'), num(D, 'dy')
    ev, roe, roic = num(D, 'evEbitda'), num(D, 'roe'), num(D, 'roic')
    mg, de = num(D, 'mgLiq'), num(D, 'divEbitda')

    # PREÇO — "está barata"
    if pl and pl > 0:
        s['L/P'] = 1 / pl
    if pvp and pvp > 0:
        s['VP/P'] = 1 / pvp
    if ev and ev > 0:
        s['EBITDA/EV'] = 1 / ev
    if dy is not None:
        s['DY'] = dy / 100

    # QUALIDADE — "a empresa presta". Nunca foram testados contra retorno neste projeto.
    if roe is not None:
        s['ROE'] = roe
    if roic is not None:
        s['ROIC'] = roic
    if mg is not None:
        s['Margem liq.'] = mg
    if de is not None:
        # Alavancagem invertida: menos dívida = melhor. Caixa líquido (negativo) vira o topo.
        s['Baixa alavancagem'] = -de

    # CRESCIMENTO do lucro do ano anterior para este — o que o `g` da TIR tenta prever.
    ant = H[t].get(str(a - 1))
    if ant:
        l0, l1 = num(ant, 'lucrolin'), num(D, 'lucrolin')
        if l0 and l1 and l0 > 0:
            s['Cresc. lucro'] = (l1 - l0) / l0
    return s


PRECO = ['L/P', 'VP/P', 'EBITDA/EV', 'DY']
QUALIDADE = ['ROE', 'ROIC', 'Margem liq.', 'Baixa alavancagem', 'Cresc. lucro']


def observar(tickers):
    obs = []
    for a in ANOS[:-1]:
        for t in sorted(tickers):
            r = retorno(t, a)
            if r is None:
                continue
            s = sinais(t, a)
            if s:
                obs.append((a, t, s, r))
    return obs


def _t_anual(sp):
    return (st.mean(sp) / (st.stdev(sp) / len(sp) ** .5)) if len(sp) > 2 and st.stdev(sp) else None


# ── A · SINAIS ISOLADOS ──────────────────────────────────────────────────────────────────
def teste_isolado(obs, nomes, titulo):
    print(f'\n{titulo}')
    print('-' * 88)
    print(f"{'Sinal':<22}{'n':>5}{'ACIMA med.':>12}{'ABAIXO med.':>13}{'spread':>10}{'t':>8}  anos certos")
    print('-' * 88)
    out = {}
    for nome in nomes:
        por_ano, acima_t, abaixo_t = {}, [], []
        for a in ANOS[:-1]:
            do_ano = [(s[nome], r) for (ay, _t, s, r) in obs if ay == a and nome in s]
            if len(do_ano) < 6:
                continue
            med = st.median(x[0] for x in do_ano)
            acima = [r for v, r in do_ano if v > med]
            abaixo = [r for v, r in do_ano if v <= med]
            if not acima or not abaixo:
                continue
            acima_t += acima
            abaixo_t += abaixo
            por_ano[a] = st.mean(acima) - st.mean(abaixo)
        if not por_ano:
            continue
        sp = list(por_ano.values())
        spread = st.mean(acima_t) - st.mean(abaixo_t)
        tt = _t_anual(sp)
        pos = sum(1 for v in sp if v > 0)
        out[nome] = (spread, pos, len(sp))
        print(f"{nome:<22}{len(acima_t)+len(abaixo_t):>5}{st.mean(acima_t)*100:>11.1f}%"
              f"{st.mean(abaixo_t)*100:>12.1f}%{spread*100:>9.1f}%"
              f"{(f'{tt:+.2f}' if tt is not None else '   —'):>8}   {pos} de {len(sp)}")
    return out


# ── B · 2x2 CONDICIONAL ──────────────────────────────────────────────────────────────────
def teste_2x2(obs, sp_nome, sq_nome):
    """Corta pela mediana ANUAL dos dois sinais e devolve o retorno médio de cada quadrante."""
    cel = {(1, 1): [], (1, 0): [], (0, 1): [], (0, 0): []}
    por_ano = {}
    for a in ANOS[:-1]:
        do_ano = [(s[sp_nome], s[sq_nome], r) for (ay, _t, s, r) in obs
                  if ay == a and sp_nome in s and sq_nome in s]
        if len(do_ano) < 6:
            continue
        mp = st.median(x[0] for x in do_ano)
        mq = st.median(x[1] for x in do_ano)
        ano_cel = {(1, 1): [], (1, 0): [], (0, 1): [], (0, 0): []}
        for p, q, r in do_ano:
            k = (1 if p > mp else 0, 1 if q > mq else 0)
            cel[k].append(r)
            ano_cel[k].append(r)
        if ano_cel[(1, 1)] and ano_cel[(0, 0)]:
            por_ano[a] = st.mean(ano_cel[(1, 1)]) - st.mean(ano_cel[(0, 0)])
    return cel, por_ano


def imprimir_2x2(obs, sp_nome, sq_nome):
    cel, por_ano = teste_2x2(obs, sp_nome, sq_nome)
    if not any(cel.values()):
        return None
    def m(k):
        return f'{st.mean(cel[k])*100:6.1f}% (n={len(cel[k]):>2})' if cel[k] else '     —      '
    sp = list(por_ano.values())
    tt = _t_anual(sp)
    pos = sum(1 for v in sp if v > 0)
    print(f'\n  {sp_nome} (barato) × {sq_nome} (qualidade)')
    print(f'    {"":<22}{sq_nome+" ALTO":>20}{sq_nome+" BAIXO":>20}')
    print(f'    {"BARATO ("+sp_nome+" alto)":<22}{m((1,1)):>20}{m((1,0)):>20}')
    print(f'    {"CARO ("+sp_nome+" baixo)":<22}{m((0,1)):>20}{m((0,0)):>20}')
    if cel[(1, 1)] and cel[(0, 0)]:
        d = st.mean(cel[(1, 1)]) - st.mean(cel[(0, 0)])
        print(f'    barato+bom − caro+ruim: {d*100:+.1f} p.p.'
              f"{'  · t ' + f'{tt:+.2f}' if tt is not None else ''}"
              f'  · {pos} de {len(sp)} anos')
    if cel[(1, 1)] and cel[(1, 0)]:
        d2 = st.mean(cel[(1, 1)]) - st.mean(cel[(1, 0)])
        print(f'    DENTRO do barato, qualidade alta − baixa: {d2*100:+.1f} p.p.'
              '   ← isto é o que justifica (ou não) somar o filtro de qualidade')
    return cel


# ── C · RANK COMPOSTO ────────────────────────────────────────────────────────────────────
def teste_composto(obs, a_nome, b_nome):
    """Percentil médio dos dois sinais dentro do ano; terço de cima contra terço de baixo."""
    tercos, por_ano = {0: [], 2: []}, {}
    for a in ANOS[:-1]:
        do_ano = [(t, s[a_nome], s[b_nome], r) for (ay, t, s, r) in obs
                  if ay == a and a_nome in s and b_nome in s]
        if len(do_ano) < 6:
            continue
        pct = {}
        for idx, nome in ((1, a_nome), (2, b_nome)):
            ordem = sorted(do_ano, key=lambda x: -x[idx])
            for i, row in enumerate(ordem):
                pct.setdefault(row[0], []).append(i / (len(ordem) - 1))
        rank = sorted(do_ano, key=lambda x: st.mean(pct[x[0]]))
        n = len(rank)
        c = max(1, n // 3)
        tercos[0] += [x[3] for x in rank[:c]]
        tercos[2] += [x[3] for x in rank[-c:]]
        por_ano[a] = st.mean(x[3] for x in rank[:c]) - st.mean(x[3] for x in rank[-c:])
    if not tercos[0] or not tercos[2]:
        return None
    sp = list(por_ano.values())
    return (st.mean(tercos[0]) - st.mean(tercos[2]),
            sum(1 for v in sp if v > 0), len(sp), _t_anual(sp))


def rodar(tickers, titulo):
    obs = observar(tickers)
    print('\n' + '═' * 88)
    print(titulo)
    print('═' * 88)
    print(f'{len(obs)} observações · {len(set(o[1] for o in obs))} tickers · '
          f'{len(set(o[0] for o in obs))} transições anuais')

    iso_p = teste_isolado(obs, PRECO, 'A1 · SINAIS DE PREÇO, isolados (acima × abaixo da mediana do ano)')
    iso_q = teste_isolado(obs, QUALIDADE, 'A2 · SINAIS DE QUALIDADE, isolados — nunca testados antes neste projeto')

    print('\nB · 2x2 CONDICIONAL — "barato E bom" contra os outros três quadrantes')
    print('-' * 88)
    for sp_nome in ('L/P', 'DY'):
        for sq_nome in ('ROE', 'Baixa alavancagem', 'Margem liq.', 'Cresc. lucro'):
            imprimir_2x2(obs, sp_nome, sq_nome)

    print('\n\nC · RANK COMPOSTO contra o sinal isolado')
    print('-' * 88)
    melhor_iso = max(iso_p.items(), key=lambda kv: kv[1][0]) if iso_p else None
    if melhor_iso:
        print(f"  melhor sinal de preço isolado: {melhor_iso[0]} "
              f"({melhor_iso[1][0]*100:+.1f} p.p., {melhor_iso[1][1]} de {melhor_iso[1][2]} anos)")
    print(f"  {'Composto':<34}{'spread':>10}{'t':>8}  anos certos   vence o isolado?")
    for a_nome in ('L/P', 'DY'):
        for b_nome in ('ROE', 'ROIC', 'Baixa alavancagem', 'Margem liq.', 'DY' if a_nome != 'DY' else 'L/P'):
            r = teste_composto(obs, a_nome, b_nome)
            if not r:
                continue
            spread, pos, nan, tt = r
            base = iso_p.get(a_nome, (0,))[0]
            venceu = 'SIM' if spread > base else 'não'
            print(f"  {a_nome + ' + ' + b_nome:<34}{spread*100:>9.1f}%"
                  f"{(f'{tt:+.2f}' if tt is not None else '   —'):>8}   {pos} de {nan}"
                  f"        {venceu} (isolado {base*100:+.1f})")
    return obs


if __name__ == '__main__':
    defensivos = {t for t in H if MOTOR.get(t) in DEFENSIVOS}
    rodar(defensivos, 'DEFENSIVOS (FIN + UTIL) — bancos, seguros, elétricas, telecom, saneamento')
    rodar(set(H), 'RADAR INTEIRO — todos os 30 tickers, para contraste')

    print('\n' + '═' * 88)
    print('LEITURA — o que este teste pode e o que não pode dizer')
    print('═' * 88)
    print("""
  PODE desqualificar: critério que erra a direção de forma consistente aqui não entra no
  motor. É barato eliminar candidato ruim com pouca amostra.

  NÃO PODE confirmar: com 5 transições anuais e ~4 empresas por quadrante por ano, um
  spread positivo é compatível com sorte. Nenhum número abaixo tem significância estatística,
  e o `t` está impresso justamente para deixar isso visível em vez de escondido.

  O QUE DESTRAVA DE VERDADE: universo de 300+ papéis × 10 anos. Isso exige série de COTAÇÃO
  histórica, e a chave de API desta sessão não tem o escopo @quotes/post/eod. Liberado esse
  escopo no Partnr, este mesmo script roda sobre o universo inteiro sem mudar de estrutura.
""")
