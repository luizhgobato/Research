#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# GERADOR DA TIR REAL — tira data/tir.data.js do estado de "snapshot feito à mão"
# ══════════════════════════════════════════════════════════════════════════════════════════
# POR QUE EXISTE — auditoria de 06/09/2026, achado ao responder "tem coisa pendente ainda?".
#
# A coluna 22 (TIR real) vinha de um arquivo estático congelado em 05/09/2026, escrito antes
# de TODAS as correções de payout daquele dia. Doze empresas divergiam mais de 5 p.p. do que
# o motor calcula hoje, e três delas de forma grosseira:
#
#     AXIA3  43% → 93%   (+50 p.p.)
#     SBSP3  19% → 50%   (+31 p.p.)
#     LEVE3  57% → 86%   (+29 p.p.)
#
# É o MESMO padrão que já apareceu três vezes neste projeto — duas fontes de verdade para o
# mesmo conceito. Só que aqui a segunda fonte é um arquivo estático, então ela não briga com
# a primeira: ela ENVELHECE EM SILÊNCIO. É o modo mais perigoso da falha, porque nada quebra.
#
# ⚠️ O QUE ESTE SCRIPT NÃO RECALCULA, e por quê:
#   · `cx` (medida de CAIXA: (FCO − capex) ÷ valor de mercado) — o HIST_SEED não tem FCO nem
#     capex; eles vieram de chamadas ao Partnr na época. É PRESERVADO do snapshot anterior.
#     Não depende de payout, então a correção de hoje não o afeta.
#   · `gCagr` (CAGR do lucro recorrente) — mesma razão: campo que não está no HIST_SEED.
#     Preservado. Também não depende de payout.
#   Ambos ficam marcados na saída como herdados, para o próximo leitor saber o que é fresco.
#
# O QUE MUDA COM A CORREÇÃO DO PAYOUT: `payout` → `retenção` → `gRoe` → `g`, e daí as duas
# medidas que dependem de g (dividendos e lucro). Ou seja, quase tudo.
import json, math, re, statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
src = (RAIZ / 'scripts/motor_teto.py').read_text()
M = {}
exec(src[:src.index("if __name__")], M)
H = M['carregar']()
M['H_GLOBAL'] = H

IPCA = M['IPCA'] / 100          # 4,44%
GT = IPCA + 0.02                # perpetuidade: IPCA + 2%
ANOS_G1 = 10
G_CAP = 0.15

antigo = (RAIZ / 'data/tir.data.js').read_text()
VELHO = {}
for m in re.finditer(r"(\w+):\s*\{([^}]*)\}", antigo):
    d = {}
    for k, v in re.findall(r"(\w+):\s*('?[^,']*'?)", m.group(2)):
        v = v.strip()
        if v in ('null', ''): d[k] = None
        elif v.startswith("'"): d[k] = v.strip("'")
        else:
            try: d[k] = float(v)
            except ValueError: d[k] = None
    VELHO[m.group(1)] = d

# ── FLUXO DE CAIXA E LUCRO RECORRENTE — coletados, não mais herdados ────────────────────
# Até 06/09/2026 os campos `cx` (medida de caixa) e `gCagr` eram HERDADOS do snapshot antigo,
# porque FCO, capex e lucro recorrente não estavam no HIST_SEED. Ficavam envelhecendo em
# silêncio, que é a mesma falha que este script foi escrito para consertar — só que menor.
# Agora vêm de data/fluxo.json, coletado do Partnr (CASH_FLOW_STATEMENT e INCOME_STATEMENT,
# frequency TTM) com data-base declarada por ticker.
#
# ⚠️ FCO − CAPEX é calculado AQUI, não lido do campo FREE_CASH_FLOW da base. Motivo: esse
# campo é inconsistente com ele mesmo. No LEVE3 ele devolve R$641,1 mi enquanto
# OPERATING_CASH_FLOW (R$862,3 mi) − CAPEX (R$114,1 mi) dá R$748,2 mi, e o FCF_PER_SHARE do
# mesmo registro implica um terceiro valor (R$577 mi). Três números para a mesma grandeza no
# mesmo registro: usar as duas pontas e fazer a subtração é a única forma auditável.
FLUXO = json.loads((RAIZ / 'data/fluxo.json').read_text())['tickers']


def fco_menos_capex(t):
    d = FLUXO.get(t) or {}
    fco, cap = d.get('fco'), d.get('capex')
    return (fco - cap) if (fco is not None and cap is not None) else None


