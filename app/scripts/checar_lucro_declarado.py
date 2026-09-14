#!/usr/bin/env python3
"""Confronta LUCRO_2026_DECLARADO com o trimestre publicado. Sai != 0 se algum divergir.

POR QUE EXISTE — 14/09/2026, pedido do usuário: "quero garantir que estamos estimando o lucro
projetado certo". A resposta honesta é que não havia como garantir: `LUCRO_2026_DECLARADO`
(motor_teto.py) é uma constante digitada a partir do relatório de cada empresa, e constante
digitada NÃO AVISA quando o fato muda.

O IRBR3 provou o custo. O relatório de 25/08/2026 declarou R$ 330 mi para 2026. O 2T26, já
publicado em 14/08, veio com PREJUÍZO de R$ 3,3 mi — o semestre fechou em R$ 90 mi. Para
chegar aos R$ 330 mi o 2º semestre teria que entregar R$ 240 mi, 2,7x o semestre inteiro que
acabou de passar. O motor seguia multiplicando o múltiplo por um lucro que já não existia.

DUAS RÉGUAS, porque nenhuma sozinha resolve:
  · 1S ANUALIZADO (1S × 2) — captura deterioração rápido, mas ignora sazonalidade. Shopping
    fatura mais no 2º semestre (Natal); seguradora e banco quase não têm sazonalidade.
  · LTM (4 trimestres) — atravessa a sazonalidade inteira, mas demora a refletir virada.
O alerta dispara quando o declarado se afasta das DUAS na mesma direção. Longe de uma e perto
da outra é sazonalidade ou virada recente, e aí o julgamento é humano, não do script.

Não corrige nada sozinho: imprime e falha. Quem decide o número é quem lê o relatório.
"""
import json, sys, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LIM = 0.15          # 15% de folga: abaixo disso é ruído de projeção, não erro de fato.

src = (RAIZ / 'scripts/motor_teto.py').read_text()
M = {}
exec(src[:src.index("if __name__")], M)
DECL = M['LUCRO_2026_DECLARADO']

try:
    TRI = json.loads((RAIZ / 'analise/trimestrais.json').read_text())
except Exception:
    raise SystemExit('analise/trimestrais.json não existe — rode scripts/coletar_trimestrais.py')


def por_ano(t):
    """{exercício: lucro} só de anos COMPLETOS (4 trimestres publicados)."""
    r = (TRI['tickers'].get(t) or {}).get('trimestres') or {}
    acc = {}
    for q, v in r.items():
        acc.setdefault(q[:4], []).append(v)
    return {a: sum(v) for a, v in acc.items() if len(v) == 4}


def run_rate(t):
    """(1S anualizado, LTM, nº de trimestres de 2026) — a régua de uma PROJEÇÃO."""
    r = (TRI['tickers'].get(t) or {}).get('trimestres') or {}
    if not r:
        return None
    qs = sorted(r)
    s26 = [q for q in qs if q.startswith('2026')]
    if not s26:
        return None
    anual = sum(r[q] for q in s26) / len(s26) * 4
    ltm = sum(r[q] for q in qs[-4:]) if len(qs) >= 4 else None
    return anual, ltm, len(s26)


print(f'Coleta de {TRI.get("coletado_em","?")} · limite de alerta ±{LIM*100:.0f}%\n')
falhas = []
for t, ent in sorted(DECL.items()):
    v = ent[0]
    tipo = ent[2] if len(ent) > 2 else ('projecao',)

    # ── MÉDIA DE CICLO: confere recalculando a média dos exercícios que ela declara.
    # O run-rate NÃO se aplica aqui, e usá-lo foi o falso positivo que criou este ramo.
    if tipo[0] == 'ciclo':
        ini, fim = tipo[1], tipo[2]
        anos = por_ano(t)
        usados = {a: x for a, x in anos.items() if ini <= int(a) <= fim}
        if len(usados) < (fim - ini + 1):
            print(f'{t:7} CICLO {ini}-{fim}: só {len(usados)} exercícios completos coletados — '
                  f'não dá para conferir')
            continue
        media = sum(usados.values()) / len(usados)
        razao = v / media
        serie = ' · '.join(f'{a} {x/1e6:+.0f}' for a, x in sorted(usados.items()))
        ok = abs(razao - 1) <= LIM
        print(f'{t:7} CICLO {ini}-{fim}  declarado R$ {v/1e6:.0f} mi  vs média R$ {media/1e6:.0f} mi '
              f'({razao:.2f}x)  {"ok" if ok else "DIVERGE"}')
        print(f'        {serie}  (mi)')
        rr = run_rate(t)
        if rr:
            print(f'        contexto, NÃO é o critério: 1S26 anualizado R$ {rr[0]/1e6:.0f} mi, '
                  f'LTM R$ {rr[1]/1e6:.0f} mi — a média de ciclo ignora isto de propósito.')
        if not ok:
            falhas.append((t, 'ciclo', v, media, serie))
        continue

    # ── PROJEÇÃO DO EXERCÍCIO: duas réguas de run-rate.
    # Alerta só quando as DUAS apontam para o mesmo lado. Longe de uma e perto da outra é
    # sazonalidade ou virada recente, e aí o julgamento é humano, não do script.
    rr = run_rate(t)
    if not rr:
        print(f'{t:7} PROJEÇÃO  declarado R$ {v/1e9:.2f} bi  — sem trimestre coletado')
        continue
    anual, ltm, n26 = rr
    ra = v / anual if anual else None
    rl = v / ltm if ltm else None
    fora = [x for x in (ra, rl) if x is not None and abs(x - 1) > LIM]
    alerta = (len(fora) == 2 and (fora[0] - 1) * (fora[1] - 1) > 0)
    sit = 'DIVERGE' if alerta else ('atenção — as duas réguas discordam' if fora else 'ok')
    print(f'{t:7} PROJEÇÃO  declarado R$ {v/1e9:6.2f} bi  vs 1S26 anualizado '
          f'R$ {anual/1e9:.2f} bi ({ra:.2f}x)  vs LTM R$ {(ltm or 0)/1e9:.2f} bi ({(rl or 0):.2f}x)'
          f'  {sit}' + (f'  [{n26} tri de 2026]' if n26 < 2 else ''))
    if alerta:
        falhas.append((t, 'projecao', v, anual, None))

if falhas:
    print('\n⚠️  DIVERGÊNCIA')
    for t, tipo, v, ref, serie in falhas:
        if tipo == 'ciclo':
            print(f'   · {t}: declarado R$ {v/1e6:.0f} mi contra média de ciclo recalculada de '
                  f'R$ {ref/1e6:.0f} mi. Série: {serie} (mi).')
        else:
            falta = v - (ref / 2)
            print(f'   · {t}: declarado R$ {v/1e6:.0f} mi. O 1S26 fechou em R$ {ref/2/1e6:.0f} mi, '
                  f'então o 2S teria que entregar R$ {falta/1e6:.0f} mi — '
                  f'{falta/(ref/2):.1f}x o semestre que passou.')
    print('\n   Revise LUCRO_2026_DECLARADO em scripts/motor_teto.py, ou tire a declaração e')
    print('   deixe o motor projetar a partir da base.')
    sys.exit(1)
print('\nTodos os lucros declarados continuam compatíveis com o dado publicado.')