def fcfe(t, A):
    """FCFE de verdade — item #9 do punch-list, 07/09/2026.

    (FCO − capex) sozinho é FCFF (caixa livre para a FIRMA, dívida + equity), não FCFE (caixa
    livre para o EQUITY) — e a medida `cx` divide isso pelo valor de mercado do EQUITY. Quem
    está pagando dívida tem uma fatia do FCO indo para o credor, nunca chegando ao acionista;
    quem está alavancando recebe caixa extra de fora que também não é "gerado pelo negócio",
    mas ainda assim chega ao acionista (via investimento, recompra, dividendo futuro).

    Soma a variação de dívida bruta do período (M['delta_divida_bruta'], em scripts/
    motor_teto.py: só os dois anos mais recentes CONSECUTIVOS, só depois da última quebra).
    Sem dado de dívida suficiente (menos de 2 anos consecutivos válidos), cai para o FCO−capex
    bruto — mais informação que nenhuma, com a diferença marcada no campo `fcfeAjustada`.
    """
    base = fco_menos_capex(t)
    if base is None:
        return None, False
    delta = M['delta_divida_bruta'](t, A)
    if delta is None:
        return base, False
    return base + delta, True


def cagr_recorrente(t):
    """Crescimento anual do lucro recorrente por REGRESSÃO LOG sobre a série inteira.

    ⚠️ POR QUE NÃO É MAIS CAGR DE PONTAS — e por que também não virou "média", que foi o que
    o usuário perguntou primeiro.

    O CAGR ponta-a-ponta usa DOIS pontos e ignora os do meio. A CLSC4 pagou por isso: a série
    do lucro recorrente é 0,67 · 0,47 · 0,67 · 0,65 · 0,65 bi. O 2022 foi um ano ruim isolado
    e a empresa se recuperou — receita de R$11,3 bi para R$12,5 bi e lucro contábil de R$0,56
    bi para R$0,88 bi no mesmo período. Mas o CAGR via só 0,67 → 0,65 = −0,72%, que o piso
    zerava. O motor dizia "não cresce" sobre uma empresa que cresce.

    ⚠️ MÉDIA GEOMÉTRICA SERIA A MESMA COISA, e isso é álgebra, não opinião: o produto dos
    fatores (1+g₁)(1+g₂)…(1+gₙ) TELESCOPA para último÷primeiro. Trocar CAGR por média
    geométrica não mudaria um único número da tabela.

    ⚠️ MÉDIA ARITMÉTICA SERIA PIOR. Ela é sistematicamente maior que o crescimento real
    (viés de Jensen: subir 50% e cair 50% dá média zero e perda de 25%). Nas 11 empresas com
    série utilizável ela foi MAIOR em todas as 11, e na ALOS3 deu 59,7% contra 29,8% reais —
    o ano da fusão puxa a média. Aplicar 59,7% compondo por 10 anos num DDM é fantasia.

    ⚠️ MEDIANA DAS VARIAÇÕES seria robusta demais: esconde queda monotônica. A PASS3 sairia
    de −14,2% para −2,4%, quando a empresa perdeu 51% do lucro recorrente em quatro anos.
    Robustez que apaga o fato não serve.

    A REGRESSÃO LOG usa todos os pontos, não telescopa e não tem viés de composição: ajusta
    a reta que melhor descreve ln(lucro) ao longo do tempo, e a inclinação é a taxa anual.
    Conserta a CLSC4 (−0,7% → +2,8%) sem salvar quem realmente encolhe: a PASS3 fica ainda
    mais negativa (−16,4%) e a SHUL4 confirma a estagnação (−3,2%).

    ⚠️ SÃO 5 PONTOS. Regressão sobre 5 observações é melhor que sobre 2 e continua frágil.
    É estimativa, não medida — e o `g` bruto vai para a saída justamente para isso ficar
    visível em vez de sumir atrás do piso de zero.
    """
    d = FLUXO.get(t) or {}
    hist = {int(k): v for k, v in (d.get('lucro_recorrente_hist') or {}).items()
            if v is not None and v > 0}
    if len(hist) < 3:
        return None
    ys = sorted(hist)
    xs = [float(y - ys[0]) for y in ys]
    ln = [math.log(hist[y]) for y in ys]
    mx, my = st.mean(xs), st.mean(ln)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    b = sum((x - mx) * (l - my) for x, l in zip(xs, ln)) / den
    return math.exp(b) - 1


# lucro normalizado: mesma função do gerador de colunas (uma fonte só)
gc = (RAIZ / 'scripts/gerar_colunas.py').read_text()
G = {'__file__': str(RAIZ / 'scripts/gerar_colunas.py')}
exec(gc[:gc.index("def gerar()")], G)


def real(nom):
    """Fisher: retorno real é DIVISÃO, não subtração."""
    return ((1 + nom) / (1 + IPCA) - 1) * 100


def tir_ddm(preco, d0, g1, gt=GT, anos=ANOS_G1):
    """TIR que iguala o preço ao fluxo de dividendos: 10 anos a g1, depois perpetuidade a gt."""
    if not preco or preco <= 0 or not d0 or d0 <= 0:
        return None
    def vp(r):
        if r <= gt: return float('inf')
        s = 0.0; d = d0
        for _ in range(anos):
            d *= (1 + g1); s += d / (1 + r) ** _ / (1 + r)
        return s + (d * (1 + gt) / (r - gt)) / (1 + r) ** anos
    lo, hi = gt + 1e-4, 3.0
    if vp(hi) > preco: return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if vp(mid) > preco: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def calcular(t, A, velho):
    c = A[max(A)]
    preco = c.get('preco'); pap = M['papeis'](t, A)
    # usar_cache=False: este script ESCREVE o lucroNorm — ler o próprio arquivo antes de
    # recalcular congelava o número para sempre (ver o comentário em gerar_colunas.py).
    ln, motor, _f = G['normalizado'](t, A, usar_cache=False)
    if not preco or not pap or not ln or ln <= 0:
        return None
    mcap = preco * pap
    po, npo, pf = M['payout_final'](t, A, H)
    if po is None: return None

    # g = MENOR entre CAGR do lucro recorrente (herdado) e ROE × retenção, capado em 15%.
    # É AQUI que a correção do payout entra também no crescimento: retenção = 1 − payout.
    val, q = M['anos_validos'](A)
    roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
    roe = M['mediana_com_tendencia'](roes, limiar_abs=2.0)[0] if roes else None
    g_roe = (roe / 100) * (1 - po) if roe is not None else None
    # ⚠️ gCagr TAMBÉM não vale para financeira, pelo mesmo motivo que o cx — e a evidência é
    # direta: o campo RECURRING_NET_INCOME devolve R$112,5 bi para o ITUB3 em 2021 (o lucro
    # recorrente real foi ~R$26 bi) e vem NULO em 2022 e 2024. É a fórmula mecânica do Partnr
    # (lucro menos operações descontinuadas, outras receitas/despesas operacionais, tributos
    # diferidos e impairment), que não descreve banco. Com esse 2021 inflado o CAGR sai em
    # −23% ao ano e o g do Itaú ia a zero, derrubando a TIR dele de 11,5% para 4,6%.
    # O snapshot antigo já não tinha gCagr em nenhuma financeira — a regra existia de fato e
    # não estava escrita, exatamente como no cx.
    g_cagr = cagr_recorrente(t) if M['MOTOR'].get(t) not in ('FIN', 'NAV') else None
    # ⚠️ CÍCLICA: o CAGR do lucro NÃO entra. A KLBN11 saiu com g = −70,1% e faixa de
    # −58,1% a 3,5% porque o CAGR herdado mede a queda do lucro até o fundo do ciclo da
    # celulose. Projetar isso como crescimento de 10 anos é o mesmo erro que já tirou o E/P
    # e o Gordon do motor de preço-teto das cíclicas: tratar um ano ruim como capacidade
    # normal. Nelas o g vem só de ROE × retenção, que é estrutural.
    if M['MOTOR'].get(t) == 'CICL':
        g_cagr = None
    cands = [x for x in (g_roe, g_cagr) if x is not None]
    if not cands: return None
    # PISO ZERO. Crescimento nominal negativo por 10 anos seguido de perpetuidade a IPCA+2%
    # é incoerente: o modelo diz que a empresa encolhe e depois volta a crescer com a
    # economia, sem nada explicando a virada. Zero significa "estagnada em termos nominais",
    # que é a hipótese conservadora defensável. É premissa, e está declarada como tal.
    g_bruto = min(cands)                 # antes do piso e do teto — é o que os dados dizem
    g = max(0.0, min(g_bruto, G_CAP))

    ey = ln / mcap                                   # earnings yield sobre lucro normalizado
    luc = real(ey + g)                               # medida LUCRO
    d0 = ln * po / pap                               # dividendo por papel, do lucro normalizado
    r = tir_ddm(preco, d0, g)
    div = real(r) if r is not None else None         # medida DIVIDENDOS
    # medida CAIXA: FCFE ÷ valor de mercado. FCFE = FCO − capex + Δdívida bruta (ver fcfe()
    # acima) — não mais o FCO−capex bruto, que é FCFF (caixa da FIRMA) e superestima quem paga
    # dívida / subestima quem alavanca. Ver comentário de fcfe() para o caso PETR4.
    #
    # ⚠️ NÃO SE APLICA A FINANCEIRA, e isto quase passou batido. Ao trocar o `cx` herdado por
    # um calculado, as financeiras ganharam a medida pela primeira vez e o resultado foi
    # absurdo: BRSR6 com faixa até 220,7%, ITUB3 até 30,1%. Motivo: o "fluxo de caixa
    # operacional" de um banco inclui variação de depósitos e da carteira de crédito — captar
    # R$10 bi entra como caixa gerado, e isso não é lucro do acionista, é passivo novo.
    # O snapshot antigo já não tinha cx em nenhuma financeira; a regra existia de fato mas não
    # estava escrita em lugar nenhum. Agora está.
    cx = None
    fcfe_val, fcfe_ajustada = None, False
    if M['MOTOR'].get(t) not in ('FIN', 'NAV'):
        fcfe_val, fcfe_ajustada = fcfe(t, A)
        cx = real(fcfe_val / mcap) if (fcfe_val and fcfe_val > 0) else None

    ms = [x for x in (cx, div, luc) if x is not None]
    if not ms: return None
    # ── campos para RECÁLCULO AO VIVO em JS (item #8, 07/09/2026) ──────────────────────
    # Até aqui med/lo/hi/cx/div/luc são calculados com `preco` = cotação do data-base do
    # HIST_SEED, e o arquivo carregava um aviso de que a TIR real "não recalcula com a
    # cotação ao vivo" — a mesma classe de defeito de duas fontes de verdade que motivou
    # este script no dia anterior, só que sem sintoma abrupto: aqui o número segue o motor,
    # mas trava no preço do dia em que rodou. Medido em 07/09/2026, um dia depois de gerado:
    # IRBR3 -9,9%, BBSE3 -8,1%, PASS3 -6,3%, CPFE3 -5,5% de defasagem.
    #
    # `pap` (papéis), `fcfe` (FCFE nominal — FCO-capex + Δdívida bruta, ver fcfe() acima — não
    # dividido por mktcap) e `d0` (dividendo por papel) não dependem do preço — dá para
    # recalcular cx/div/luc no browser a cada atualização de cotação sem re-rodar Python, do
    # mesmo jeito que calcularPrecoTeto() já faz para o preço-teto. `g` também não depende do
    # preço, então fica como está. `fcfeAjustada` diz se a dívida entrou na conta (True) ou se
    # caiu para o FCO−capex bruto por falta de 2 anos consecutivos de dívida bruta (False).
    return dict(med=st.median(ms), lo=min(ms), hi=max(ms), cx=cx, div=div, luc=luc,
                amp=max(ms) - min(ms), g=g * 100, gBruto=g_bruto * 100,
                gRoe=(g_roe * 100 if g_roe is not None else None),
                gCagr=(g_cagr * 100 if g_cagr is not None else None),
                payout=po * 100, lucroNorm=ln, motor=motor,
                # ⚠️ ATÉ 13/09/2026 esta linha era `(velho or {}).get('seg') or MOTOR.get(t)`,
                # e o `velho` vinha do snapshot de 05/09 — anterior à criação do grupo UTIL.
                # Resultado: 14 tickers carregavam seg:'IND' e só 1 dizia 'UTIL', enquanto o
                # MOTOR de motor_teto.py classificava 8 como UTIL. O campo preferia a fonte
                # velha e envelhecia em silêncio, que é exatamente a falha da seção 24 — só
                # que dentro do script escrito para consertá-la. O MOTOR é a única fonte.
                seg=M['MOTOR'].get(t, 'IND'),
                fonte=pf[0], pap=pap, d0=d0, fcfe=fcfe_val, fcfeAjustada=fcfe_ajustada,
                precoBase=preco)


def n(v, casas=2):
    return 'null' if v is None else f'{v:.{casas}f}'


if __name__ == '__main__':
    out = {}
    for t in sorted(H):
        r = calcular(t, H[t], VELHO.get(t))
        if r: out[t] = r
    linhas = []
    for t, r in sorted(out.items(), key=lambda kv: -kv[1]['med']):
        linhas.append(
            f"  {t+':':10}{{ med:{r['med']:6.2f}, lo:{r['lo']:6.2f}, hi:{r['hi']:6.2f}, "
            f"cx:{n(r['cx']):>6}, div:{n(r['div']):>6}, luc:{n(r['luc']):>6}, "
            f"amp:{r['amp']:6.2f}, g:{r['g']:6.2f}, gBruto:{r['gBruto']:7.2f}, gRoe:{n(r['gRoe']):>6}, "
            f"gCagr:{n(r['gCagr']):>6}, payout:{r['payout']:5.1f}, "
            f"lucroNorm:{r['lucroNorm']:.0f}, motor:'{r['motor']}', seg:'{r['seg']}', "
            f"fonte:'{r['fonte']}', pap:{r['pap']:.0f}, d0:{r['d0']:.4f}, "
            f"fcfe:{n(r['fcfe'], 0)}, fcfeAjustada:{'true' if r['fcfeAjustada'] else 'false'}, "
            f"precoBase:{r['precoBase']:.2f} }},")

    # ⚠️ NÃO derivar o cabeçalho do arquivo antigo. Até 13/09/2026 esta parte fazia
    # `cab = antigo[:...]` e depois `cab += <bloco de aviso>` — ou seja, relia o cabeçalho já
    # gerado e ANEXAVA o aviso de novo. Cada execução acrescentava mais uma cópia: o arquivo
    # em produção chegou a carregar o mesmo bloco NOVE vezes. Um gerador que não é idempotente
    # produz saída diferente a cada rodada com a mesma entrada, e isso torna o diff do git
    # inútil justamente onde ele é a única auditoria (o arquivo é gerado, ninguém o revisa
    # linha a linha). O cabeçalho agora é escrito do zero, sempre igual.
    cab = ("// ══════════════════════════════════════════════════════════════════════════════════════════\n"
           "// TIR REAL — faixa de três medidas independentes   ·   GERADO por scripts/gerar_tir.py\n"
           "// ══════════════════════════════════════════════════════════════════════════════════════════\n"
           "// ⚠️ ARQUIVO GERADO — não editar à mão. Rode `python3 scripts/gerar_tir.py`.\n"
           "//\n")
    cab += ("// ⚠️ REGERADO EM 06/09/2026, campos ao-vivo acrescentados 07/09/2026. Este arquivo era\n"
            "// um SNAPSHOT ESTÁTICO escrito à mão em 05/09, antes das correções de payout daquele\n"
            "// dia — e por isso ficou com premissas de duas versões atrás sem que nada quebrasse.\n"
            "// Doze empresas divergiam mais de 5 p.p. do que o motor calcula (AXIA3 43%→93%,\n"
            "// SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo estático não briga com o motor: ele\n"
            "// envelhece em silêncio, que é o modo mais perigoso da falha. Agora é gerado, e o\n"
            "// payout vem de payout_final() — a mesma função que alimenta o preço-teto e a coluna\n"
            "// de payout do Radar.\n"
            "//\n"
            "// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,\n"
            "// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a\n"
            "// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.\n"
            "//\n"
            "// ⚠️ `med/lo/hi/cx/div/luc` NESTE ARQUIVO SÃO CALCULADOS COM O PREÇO DO DATA-BASE\n"
            "// (`precoBase`), NÃO com a cotação ao vivo — igual ao preço-teto ANTES de recalcular\n"
            "// em cada atualização de página. Por isso `pap`, `d0` e `fcfe` também estão aqui: são\n"
            "// os insumos que não dependem de preço, e js/decisao.js usa `_tirAoVivo()` para\n"
            "// recompor cx/div/luc com a cotação do DOM a cada render — os três campos estáticos\n"
            "// ficam só como fallback caso a cotação da linha ainda não tenha carregado.\n")
    novo = (cab + f"const TIR_DATA_EM = '06/09/2026';\n"
            f"const TIR_NTNB = 7.70;   // NTN-B 2035 (IPCA + %). Atualizar junto com os dados.\n"
            f"const TIR_SEED = {{\n" + "\n".join(linhas) + "\n};\n")
    (RAIZ / 'data/tir.data.js').write_text(novo)

    print(f"{'ativo':8}{'med':>7}{'faixa':>16}{'payout':>8}{'g':>7}  fonte")
    for t, r in sorted(out.items(), key=lambda kv: -kv[1]['med']):
        v = VELHO.get(t, {})
        mudou = '' if v.get('med') is None else f"  (antes {v['med']:.1f}%)"
        print(f"{t:8}{r['med']:6.1f}%{f'{r[chr(108)+chr(111)]:.1f} → {r[chr(104)+chr(105)]:.1f}%':>16}"
              f"{r['payout']:7.0f}%{r['g']:6.1f}%  {r['fonte']}{mudou}")
    print(f"\n{len(out)} ativos → data/tir.data.js")
