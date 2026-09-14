#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# MOTOR DE PREÇO-TETO — uma régua só, aplicada às 30 empresas
# ══════════════════════════════════════════════════════════════════════════════════════════
# Antes: 16 tetos calculados à mão em momentos diferentes, com parâmetros fixos, e 13 herdados
# de análises antigas sem motor declarado. Este script recalcula TODOS pelo motor do setor,
# com os mesmos parâmetros, e gera a tooltip de auditoria de cada um.
#
# O QUE MUDOU NOS CRITÉRIOS (e por quê):
#
# 1. TAXA LIVRE DE RISCO passa a ser a NTN-B longa, não a Selic.
#    A Selic é taxa de política, de curto prazo, e hoje está no pico do ciclo. O modelo é de
#    PERPETUIDADE — ancorar num juro de 12 meses faz o teto oscilar com o Copom em vez de com
#    o negócio. NTN-B 2035 = IPCA + 7,70% → nominal 12,48%.
#
# 2. Ke DEIXA DE SER 16% FIXO: Ke = juro longo + prêmio de risco de 5,5 p.p. = 17,98%.
#    Com Ke fixo, os tetos ficavam otimistas justamente quando a renda fixa estava mais
#    atraente — o modelo não reagia ao ciclo de juros.
#
# 3. g DE LONGO PRAZO cai de 8% para IPCA + 2% = 6,44%.
#    8% nominal para sempre é acima do PIB nominal de longo prazo. E 6,44% é exatamente a
#    perpetuidade que a TIR real (data/tir.data.js) já usava — as duas metodologias do projeto
#    paravam de discordar entre si sobre a mesma empresa.
#
# 4. BAZIN VIRA GORDON: yield exigido = Ke − g = 11,54%, em vez da constante arbitrária de
#    8-9%. Um só parâmetro governa dividendo e capital.
#
# 5. TRAVA DO GORDON: se ROE < g + 3 p.p., o P/VP justo NÃO é calculado pela fórmula.
#    (ROE − g)/(Ke − g) explode quando o numerador encolhe: com ROE de 11,4% e g de 8%, uma
#    mudança de 2 p.p. no Ke movia o teto do Santander em 40%. Nesses casos usamos o P/VP
#    MÍNIMO HISTÓRICO da própria empresa — piso empírico em vez de fórmula instável.
#
# 6. MARGEM DE SEGURANÇA ESCALA COM A CONVICÇÃO: ★★★ 10%, ★★☆ 15%, ★☆☆ 25%.
#    Antes eram 15% para todos, e a estrela era decorativa. Quanto menos confiança na premissa,
#    mais desconto deve ser exigido — agora isso entra na conta.
#
# Fonte de tudo: data/historico.data.js (Partnr/CVM). Rodar: python3 scripts/motor_teto.py
import re, json, math, statistics as st

IPCA = 4.44
# ⚠️ JUÍZO MAIS IMPORTANTE DO MOTOR — a taxa livre de risco é NORMALIZADA, não a spot.
# A NTN-B longa hoje paga IPCA+7,70%, nível historicamente alto. Usar a spot num modelo de
# PERPETUIDADE congela o estresse de hoje para sempre — o mesmo erro de avaliar cíclica pelo
# lucro de pico. Usamos IPCA+5,5%, perto da média histórica da NTN-B longa.
# Consequência a declarar: com a spot (Ke ~18%) praticamente TODA a bolsa fica acima do teto.
RF_REAL_NORM = 5.5
RF   = ((1 + RF_REAL_NORM/100) * (1 + IPCA/100) - 1) * 100   # 10,18% nominal
ERP  = 5.0                                                   # prêmio de risco de ações base
KE_BASE = RF + ERP                                           # 15,18%
G    = IPCA + 2.0                                            # 6,44% — mesma perpetuidade da TIR real
ANOS_G1 = 10                                                 # estágio de crescimento antes da perpetuidade
G1_CAP  = 15.0
MARGEM = {3: 0.10, 2: 0.15, 1: 0.25}                         # por convicção (nº de estrelas)
KE_MIN, KE_MAX = 13.0, 22.0

# ── Ke POR EMPRESA, mecânico ───────────────────────────────────────────────────────────────
# Escolha do usuário: Ke variável por risco. Para não virar opinião minha, os três ajustes
# saem de dado observável da própria série — volatilidade do resultado, tamanho e alavancagem.
def ke_empresa(t, A):
    import statistics as _st
    c = A[max(A)]
    roes = [A[y]['roe'] for y in A if A[y].get('roe') is not None]
    if len(roes) < 3 or not c.get('lucrolin') or not c.get('lpa') or c['lpa'] <= 0:
        return KE_BASE, 'Ke base (série curta para ajustar por risco)'
    mc = c['preco'] * (c['lucrolin']/c['lpa']) / FATOR_UNIT.get(t, 1)
    cv = _st.pstdev(roes)/abs(_st.mean(roes)) if _st.mean(roes) else 9
    a_vol = -1.0 if cv < 0.25 else (0.0 if cv <= 0.50 else 1.5)
    a_tam = -1.0 if mc > 50e9 else (0.0 if mc >= 10e9 else 1.5)
    de = c.get('divEbitda')
    a_alv = 0.0 if de is None else (-0.5 if de < 1 else (0.0 if de <= 3 else 1.5))
    ke = max(KE_MIN, min(KE_MAX, KE_BASE + a_vol + a_tam + a_alv))
    det = (f'Ke {ke:.2f}% = base {KE_BASE:.2f}% (juro real normalizado {RF_REAL_NORM}% + IPCA + prêmio {ERP}%) '
           f'{a_vol:+.1f} volatilidade do ROE (CV {cv:.2f}) {a_tam:+.1f} tamanho (R$ {mc/1e9:.0f} bi) '
           f'{a_alv:+.1f} alavancagem ({"n/d" if de is None else f"{de:.1f}x"})')
    return ke, det

def ddm2(D0, g1, ke, anos=ANOS_G1, gt=G):
    """DDM de 2 estágios — MESMO modelo da TIR real, resolvido para preço em vez de taxa."""
    pv, d = 0.0, D0
    for a in range(1, anos+1):
        d *= (1 + g1/100); pv += d/(1 + ke/100)**a
    pv += (d*(1 + gt/100)/((ke - gt)/100))/(1 + ke/100)**anos
    return pv

# Valor patrimonial por PAPEL NEGOCIADO, do balanço — para units o P/VP da base erra por um
# fator inteiro (BPAC11 reportava 6,96x contra 2,70x real).
VPA_BALANCO = {'BPAC11': 21.371, 'SANB11': 33.947}
FATOR_UNIT  = {'KLBN11': 5, 'SANB11': 2, 'BPAC11': 3}

# ══ O FATOR DE UNIT NOS MÚLTIPLOS DA BASE É MEDIDO, NÃO DECLARADO (14/09/2026) ═══════════
# Bug encontrado pelo usuário: "o P/L mediano do BTG está errado, não é esse". Estava — o
# motor mostrava 39,45x para o BPAC11. O BTG negocia perto de 11x.
#
# A CAUSA: para alguns papéis a Partnr traz `pl` e `pvp` como PREÇO DA UNIT ÷ VALOR POR AÇÃO.
# Como a unit do BPAC11 é 1 ON + 2 PN, o múltiplo sai 3× inflado. O motor já tinha FATOR_UNIT
# e o aplicava no LPA derivado e no P/VP — mas `teto_ep` lia o campo `pl` CRU, e era esse
# campo que ganhava da derivação sempre que existia. O `pl_setorial` lia cru também, então o
# P/L mediano do grupo FIN saía contaminado junto.
#
# ⚠️ E O FATOR DECLARADO NÃO SERVE PARA ISSO. Conferindo contra o balanço (valor de mercado ÷
# lucro, e valor de mercado ÷ patrimônio), a unit do KLBN11 vale 5 ações mas os campos `pl` e
# `pvp` dela JÁ VÊM por unit — fator medido 0,99. Dividir por 5 quebraria a Klabin para
# consertar o BTG. Não há regra de unit que acerte os três; só medição acerta.
#
#   ativo    campo pl   pl do balanço   fator medido
#   BPAC11      32,48           11,55           2,81  → 3
#   SANB11      15,52            7,73           2,01  → 2
#   KLBN11      43,67           43,96           0,99  → 1   (é unit, e mesmo assim não infla)
#
# A medição decide o VALOR; a lista FATOR_UNIT decide quem é ELEGÍVEL. Papel que não é unit
# nunca entra, por mais que a contagem de papéis esteja ruidosa num ano (o ITUB3 mede 1,19 e
# o BMEB4 1,13 — arredondam para 1, mas nem chegam a ser testados).
_FATOR_PL_CACHE = {}


def fator_multiplo(t, A):
    """Divisor a aplicar nos campos `pl` e `pvp` da base. 1 quando não há inflação de unit."""
    if t in _FATOR_PL_CACHE:
        return _FATOR_PL_CACHE[t]
    f = 1
    if t in FATOR_UNIT:
        c = A[max(A)]
        pap = papeis(t, A)
        li, pr = c.get('lucrolin'), c.get('preco')
        if pap and pr and li and li > 0 and c.get('pl'):
            k = c['pl'] / (pr * pap / li)
            if k >= 1.5:
                f = min(round(k), max(FATOR_UNIT.values()))
    _FATOR_PL_CACHE[t] = f
    return f


def pl_ano(t, A, y):
    """P/L do exercício `y`, já corrigido do fator de unit. UMA definição, três consumidores:
    teto_ep, pl_setorial e a coluna P/L mediano do Radar (scripts/gerar_colunas.py).

    Campo `pl` da base quando existe; senão DERIVADO de preço ÷ LPA. O SHUL4 expôs a segunda
    via: a base não traz `pl` para ele em nenhum dos 6 anos, e sem a derivação ele caía no
    fallback setorial — cujo único par sem quebra no grupo IND é a LEVE3 (autopeças). Um par
    não é setor. Mas `preco` e `lpa` estão lá nos 6 anos: 8,41/1,08 = 7,8x, 4,71/0,76 = 6,2x.
    Derivar é aritmética sobre dado da mesma fonte, não estimativa.
    """
    d = A.get(y) or {}
    v = d.get('pl')
    if v:
        v = v / fator_multiplo(t, A)
        if 0 < v < 60:
            return v
    pr, lp = d.get('preco'), d.get('lpa')
    if pr and lp and lp > 0:
        dv = pr / (lp * FATOR_UNIT.get(t, 1))
        if 0 < dv < 60:
            return dv
    return None

MOTOR = {
    # financeiras e seguradoras → P/VP × ROE
    # SAUD3 = BRADSAUDE (ticker anterior ODPV3, Odontoprev). Estava classificada como
    # industrial/serviço e recebia E/P histórico — motor errado por dois motivos:
    #  (1) o histórico pré-2026 é da ODONTOPREV (planos odontológicos, 545 mi ações, R$6 bi de
    #      valor de mercado). A empresa de hoje incorporou os ativos de saúde do Bradesco e tem
    #      2.927 mi de ações e R$42,7 bi. Nenhum múltiplo daquela série ancora esta empresa.
    #  (2) o balanço é de OPERADORA DE SAÚDE: R$13,2 bi de "caixa líquido" são investimentos
    #      lastreando reservas técnicas, não caixa livre de indústria.
    # O motor E/P devolvia teto de R$3,71 contra cotação de R$14,60 (−294%), e o fallback
    # setorial piorava para R$1,80 porque o único par sem quebra no grupo era a LEVE3
    # (autopeças). Reclassificada para FIN, que é o motor de capital alocado.
    # ⚠️ FIN FOI PARTIDO EM DOIS em 14/09/2026. Antes banco e seguradora dividiam o mesmo
    # grupo de pares, e o múltiplo de um virava régua do outro — a SAUD3 (Bradsaúde, saúde
    # suplementar) recebia o P/L mediano de 8,6x dos bancos enquanto a própria série dela
    # rodava entre 10,9x e 15,2x. São negócios diferentes: banco ganha no spread de crédito
    # e carrega risco de inadimplência; seguradora ganha no resultado de subscrição e no
    # float, e o ciclo de uma não é o da outra. Também alinha o grupo de pares ao segmento
    # que a tabela exibe desde 13/09 (Bancos e Seguros são chips separados).
    **{t: 'FIN' for t in ['BBDC3','ITUB3','BMEB4','BRSR6','SANB11','BPAC11','ROXO34']},
    **{t: 'SEG' for t in ['BBSE3','CXSE3','PSSA3','IRBR3','SAUD3']},
    # holdings puras → NAV (mantidos manuais: exigem valor de mercado das investidas)
    **{t: 'NAV' for t in ['ITSA4','BRAP4']},
    # cíclicas de commodity → EV/EBITDA meio-de-ciclo
    **{t: 'CICL' for t in ['PETR4','VALE3','KLBN11','RANI3']},
    # utilities e TELECOM → EV/EBITDA + Gordon sobre dividendo sustentável
    # Telecom entra aqui por decisão nova: infraestrutura, receita recorrente, capex pesado —
    # mesmo perfil econômico de utility. Antes não tinha motor nenhum na metodologia.
    **{t: 'UTIL' for t in ['CPFE3','PASS3','CLSC4','AXIA3','AURE3','SBSP3','TIMS3','FIQE3']},
    # shoppings → P/FFO próprio (ver teto_ffo). Lucro e patrimônio não servem aqui: o imóvel
    # entra a custo histórico e é depreciado, quando na prática não perde valor.
    **{t: 'SHOP' for t in ['ALOS3','MULT3']},
    # varejo → estavam SEM grupo desde que foram adicionadas em 13/09/2026, caíam no default
    # e ficavam sem preço justo nenhum.
    **{t: 'VAREJO' for t in ['VIVA3','ASAI3']},
    # industrial/serviço de lucro estável → E/P histórico
    **{t: 'IND' for t in ['LEVE3','SHUL4','FLRY3']},
}

def carregar():
    s = open('data/historico.data.js', encoding='utf-8').read()
    H = {}
    for m in re.finditer(r'\n  (\w+): \{(.*?)\n  \},', s, re.S):
        A = {}
        for a in re.finditer(r'(20\d\d): \{([^}]*)\}', m.group(2)):
            A[int(a.group(1))] = {k: (None if v == 'null' else float(v))
                                  for k, v in re.findall(r'(\w+):\s*(-?[\d.]+|null)', a.group(2))}
        H[m.group(1)] = A
    return H

# ── COSMÉTICO vs REAL: a correção de 06/09/2026 ──────────────────────────────────────────
# A corrida de múltiplos (scripts/backtest_multiplos.py, seção 12) me obrigou a olhar de novo
# para `ano_quebra` e mostrou que eu tinha diagnosticado o problema ao contrário.
#
# O QUE EU DISSE QUE ERA O BUG: "o detector é cego para grupamento". ERRADO — ele usa
# abs(b/a − 1), que é simétrico, e detecta o grupamento do IRBR3 (1.264 mi → 82 mi) sem
# problema. Registro aqui porque a afirmação errada chegou a ser dita ao usuário.
#
# O BUG DE VERDADE é que o detector trata como iguais dois eventos que NÃO são iguais:
#
#   DESDOBRAMENTO / GRUPAMENTO (cosmético) — muda a quantidade de ações e nada mais. A empresa
#   é a mesma no dia seguinte. Os MÚLTIPLOS atravessam intactos, porque preço e valor por ação
#   mudam juntos: SBSP3 2025→2026 fez 5:1 (preço R$133,39 → R$26,19) e o P/VP foi de 2,59 para
#   1,96 — variação de negócio, não de unidade. O IRBR3 idem (P/VP 1,27 · 0,52 · 0,87 ao longo
#   do grupamento). Descartar o histórico aqui é jogar dado bom fora: o SBSP3 ficava com UM ano
#   de série e caía no fallback setorial com convicção ★☆☆, sem nenhuma razão.
#
#   INCORPORAÇÃO / EMISSÃO (real) — a empresa passa a ser outra. SAUD3: ações +437% E lucro
#   +81% E receita transformada. Aqui os múltiplos antigos não descrevem nada, e descartar é
#   obrigatório.
#
# COMO DISTINGUIR, mecanicamente: num evento cosmético o NEGÓCIO não se mexe. A receita é o
# indicador mais estável disso (o lucro oscila por conta própria). Se as ações saltam mais de
# 25% mas a receita fica dentro de ±25%, foi cosmético — o histórico de múltiplos permanece
# válido. Bancos e seguradoras sem linha de receita caem no lucro como segunda opção; sem
# nenhum dos dois, o motor mantém o comportamento conservador antigo (trata como quebra real).
#
# ⚠️ O que continua INVÁLIDO mesmo no caso cosmético: comparar PREÇO ou qualquer valor
# ABSOLUTO por ação (LPA, VPA, DPS) entre os dois lados da quebra — a série de preços do
# Partnr não é reexpressa retroativamente. O motor só usa múltiplos na série histórica e
# valores absolutos do ano corrente, então está seguro; qualquer código novo que leia
# A[ano]['preco'] de anos antigos precisa reaplicar o fator.
LIM_NEGOCIO = 0.25

LIM_CAP = 0.30

def _cosmetico(A, y0, y1):
    """True se a quebra entre y0 e y1 foi só desdobramento/grupamento (negócio inalterado).

    DUAS condições, e as duas são necessárias. A primeira versão usava só a receita e
    classificou a FUSÃO ALIANSCE+BRMALLS (ALOS3 2022, ações ×2,15) como cosmética, porque a
    receita subiu só 19% — a fusão fechou no meio do ano e o exercício pegou meia empresa nova.
    Um teste que aprova uma fusão de R$10 bi como "só mudou a unidade" não serve.

      (1) NEGÓCIO PARADO — receita dentro de ±25% (lucro como segunda opção, para banco e
          seguradora que não têm linha de receita).
      (2) VALOR DE MERCADO CONTÍNUO — num desdobramento puro o preço cai exatamente na
          proporção em que as ações sobem, então `(preço_novo/preço_velho) × (ações_novas/
          ações_velhas)` fica em torno de 1. O SBSP3 5:1 dá 0,196 × 4,99 = **0,98** ✓. Uma
          incorporação ou um follow-on quebra essa identidade porque entra capital novo.

    O IRBR3 é o caso instrutivo: foi grupamento E follow-on no mesmo ano, e o produto dá 3,6.
    Reprovado, e corretamente — a empresa levantou capital, não só reempacotou ações.
    Na dúvida o teste reprova, que é o lado seguro: descartar história boa custa convicção
    (★☆☆), misturar duas empresas na mesma conta custa um teto errado.
    """
    neg = None
    for campo in ('receita', 'lucrolin'):
        a, b = A[y0].get(campo), A[y1].get(campo)
        if a and b and a != 0:
            neg = abs(abs(b) / abs(a) - 1) <= LIM_NEGOCIO
            break
    if not neg:
        return False

    p0, p1 = A[y0].get('preco'), A[y1].get('preco')
    try:
        n0 = A[y0]['lucrolin'] / A[y0]['lpa']
        n1 = A[y1]['lucrolin'] / A[y1]['lpa']
    except (KeyError, TypeError, ZeroDivisionError):
        return False
    if not p0 or not p1 or not n0 or not n1 or p0 <= 0 or n0 <= 0:
        return False
    return abs((p1 / p0) * (n1 / n0) - 1) <= LIM_CAP


def ano_quebra(A, limiar=0.25):
    """Devolve o primeiro ano em que a contagem de ações saltou mais que o limiar.

    POR QUE EXISTE — o caso SAUD3, achado pelo usuário: a empresa emitiu 2,4 BILHÕES de ações
    numa incorporação (544 mi → 2.927 mi). O lucro cresceu 1,8x, as ações 5,4x, e o LPA CAIU de
    R$1,07 para R$0,36. O motor multiplicou o P/L mediano da empresa ANTIGA (valor de mercado
    de R$6 bi) pelo LPA da empresa NOVA (R$42,7 bi) e devolveu teto de R$3,71 contra cotação de
    R$14,60. A própria metodologia manda "não misturar bases" — e o motor misturava.

    A varredura achou 7 casos: ALOS3(2022) AXIA3(2022,2025) FLRY3(2023) IRBR3(2022)
    SAUD3(2026) SBSP3(2026) SHUL4(2022). Inclui grupamento (IRBR3: 1.264mi→82mi) e
    desdobramento (SBSP3 5:1), que são cosméticos, e incorporações reais, que não são —
    o motor não tenta distinguir: em qualquer um deles a série per-share deixa de ser
    comparável se a fonte não reexpressou os dois lados.
    """
    ys = sorted(y for y in A if A[y].get('lucrolin') and A[y].get('lpa') and A[y]['lpa'] != 0)
    ac = {y: A[y]['lucrolin']/A[y]['lpa'] for y in ys}
    ult = None
    for i in range(1, len(ys)):
        a, b = ac[ys[i-1]], ac[ys[i]]
        if a > 0 and b > 0 and abs(b/a - 1) > limiar and not _cosmetico(A, ys[i-1], ys[i]):
            ult = ys[i]
    return ult

# ── QUEBRA OPERACIONAL: mudança de empresa sem mudança de ações ──────────────────────────
# `ano_quebra` só enxerga a base ACIONÁRIA. A SBSP3 mostrou o buraco: a privatização de 2024
# não emitiu ação nenhuma, e mesmo assim o EBITDA foi de R$9,1 bi para R$18,2 bi (+99%) e a
# receita de R$25,6 bi para R$36,1 bi (+41%). Os múltiplos de 2021-2023 são de uma estatal;
# os de 2024-2026 são de uma empresa privada. Nenhuma contagem de ações denuncia isso.
# Resultado: EV/EBITDA mediano de 6 anos misturava os dois regimes e o teto saía em R$4,28.
#
# Regra: salto de mais de 50% no EBITDA **e** de mais de 25% na receita no mesmo ano marca
# mudança de regime operacional. Exigir os DOIS evita confundir com um ano bom de margem.
LIM_EBITDA_OP, LIM_REC_OP = 0.50, 0.25

def quebra_operacional(A):
    ys = sorted(A); ult = None
    for i in range(1, len(ys)):
        a, b = A[ys[i-1]], A[ys[i]]
        eb0, eb1 = a.get('ebitda'), b.get('ebitda')
        r0, r1 = a.get('receita'), b.get('receita')
        if not (eb0 and eb1 and r0 and r1 and eb0 > 0 and r0 > 0): continue
        if (eb1/eb0 - 1) > LIM_EBITDA_OP and (r1/r0 - 1) > LIM_REC_OP:
            ult = ys[i]
    return ult

def anos_nao_operacionais(A):
    """Anos em que o LUCRO não veio de operar o negócio.

    POR QUE EXISTE — o caso ALOS3 2023, achado pelo usuário ao perguntar de onde saía o teto.
    A fusão com a brMalls gerou ganho contábil de reavaliação: lucro de R$ 3,49 bi contra ~R$
    1,0 bi de operação normal, e P/L de 3,4x contra 13x a 16x nos outros anos. O filtro de
    quebra de série detectou a fusão (na contagem de ações, em 2022) e, ao cortar o que vinha
    ANTES, deixou justamente o ano do ganho. Resultado: o percentil 25 da série de P/L caía
    sobre esse 3,4x e o teto da ALOS3 saía 24% abaixo do que qualquer ano real sustentava.

    Regra: margem líquida acima de 100% — lucro maior que a receita, o que operação nenhuma
    produz — em empresa cuja margem TÍPICA fica abaixo disso. A segunda metade da regra é o
    que protege a ITSA4: numa holding a "receita" é equivalência patrimonial e a margem passa
    de 160% em TODOS os anos. Margem alta o tempo todo é o negócio; margem alta em um ano só
    é evento.
    """
    mg = {y: A[y].get('mgLiq') for y in A if A[y].get('mgLiq') is not None}
    if len(mg) < 3:
        return set()
    if st.median(mg.values()) > 100:
        return set()
    return {y for y, v in mg.items() if v > 100}


def anos_validos(A):
    """Anos utilizáveis para múltiplo per-share: posteriores à última quebra e operacionais."""
    q = max([x for x in (ano_quebra(A), quebra_operacional(A)) if x], default=None)
    fora = anos_nao_operacionais(A)
    ys = [y for y in sorted(A) if y not in fora]
    return ([y for y in ys if y >= q], q) if q else (ys, None)

def mediana_com_tendencia(vals, limiar_rel=0.12, limiar_abs=None, truncar=True):
    """Mediana que detecta TENDÊNCIA e ignora a metade velha da série quando ela existe.

    POR QUE ISTO EXISTE — foi o defeito que fez TODAS as 9 financeiras reprovarem:
    a mediana é o instrumento certo para série que OSCILA e o errado para série que SOBE.
    Os bancos brasileiros melhoraram de forma persistente na janela 2021-2026 (ITUB3 +3,3 p.p.,
    CXSE3 +6,6 p.p., PSSA3 +6,2 p.p. entre a primeira e a segunda metade), e a mediana de 6
    anos ancorava no passado. Resultado: preço-teto sistematicamente abaixo do mercado, e o
    Radar dizendo que o setor financeiro inteiro estava caro.

    Prova de que era isto e não o Ke: o Ke implícito no preço de mercado (Gordon invertido)
    dava 13,0% no ITUB3 contra os 13,2% que o motor usa — praticamente igual. Com o ROE ATUAL
    de 21,0%, o P/VP justo sai 2,16x contra 2,21x negociado. O erro estava no ROE, não na taxa.

    Regra: compara a média das duas metades. Se diferirem mais que o limiar, a série tem
    tendência e vale a mediana só da metade recente. Vale nos dois sentidos — o SANB11
    deteriorou (−7,0 p.p.) e passa a usar o ROE recente, MENOR, ficando mais conservador.
    """
    if not truncar:
        # ⚠️ 14/09/2026 — SEM TRUNCAGEM onde o ajuste de ROE atua. Ver faixa_com_tendencia.
        return st.median(vals), f'mediana plena de {len(vals)} anos (a correção de fase fica com o ROE)'
    if len(vals) < 5: return st.median(vals), 'série curta — mediana simples'
    meio = len(vals)//2
    velho, novo = vals[:meio], vals[meio:]
    d = st.mean(novo) - st.mean(velho)
    lim = limiar_abs if limiar_abs is not None else abs(st.mean(velho))*limiar_rel
    if abs(d) > lim:
        # ⚠️ MÉDIA, não mediana, quando a janela recente é curta. Achado pelo usuário em
        # 13/09/2026: "o lucro normalizado está quase igual ao de 2025 em todos". Estava — 12
        # de 27. Com 6 anos de série a metade recente tem 3 pontos, e a MEDIANA DE 3 é só
        # "escolher um deles"; numa série que subiu e estabilizou, o do meio é quase sempre o
        # ano corrente, e aí o normalizado vira o próprio lucro do ano. ITUB3, TIMS3, BRSR6 e
        # BMEB4 caíam todos nisso.
        # A mediana existe para proteger de outlier — com 3 pontos não há o que proteger, ela
        # só descarta 2 de 3 observações e devolve um dado cru. A média usa as três. A partir
        # de 5 pontos a proteção volta a valer mais que a informação descartada.
        est = st.median(novo) if len(novo) >= 5 else st.mean(novo)
        como = 'mediana' if len(novo) >= 5 else 'média'
        return est, f'TENDÊNCIA {d:+.1f} entre as metades da série → {como} dos {len(novo)} anos recentes'
    return st.median(vals), f'série estável ({d:+.1f} entre as metades) → mediana dos {len(vals)} anos'

def faixa_com_tendencia(vals, limiar_rel=0.12, limiar_abs=None, truncar=True):
    """Percentis 25/50/75 do múltiplo, com a MESMA regra de tendência de mediana_com_tendencia.

    ══ POR QUE O TETO VIROU FAIXA EM 13/09/2026 ══════════════════════════════════════════
    O motor entregava UM número e uma nota de confiança em estrelas. `backtest_margem.py`
    reconstruiu o teto ponto no tempo (base truncada a cada ano) e mediu as duas coisas:

      · como PORTEIRA o teto funciona — abaixo dele rendeu +21,4 p.p. (defensivos) e
        +22,2 p.p. (Radar) a mais que acima dele;
      · como RÉGUA não funciona — ordenar pela margem deu spread NEGATIVO (−10,7 p.p.,
        acertando 1 de 3 anos). Margem de 50% não rendeu mais que margem de 10%;
      · a CONVICÇÃO não mede confiança — no Radar inteiro o teto ★★★ rendeu 18,3% e o ★
        rendeu 18,9%. A estrela prometia precisão que o método não tem.

    Um número com estrela comunica exatidão falsa. Uma FAIXA comunica a incerteza real: ela
    nasce larga quando o múltiplo da empresa oscilou muito, e estreita quando o mercado
    precificou o negócio de forma reconhecível ano após ano. A largura É a convicção, sem
    precisar de rótulo separado — e diferente da estrela, ela é derivada do dado, não de uma
    régua de dispersão que eu inventei.

    Percentil 25 e 75, e não mínimo e máximo, porque um único ano de pânico ou euforia não
    deve definir o limite — é a mesma razão de o motor usar mediana em vez de média desde a
    seção 19.
    """
    if len(vals) < 3:
        m = st.median(vals)
        return m, m, m, 'série curta — sem faixa, ponto único'
    if len(vals) == 3:
        # ⚠️ 13/09/2026 — com 3 pontos não existe percentil, mas existe AMPLITUDE OBSERVADA,
        # e ela é informação. Devolver ponto único aqui custava o teto de compra inteiro:
        # desde que UM método decide sozinho, faixa de largura zero aciona a supressão do
        # _sanidade, e ALOS3, AXIA3, IRBR3, PASS3, SAUD3 e SBSP3 saíam sem teto por causa da
        # convenção, não do dado. Mínimo a máximo de 3 anos é mais largo que p25-p75 — é o
        # lado certo para errar: comunica que a amostra é pequena em vez de fingir precisão.
        return min(vals), st.median(vals), max(vals), 'série de 3 anos — amplitude observada (mín-máx), não percentis'
    base = sorted(vals)
    nota = f'percentis de {len(vals)} anos'
    # ══ truncar=False: A CORREÇÃO DE FASE FICA COM O ROE (14/09/2026) ═════════════════════
    # O usuário escreveu a regra que quer, e ela diz "P/L MEDIANO HISTÓRICO × (ROE atual ÷
    # ROE histórico)". Mediana histórica é a da SÉRIE INTEIRA — não a dos 3 anos recentes.
    #
    # E não é só literalidade: truncar a série e AINDA multiplicar pelo ajuste de ROE aplica
    # a correção de recência DUAS VEZES. Os dois mecanismos fazem o mesmo trabalho — dizer
    # que a empresa de hoje não é a dos anos antigos —, só que a truncagem faz isso mudo
    # (joga metade da série fora sem declarar por quê) e o ROE faz declarando o motivo e o
    # tamanho. Onde o ROE atua, a truncagem sai.
    # O ITUB3 é o caso: truncado, a âncora era 10,0x (só 2024-2026, o período CARO); plena,
    # 7,8x. Com o ajuste de ROE de 1,156 em cima, a versão truncada cobrava 11,56x — o
    # múltiplo caro E o prêmio de rentabilidade, pelo mesmo fato.
    if truncar and len(vals) >= 5:
        # ⚠️ 14/09/2026 — A DETECÇÃO DE TENDÊNCIA COMPARA MEDIANAS, NÃO MÉDIAS.
        # Pedido do usuário: "troca média por mediana do P/L". O valor que esta função devolve
        # já era mediana (percentil 50); a média sobrevivia só aqui, no teste que decide se a
        # série tem tendência — e era incoerente com o resto do método. Um único ano de pânico
        # ou euforia move a média de uma metade de 3 pontos e liga (ou desliga) o truncamento
        # da série inteira; é exatamente o que a mediana existe para evitar, e é a mesma razão
        # que já tinha tirado a média do valor reportado na seção 19.
        meio = len(vals) // 2
        velho, novo = vals[:meio], vals[meio:]
        d = st.median(novo) - st.median(velho)
        lim = limiar_abs if limiar_abs is not None else abs(st.median(velho)) * limiar_rel
        if abs(d) > lim and len(novo) >= 3:
            base = sorted(novo)
            nota = (f'TENDÊNCIA {d:+.1f} entre as metades → faixa só dos {len(novo)} anos recentes')
    n = len(base)

    def _p(q):
        # Percentil linear simples. Com 4-6 pontos qualquer método sofisticado de interpolação
        # é enfeite: a incerteza da amostra é ordens de grandeza maior que a da interpolação.
        i = q * (n - 1)
        lo, hi = int(i), min(int(i) + 1, n - 1)
        return base[lo] + (base[hi] - base[lo]) * (i - lo)

    return _p(0.25), _p(0.50), _p(0.75), nota


def papeis_txt(pap):
    """Contagem de papéis para leitura humana. "4542 mi papéis" faz o leitor contar zeros."""
    return f'{pap/1e9:.1f} bi papéis'.replace('.', ',') if pap >= 1e9 else f'{pap/1e6:.0f} mi papéis'


def recentrar(p25, p50, p75, alvo):
    """Faixa do múltiplo próprio, RECENTRADA no múltiplo que de fato foi aplicado.

    ⚠️ Bug encontrado em 13/09/2026, quando o preço justo virou método único e a faixa passou
    a ser a do próprio método em vez do conjunto: o justo saía FORA da própria faixa. BPAC11
    R$121,75 com faixa de R$181,65 a R$206,04; SANB11, CXSE3, TIMS3, BBSE3 e BRSR6 igual.

    A causa: `justo` usa o múltiplo-alvo já MISTURADO com os pares (alvo_com_pares), enquanto
    p25/p75 vinham da série da própria empresa, sem a mistura. Duas réguas diferentes na mesma
    linha — e uma faixa que não contém o número que ela deveria descrever não é faixa, é ruído.

    A correção preserva o que a faixa mede — a AMPLITUDE RELATIVA da oscilação histórica do
    múltiplo — e a aplica ao múltiplo usado: k = alvo ÷ mediana própria, faixa × k. Se o
    mercado paga 8x e a empresa oscilou entre −20% e +30% da própria mediana, a faixa vira
    6,4x a 10,4x. O que a mistura com pares muda é o CENTRO, não a incerteza.
    """
    if not p50 or p50 <= 0 or not alvo or alvo <= 0:
        return p25, p75
    k = alvo / p50
    return p25 * k, p75 * k


def serie_pvp(t, A, val=None):
    """P/VP corrigido para units, com o fator MEDIDO contra o balanço (ver fator_multiplo).
    Conferido: SANB11 1,74x ÷ 2 = 0,87x contra 0,88x do balanço; BPAC11 6,95x ÷ 3 = 2,32x
    contra 2,69x. ⚠️ O KLBN11 é unit e mede fator 1 — o campo dela já vem por unit (1,47x
    contra 1,56x do balanço), e dividir por 5 daria 0,29x. Por isso o fator é medido."""
    f = fator_multiplo(t, A)
    ys = val if val is not None else sorted(A)
    return [A[y]['pvp']/f for y in ys if A[y].get('pvp') and A[y]['pvp'] > 0]

def serie(A, campo, excl_zero=True, respeitar_quebra=True):
    """Série de um campo, restrita aos anos comparáveis.

    ⚠️ CORREÇÃO DE 06/09/2026 — a trava de quebra de série existia em 2 dos 6 motores.
    `teto_fin` e `teto_ep` chamavam anos_validos(); `teto_ev`, `teto_bazin` e os motores de
    holding e shopping usavam a série INTEIRA, privatização e incorporação incluídas. Eu disse
    ao usuário que o SBSP3 caía no fallback por quebra de série — não caía: o motor de utility
    nunca consultou a função. Ele sempre usou os 6 anos.

    É isso que produzia os três piores tetos da tabela:
      · SBSP3  −134% — EV/EBITDA mediano de 6 anos, dos quais 5 são pré-privatização
      · AXIA3  −121% — série com EV/EBITDA de 6,01x a 27,50x, mediana de coisa nenhuma
      · CLSC4  −202% — ver mediana_com_tendencia abaixo
    """
    ys = sorted(A)
    if respeitar_quebra:
        ys, _q = anos_validos(A)
    v = [A[y][campo] for y in ys if A[y].get(campo) is not None]
    return [x for x in v if (x > 0 or not excl_zero)]

def vpa(t, A):
    """Valor patrimonial POR PAPEL NEGOCIADO (por unit, quando for unit).

    ⚠️ A conversão de units mora AQUI, e só aqui. VPA_BALANCO já é por papel (foi lido do
    balanço à mão). O caminho derivado não era: `preco ÷ pvp_reportado` dá patrimônio por
    AÇÃO, porque o pvp do Partnr é preço-da-unit sobre patrimônio-por-ação. Quem consumia
    isso junto com um P/VP-alvo já corrigido errava por um fator inteiro (KLBN11: R$3,96 em
    vez de R$19,80). Centralizar aqui evita a oitava aparição do mesmo erro.
    """
    if t in VPA_BALANCO: return VPA_BALANCO[t]
    c = A.get(max(A), {})
    if c.get('pvp') and c['pvp'] > 0 and c.get('preco'):
        return c['preco'] / c['pvp'] * fator_multiplo(t, A)
    return None

# ── FCFE DE VERDADE — item #9 do punch-list de 06/09/2026 (07/09/2026) ───────────────────
# A medida CAIXA da TIR real (`cx`, em scripts/gerar_tir.py) usava (FCO − capex) ÷ valor de
# mercado como proxy de "quanto sobra para o acionista". Isso é FCFF (fluxo de caixa livre
# para a FIRMA inteira, dívida + equity), não FCFE (fluxo livre para o EQUITY) — e o
# denominador é só o valor de mercado do equity. Misturar numerador de firma com denominador
# de equity superestima o retorno de quem está pagando dívida (o caixa operacional "sobra",
# mas uma fatia dele vai para o credor, não para o acionista) e subestima o de quem está
# alavancando (a empresa capta mais do que gera de caixa próprio, e esse dinheiro também
# chega ao acionista via investimento, recompra ou futuro dividendo maior).
#
# O caso que expôs isto: PETR4 pagou R$17,5 bi de dívida bruta líquida no período — caixa que
# ENTROU pela operação (FCO) mas SAIU para o credor, nunca chegando ao acionista. O FCO−capex
# bruto (R$109,4 bi) superestima o FCFE real (R$91,9 bi) em 16%.
#
# FCFE = FCO − capex + variação de dívida BRUTA (não líquida — líquida mistura caixa, que já
# está do lado errado da equação e dobraria a contagem). Uso ΔDívida Bruta entre os dois anos
# mais recentes e CONSECUTIVOS da base (não a série toda: dívida líquida some estrutural,
# variação ano-a-ano é o que financiamento realmente significa). Só depois da última quebra
# (anos_validos) — puxar dívida de antes de uma incorporação ou privatização não é
# financiamento orgânico, é consolidação contábil.
def delta_divida_bruta(t, A):
    val, _ = anos_validos(A)
    anos = sorted(y for y in val if A[y].get('divbruta') is not None)
    if len(anos) < 2:
        return None
    y1, y0 = anos[-1], anos[-2]
    if y1 - y0 != 1:
        return None   # não consecutivos: não dá para atribuir a financiamento de um período
    return A[y1]['divbruta'] - A[y0]['divbruta']

def payout_mediano(t, A):
    """Payout realizado, por identidade: payout = DY × P/L.

    A identidade é EXATA, não aproximação — o preço se cancela:
        DY × P/L = (DPS ÷ Preço) × (Preço ÷ LPA) = DPS ÷ LPA
    Uso DY e P/L em vez de reconstruir o DPS porque os dois vêm prontos do Partnr: uma fonte,
    uma conta, zero estimativa minha.

    ⚠️ UNITS: o Partnr calcula o P/L da UNIT com LPA por AÇÃO, então o P/L sai inflado pelo
    fator. Sem corrigir, o BPAC11 dava payout de 72% em vez de 26%.

    ⚠️ TENDÊNCIA (corrigido em 06/09/2026). A versão anterior usava mediana simples e tinha o
    MESMO defeito que eu já havia corrigido no ROE e no P/VP e não tinha trazido para cá. O
    ITUB3 denuncia: 22% · 22% · 30% · 50% · 112% · 68% ao longo da janela. A mediana simples
    dá 40%; a análise da linha do Radar dizia 74%; e a metade recente dá 68%. O banco MUDOU de
    política de distribuição no meio da série, e a mediana de 6 anos descreve o Itaú de 2021.
    Agora passa por mediana_com_tendencia, como todo o resto.
    """
    # MÉTODO: razão de ACUMULADOS, não mediana de razões anuais.
    #
    # Tentei antes a mediana com correção de tendência e ela quebrou nas cíclicas: no fundo do
    # ciclo o LUCRO some e o payout daquele ano explode sem que a empresa tenha distribuído
    # nada de anormal (KLBN11 2026: P/L de 43,67x devolve payout de 220%; VALE3 e SBSP3 batiam
    # no teto de 100%). Corrigir por tendência piorava, porque a metade RECENTE é justamente
    # onde estão os anos deprimidos.
    #
    # A razão de acumulados — Σ dividendos ÷ Σ lucros da janela — é o que uma empresa de fato
    # distribuiu do que de fato ganhou no período. Um ano de lucro perto de zero contribui
    # pouco para os dois lados e não domina o resultado. É também como a política de
    # dividendos é escrita na prática ("distribuímos X% do lucro"), medida ao longo do ciclo.
    val, _q = anos_validos(A)
    f = FATOR_UNIT.get(t, 1)
    div = lucro = 0.0; n = 0
    for y in val:
        d = A[y]
        lpa_unit = (d.get('lpa') or 0) * f
        # ⚠️ DY == 0 É DADO FALTANDO, NÃO DIVIDENDO ZERO. Achado pelo usuário ao conferir a
        # CPFE3: nenhum ano dela tem payout abaixo de 55% (110% · 72% · 60% · 55%) e o meu
        # agregado dava 44%. O Partnr traz dy=0 em 2025 e 2026 para a CPFL, que PAGOU nos dois
        # anos — o zero entrava no numerador e o lucro inteiro no denominador, afundando a
        # razão. Eu já tinha tropeçado nesse mesmo zero antes e corrigido só na EXIBIÇÃO
        # (js/fundamentos.js mostra "—" em vez de "0,0%"); o cálculo continuou comendo o zero.
        #
        # ⚠️ VIÉS QUE ISSO INTRODUZ, declarado: uma empresa que genuinamente NÃO pagou naquele
        # ano também sai da conta, e o payout resultante fica mais alto do que a realidade.
        # É o lado errado menos ruim: tratar dado ausente como zero produz números que nenhum
        # ano da série sustenta, enquanto excluir apenas ignora o ano.
        if not d.get('preco') or not d.get('dy') or lpa_unit <= 0:
            continue          # ano de prejuízo, ou sem DY, sai dos DOIS lados da razão
        div += d['dy']/100 * d['preco']
        lucro += lpa_unit
        n += 1
    if n < 2 or lucro <= 0:
        return (None, n)
    return (min(div/lucro, 1.0), n)

# ── POLÍTICA DE DIVIDENDOS DECLARADA ─────────────────────────────────────────────────────
# Regra proposta pelo usuário: "a primeira regra do motor de payout deveria ser o que a empresa
# declara em sua política, e depois a mediana entre o que se enquadra". A intenção está certa —
# guidance é compromisso e é forward-looking, e o realizado é passado. Mas a pesquisa nos RIs
# (06/09/2026) mostrou que, na B3, a política declarada quase nunca é utilizável como número:
#
#   · DAS 30, SÓ 7 têm compromisso formal acima do mínimo legal.
#   · E 4 DESSES 7 nem usam lucro líquido como base: PETR4 distribui 45% de (FCO − capex),
#     VALE3 30% de (EBITDA − investimento corrente), KLBN11 10-20% do EBITDA ajustado e TIMS3
#     declara VALOR ABSOLUTO (R$ 5,3-5,5 bi em 2026). Nenhum é conversível em "% do lucro"
#     sem eu estimar as duas pontas.
#   · ITUB3, BBSE3, IRBR3 e AURE3 têm documento CHAMADO "política de dividendos" cujo conteúdo
#     é o mínimo estatutário de 25% da Lei 6.404 — que toda S.A. brasileira tem. Isso não é
#     política, é o piso legal, e usá-lo como âncora seria projetar o dividendo do Itaú em 25%.
#
# Sobra o desenho honesto: a política entra como RESTRIÇÃO (piso ou teto) sobre o realizado,
# não como substituta dele. O realizado é a estimativa; a política é o limite que a empresa
# se comprometeu a respeitar. Onde os dois convivem, o resultado é o realizado CLIPADO.
#
# tipo: 'piso' | 'teto' | 'estatutario' | 'outra_base' | 'nao_paga'
POLITICA = {
    'CPFE3':  (0.50, 'piso',        'Mínimo de 50% do lucro líquido ajustado (Política de Distribuição de Dividendos, 16/12/2021)'),
    'BRSR6':  (0.40, 'piso',        'Payout de 40% do lucro líquido, reduzido de 50% a partir de 2024 (RI Banrisul)'),
    'SBSP3':  (0.50, 'teto',        'Escala crescente: até 50% em 2026-27, até 75% em 2028-29, até 100% a partir de 2030, ajustado pelo Fator U (Política aprovada pelo CA em 14/06/2024)'),
    'PETR4':  (None, 'outra_base',  '45% de (FCO − capex), não do lucro líquido, condicionado à dívida bruta (Política de Remuneração, jul/2023, reiterada em 05/03/2026)'),
    'VALE3':  (None, 'outra_base',  '30% de (EBITDA ajustado − investimento corrente), não do lucro (Política de 29/03/2018)'),
    'KLBN11': (None, 'outra_base',  '10% a 20% do EBITDA ajustado, distribuição trimestral, com meta de alavancagem 2,5-3,5x (nova política de 29/10/2024)'),
    'TIMS3':  (None, 'outra_base',  'Guidance em VALOR ABSOLUTO: R$ 5,3-5,5 bi em 2026 (Plano Estratégico 2026)'),
    'ITUB3':  (0.25, 'estatutario', 'A "política" do Itaú (CA 26/01/2026) declara apenas "não inferior a 25%" — é o mínimo da Lei 6.404, não uma meta'),
    'BBSE3':  (0.25, 'estatutario', 'Política de 30/05/2025 declara o mínimo estatutário de 25%; o payout efetivo de 80-90% é decisão semestral do Conselho, não compromisso'),
    'IRBR3':  (0.25, 'estatutario', 'A própria empresa declarou "o mínimo legal de 25%" ao retomar dividendos no 4T25 (mar/2026)'),
    'AURE3':  (0.25, 'estatutario', 'Política de 11/04/2022 = mínimo estatutário de 25%'),
    'ROXO34': (0.00, 'nao_paga',    'Nu Holdings não paga dividendos — reinveste 100% do lucro. Sediada nas Cayman, não sujeita à Lei 6.404'),
}

def payout_setorial(t, H):
    """Payout mediano dos pares do mesmo grupo — só para quem não tem série própria."""
    if not H: return None
    m = MOTOR.get(t)
    ps = []
    for p, B in H.items():
        if p == t or MOTOR.get(p) != m: continue
        v, n = payout_mediano(p, B)
        if v and n >= 4: ps.append(v)
    return st.median(ps) if len(ps) >= 2 else None

def payout_final(t, A, H=None):
    """Realizado, CLIPADO pela política declarada quando ela existe e é % do lucro."""
    real, n = payout_mediano(t, A)
    pol0 = POLITICA.get(t)
    if pol0 and pol0[1] == 'nao_paga':
        # ANTES do fallback de pares. O ROXO34 caía no payout mediano dos bancos brasileiros
        # (47%) porque a checagem da política vinha depois, e o Nu Holdings NÃO PAGA DIVIDENDO
        # NENHUM — reinveste 100%. Um fato declarado tem precedência sobre qualquer inferência.
        return 0.0, n, ('nao_paga', pol0[2], real)
    if real is None:
        # Sem série própria (IRBR3 retomou dividendos há 1 ano). Antes isto matava o teto_fin
        # inteiro e a empresa caía no peer comp bruto — o IRB foi parar em R$84,67 contra
        # cotação de R$56,78. O payout dos pares é uma premissa fraca, mas é MUITO menos
        # destrutiva que perder os três motores de valuation por causa de um único campo.
        ps = payout_setorial(t, H or H_GLOBAL)
        if ps: return ps, 0, ('pares', f'Payout mediano dos pares do grupo {MOTOR.get(t)} — a empresa não tem série própria de dividendos utilizável (menos de 2 anos).', None)
    pol = POLITICA.get(t)
    if not pol:
        return real, n, ('realizado', None, real)
    alvo, tipo, texto = pol
    if tipo == 'nao_paga':
        return 0.0, n, ('nao_paga', texto, real)
    if tipo in ('outra_base', 'estatutario') or alvo is None or real is None:
        return real, n, (tipo, texto, real)
    ajust = max(real, alvo) if tipo == 'piso' else min(real, alvo)
    return ajust, n, (tipo, texto, real)

def rim_fade(B0, roe, ke, po, N=ANOS_G1, rt=None):
    """LUCRO RESIDUAL com vantagem competitiva que SE DISSIPA.

    V = patrimônio + valor presente do retorno ACIMA do custo de capital, com o ROE
    convergindo linearmente para o Ke em N anos. Depois disso o excedente é ZERO — não há
    perpetuidade de vantagem.

    POR QUE SUBSTITUIU O GORDON/DDM NAS FINANCEIRAS:
    O Gordon põe todo o valor numa perpetuidade dividida por (Ke − g), um número pequeno.
    Mexer 1 p.p. no Ke movia o teto ~11%, e entre Ke de 13% e 16% o resultado variava 1,46x —
    a mesma alavanca que fez o teto do SANB11 dobrar de um dia para o outro.
    Aqui o PATRIMÔNIO (número de balanço, auditado) carrega 80% do resultado e a premissa
    frágil governa só o resto: a mesma variação de Ke move 1,11x.

    ⚠️ O CUSTO: assumir que toda vantagem se dissipa em 10 anos penaliza franquia genuína.
    A BBSE3 (ROE 78,8%) cai de R$70,64 pelo Gordon para ~R$23 aqui. É conservador, e para ela
    talvez conservador demais — por isso a validação cruzada por múltiplo próprio existe.
    """
    if rt is None: rt = ke
    V = B0; B = B0
    for t_ in range(1, N+1):
        r = roe + (rt - roe)*t_/N
        V += ((r - ke)/100*B)/(1 + ke/100)**t_
        B += (r/100*B)*(1 - po)
    return V

def teto_fin(t, A):
    """Banco e seguradora: DDM de 2 estágios.

    Antes era P/VP×ROE de UM estágio com Ke e g fixos. Trocado porque o motor de um estágio
    NÃO comporta franquia que cresce acima do PIB: testando o Ke que o mercado pratica, ITUB3
    e CXSE3 davam ~11,8%, ABAIXO do juro longo — sinal de que o g de 6,44% para sempre é que
    estava errado, não o preço. O DDM de 2 estágios resolve deixando a empresa crescer ao
    ritmo que o ROE e a retenção sustentam por 10 anos, e só então convergir para o PIB.
    """
    c = A[max(A)]
    val, q = anos_validos(A)   # ignora anos anteriores a uma quebra de série
    roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
    roe, roe_nota = mediana_com_tendencia(roes, limiar_abs=2.0) if roes else (None, '')
    if q: roe_nota = f'⚠️ QUEBRA DE SÉRIE em {q}: só anos a partir dali. ' + roe_nota
    po, n, _fonte = payout_final(t, A)   # realizado clipado pela política declarada
    lpa = c.get('lpa')
    if roe is None or po is None or not lpa or lpa <= 0: return None
    ke, det = ke_empresa(t, A)

    # ── TRAVA DA REESTRUTURAÇÃO / ROE BAIXO ────────────────────────────────────────────────
    # Existia na versão P/VP×ROE e eu a PERDI ao trocar o motor para DDM — foi o que produziu
    # o teto de R$8,18 do IRBR3 contra cotação de R$56,78 (−525%).
    # Duas causas se somam nesses casos:
    #  (a) a MEDIANA atravessa quebra de série. O IRB teve ROE de −16,8%, −16,7% e −3,0% na
    #      crise e 17,2%, 7,5%, 4,5% depois — a mediana da série inteira dá 0,8%, que não
    #      descreve nem a empresa velha nem a nova.
    #  (b) DDM sobre empresa que quase não distribui e rende pouco converge para ~zero, mesmo
    #      tendo patrimônio real. Matematicamente correto, praticamente inútil.
    # Quando ROE mediano não supera g em 3 p.p., abandonamos o fluxo e ancoramos no BALANÇO:
    # P/VP MÍNIMO da própria série × VPA. É piso empírico — o menor múltiplo que o mercado já
    # pagou por aquele patrimônio — em vez de uma projeção de dividendo que não se sustenta.
    if roe < G + 3.0:
        v = vpa(t, A); pvps = serie(A, 'pvp')
        if v and pvps:
            alvo = min(pvps)
            quebra = any((A[y].get('roe') or 0) < 0 for y in A)
            return dict(justo=alvo*v, conv=1, ke=ke,
                motor=f'P/VP mínimo histórico {alvo:.2f}x × VPA R$ {v:.2f}',
                nota=f'⚠️ TRAVA: ROE mediano de {roe:.1f}% não supera g ({G:.2f}%) em 3 p.p. — o DDM '
                     f'convergiria para perto de zero mesmo com patrimônio real. Ancorado no piso '
                     f'empírico: menor P/VP da série ({alvo:.2f}x; faixa {min(pvps):.2f}-{max(pvps):.2f}x). '
                     + (f'⚠️ QUEBRA DE SÉRIE: há anos de PREJUÍZO na janela, então a mediana de ROE '
                        f'mistura duas empresas diferentes. Trate este teto como marcador. ' if quebra else '')
                     + det)

    v = vpa(t, A)
    pvps = serie_pvp(t, A, val)
    if not v or not pvps: return None

    # ── TRÊS MOTORES INDEPENDENTES → MEDIANA ──────────────────────────────────────────────
    # Regra que a seção 0 da metodologia já mandava e que eu não aplicava nas financeiras:
    # havendo mais de um método, o justo é o consenso e a DISPERSÃO vira a convicção.
    # Por que isto resolve a instabilidade que derrubou a confiança no teto: nenhum motor
    # sozinho manda. Trocar um deles move pouco a mediana, porque os outros dois seguram.
    #   A · Gordon / P/VP×ROE  → generoso: assume vantagem competitiva eterna
    #   B · Lucro residual     → conservador: vantagem cai pela metade em 10 anos
    #   C · Múltiplo próprio   → SEM premissa minha: P/VP mediano da série × VPA
    # A é sensível ao Ke, B pouco, C nada. A mediana herda o meio-termo.
    mA = v*(roe - G)/(ke - G) if ke > G else None
    mB = rim_fade(v, roe, ke, po, rt=(roe + ke)/2)
    pvp_alvo, pvp_nota = mediana_com_tendencia(pvps)
    mC = pvp_alvo*v
    vals = [x for x in (mA, mB, mC) if x and x > 0]
    if not vals: return None
    justo = st.median(vals)
    disp = (max(vals) - min(vals))/max(vals)
    conv_disp = 3 if disp < 0.15 else (2 if disp < 0.35 else 1)
    # Convicção = a PIOR entre a dispersão dos motores e a qualidade da série.
    # payout de um ano só não é política de dividendos, é um ponto (IRBR3 retomou em 2026).
    conv = min(conv_disp, 1 if n < 3 else (3 if (n >= 5 and len(roes) >= 5) else 2))
    return dict(justo=justo, conv=conv, ke=ke,
        motor=f'Mediana de 3 motores: Gordon R$ {mA:.2f} · lucro residual R$ {mB:.2f} · múltiplo próprio R$ {mC:.2f}',
        nota=f'Consenso dos três, dispersão {disp*100:.0f}% → convicção pela dispersão. '
             f'ROE {roe:.1f}%: {roe_nota}. P/VP alvo {pvp_alvo:.2f}x: {pvp_nota} '
             f'(série {min(pvps):.2f}-{max(pvps):.2f}x, corrigida para units). '
             f'Payout mediano {po*100:.0f}% ({n} anos), VPA R$ {v:.2f}. '
             f'Nenhum motor decide sozinho: o Gordon assume vantagem eterna, o residual assume que ela cai '
             f'pela metade em 10 anos, e o múltiplo próprio não usa premissa nenhuma minha. {det}')

def teto_ev(t, A, ciclico):
    """EV/EBITDA. Cíclica usa EBITDA médio do ciclo; utility usa o recorrente mais recente."""
    c = A[max(A)]
    mult = serie(A, 'evEbitda')
    if not mult or not c.get('divliq') is not None: return None
    eb = serie(A, 'ebitda')
    if not eb: return None

    # DISPERSÃO DO EBITDA — se o EBITDA da própria empresa varia mais de 2x dentro da janela,
    # a mediana do múltiplo não descreve nada: cada ano foi medido contra um denominador
    # diferente. O AXIA3 é o caso — EBITDA de R$8,5 bi a R$26,2 bi e EV/EBITDA de 6,01x a
    # 27,50x na mesma série. O motor devolvia R$25,13 contra cotação de R$55,52 (−121%) com
    # cara de opinião. Recusar é a resposta honesta.
    # Dois cortes, apertados depois que o AXIA3 passou pela primeira versão por pouco:
    #   · MÍNIMO DE ANOS — com 2 observações não existe mediana, existe média de dois pontos.
    #     O AXIA3 tinha quebra em 2025, sobravam 2025 e 2026, e o múltiplo-alvo saiu 20,39x
    #     num setor cujos pares rodam entre 5x e 9x. O número passou na trava de ±100% e foi
    #     publicado como R$45,19. Não era análise, era extrapolação de dois pontos.
    #   · DISPERSÃO 2,0x → 1,7x — o AXIA3 tinha EBITDA de R$8,5 bi e R$16,3 bi na janela
    #     válida (1,9x) e escapou por 0,1. O limite de 2,0x foi escolhido por mim sem teste;
    #     1,7x também é arbitrário, mas é o valor que reprova o caso que eu já sei estar errado.
    if not ciclico:
        if len(mult) < 3 or len(eb) < 3:
            return None
        if max(eb)/min(eb) > 1.7:
            return None

    # TENDÊNCIA — a mesma regra das financeiras, agora em utility. Eu havia escrito na
    # metodologia que NÃO aplicaria mediana_com_tendencia fora de financeiras, argumentando
    # que "em cíclica a mediana precisa cobrir pico E fundo". O argumento vale para cíclica de
    # commodity e eu o estendi para utility sem checar — utility não oscila com preço de
    # commodity, ela faz RE-RATING ESTRUTURAL (privatização, revisão tarifária).
    # CLSC4: EV/EBITDA subiu 3,15x → 5,70x de forma monotônica em 6 anos. A mediana (≈4,2x)
    # descreve uma empresa que não existe mais e devolvia teto de R$51,72 contra R$156,00.
    # ⚠️ A FAIXA (p25-p75 do próprio múltiplo) passou a ser OBRIGATÓRIA aqui em 13/09/2026.
    # Antes teto_ev era um dos vários métodos votando e a faixa saía do conjunto; agora ele
    # DECIDE SOZINHO nas cíclicas, e sem faixa própria o limite inferior não existe — o
    # _sanidade suprimia o teto de compra de KLBN11, PETR4, VALE3 e RANI3 por "método único
    # sem série para formar faixa", quando a série existia e era justamente a do múltiplo.
    p25, p50, p75, nota_fx = faixa_com_tendencia(mult, limiar_rel=0.12)
    decl_m = MULTIPLO_DECLARADO.get(t)
    if decl_m and decl_m[0] == 'EV/EBITDA':
        alvo_decl = decl_m[1]
    else:
        alvo_decl = None
    if ciclico:
        # Cíclica não corta a série pela metade: o ciclo inteiro É a amostra, e a metade
        # recente descreve só onde o ciclo estava. Percentis da série toda.
        b = sorted(mult); n = len(b)
        _p = lambda q: b[int(q*(n-1))] + (b[min(int(q*(n-1))+1, n-1)] - b[int(q*(n-1))]) * (q*(n-1) - int(q*(n-1)))
        p25, p50, p75 = _p(0.25), st.median(mult), _p(0.75)
        alvo, nota_alvo = p50, 'MEDIANA da série inteira (cíclica cobre pico e fundo)'
        nota_fx = f'percentis dos {len(mult)} anos, série inteira'
    else:
        alvo, nota_alvo = mediana_com_tendencia(mult, limiar_rel=0.12)
    if alvo_decl is not None:
        nota_alvo = (f'DECLARADO no relatório ({alvo_decl:.2f}x, contra {alvo:.2f}x da própria '
                     f'série). {decl_m[3]}')
        alvo = alvo_decl
    ebitda = st.mean(eb) if ciclico else eb[-1]
    pap = papeis(t, A)
    if not pap: return None
    dl = (c.get('divliq') or 0)
    _pr = lambda mu: (mu*ebitda - dl) / pap
    justo = _pr(alvo)
    fx = (_pr(p25), _pr(p75))
    if not (fx[0] and fx[1] and fx[0] > 0 and fx[1] > fx[0]):
        fx = None
    conv = 3 if len(mult) >= 5 else 2
    base = 'EBITDA médio de %d anos (R$ %.1f bi)' % (len(eb), ebitda/1e9) if ciclico else 'EBITDA LTM (R$ %.1f bi)' % (ebitda/1e9)
    return dict(justo=justo, conv=conv, chave='EV/EBITDA', faixa=fx,
        conta=(f'{base} × EV/EBITDA {alvo:.2f}x − dívida líquida R$ {dl/1e9:.1f} bi, '
               f'÷ {papeis_txt(pap)}'),
        origem_mult=((f'o múltiplo DECLARADO no relatório ({alvo:.2f}x), contra a mediana de '
                      f'{len(mult)} anos da própria série. {decl_m[3]}') if alvo_decl is not None
                     else (f'o EV/EBITDA mediano da própria empresa ao longo de {len(mult)} anos '
                           f'({alvo:.2f}x; a série foi de {min(mult):.1f}x a {max(mult):.1f}x)'
                           + (' — em cíclica a janela cobre pico e fundo do ciclo de propósito'
                              if ciclico else ''))),
        motor=f'EV/EBITDA {alvo:.2f}x sobre {base}',
        nota=f'Múltiplo-alvo {alvo:.2f}x = {nota_alvo} do próprio histórico ({len(mult)} anos: {min(mult):.1f}x a {max(mult):.1f}x), não de pares. '
             f'Faixa {p25:.2f}x a {p75:.2f}x ({nota_fx}). '
             f'EV justo − dívida líquida R$ {dl/1e9:.1f} bi ÷ {pap/1e6:.0f} mi papéis.')

def teto_bazin(t, A):
    """Gordon sobre dividendo sustentável. Substitui o Bazin de yield arbitrário."""
    c = A[max(A)]
    # ⚠️ Este bloco tinha uma CÓPIA da lógica de payout, com todos os defeitos que já haviam
    # sido corrigidos na função oficial: sem correção de units, mediana das razões anuais em
    # vez de razão de acumulados, e tratando dy=0 (dado faltando) como dividendo zero. Duas
    # fontes de verdade para o mesmo conceito, e a errada era a que alimentava o Gordon de
    # utilities e telecom. Agora chama payout_final(), que aplica também a política declarada.
    payout, n_po, _fonte = payout_final(t, A)
    lpa, lucro = c.get('lpa'), c.get('lucrolin')
    if payout is None or not lpa or lpa <= 0: return None
    # ⚠️ GORDON SÓ VALE PARA QUEM DISTRIBUI. Com payout baixo o modelo desconta um dividendo
    # minúsculo e IGNORA o que a empresa faz com o lucro retido — ela reinveste, e isso vira
    # valor que o Gordon não enxerga. O SHUL4 (payout 6%) despencou para R$2,10 contra cotação
    # de R$4,45 quando este método entrou na votação. Abaixo de 20% o método se retira em vez
    # de poluir a mediana; os múltiplos continuam respondendo por essas empresas.
    if payout < 0.20: return None
    pos = [payout] * max(n_po, 1)
    dps = lpa * FATOR_UNIT.get(t, 1) * payout
    if dps <= 0: return None
    ke, det = ke_empresa(t, A)
    ye = ke - G
    return dict(justo=dps/(ye/100), conv=2, ke=ke,
        motor=f'Gordon: DPS sustentável R$ {dps:.2f} ÷ {ye:.2f}%',
        nota=f'DPS = LPA R$ {lpa*FATOR_UNIT.get(t,1):.2f} × payout mediano {payout*100:.0f}% ({len(pos)} anos). '
             f'Yield exigido = Ke − g = {ye:.2f}%, substitui o Bazin de 8-9% arbitrário. {det}')

# ══════════════════════════════════════════════════════════════════════════════════════════
# CRESCIMENTO PARA PROJETAR O FUNDAMENTO — mora aqui e não em gerar_colunas.py de propósito.
# ══════════════════════════════════════════════════════════════════════════════════════════
# O usuário: "o preço justo não está igual definimos da Allos, que era o LPA estimado x o
# múltiplo". Estava mesmo diferente — os métodos multiplicavam o múltiplo pelo fundamento dos
# ÚLTIMOS 12 MESES, enquanto a coluna de LPA da tabela já mostrava o projetado para 2026. Duas
# contas de LPA na mesma linha: ITUB3 R$ 4,35 no motor contra R$ 5,16 na tela, e a BBSE3 com o
# motor usando um LPA MAIOR justamente onde o lucro vai cair.
#
# A função vive no motor porque os três scripts o carregam com exec() — assim existe UMA
# definição. A alternativa seria motor_teto ler data/tir.data.js, que é escrito por gerar_tir,
# que lê motor_teto: o mesmo ciclo de cache que congelou o lucro normalizado da TIM.
CRESC_CAP = 25.0

# ══════════════════════════════════════════════════════════════════════════════════════════
# O QUE O RELATÓRIO SABE E O MOTOR NÃO — lucro de 2026 e múltiplo, declarados
# ══════════════════════════════════════════════════════════════════════════════════════════
# O usuário: "para o nosso motor as variáveis mais importantes são o lucro estimado 2026 e o
# múltiplo a qual a empresa está sendo valorada, então precisamos ser assertivos nessas
# métricas — o relatório detalhado de cada empresa deve nos dar insumos para definirmos esses
# critérios de forma assertiva".
#
# Ele está certo: preço justo = LPA projetado × múltiplo, então a precisão do motor inteiro
# mora nessas duas variáveis, e as duas saíam de regressão estatística sobre o histórico —
# nenhuma olhava a empresa. Guidance da companhia, consenso de mercado e projeção de casa de
# análise são informação que a regressão não tem como capturar.
#
# REGRA: o declarado VENCE o estimado, e a tooltip diz de onde veio. Mesmo princípio que
# POLITICA já aplica ao payout desde 06/09.
#
# ⚠️ SÓ ENTRA AQUI O QUE O RELATÓRIO DÁ EM NÚMERO ABSOLUTO DE LUCRO DE 2026. Oito dos catorze
# relatórios projetam EBITDA (PASS3), NOI (ALOS3, MULT3), LPA em 2031 (CPFE3, ROXO34) ou lucro
# num horizonte de 3 anos (TIMS3, LEVE3) — converter qualquer um desses em lucro de 2026 exigiria
# premissa minha sobre depreciação, papéis ou cronograma, e premissa minha disfarçada de
# guidance é pior que estimativa assumida. Esses continuam no motor estatístico.
# ⚠️ TERCEIRO ELEMENTO, opcional, desde 14/09/2026: como o número foi construído. Quem lê é
# `scripts/checar_lucro_declarado.py`, e sem isso ele usa a régua errada.
#
#   ('projecao',)          → é uma projeção do EXERCÍCIO de 2026. Confere contra o run-rate:
#                            1S anualizado e LTM. Afastar-se dos dois na mesma direção é erro.
#   ('ciclo', ini, fim)    → é a MÉDIA DE UM CICLO, e ignora o run-rate de propósito. Confere
#                            recalculando a média daqueles exercícios com o dado publicado.
#
# A distinção nasceu de um falso positivo meu: o verificador acusou o IRBR3 de divergir 1,83x
# do 1S26 anualizado. Divergia mesmo — e ESTÁ CERTO assim. O número é a média de 2023-2025
# (−218 mi, +806 mi, +391 mi → média 326 mi contra os 330 declarados), escolhida porque o
# próprio relatório se recusa a projetar 2026 com a contabilidade IFRS e a gerencial
# divergindo de sinal. Comparar média de ciclo com run-rate é comparar coisas diferentes.
LUCRO_2026_DECLARADO = {
    'BBSE3': (8.65e9,
              'Cenário BASE do relatório de 25/08/2026, que usa o guidance oficial da companhia '
              '(resultado operacional consolidado −7% a −3% para 2026; o base é o meio, −5%) e '
              'coincide com o consenso de mercado de R$ 8,65-8,69 bi.',
              ('projecao',)),
    'ITUB3': (50.6e9,
              'Cenário BASE do relatório de 25/08/2026: crescimento financeiro padrão de 8% a.a. '
              'sobre o lucro RECORRENTE de 2025. O conservador (piso do guidance de carteira, '
              '+5,5%) dá R$ 49,2 bi e o otimista (ritmo do 2T26, +9,6%) dá R$ 52,5 bi.',
              ('projecao',)),
    'CXSE3': (4.64e9,
              'Cenário BASE do relatório de 25/08/2026: crescimento financeiro de 8% a.a. sem '
              'novo choque regulatório. ⚠️ Não há guidance numérico oficial da companhia — o '
              'conservador (+3%, prestamista não recupera) dá R$ 4,43 bi.',
              ('projecao',)),
    'BMEB4': (1.03e9,
              'Cenário BASE do relatório de 25/08/2026: ponto médio entre o g financeiro padrão '
              '(8%) e o crescimento implícito pela retenção de capital (ROE × retenção ≈ 19,3%). '
              '⚠️ Sem guidance oficial; o otimista replica a projeção do Safra (R$ 1,20 bi).',
              ('projecao',)),
    'FIQE3': (218e6,
              'Cenário BASE do relatório de 24/08/2026 (LPA R$ 0,55). A faixa vai de R$ 205 mi '
              '(conservador) a R$ 232 mi (otimista).',
              ('projecao',)),
    'IRBR3': (330e6,
              'Cenário CONSERVADOR do relatório de 25/08/2026 — e é o único disponível: o próprio '
              'relatório se recusa a publicar um cenário base, porque a divergência entre lucro '
              'contábil (IFRS) e gerencial inverteu de sinal no 2T26. É o lucro médio de ciclo '
              '2023-2025, tratando o trimestre como ruído. O otimista, sobre o run-rate gerencial '
              'do 2T26, daria R$ 740 mi — mais que o dobro.',
              ('ciclo', 2023, 2025)),
}

# Múltiplo-alvo declarado. Vence a mediana da própria série e o ajuste de ROE (14/09/2026).
# (chave, múltiplo-alvo, (piso, teto) da sensibilidade do relatório, justificativa)
# ⚠️ A FAIXA NÃO É ENFEITE: é ela que alimenta os três cenários do relatório. Sem ela, os
# cenários caíam no percentil 25/75 da própria série — e na RANI3 o múltiplo declarado (5,5x)
# é MAIOR que o p75 da série (5,41x), o que punha o cenário otimista ABAIXO do base.
MULTIPLO_DECLARADO = {
    'RANI3': ('EV/EBITDA', 5.5, (5.0, 6.0),
              'Relatório de 24/08/2026: EV/EBITDA de MEIO DE CICLO, faixa sensibilizada de 5,0x '
              '(ciclo de papel/celulose enfraquece) a 6,0x (nova capacidade amadurece). O motor '
              'estatístico usava a mediana da própria série, que mede onde o ciclo esteve, não '
              'onde ele normaliza.'),
}

CRESCIMENTO_DECLARADO = {
    'BBSE3': (-5.0,
              'Consenso de mercado para 2026: lucro de R$ 8,6 bi, −5,4% sobre 2025. O guidance '
              'da companhia divulgado com o 4T25 projeta prêmios emitidos de −1,5% (faixa −3% a '
              '+2%), depois de 2025 fechar em −8,8%, abaixo do próprio guidance revisado. '
              'Pressões: seguro agrícola em queda pelo terceiro ano, prestamista afetado pela '
              'Selic alta e saída líquida na Brasilprev após o IOF sobre VGBL.'),
}


def _reg_log(vals):
    """Inclinação anual de ln(valor) — o mesmo estimador de cagr_recorrente()."""
    pts = [(y, v) for y, v in vals if v and v > 0]
    if len(pts) < 3: return None
    xs = [y for y, _ in pts]; ys = [math.log(v) for _, v in pts]
    mx, my = st.mean(xs), st.mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if not den: return None
    return (math.exp(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den) - 1) * 100


_FLUXO = None

def _recorrente(t):
    """CAGR do LUCRO RECORRENTE por regressão log, de data/fluxo.json.

    Lido direto do arquivo, que é coletado à mão e não sai da pipeline — então não há o ciclo
    de "o gerador lê a própria saída" que congelou o lucro normalizado da TIM. O motor anula
    este conceito para banco, seguradora, holding e cíclica; nesses casos a função devolve None
    e a decisão cai nas outras duas opiniões.
    """
    global _FLUXO
    if _FLUXO is None:
        try:
            _FLUXO = json.load(open('data/fluxo.json', encoding='utf-8'))['tickers']
        except Exception:
            _FLUXO = {}
    h = (_FLUXO.get(t) or {}).get('lucro_recorrente_hist') or {}
    return _reg_log([(int(y), v) for y, v in h.items() if v is not None])


def base_projecao(t, A):
    """(lucro-base do exercício, rótulo) para projetar 2026. Normalmente o ano de 2025.

    ⚠️ EXCEÇÃO QUE CORRIGE DOIS PREÇOS JUSTOS ERRADOS, 14/09/2026. Quando houve QUEBRA DE
    SÉRIE em 2025 ou depois, o exercício de 2025 não é base limpa: o lucro é de antes do
    evento societário e a contagem de papéis é de depois. Dividir um pelo outro mistura duas
    empresas e o LPA sai pela metade.

      AXIA3 · quebra 2025 · lucro 2025 R$ 6,56 bi contra LTM R$ 12,06 bi (+84%)
              LPA saía R$ 2,24 quando o run-rate já era R$ 4,12
      SAUD3 · quebra 2026 · lucro 2025 R$ 0,58 bi contra LTM R$ 1,05 bi (+81%)
              LPA saía R$ 0,20 quando o run-rate já era R$ 0,36

    Nesses casos a base passa a ser o LUCRO DOS ÚLTIMOS 12 MESES, que já é pós-evento e
    reconcilia com a contagem de papéis atual. É menos estável que um exercício fechado —
    e por isso a nota diz que a base mudou — mas é a única que descreve a empresa de hoje.
    """
    # ⚠️ NÃO há atalho para LUCRO_2026_DECLARADO aqui. Houve, e custou a coluna de
    # crescimento: teto_ep já trata o declarado ANTES de chamar esta função, então o atalho
    # só servia para devolver None a quem perguntasse o lucro-base — e a tabela precisa dele
    # para mostrar de quanto foi a variação de 2025 para o 2026 declarado. As 6 linhas
    # declaradas ficaram com "SEM TAXA DE CRESCIMENTO" na tela.
    q = ano_quebra(A)
    ltm = A[max(A)].get('lucrolin')
    if q and q >= 2025 and ltm and ltm > 0:
        return ltm, (f'LUCRO LTM (não o exercício de 2025): houve quebra de série em {q}, '
                     f'então o lucro de 2025 é de antes do evento societário e os papéis são '
                     f'de depois — dividir um pelo outro mistura duas empresas')
    l25 = (A.get(2025) or {}).get('lucrolin')
    if (not l25 or l25 <= 0) and (not ltm or ltm <= 0):
        # ROXO34: a base não traz lucro em reais, só o LPA lido à mão de um release. O motor
        # já reconstituía o lucro por LPA × papéis lá dentro do teto_ep; a tabela mostrava "—".
        c = A[max(A)]
        pap = papeis(t, A)
        if c.get('lpa') and c['lpa'] > 0 and pap:
            return c['lpa'] * pap, ('LPA × papéis — a base não traz lucro em reais para esta '
                                    'empresa, só o lucro por ação')
    if (not l25 or l25 <= 0) and ltm and ltm > 0:
        # ASAI3 e ROXO34: a base não tem exercício de 2025 (a DRE anual da Partnr não cobre a
        # empresa). O motor já caía no LTM aqui dentro do teto_ep; a tabela não, e mostrava
        # "—" na coluna de lucro enquanto o preço justo usava um número. Uma definição só.
        return ltm, 'LUCRO LTM — a base não tem o exercício de 2025 fechado para esta empresa'
    return l25, 'exercício fechado de 2025'


def crescimento(t, A, H=None):
    """(taxa %, origem) para projetar o fundamento de hoje ao exercício seguinte.

    Ordem: taxa DECLARADA pela companhia ou pelo consenso vence tudo (princípio que POLITICA já
    aplica ao payout). Senão, o CAGR do lucro RECORRENTE quando existe. Senão, o MENOR entre
    ROE × retenção e a regressão log do lucro contábil — as duas opiniões que sobram quando o
    conceito de recorrente não se aplica.
    """
    decl = CRESCIMENTO_DECLARADO.get(t)
    if decl:
        return decl[0], decl[1]
    # ⚠️ FIN, NAV e CICL NÃO USAM O RECORRENTE, e a regra não é minha: está em gerar_tir.py
    # desde que o Itaú saiu com −23% ao ano por esse caminho — a série de "recorrente" de um
    # banco na base mede outra coisa. Nas cíclicas o motivo é o outro já conhecido: o CAGR
    # herdado mede a queda até o fundo do ciclo, e projetar isso é tratar ano ruim como
    # capacidade normal (a KLBN11 saía com −70%).
    # ⚠️ SHOPPING PROJETA O FFO. Pedido do usuário em 13/09/2026 ("para shopping trocar lucro
    # líquido por FFO em todas as colunas"), e a regra tem que morar AQUI, não em
    # gerar_colunas.py: `crescimento()` é o que teto_ffo() usa para projetar o FFO por papel do
    # preço justo. Se a tabela crescesse o FFO e o motor crescesse o lucro, a coluna "Lucro
    # Projetado 2026" e o fundamento dentro do preço justo divergiriam na mesma linha — que é
    # o defeito que esta sessão inteira veio corrigir.
    # O lucro de shopping carrega reavaliação de ativo e ganho de venda; o FFO, não. Crescer um
    # e multiplicar o outro pelo múltiplo é misturar duas grandezas.
    if MOTOR.get(t) == 'SHOP':
        gf = _reg_log(serie_ffo(t, A))
        if gf is not None:
            return (max(-CRESC_CAP, min(gf, CRESC_CAP)),
                    'regressão log do FFO da própria série (shopping não projeta lucro contábil)')
    rec = _recorrente(t) if MOTOR.get(t) not in ('FIN', 'NAV', 'CICL') else None
    if rec is not None:
        return max(-CRESC_CAP, min(rec, CRESC_CAP)), 'CAGR do lucro recorrente por regressão log'
    val, _q = anos_validos(A)
    reg = _reg_log([(y, A[y].get('lucrolin')) for y in val])
    roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
    po, _n, _f = payout_final(t, A, H)
    groe = (mediana_com_tendencia(roes, limiar_abs=2.0)[0] * (1 - po)
            if (roes and po is not None and po < 1) else None)
    cands = [x for x in (reg, groe) if x is not None]
    if not cands:
        return None, None
    g = min(cands)
    fonte = ('regressão log do lucro da própria série' if g == reg
             else 'ROE × retenção')
    return max(-CRESC_CAP, min(g, CRESC_CAP)), fonte


def projetar(t, A, valor, H=None):
    """Aplica o crescimento a um fundamento por papel. Devolve (valor projetado, taxa, fonte)."""
    if valor is None:
        return None, None, None
    g, fonte = crescimento(t, A, H)
    if g is None:
        return valor, None, None
    return valor * (1 + g / 100), g, fonte


def teto_ep(t, A, pl_setor=None, com_pares=True):
    """E/P histórico, respeitando quebra de série."""
    c = A[max(A)]
    val, q = anos_validos(A)

    pls = [x for x in (pl_ano(t, A, y) for y in val) if x]
    # LPA de referência: o campo da base, ou derivado do lucro LTM ÷ papéis quando ele falta.
    # A ASAI3 é o caso — a base não traz `lpa` para ela, e sem este fallback a empresa saía
    # sem preço justo por falta de UM campo, tendo lucro e contagem de papéis.
    lpa = c.get('lpa')
    if not lpa or lpa <= 0:
        _l, _p = c.get('lucrolin'), papeis(t, A)
        lpa = (_l / _p) if (_l and _l > 0 and _p) else None
    if not lpa or lpa <= 0: return None
    faixa_mult = None
    if len(pls) >= 3:
        p25, alvo, p75, nfx = faixa_com_tendencia(pls, truncar=False)
        faixa_mult = (p25, p75)
        mediana_propria = alvo
        conv = 3 if len(pls) >= 5 else 2
        nota = (f'P/L: faixa {p25:.1f}x–{p75:.1f}x (mediana {alvo:.1f}x) · {nfx}, '
                f'série de {len(pls)} anos ({min(pls):.1f}x a {max(pls):.1f}x)'
                + (f', restrito a partir de {q} por QUEBRA DE SÉRIE.' if q else '.'))
    elif pl_setor or PL_SETOR.get('_UNIVERSO'):
        # Sem histórico próprio comparável: usa a mediana dos PARES do mesmo motor que NÃO
        # têm quebra; sem pares, a do universo inteiro. Introduz viés de peer comp, e desde
        # 13/09/2026 é o que garante que TODA empresa com lucro positivo tenha preço justo —
        # pedido do usuário: "toda empresa deve ter um preço justo com base no LPA × múltiplo".
        universo = pl_setor is None
        pl_setor = pl_setor or PL_SETOR['_UNIVERSO']
        alvo = pl_setor; conv = 1; mediana_propria = pl_setor; mediana_propria = pl_setor
        nota = (f'⚠️ Só {len(pls)} anos de P/L comparável' + (f' (quebra de série em {q})' if q else ' na base') + ', insuficiente. '
                + (f'O grupo {MOTOR.get(t) or "—"} não tem par com série limpa, então o múltiplo '
                   f'vem do P/L mediano do UNIVERSO ({alvo:.1f}x). ' if universo else
                   f'Ancorado no P/L mediano dos PARES sem quebra ({alvo:.1f}x). ')
                + 'Peer comp tem viés próprio — é a régua do setor, não desta empresa.'
                + (f' O histórico anterior a {q} descreve uma empresa com outra base acionária '
                   f'e NÃO serve de âncora.' if q else ''))
    else:
        return None
    # ⚠️ LPA PROJETADO, não o dos últimos 12 meses. Múltiplo é quanto se paga por um lucro
    # FUTURO; multiplicá-lo pelo lucro que já passou embute a premissa de crescimento zero sem
    # dizer. E a tabela já mostrava o LPA projetado na coluna própria — eram duas contas de LPA
    # na mesma linha, ITUB3 com R$ 4,35 aqui e R$ 5,16 na tela.
    # ⚠️ O LPA PROJETADO SAI DO LUCRO, não do campo `lpa` da base — e é de propósito: é assim
    # que a coluna da tabela o calcula (lucro de 2025 × (1+g) ÷ papéis) e os dois têm que dar o
    # MESMO número. Crescer o campo `lpa` dava R$ 4,80 no ITUB3 contra R$ 5,16 na tela, porque
    # o `lpa` da base (R$ 4,35) não reconcilia com lucro ÷ papeis() (R$ 4,89): a contagem de
    # papéis é ancorada com a regra de ±25% e nem sempre cai no divisor que a fonte usou.
    # Partindo do lucro, a identidade fecha por construção.
    alvo0 = alvo
    alvo, nota_pares, origem_mult = (alvo_com_pares(t, 'E/P', alvo, len(pls), A) if com_pares
                                      else (alvo, '', f'o E/P mediano da própria empresa ({alvo:.2f}x)'))
    if faixa_mult:
        faixa_mult = recentrar(faixa_mult[0], mediana_propria, faixa_mult[1], alvo)
    pap_ep = papeis(t, A)
    decl = LUCRO_2026_DECLARADO.get(t)
    if decl and pap_ep:
        # Lucro de 2026 vindo do relatório: não há projeção a fazer, só dividir por papéis.
        lpa_unit = decl[0] / pap_ep
        g = None
        nota_g = (f' LPA projetado R$ {lpa_unit:.2f} = lucro de 2026 R$ {decl[0]/1e9:.2f} bi '
                  f'DECLARADO ÷ {pap_ep/1e6:.0f} mi papéis. {decl[1]}')
        l25 = decl[0]
    else:
        l25, rot_base = base_projecao(t, A)
    if decl and pap_ep:
        pass
    elif l25 and l25 > 0 and pap_ep:
        base_lpa, g, fonte_g = projetar(t, A, l25, H_GLOBAL)
        lpa_unit = base_lpa / pap_ep
        nota_g = (f' LPA projetado R$ {lpa_unit:.2f} = lucro base R$ {l25/1e9:.2f} bi '
                  f'({rot_base}) × (1{g:+.1f}%) ÷ {pap_ep/1e6:.0f} mi papéis, {fonte_g}.'
                  if g is not None else '')
    else:
        lpa_unit = lpa * FATOR_UNIT.get(t, 1)
        g, nota_g = None, ' ⚠️ Sem lucro de 2025 positivo: usa o LPA dos últimos 12 meses.'
    # `conta` e `origem_mult` existem SÓ para a tooltip do preço justo, e é de propósito que
    # sejam campos e não a string `motor`: o usuário pediu, três vezes, que ali esteja "o
    # racional pra chegar no valor, somente isso". Parsear `motor` com regex para extrair a
    # conta já falhou neste projeto (o vazamento de valor entre tickers do `gCagr`).
    return dict(justo=alvo*lpa_unit, conv=conv, chave='E/P', alvo=alvo0,
        conta=f'LPA projetado 2026 R$ {lpa_unit:.2f} × P/L {alvo:.2f}x',
        origem_mult=origem_mult,
        faixa=((faixa_mult[0]*lpa_unit, faixa_mult[1]*lpa_unit) if faixa_mult else None),
        motor=f'E/P: P/L {nota_pares or f"{alvo:.2f}x"} × LPA projetado R$ {lpa_unit:.2f}',
        nota=nota + nota_g)

# ══════════════════════════════════════════════════════════════════════════════════════════
# DOIS MÉTODOS UNIVERSAIS — para que NENHUMA empresa fique sem ao menos duas leituras
# ══════════════════════════════════════════════════════════════════════════════════════════
# Decisão do usuário, e ela corrige uma postura minha que estava errada: eu tinha passado a
# RECUSAR quando o motor produzia número absurdo. Recusar é honesto sobre a minha incerteza,
# mas é inútil para quem precisa decidir — e o defeito nunca foi "esta empresa não tem valor
# calculável", foi "o método que eu escolhi para ela não serve".
#
# A resposta certa é MAIS métodos, não menos números. Estes dois funcionam onde os outros
# quebram, e servem de validação cruzada para todos:
#
#   P/VP — não depende de lucro. Sobrevive a prejuízo (AURE3, LPA negativo em 3 de 6 anos),
#          a lucro distorcido (ALOS3, reavaliação de ativos) e a ciclo (VALE3). O patrimônio
#          é a linha mais estável do balanço.
#   EV/RECEITA — não depende de lucro NEM de EBITDA. Sobrevive a margem colapsando e a
#          EBITDA volátil (AXIA3 foi de R$26,2 bi para R$8,5 bi e voltou para R$16,3 bi;
#          a receita fez 40,2 → 41,3 → 44,6, tranquila).
#
# Nenhum dos dois é bom SOZINHO: P/VP ignora rentabilidade (patrimônio grande e ROE ruim
# destrói valor) e EV/Receita ignora margem (receita alta com prejuízo não vale nada). Eles
# valem como o 2º e o 3º voto de uma mediana, e é assim que entram.
def papeis(t, A):
    """Quantidade de papéis NEGOCIADOS (units, quando for o caso).

    ⚠️ Por que não é simplesmente `lucro ÷ LPA` do último ano: essa razão EXPLODE quando o
    lucro se aproxima de zero. A KLBN11 tem lucro pequeno e LPA de R$0,09 em 2026 — a divisão
    devolvia uma contagem de papéis absurda e o teto saiu em R$3,46 contra cotação de R$19,40
    (−460%), quando os métodos de múltiplo davam ~R$19. Um erro de contagem, não de valuation.

    Solução: MEDIANA da contagem implícita ao longo dos anos válidos. A quantidade de ações é
    a grandeza mais estável de uma empresa (fora quebra de série, que anos_validos já corta),
    então a mediana é robusta ao ano em que o lucro passou perto de zero.
    """
    val, _q = anos_validos(A)
    ns = []
    for y in val:
        d = A[y]
        if d.get('lucrolin') and d.get('lpa') and d['lpa'] != 0:
            n = abs(d['lucrolin']/d['lpa'])
            if n > 0: ns.append(n)
    if not ns: return None
    # ⚠️ DESDOBRAMENTO/GRUPAMENTO É QUEBRA PARA CONTAGEM, mesmo sendo cosmético para MÚLTIPLO.
    # `anos_validos` mantém a série inteira num split (e faz certo: P/L e P/VP atravessam
    # intactos). Mas a QUANTIDADE DE AÇÕES não atravessa. A SBSP3 fez 5:1 em 2026 e a série de
    # contagem ficou 683 mi · 705 mi · 3.519 mi — a mediana devolvia 705 mi, cinco vezes menos
    # que a real, e o LPA saía cinco vezes maior.
    # Correção: ancora no ANO MAIS RECENTE e só admite na mediana os anos cuja contagem está
    # dentro de ±25% dele. Mantém a robustez contra o ano de lucro perto de zero (que era a
    # razão de existir a mediana) sem misturar bases acionárias diferentes.
    ref = ns[-1]
    prox = [x for x in ns if abs(x/ref - 1) <= 0.25] or [ref]
    return st.median(prox) / FATOR_UNIT.get(t, 1)

def teto_pvp(t, A, com_pares=True):
    val, q = anos_validos(A)
    pv = serie_pvp(t, A, val)
    if len(pv) < 3: return None
    alvo, nota = mediana_com_tendencia(pv, limiar_rel=0.12, truncar=False)
    p25, _p50, p75, _nfx = faixa_com_tendencia(pv, limiar_rel=0.12, truncar=False)
    # ⚠️ UNITS, sétima vez. `vpa()` devolve preço_unit ÷ pvp_reportado, e o pvp do Partnr é
    # preço da UNIT sobre patrimônio por AÇÃO — então vpa() sai POR AÇÃO. Já `alvo` vem de
    # serie_pvp(), que divide pelo fator e portanto é POR UNIT. Multiplicar os dois sem
    # reconciliar erra por um fator inteiro: a KLBN11 dava R$3,96 (= R$19,80 ÷ 5).
    v = vpa(t, A)
    if not v or v <= 0: return None
    alvo0 = alvo
    alvo, nota_pares, origem_mult = (alvo_com_pares(t, 'P/VP', alvo, len(pv), A) if com_pares
                                      else (alvo, '', f'o P/VP mediano da própria empresa ({alvo:.2f}x)'))
    p25, p75 = recentrar(p25, alvo0, p75, alvo)
    return dict(justo=alvo*v, conv=2, chave='P/VP', alvo=alvo0, faixa=(p25*v, p75*v),
        conta=f'VPA R$ {v:.2f} × P/VP {alvo:.2f}x', origem_mult=origem_mult,
        motor=f'P/VP {nota_pares or f"{alvo:.2f}x"} × VPA R$ {v:.2f} por papel',
        nota=f'P/VP-alvo = {nota} de {len(pv)} anos ({min(pv):.2f}x a {max(pv):.2f}x), corrigido para units. '
             f'Não depende de lucro — é o método que sobrevive a prejuízo e a lucro contábil distorcido. '
             f'⚠️ Ignora rentabilidade: patrimônio grande com ROE ruim vale menos que isto sugere.'
             + (f' Restrito a partir de {q} por quebra de série.' if q else ''))

def teto_ev_receita(t, A, com_pares=True):
    val, q = anos_validos(A)
    r = []
    for y in val:
        d = A[y]
        if d.get('evEbitda') and d.get('ebitda') and d.get('receita') and d['receita'] > 0 and d['ebitda'] > 0:
            r.append(d['evEbitda']*d['ebitda']/d['receita'])
    c = A[max(A)]
    if len(r) < 3 or not c.get('receita') or not c.get('lucrolin') or not c.get('lpa') or c['lpa'] == 0:
        return None
    alvo, nota = mediana_com_tendencia(r, limiar_rel=0.15, truncar=False)
    p25, _p50, p75, _nfx = faixa_com_tendencia(r, limiar_rel=0.15, truncar=False)
    pap = papeis(t, A)
    if not pap: return None
    dl = (c.get('divliq') or 0)
    def _justo(mult):
        return (mult*c['receita'] - dl) / pap
    alvo0 = alvo
    alvo, nota_pares, origem_mult = (alvo_com_pares(t, 'EV/Receita', alvo, len(r), A) if com_pares
                                      else (alvo, '', f'o EV/Receita mediano da própria empresa ({alvo:.2f}x)'))
    p25, p75 = recentrar(p25, alvo0, p75, alvo)
    justo = _justo(alvo)
    if justo <= 0: return None
    fx = tuple(sorted((_justo(p25), _justo(p75))))
    return dict(justo=justo, conv=2, chave='EV/Receita', alvo=alvo0,
        faixa=(fx if fx[0] > 0 else None),
        conta=(f'receita R$ {c["receita"]/1e9:.1f} bi × EV/Receita {alvo:.2f}x '
               f'− dívida líquida R$ {dl/1e9:.1f} bi, ÷ {papeis_txt(pap)}'),
        origem_mult=origem_mult,
        motor=f'EV/Receita {nota_pares or f"{alvo:.2f}x"} × receita R$ {c["receita"]/1e9:.1f} bi',
        nota=f'EV/Receita-alvo = {nota} de {len(r)} anos ({min(r):.2f}x a {max(r):.2f}x). '
             f'Não depende de lucro nem de EBITDA — sobrevive a margem colapsando e a EBITDA volátil. '
             f'EV justo − dívida líquida R$ {(c.get("divliq") or 0)/1e9:.1f} bi ÷ {pap/1e6:.0f} mi papéis. '
             f'⚠️ Ignora margem: receita alta com prejuízo não vale o que isto sugere.'
             + (f' Restrito a partir de {q} por quebra de série.' if q else ''))


# ── ÚLTIMO RECURSO: múltiplo dos PARES ───────────────────────────────────────────────────
# AURE3 e ROXO34 ficavam sem nenhum número: a Auren tem quebra operacional em 2025 (aquisição
# que dobrou o EBITDA e somou R$17 bi de dívida) e sobram 2 anos válidos; o ROXO34 tem 1 ano
# de base. Todo método próprio exige 3 anos, e com razão.
#
# Quando a empresa não tem história utilizável, sobra a história dos PARES. É pior — importa
# o viés de quem escolheu a lista de pares, e não conhece as particularidades da empresa —
# mas é melhor que célula vazia, que foi o que o usuário recusou com razão: "toda ação tem
# que ter um jeito de calcular o preço justo".
#
# Entra SÓ quando há menos de 2 métodos próprios, e sempre com ★☆☆.
def ffo_ano(t, A, y):
    """FFO do exercício `y`, em reais TOTAIS (não por papel). None quando falta insumo.

    FFO = lucro líquido + depreciação e amortização, e D&A sai de EBITDA − EBIT porque a base
    não traz a linha separada. É a definição que o motor de shopping usa desde 07/09/2026.

    ⚠️ Esta função existe no nível do MÓDULO desde 13/09/2026, quando o usuário pediu que a
    tabela inteira trocasse lucro líquido por FFO nos shoppings. Antes a conta morava dentro
    de teto_ffo() como função local, e gerar_colunas.py teria que reimplementá-la — que é
    exatamente o padrão de "duas definições do mesmo conceito" que já custou quatro bugs
    neste projeto. Uma definição, dois consumidores.
    """
    d = A.get(y) or {}
    li, eb, ei = d.get('lucrolin'), d.get('ebitda'), d.get('ebit')
    if li is None or eb is None or ei is None:
        return None
    v = li + eb - ei
    return v if v > 0 else None


def serie_ffo(t, A, respeitar_quebra=True):
    """[(ano, FFO)] dos exercícios comparáveis."""
    ys, _q = anos_validos(A) if respeitar_quebra else (sorted(A), None)
    return [(y, f) for y in ys for f in (ffo_ano(t, A, y),) if f]


def teto_ffo(t, A, com_pares=True):
    """P/FFO próprio — o múltiplo certo para shopping.

    POR QUE SHOPPING NÃO PODE USAR E/P NEM P/VP, e a própria metodologia já dizia isso antes
    de o motor obedecer: a contabilidade carrega o imóvel a CUSTO HISTÓRICO e o deprecia como
    se ele virasse pó em algumas décadas. Shopping bem administrado não perde valor — ganha.
    Essa depreciação é despesa que não sai caixa nenhum, e ela derruba as duas pontas ao mesmo
    tempo: o LUCRO (denominador do E/P) e o PATRIMÔNIO (denominador do P/VP). Na ALOS3 são
    R$ 630 mi por ano, 29% do EBITDA — o lucro aparece como R$ 1,03 bi quando a operação gera
    R$ 1,66 bi de caixa.

    FFO = lucro líquido + depreciação e amortização. É o padrão do setor por esse motivo.
    ⚠️ PROXY, declarado: o FFO oficial (NAREIT/ABRASCE) também tira ganho de venda de ativo e
    ajuste a valor justo, que a base não separa. Por isso ele diverge do FFO que a companhia
    reporta — na ALOS3, R$ 1,66 bi aqui contra R$ 1,36 bi no release.

    ⚠️ E por isso o P/FFO NÃO é comparável ENTRE empresas: MULT3 e IGTI11 usam valor justo e
    quase não depreciam (6% e 11% do EBITDA contra 29% da ALOS3), então "lucro + D&A" mede
    coisas diferentes em cada uma. Trocar lucro reportado por recorrente inverte quem está
    mais barata. Aqui ele é usado só contra a PRÓPRIA série da empresa, que é onde a definição
    se mantém constante.
    """
    val, q = anos_validos(A)
    fator = FATOR_UNIT.get(t, 1)

    def _ffo_pap(y):
        # FFO POR PAPEL. Os papéis saem de lucro ÷ LPA (implícitos, da mesma fonte do LPA)
        # para que numerador e denominador venham do mesmo lugar — ver a nota de units.
        d = A[y]
        li, lpa = d.get('lucrolin'), d.get('lpa')
        f = ffo_ano(t, A, y)
        if not f or not li or not lpa or lpa == 0 or li <= 0:
            return None
        return f / (li / lpa) * fator

    pfs = []
    for y in val:
        f, pr = _ffo_pap(y), A[y].get('preco')
        if f and pr:
            pfs.append(pr / f)
    # ⚠️ O FFO POR PAPEL DO ANO CORRENTE USA papeis(), não a contagem implícita. A série
    # histórica continua na contagem implícita de cada ano (é o certo: o múltiplo de 2022 tem
    # que ser medido com os papéis de 2022), mas o número que vai ser MULTIPLICADO pelo
    # múltiplo precisa ser o mesmo que a coluna da tabela exibe — senão ALOS3 mostra FFO/ação
    # de R$ 3,37 na tela e o preço justo usa R$ 3,54. Mesma convenção do teto_ep, que também
    # projeta o LPA sobre papeis().
    pap_ffo = papeis(t, A)
    # ANO-BASE 2025, igual ao resto da tabela. Usar o LTM aqui fazia a coluna "FFO projetado
    # 2026" mostrar R$ 3,37 na ALOS3 enquanto o preço justo multiplicava R$ 3,54 — o mesmo
    # conceito com dois números na mesma linha.
    f_hoje = ffo_ano(t, A, 2025) or ffo_ano(t, A, max(A))
    atual = (f_hoje / pap_ffo * fator) if (f_hoje and pap_ffo) else _ffo_pap(max(A))
    if len(pfs) < 3 or not atual:
        return None
    p25, alvo, p75, nfx = faixa_com_tendencia(pfs, limiar_rel=0.15, truncar=False)
    alvo0 = alvo
    alvo, nota_pares, origem_mult = (alvo_com_pares(t, 'P/FFO', alvo, len(pfs), A) if com_pares
                                      else (alvo, '', f'o P/FFO mediano da própria empresa ({alvo:.2f}x)'))
    p25, p75 = recentrar(p25, alvo0, p75, alvo)
    atual0 = atual
    atual, g, fonte_g = projetar(t, A, atual0, H_GLOBAL)   # mesmo motivo do E/P
    if g is not None:
        nfx += f' · FFO/papel projetado R$ {atual:.2f} = R$ {atual0:.2f} × (1{g:+.1f}%), {fonte_g}'
    return dict(justo=alvo * atual, conv=2, chave='P/FFO', alvo=alvo0,
        faixa=(p25 * atual, p75 * atual),
        conta=f'FFO por papel projetado R$ {atual:.2f} × P/FFO {alvo:.2f}x',
        origem_mult=origem_mult,
        motor=f'P/FFO {nota_pares or f"{alvo:.2f}x"} × FFO/papel projetado R$ {atual:.2f}',
        nota=f'P/FFO-alvo = {nfx}, série de {len(pfs)} anos ({min(pfs):.1f}x a {max(pfs):.1f}x). '
             f'FFO = lucro líquido + depreciação — devolve a despesa que não sai caixa e que a '
             f'contabilidade cobra do imóvel como se ele se desgastasse. '
             f'⚠️ PROXY: o FFO oficial também exclui ganho de venda de ativo e ajuste a valor '
             f'justo, que a base não separa. ⚠️ NÃO comparar com o P/FFO de outra operadora: '
             f'quem usa valor justo quase não deprecia e o mesmo cálculo mede outra coisa.'
             + (f' Restrito a partir de {q} por quebra de série.' if q else ''))


def teto_setorial(t, A, H, campo=None):
    """campo=None tenta EV/EBITDA e cai para P/VP quando o EV não cobre a dívida.

    A AURE3 é o caso: dívida líquida de R$20,0 bi contra EBITDA de R$3,2 bi (6,3x, herança da
    aquisição de 2024). No múltiplo dos pares o valor de firma não cobre a dívida e o valor do
    equity dá NEGATIVO — o que é uma informação real sobre a empresa, não uma falha de conta,
    mas não é exibível como preço. Nesses casos vale o patrimônio: o P/VP dos pares sobre o
    VPA dela ainda é positivo e diz quanto o mercado paga pelo capital que sobra."""
    m = MOTOR.get(t)
    c = A[max(A)]
    if campo is None:
        campo = 'pvp' if m in ('FIN', 'NAV') else 'evEbitda'
    pares = []
    for p, B in H.items():
        if p == t or MOTOR.get(p) != m: continue
        val, _ = anos_validos(B)
        if len(val) < 4: continue
        s = serie_pvp(p, B, val) if campo == 'pvp' else [B[y][campo] for y in val if B[y].get(campo) and B[y][campo] > 0]
        if len(s) >= 4: pares.append(st.median(s))
    if len(pares) < 2: return None
    alvo = st.median(pares)
    # A faixa do peer comp é a DISPERSÃO ENTRE OS PARES: mínimo e máximo do múltiplo de cada
    # um. Não é a oscilação histórica de ninguém — é o desacordo do setor sobre quanto vale
    # este tipo de negócio hoje. Sem ela, quem cai no último recurso (AURE3) saía também sem
    # teto de compra, agora que um método decide sozinho.
    lo_m, hi_m = min(pares), max(pares)
    if campo == 'pvp':
        v = vpa(t, A)
        if not v or v <= 0: return None
        justo = alvo * v
        fx = (lo_m*v, hi_m*v)
        desc = f'P/VP mediano dos pares {alvo:.2f}x × VPA R$ {v:.2f}'
        conta = f'VPA R$ {v:.2f} × P/VP {alvo:.2f}x'
    else:
        eb = c.get('ebitda'); pap = papeis(t, A)
        if not eb or eb <= 0 or not pap: return None
        dl = (c.get('divliq') or 0)
        justo = (alvo*eb - dl) / pap
        fx = ((lo_m*eb - dl)/pap, (hi_m*eb - dl)/pap)
        desc = f'EV/EBITDA mediano dos pares {alvo:.2f}x × EBITDA R$ {eb/1e9:.1f} bi'
        conta = (f'EBITDA R$ {eb/1e9:.1f} bi × EV/EBITDA {alvo:.2f}x − dívida líquida '
                 f'R$ {dl/1e9:.1f} bi, ÷ {papeis_txt(pap)}')
    if justo <= 0:
        # EV não cobre a dívida: o equity dá NEGATIVO. Informação real sobre a empresa, não
        # falha de conta — mas não é exibível como preço. Cai para o patrimônio.
        r = teto_setorial(t, A, H, 'pvp') if campo != 'pvp' else None
        if r:
            r['nota'] = (f'⚠️ POR QUE P/VP E NÃO LPA × MÚLTIPLO: a empresa dá PREJUÍZO, então '
                         f'P/L não existe — múltiplo sobre lucro negativo não é múltiplo. E o '
                         f'EV/EBITDA dos pares ({alvo:.2f}x) sobre o EBITDA de '
                         f'R$ {(c.get("ebitda") or 0)/1e9:.1f} bi não cobre a dívida líquida de '
                         f'R$ {(c.get("divliq") or 0)/1e9:.1f} bi: o valor do equity sai '
                         f'NEGATIVO (R$ {justo:.2f}), que é informação real sobre a alavancagem '
                         f'e não é exibível como preço. Sobra o patrimônio. || ' + r['nota'])
        return r
    if not (fx[0] and fx[0] > 0 and fx[1] > fx[0]):
        fx = None
    return dict(justo=justo, conv=1, chave='Pares', faixa=fx,
        motor=desc, conta=conta,
        origem_mult=(f'o múltiplo mediano dos {len(pares)} pares do grupo {m} ({alvo:.2f}x) — '
                     f'a própria empresa não tem série utilizável'),
        nota=(f'⚠️ ÚLTIMO RECURSO — a própria empresa não tem série utilizável (quebra recente '
              f'ou histórico curto demais), então o múltiplo vem dos {len(pares)} pares do grupo '
              f'{m} com pelo menos 4 anos limpos (faixa {lo_m:.2f}x a {hi_m:.2f}x = desacordo '
              f'entre os pares, não oscilação histórica desta empresa). '
              f'Peer comp carrega o viés de quem montou a lista '
              f'e ignora o que esta empresa tem de diferente. Convicção ★☆☆ obrigatória.'))


# ── HOLDING: paridade histórica com a investida principal ────────────────────────────────
# ITSA4 e BRAP4 estavam com teto MANUAL — herdados de análises antigas, sem régua comum. O
# motivo declarado era que "NAV exige o valor de mercado das investidas", que a base não traz.
# Traz, sim, para estes dois casos: a investida principal está no MESMO Radar.
#
#   ITSA4 → ITUB3 (o Itaú é a esmagadora maioria do NAV da Itaúsa)
#   BRAP4 → VALE3 (a Bradespar é, na prática, um veículo de participação na Vale)
#
# COMO FUNCIONA — a razão `preço da holding ÷ preço da investida` é o desconto de holding
# medido pelo próprio mercado, ano a ano, sem eu precisar estimar NAV nenhum:
#
#   ITSA4/ITUB3: 0,468 · 0,389 · 0,360 · 0,328 · 0,321 · 0,318   ← desconto ABRINDO
#   BRAP4/VALE3: 0,321 · 0,334 · 0,332 · 0,304 · 0,277 · 0,285   ← estável
#
# O alvo é essa razão (com mediana_com_tendencia, porque a da Itaúsa tem tendência clara), e
# ela multiplica o PREÇO JUSTO da investida calculado pelo próprio motor — não o preço de
# mercado dela. Assim a holding herda a avaliação fundamentalista da controlada, descontada
# pelo desconto de holding que o mercado historicamente pratica.
#
# ⚠️ LIMITE HONESTO: isto NÃO é um NAV. Não enxerga os outros ativos (Alpargatas, Dexco, NTS
# e Copa na Itaúsa), não enxerga a dívida da holding, e não sabe dizer se o par inteiro está
# caro — se o motor errar no ITUB3, erra na ITSA4 junto, na mesma direção. Por isso a
# convicção é limitada a ★★☆, nunca ★★★, por mais estável que a razão seja.
PARENT = {'ITSA4': 'ITUB3', 'BRAP4': 'VALE3'}

def teto_nav(t, A, H, justo_pai):
    pai = PARENT.get(t)
    if not pai or not justo_pai or pai not in H:
        return None
    B = H[pai]
    val, q = anos_validos(A)
    raz = [A[y]['preco']/B[y]['preco'] for y in val
           if y in B and A[y].get('preco') and B[y].get('preco') and B[y]['preco'] > 0]
    if len(raz) < 4:
        return None
    alvo, nota_alvo = mediana_com_tendencia(raz, limiar_rel=0.10)
    # Faixa = p25-p75 do DESCONTO DE HOLDING praticado pelo mercado. Mesmo motivo de teto_ev:
    # o método decide sozinho nas holdings desde 13/09/2026, então precisa da própria faixa.
    # Sem ela, ITSA4 e BRAP4 saíam com o teto de compra suprimido.
    p25, _p50, p75, nota_fx = faixa_com_tendencia(raz, limiar_rel=0.10)
    disp = (max(raz) - min(raz)) / max(raz)
    conv = 2 if disp < 0.30 else 1          # teto de ★★☆: ver limite honesto acima
    return dict(justo=alvo*justo_pai, conv=conv, chave='Paridade',
        faixa=((p25*justo_pai, p75*justo_pai) if p75 > p25 else None),
        conta=f'preço justo de {pai} R$ {justo_pai:.2f} × paridade {alvo:.3f}',
        origem_mult=(f'a razão entre o preço de {t} e o de {pai} ao longo de {len(raz)} anos '
                     f'({alvo:.3f}) — o desconto de holding que o mercado pratica'),
        motor=f'Paridade com {pai}: {alvo:.3f}× o preço justo de {pai} (R$ {justo_pai:.2f})',
        nota=(f'Razão preço {t} ÷ preço {pai} = {nota_alvo} de {len(raz)} anos '
              f'({min(raz):.3f} a {max(raz):.3f}, dispersão {disp*100:.0f}%; faixa '
              f'{p25:.3f} a {p75:.3f}, {nota_fx}). É o desconto de '
              f'holding medido pelo próprio mercado, não um NAV estimado por mim. '
              f'⚠️ NÃO enxerga os demais ativos da holding nem a dívida dela, e não sabe dizer '
              f'se o par inteiro está caro: se o motor errar em {pai}, erra aqui junto. '
              f'Convicção limitada a ★★☆ por isso.'))


# ── TRAVA DE SANIDADE: o motor tem o direito de dizer "NÃO SEI" ──────────────────────────
# Camada 2 da correção de 06/09/2026, pedida pelo usuário depois de perguntar se o preço-teto
# era confiável. A resposta honesta era: 7 de 25 sim, 12 não, e 5 desses eu chamo de errados.
#
# O problema não é o motor errar — é ele errar com CARA DE OPINIÃO. Uma margem de −202% na
# CLSC4 não significa "a Celesc está 3x cara"; significa que o motor não descreve a Celesc.
# Enquanto as duas mensagens saem no mesmo formato (um número em reais, com tooltip e
# convicção), o leitor não tem como distinguir análise de falha.
#
# Regra: margem além de ±LIM_MARGEM não vira teto. Vira recusa, com o motivo escrito.
# É a mesma regra que o resto do projeto já segue — "célula vazia é melhor que número errado" —
# e que só o preço-teto não obedecia.
#
# ⚠️ O limite é ARBITRÁRIO e eu o declaro como tal: 100% de margem significa que o motor acha
# que o papel vale metade (ou o dobro) do que o mercado paga. Divergências dessa ordem existem
# de verdade, mas com 6 anos de série e um Ke estimado eu não tenho como distinguir uma
# convicção contrária ao mercado de um motor quebrado — e, nas 5 vezes em que isso aconteceu
# neste projeto, era motor quebrado nas 5.
LIM_MARGEM = 1.00
H_GLOBAL = None   # preenchido no __main__; o motor NAV precisa ler a investida

# ── QUANDO A FAIXA NÃO PODE VIRAR TETO DE COMPRA (13/09/2026) ───────────────────────────
# A faixa substituiu a convicção em estrelas, e com isso ganhou a obrigação que a estrela
# tinha e não cumpria: dizer quando o motor NÃO sabe. Duas situações, ambas descobertas ao
# rodar a versão nova e olhar os extremos em vez de aceitar o número:
#
#  · FAIXA LARGA DEMAIS — o IRBR3 saiu com faixa de R$24,25 a R$55,79 (57% de largura, E/P
#    contra P/VP) e teto de compra de R$24,25 contra cotação de R$56,78: margem de −134%.
#    Com os métodos discordando tanto, o limite inferior não é "estimativa conservadora de
#    valor", é só a saída do método mais pessimista. Publicar isso como teto é dar precisão
#    a um desacordo.
#  · MÉTODO ÚNICO SEM FAIXA — o SAUD3 ficou com E/P de peer comp, ponto único, margem de
#    −357%. Pior: a metodologia já registra (seção sobre MOTOR) que o histórico pré-2026 é da
#    ODONTOPREV, empresa diferente — nenhum múltiplo daquela série ancora esta. A trava que
#    protegia esse caso vivia dentro do `teto_fin`, e eu a removi junto com o Ke sem notar.
#
# Nos dois casos a FAIXA continua sendo exibida: ela é informação sobre a empresa. O que
# desaparece é o TETO DE COMPRA, porque um número de compra exige confiança que aqui não
# existe. É o mesmo princípio do SEM_TETO do ROXO34 — recusa declarada em vez de número que
# parece resposta.
LIM_LARGURA = 0.50

def _sanidade(t, r, cot):
    """Devolve r, ou None quando a margem é grande demais para ser afirmação."""
    if not r or not cot or not r.get('justo'):
        return r
    larg = r.get('largura')
    # ⚠️ 13/09/2026 — esta trava era UMA e passou a ser DUAS, porque `largura` mudou de
    # significado quando o preço justo virou método único. Antes ela media o DESACORDO ENTRE
    # MÉTODOS (E/P dizendo R$20 e P/VP dizendo R$50); agora mede a OSCILAÇÃO HISTÓRICA de um
    # múltiplo só. São incertezas de naturezas diferentes e merecem respostas diferentes:
    #
    #  · SEM FAIXA NENHUMA (largura 0) — a série tem menos de 3 anos utilizáveis. Não é
    #    "o múltiplo é estável", é "não há múltiplo". Um ponto não é preço justo, e publicar
    #    o AXIA3 a R$22,33 contra cotação de R$55,52 seria dar cara de opinião a n=2.
    #    → RECUSA: a linha sai sem preço justo, com o motivo escrito.
    #  · FAIXA LARGA (acima de LIM_LARGURA) — a série existe e é volátil. É o retrato honesto
    #    de uma cíclica: o EV/EBITDA da VALE3 foi de 2,6x a 6,0x ao longo do ciclo. A mediana
    #    continua sendo a melhor estimativa única e FICA na tabela; o que não se sustenta é
    #    transformar o limite inferior de uma faixa dessas em preço de entrada.
    #    → mantém o preço justo, suprime só o TETO DE COMPRA.
    if larg is not None and larg == 0 and not (r.get('faixa') and r['faixa'][1] > r['faixa'][0]):
        # ⚠️ ISTO RECUSAVA O PREÇO JUSTO até 13/09/2026 (AXIA3, PASS3, SAUD3). Passou a só
        # AVISAR, pela mesma decisão do usuário que derrubou o SEM_TETO: sem série própria não
        # há faixa, mas há múltiplo dos pares e há lucro. A faixa vira ponto único e o TETO DE
        # COMPRA continua suprimido — não dá para derivar preço de entrada de uma amostra que
        # não tem dispersão. O preço justo fica, com a ressalva escrita.
        return {**r, 'teto_suprimido': True,
                'nota': ('⚠️ SEM FAIXA — o método que decide esta linha rodou sobre menos de 3 '
                         'exercícios comparáveis, então não há amplitude histórica: o número é '
                         'um ponto, não uma faixa. Sem teto de compra por isso. Trate como '
                         'marcador, não como preço de entrada. || ' + (r.get('nota') or ''))}
    if larg is not None and larg > LIM_LARGURA:
        return {**r, 'teto_suprimido': True,
                'nota': (f'⛔ SEM TETO DE COMPRA — o múltiplo oscilou {larg*100:.0f}% ao longo da '
                         f"série (faixa de R$ {r['faixa'][0]:.2f} a R$ {r['faixa'][1]:.2f}). O preço "
                         f'justo continua valendo — é a mediana do múltiplo, a melhor estimativa '
                         f'única —, mas o limite inferior de uma faixa tão larga é o ano mais '
                         f'pessimista da série, não uma estimativa conservadora de valor. '
                         f'Dar um preço de entrada aqui seria emprestar precisão à volatilidade. '
                         + '|| ' + r['nota'])}
    # O teto é o LIMITE INFERIOR DA FAIXA desde 13/09/2026 — não mais justo × (1 − margem por
    # convicção). A margem fixa por estrela dava falsa precisão e a estrela não media confiança
    # (ver faixa_com_tendencia). Quem não tem faixa (método único sem série) cai no justo.
    fx = r.get('faixa')
    teto = fx[0] if (fx and fx[0] and fx[0] > 0) else r['justo']
    if teto <= 0:
        return r
    # Mesma convenção da coluna do Radar: margem de segurança = (teto − cotação) ÷ teto.
    # A primeira versão dividia pela cotação e a trava nunca disparava — dividir pelo preço
    # limita a margem negativa a −100% por construção, e o SBSP3 (−512% na régua certa)
    # aparecia como −84% e passava.
    marg = (teto - cot) / teto
    if abs(marg) <= LIM_MARGEM:
        return r
    lado = 'ACIMA' if marg > 0 else 'ABAIXO'
    # NÃO recusa mais (decisão do usuário, 06/09/2026): marca e rebaixa a convicção, mas
    # entrega o número. Ver _calcular_bruto — com consenso de vários métodos, margem extrema
    # passou a ser informação sobre a empresa, não sintoma de motor único quebrado.
    return {**r,
        'nota': r['nota'] + f' ⚠️ MARGEM EXTREMA: o teto fica {abs(marg)*100:.0f}% {lado} da cotação. '
             f'Convicção forçada a ★☆☆. Isto pode significar que o mercado discorda muito do '
             f'histórico da empresa — ou que os métodos ainda não descrevem bem este caso.'}
    return dict(justo=None, conv=0, recusa=True,
        motor='SEM PREÇO JUSTO — o motor não descreve esta empresa',
        nota=(f'RECUSADO: o teto calculado (R$ {teto:.2f}) fica {abs(marg)*100:.0f}% {lado} da '
              f'cotação de R$ {cot:.2f}. Além de {LIM_MARGEM*100:.0f}% eu não consigo distinguir '
              f'"o mercado está errado" de "o meu motor está errado" — e nas 5 vezes em que isso '
              f'aconteceu neste projeto, era o motor. Motivo provável nesta linha: série curta, '
              f'quebra societária recente ou re-rating estrutural que a mediana histórica não '
              f'acompanha. O que existe de real sobre a empresa continua nas outras colunas '
              f'(L/P, ROE, dívida, crescimento) — só o teto foi suprimido.'))

# ── SEM-TETO DECLARADO — item #3 do punch-list de 06/09/2026 ("ROXO34: motor decente ou
# recusa declarada") ──────────────────────────────────────────────────────────────────────
# ROXO34 continuava com margem de -122% mesmo depois da arquitetura de consenso: não porque
# os três métodos do motor FIN discordassem entre si (a nota dizia "dispersão pela concordância
# entre eles"), mas porque Gordon, lucro residual e múltiplo próprio (P/VP-alvo) rodam todos
# sobre EXATAMENTE UM ano de dado — 2025, o único que existe na base para este ticker. A Nu
# Holdings é BDR de empresa estrangeira (Nu Holdings Ltd, NYSE, sede nas Cayman), fora da
# cobertura B3/CVM do MCP Partnr; ROE 33% e P/VP 5,06x vêm de um release lido à mão (ver
# data/historico.data.js), sem série para saber se são o padrão da empresa ou um ano atípico.
# Rodar um "consenso de 3 métodos" sobre n=1 fabrica validação cruzada aparente: os três
# concordam porque vêm da MESMA fonte única, não porque fontes independentes bateram — é
# exatamente o requisito que este motor cobra de toda outra empresa da base (2+ anos válidos,
# ou peer fallback) e que aqui não existe como cumprir.
#
# Não é "achar um motor melhor" — não há segunda fonte para checar a primeira. É recusa
# declarada: sem preço-teto, com o motivo escrito, em vez de um número de aparência precisa
# sobre dado insuficiente. As outras colunas (payout, TIR, ROE, P/VP) continuam calculadas —
# só o teto, que depende de extrapolar 10 anos a partir de um ponto, foi suprimido.
SEM_TETO = {
    'ROXO34': ('BDR de empresa estrangeira (Nu Holdings, NYSE/Cayman), fora da cobertura B3/CVM '
               'do MCP Partnr. A base tem exatamente 1 ano de dado (2025, lido à mão de release), '
               'sem série para separar padrão de ano atípico. Gordon, lucro residual e múltiplo '
               'próprio rodariam todos sobre esse único ponto — "consenso de métodos" seria '
               'validação cruzada aparente, não real: os três concordariam porque vêm da mesma '
               'fonte única. Sem segunda fonte independente, não há preço justo defensável. '
               'Payout, TIR real e as demais colunas continuam calculados normalmente.'),
    # ── Adicionadas em 13/09/2026 ────────────────────────────────────────────────────────
    # Caso DIFERENTE do ROXO34 e pelo mesmo motivo de fundo: falta de dado, não falha de
    # motor. Aqui não é a empresa que está fora da cobertura — é a CHAVE DE API desta sessão
    # que não tem escopo para cotação histórica (@quotes/post/eod) nem para valuation ratios
    # anuais. Sem preço por exercício não existe P/L nem P/VP histórico, e todo método do
    # motor (E/P histórico, EV/EBITDA meio-de-ciclo, P/VP-alvo, Gordon) ancora em múltiplo da
    # própria série. Rodar qualquer um deles sobre o único ano com preço seria o erro do
    # ROXO34 outra vez, agora sabendo. Sai "—" com o motivo na tooltip; L/P, DY, margem e
    # alavancagem continuam calculados normalmente — é o que ordena a fila desde 13/09/2026.
    'VIVA3': ('Série sem preço histórico: a chave de API do MCP Partnr desta sessão não tem '
              'escopo de cotação histórica nem de valuation ratios anuais, então não há P/L '
              'nem P/VP por exercício para ancorar múltiplo da própria série. A DRE de '
              '2021-2025 está completa e auditável (receita, lucro, EBITDA, margens, LPA) — '
              'o que falta é só o lado do PREÇO. Assim que a série de cotação entrar, esta '
              'linha passa a ter preço justo sem mudar mais nada.'),
    'ASAI3': ('Mesma falta de preço histórico da VIVA3, e ainda menos série: a DRE anual '
              'recente não voltou da API (só 2019-2020, anteriores ao spin-off do GPA, com '
              'base de ações incomparável — LPA de R$5,80 em 2020 contra R$0,71 no LTM). '
              'Restam margem líquida e dív.líq/EBITDA por exercício. A margem caindo de '
              '3,84% (2021) para 0,64% (2025) é informação real e está na tabela; preço justo, não.'),
}

def calcular(t, A):
    r = _sanidade(t, _calcular_bruto(t, A, H_GLOBAL), (A[max(A)] or {}).get('preco'))
    # ⚠️ SEM_TETO DEIXOU DE RECUSAR em 13/09/2026. O usuário: "para as empresas que não têm
    # preço justo, preencher — toda empresa deve ter um preço justo com base no LPA × múltiplo".
    #
    # A recusa declarada existia porque essas empresas não têm SÉRIE DE PREÇO própria (VIVA3,
    # ASAI3) ou têm um ano só de dado (ROXO34), e sem série não há múltiplo PRÓPRIO. Só que o
    # múltiplo não precisa ser próprio: o dos pares serve, e o lucro delas é real e auditável.
    # O que a série curta tira é a possibilidade de dizer "esta empresa costuma negociar a X" —
    # e isso vira ressalva na nota, não ausência de número.
    if t in SEM_TETO and r and r.get('justo'):
        r = {**r, 'nota': (f'⚠️ SÉRIE PRÓPRIA INSUFICIENTE — o múltiplo NÃO é o histórico desta '
                           f'empresa, é o dos pares. {SEM_TETO[t]} || ') + r['nota']}
    elif t in SEM_TETO:
        return dict(justo=None, conv=0, recusa=True,
            motor='SEM PREÇO JUSTO — sem lucro nem múltiplo aplicável',
            nota=f'RECUSA DECLARADA: {SEM_TETO[t]}')
    return r

def _calcular_bruto(t, A, H=None):
    """UM MÚLTIPLO, NÃO UMA MEDIANA DE VÁRIOS.

    ══ A mudança de 13/09/2026, pedida pelo usuário ══
    "O preço justo ainda não está LPA × múltiplo que a empresa deve ser negociada. Está a
    mediana de um monte de critérios que não acho justo. Deve ser LPA projetado × múltiplo
    que a empresa deve ser negociada com base no seu histórico e de seus pares."

    Ele está certo, e o defeito da versão anterior era conceitual, não numérico. Rodar E/P,
    P/VP, EV/Receita e EV/EBITDA e tirar a mediana responde a uma pergunta que ninguém fez —
    "qual o número do meio entre quatro réguas diferentes?" — e o resultado não é defensável
    em uma frase. A ALOS3 saía por R$21,42 sem que fosse possível dizer POR QUE: era o meio
    de P/FFO R$26,74 e EV/Receita R$32,60 e mais dois. O relatório dela dizia R$29,50 usando
    o que qualquer analista usa — FFO projetado × P/FFO que o setor pratica — e era o número
    que fazia sentido.

    Agora cada empresa tem UM método que DECIDE, escolhido pelo que o negócio é:

      SHOP  → P/FFO      · o imóvel entra a custo e é depreciado; lucro e patrimônio mentem
      NAV   → Paridade   · holding vale o que a investida vale, com o desconto que o mercado pratica
      CICL  → EV/EBITDA  · sobre a MÉDIA do ciclo; o lucro de um ano é fundo ou pico, nunca normal
      resto → P/L        · LPA PROJETADO × múltiplo-alvo (própria história + pares)

    Os outros métodos continuam sendo calculados e aparecem na tooltip como VERIFICAÇÃO —
    se discordarem muito, isso é informação sobre a empresa —, mas não entram na conta.

    A FAIXA passa a ser a do próprio método: percentil 25 a 75 do múltiplo ao longo da série.
    Antes era "do mais pessimista ao mais otimista entre métodos", que media desacordo entre
    réguas; agora mede a OSCILAÇÃO HISTÓRICA da régua escolhida, que é a incerteza real.

    ⚠️ ONDE ISTO É PIOR QUE A MEDIANA, e o usuário precisa saber:
      · CÍCLICA NO FUNDO — o EV/EBITDA médio protege, mas se a série de EBITDA for curta o
        método se recusa e a linha fica sem preço justo, onde antes três métodos fracos
        produziam um número qualquer.
      · PREJUÍZO ou LPA perto de zero — P/L não existe com lucro negativo. A empresa cai no
        encadeamento abaixo e, se nada responder, sai sem número. É o preço de ter um método
        com significado: ele pode dizer "não se aplica", e a mediana nunca dizia.
    """
    m = MOTOR.get(t)

    def _nav():
        if not H: return None
        pai = PARENT.get(t)
        rp = _calcular_bruto(pai, H[pai], H) if pai and pai in H else None
        return teto_nav(t, A, H, rp['justo'] if rp and rp.get('justo') else None)

    # ── O ENCADEAMENTO, por grupo ────────────────────────────────────────────────────────
    # O PRIMEIRO que produzir número é o método que decide. Os demais viram verificação.
    # A ordem não é preferência estética: é o que descreve o negócio, do mais específico ao
    # mais genérico. Existe justamente porque um método com significado pode se recusar —
    # P/L não existe com prejuízo, P/FFO não existe sem D&A na base.
    if m == 'SHOP':
        ordem = [('P/FFO', lambda: teto_ffo(t, A)),
                 ('EV/Receita', lambda: teto_ev_receita(t, A)),
                 ('P/L', lambda: teto_ep(t, A, pl_setor=PL_SETOR.get(m)))]
    elif m == 'NAV':
        ordem = [('Paridade', _nav), ('P/VP', lambda: teto_pvp(t, A))]
    elif m == 'CICL':
        ordem = [('EV/EBITDA', lambda: teto_ev(t, A, True)),
                 ('EV/Receita', lambda: teto_ev_receita(t, A)),
                 ('P/VP', lambda: teto_pvp(t, A))]
    elif m == 'FIN':
        ordem = [('P/L', lambda: teto_ep(t, A, pl_setor=PL_SETOR.get(m))),
                 ('P/VP', lambda: teto_pvp(t, A))]
    elif m in ('UTIL', 'VAREJO'):
        ordem = [('P/L', lambda: teto_ep(t, A, pl_setor=PL_SETOR.get(m))),
                 ('EV/EBITDA', lambda: teto_ev(t, A, False)),
                 ('EV/Receita', lambda: teto_ev_receita(t, A))]
    else:
        ordem = [('P/L', lambda: teto_ep(t, A, pl_setor=PL_SETOR.get(m))),
                 ('EV/Receita', lambda: teto_ev_receita(t, A)),
                 ('P/VP', lambda: teto_pvp(t, A))]

    principal, escolhido, posicao, verif = None, None, 0, []
    for i, (nome, f) in enumerate(ordem):
        try:
            r = f()
        except Exception:
            r = None
        if not (r and r.get('justo') and r['justo'] > 0):
            continue
        if principal is None:
            principal, escolhido, posicao = r, nome, i
        else:
            verif.append(r)

    # ÚLTIMO RECURSO — peer comp puro, quando a empresa não tem série própria para múltiplo
    # nenhum. Continua sendo um método só, não uma mediana.
    if principal is None and H:
        r = teto_setorial(t, A, H)
        if r and r.get('justo') and r['justo'] > 0:
            principal, escolhido, posicao = r, 'Pares', 99
    if principal is None:
        return None

    # ── VERIFICAÇÃO — calculada, mostrada, sem voto ──────────────────────────────────────
    # Tudo que não entrou no encadeamento do grupo. Nunca muda o preço justo; existe para a
    # tooltip poder dizer "a outra régua daria R$X" quando as duas discordam.
    ja = {id(principal)} | {id(x) for x in verif}
    for f in (lambda: teto_ep(t, A, pl_setor=PL_SETOR.get(m)), lambda: teto_pvp(t, A),
              lambda: teto_ev_receita(t, A), lambda: teto_ev(t, A, m == 'CICL'),
              lambda: teto_ffo(t, A)):
        try:
            r = f()
        except Exception:
            r = None
        if r and r.get('justo') and r['justo'] > 0 and id(r) not in ja \
           and not any(x.get('chave') == r.get('chave') for x in verif) \
           and r.get('chave') != principal.get('chave'):
            verif.append(r)

    justo = principal['justo']
    fx = principal.get('faixa')
    if fx and fx[0] and fx[1] and fx[0] > 0:
        faixa_lo, faixa_hi = fx
    else:
        faixa_lo = faixa_hi = justo
    largura = (faixa_hi - faixa_lo) / faixa_hi if faixa_hi > 0 else 1.0

    # A ARITMÉTICA, campo a campo: o que DECIDE vem primeiro e marcado.
    detalhe = ([dict(chave=escolhido, justo=round(justo, 2), papel='principal',
                     conta=principal.get('conta') or principal.get('motor', ''),
                     origemMult=principal.get('origem_mult', ''),
                     faixa=[round(faixa_lo, 2), round(faixa_hi, 2)])]
               + [dict(chave=x.get('chave') or '—', justo=round(x['justo'], 2),
                       papel='verificação', conta=x.get('conta') or x.get('motor', ''),
                       faixa=([round(v, 2) for v in x['faixa']]
                              if (x.get('faixa') and x['faixa'][0] and x['faixa'][1]) else None))
                  for x in sorted(verif, key=lambda z: z['justo'])])

    fora = [x for x in verif
            if x['justo'] and not (faixa_lo <= x['justo'] <= faixa_hi)]
    nota_verif = ''
    if verif:
        nota_verif = (' || VERIFICAÇÃO (não entra na conta): '
                      + ' · '.join(f"{x.get('chave')} R$ {x['justo']:.2f}" for x in
                                   sorted(verif, key=lambda z: z['justo']))
                      + ('. Todas dentro da faixa. ' if not fora else
                         f". {len(fora)} fora da faixa — as réguas discordam, olhe a empresa. "))
    nota_fb = ''
    if posicao > 0:
        nota_fb = (f'⚠️ O método padrão do grupo não se aplicou a esta empresa (dado faltando ou '
                   f'fundamento negativo); decidiu {escolhido}, o seguinte do encadeamento. ')

    return dict(justo=justo, faixa=(faixa_lo, faixa_hi), largura=largura, nMetodos=1,
        metodos=detalhe,
        motor=f'{escolhido} · faixa R$ {faixa_lo:.2f} a R$ {faixa_hi:.2f}',
        nota=(f'PREÇO JUSTO por {escolhido}, MÉTODO ÚNICO — o múltiplo que descreve este '
              f'negócio, aplicado ao fundamento projetado. Não é mediana de réguas diferentes. '
              f'A faixa de R$ {faixa_lo:.2f} a R$ {faixa_hi:.2f} (largura {largura*100:.0f}%) é a '
              f'OSCILAÇÃO HISTÓRICA do próprio múltiplo — percentil 25 a 75 da série —, e o '
              f'limite inferior é o teto de compra. '
              + nota_fb + principal.get('nota', '') + nota_verif))


def pl_setorial(H):
    """P/L mediano dos pares de cada motor, usando SÓ empresas sem quebra de série.

    A chave `_UNIVERSO` é a mediana de TODAS as empresas com série limpa, e existe desde
    13/09/2026 para o grupo que não tem par nenhum: VAREJO tem duas empresas (VIVA3 e ASAI3)
    e as duas entraram sem histórico de preço, então o grupo não produzia mediana e as duas
    ficavam sem preço justo. Um P/L de 22 empresas é referência pior que a do setor certo, e
    melhor que nenhuma — e a célula diz qual das duas está sendo usada.
    """
    por = {}
    todas = []
    for t, A in H.items():
        m = MOTOR.get(t)
        if ano_quebra(A): continue
        pls = [x for x in (pl_ano(t, A, y) for y in A) if x]
        if len(pls) >= 4:
            todas.append(st.median(pls))
            if m: por.setdefault(m, []).append(st.median(pls))
    out = {k: st.median(v) for k, v in por.items() if v}
    if todas:
        out['_UNIVERSO'] = st.median(todas)
    return out

PL_SETOR = {}

# ══════════════════════════════════════════════════════════════════════════════════════════
# MÚLTIPLO DOS PARES — a metade que faltava no preço justo
# ══════════════════════════════════════════════════════════════════════════════════════════
# `backtest_pares.py` (13/09/2026) testou as três âncoras ponto no tempo, 54 observações:
#
#   MÉDIA própria + pares   +14,1 p.p.   t +9,07   3 de 3 anos   p 0,040
#   PARES do setor          +11,1 p.p.   t +4,21   3 de 3 anos   p 0,081
#   PRÓPRIA (motor)          -1,8 p.p.   t -0,21   2 de 3 anos   p 0,549
#
# A média ganhou das DUAS pontas que a compõe, nas duas formas de corte. O mecanismo está na
# última linha da saída: própria e pares concordam no veredicto em apenas 39% das linhas — são
# informações independentes, e somar cancela o erro de cada uma. A própria prende a empresa no
# patamar dela e nunca enxerga re-rating; a dos pares ignora o que ela tem de específico.
#
# O usuário mandou implementar e o assunto virou outro antes de eu fazer. Ficou de fora até
# aqui: o preço justo usava SÓ o múltiplo próprio, que é justamente a âncora que deu negativo.
#
# ⚠️ Pares = mesmo grupo de motor, o ticker FORA da própria mediana, mínimo de 3. Com menos, o
# múltiplo próprio decide sozinho — mediana de 2 pares é a opinião de duas empresas, não do
# setor. SHOP tem 2 empresas e fica assim.
# Limites do ajuste de ROE sobre o múltiplo histórico. Ver alvo_com_pares().
# ⚠️ SEM EFEITO DESDE 14/09/2026 — mantidas só para não quebrar quem as importa.
# O teto de ±30% saiu quando o usuário escreveu a regra que quer, e ela não tem teto:
# 'P/L Ajustado = P/L Mediano Histórico × (ROE Atual ÷ ROE Histórico)'. Ver alvo_com_pares.
ROE_AJUSTE_MIN, ROE_AJUSTE_MAX = 0.0, 99.0

MIN_PARES = 3
MULT_PARES = {}

def multiplos_pares(H):
    """{(motor, chave): mediana do múltiplo-alvo dos pares}. Pré-passe, como pl_setorial."""
    por = {}
    for t, A in H.items():
        g = MOTOR.get(t)
        if not g:
            continue
        for f in (lambda: teto_ep(t, A, com_pares=False), lambda: teto_pvp(t, A, com_pares=False),
                  lambda: teto_ev_receita(t, A, com_pares=False),
                  lambda: teto_ffo(t, A, com_pares=False)):
            try:
                r = f()
            except Exception:
                r = None
            if r and r.get('alvo') and r['alvo'] > 0:
                por.setdefault((g, r['chave']), []).append((t, r['alvo']))
    return por


# P/VP FICA DE FORA DA MÉDIA COM PARES, e não é preferência: é identidade. O P/VP justo de uma
# empresa é ≈ (ROE − g) ÷ (Ke − g) — ele É uma função do ROE. Misturar o P/VP de empresas com
# ROE diferente compara negócios diferentes, e o projeto já tinha registrado o tombo: "o BBSE3
# caiu de R$29,04 para R$17,76 por causa de um P/VP mediano de pares que nada tem a ver com uma
# seguradora de ROE 79%". Ligando os pares, o erro voltou nas duas pontas — a BBSE3 (ROE 79%)
# perdeu 18% ao ser comparada com bancos de ROE 20%, e pior, o IRBR3 (ROE 5%) GANHOU 69%
# herdando o P/VP de quem lucra quatro vezes mais.
# Os múltiplos de FLUXO não têm esse acoplamento mecânico e continuam na média.
# ⚠️ Declarado: `backtest_pares.py` validou a média sobre um conjunto que INCLUÍA P/VP. Tirá-lo
# é desviar da configuração testada — mas o mecanismo acima não é questão de amostra, e os dois
# casos são concretos. Se for para revalidar, é o backtest que roda de novo, não o P/VP que
# volta calado.
PARES_SEM = {'P/VP'}

def serie_roe(t, A):
    """(roe_hoje, [(ano, roe) dos anos comparáveis], rótulo da métrica) — a rentabilidade.

    UMA DEFINIÇÃO, DOIS CONSUMIDORES, e é de propósito: quem ajusta o múltiplo em
    `alvo_com_pares` e quem preenche a coluna ROE mediano do Radar (scripts/gerar_colunas.py)
    têm que ler o MESMO número. Se a coluna mostrasse uma série e o motor usasse outra, o
    leitor faria a divisão na tela e não bateria com o fator que a tooltip do Múltiplo declara
    — que é o defeito que este projeto já pagou quatro vezes em campos diferentes.

    EM SHOPPING O NUMERADOR É O FFO, não o lucro líquido: o usuário pediu FFO em TODAS as
    colunas do Radar, e o ajuste de múltiplo é uma delas. O patrimônio vem implícito do ROE
    contábil do próprio ano (lucro ÷ ROE), então o denominador é o mesmo dos dois lados e a
    razão roe_hoje/roe_mediano — que é tudo o que o ajuste usa — não depende dele.

    ⚠️ A RESSALVA DO FFO ÷ PATRIMÔNIO permanece: o imóvel está no balanço a custo histórico,
    então este retorno lê ALTO por construção e não se compara com o de empresa que não
    carrega imóvel. Para o AJUSTE isso não contamina nada, porque ele só usa a razão da
    empresa contra ela mesma — mas a coluna diz na tooltip, porque lá o número é lido de frente.
    """
    val, _q = anos_validos(A)
    shop = MOTOR.get(t) == 'SHOP'

    def _roe(y):
        d = A.get(y) or {}
        r = d.get('roe')
        if r is None or r == 0:
            return None
        if not shop:
            return r
        f, li = ffo_ano(t, A, y), d.get('lucrolin')
        if not f or not li or li <= 0:
            return None
        return f / (li / (r / 100)) * 100

    serie = [(y, v) for y in val for v in (_roe(y),) if v is not None]
    hoje = _roe(max(A))
    return hoje, serie, ('FFO ÷ patrimônio' if shop else 'ROE')


def alvo_com_pares(t, chave, alvo_proprio, n_anos=None, A=None):
    """Múltiplo-alvo: a MEDIANA HISTÓRICA DA PRÓPRIA EMPRESA, ajustada pela rentabilidade.
    Devolve (alvo, nota, origem).

    ══ MUDANÇA DE 14/09/2026, pedida pelo usuário ══
    "Para a conta de múltiplo, vamos levar em consideração somente os últimos 6 anos da média
    de P/L que a empresa foi negociada. Mas temos que levar em consideração o ROE médio do
    período também. Não vamos mais levar em consideração o múltiplo do setor."

    Duas mudanças, e a primeira contraria um backtest — por isso fica registrada com o número.

    1 · O MÚLTIPLO DOS PARES SAI DA CONTA. Ele entrou em 13/09 porque `backtest_pares.py`
        mediu a média (própria + pares) em +14,1 p.p. contra as duas pontas isoladas, com
        p=0,040 em 54 observações; a âncora própria SOZINHA foi a que deu negativo
        (−1,8 p.p., p=0,549).
        ⚠️ O QUE ISSO CUSTA: a mediana histórica própria prende a empresa no patamar em que ela
        já negociou e nunca enxerga re-rating. A evidência apontava para o outro lado.
        O QUE A DECISÃO GANHA, e é o argumento do usuário: a mediana do setor mistura empresas
        com rentabilidade e risco distintos. O BPAC11 mostra o custo do peer comp — P/L próprio
        de 39,4x contra 7,5x dos bancos, e a média cortava a diferença pela metade sem que
        nada no negócio justificasse o corte.

    2 · O ROE ENTRA COMO AJUSTE, e é ele que substitui a informação que os pares traziam.
        Mediana histórica pura ignora que a empresa pode estar mais (ou menos) rentável hoje do
        que foi na média do período. Pela relação de Gordon, P/L = payout ÷ (Ke − g) e
        g = ROE × retenção: mais ROE significa mais crescimento sustentável e, com tudo o mais
        constante, múltiplo justificadamente maior.

            ajuste = ROE atual ÷ ROE MEDIANO do período   (proporção direta, sem teto)

        ⚠️ O LIMITE DE ±30% SAIU EM 14/09/2026, a pedido do usuário, que escreveu a regra
        com proporção direta e sem teto. O que o teto protegia continua verdadeiro e fica
        registrado: proporção direta faz o múltiplo DOBRAR quando o ROE dobra, e a teoria não
        sustenta isso — a relação entre ROE e P/L justo é não-linear e depende de payout e de
        Ke, nenhum dos dois observável sem premissa (o Ke variável saiu do motor em 13/09 por
        isso, seção 30). Sem teto, o ajuste pode DOMINAR a mediana histórica em vez de só
        movê-la. Nenhuma linha do Radar hoje passa de ±45%, então o efeito prático é pequeno;
        o risco aparece em empresa que vem de ano de prejuízo ou de lucro extraordinário.
    """
    janela = f' ao longo de {n_anos} anos' if n_anos else ''
    nome = {'E/P': 'P/L'}.get(chave, chave)

    d = MULTIPLO_DECLARADO.get(t)
    if d and d[0] == chave:
        return d[1], f'{d[1]:.2f}x DECLARADO', (
            f'o múltiplo-alvo DECLARADO no relatório ({d[1]:.2f}x, contra '
            f'{alvo_proprio:.2f}x da própria série). {d[3]}')

    proprio = f'o {nome} mediano da própria empresa{janela} ({alvo_proprio:.2f}x)'
    if A is None:
        return alvo_proprio, '', proprio

    roe_hoje, pares_roe, metrica = serie_roe(t, A)
    roes = [v for _y, v in pares_roe]
    if len(roes) < 3 or roe_hoje is None or roe_hoje <= 0:
        return alvo_proprio, '', (proprio + ' — sem ROE suficiente na série para ajustar pela '
                                            'rentabilidade, fica a média histórica pura')
    roe_med = st.median(roes)
    if roe_med <= 0:
        return alvo_proprio, '', (proprio + ' — ROE mediano do período não é positivo, '
                                            'sem ajuste possível')

    bruto = roe_hoje / roe_med
    aj = bruto
    alvo = alvo_proprio * aj
    limitado = False
    return alvo, f'{alvo:.2f}x = {alvo_proprio:.2f}x × ajuste de ROE {aj:.2f}', (
        f'{proprio}, ajustado pela rentabilidade ({metrica}): hoje {roe_hoje:.1f}% contra '
        f'{roe_med:.1f}% de mediana do período dá fator {bruto:.2f}'
        + f' → múltiplo-alvo {alvo:.2f}x. Proporção direta, sem teto: mais rentável que a '
          f'própria mediana merece múltiplo maior; menos rentável, menor. O múltiplo do setor '
          f'NÃO entra desde 14/09/2026.')


if __name__ == '__main__':
    H = carregar(); out = {}
    globals()['H_GLOBAL'] = H
    PL_SETOR.update(pl_setorial(H))
    MULT_PARES.update(multiplos_pares(H))
    print('P/L mediano dos pares sem quebra:', {k: round(v,1) for k,v in PL_SETOR.items()}, '\n')
    print("Teto = limite INFERIOR da faixa de múltiplos próprios (p25-p75). "
          "Ke, Gordon/Bazin e convicção em estrelas saíram em 13/09/2026 — ver seção 30.\n")
    print(f"{'ativo':>7} {'motor':>5} {'justo':>9} {'FAIXA lo':>9} {'faixa hi':>9} {'larg':>6} {'cotação':>8} {'m.seg':>7}")
    print("-" * 74)
    for t, A in sorted(H.items()):
        r = calcular(t, A)
        if r and r.get('recusa'):
            # RECUSA EXPLÍCITA. Duas origens possíveis: LIM_MARGEM (não usada desde 06/09,
            # ver _sanidade) ou SEM_TETO (declarada por ticker, ex.: ROXO34, 07/09/2026). Vai
            # para o JSON com justo=None para que o Radar apague o teto e exiba o motivo — é
            # diferente de "não tenho motor para isto".
            out[t] = {**r, 'teto': None, 'cot': A[max(A)].get('preco')}
            motivo = ('SEM-TETO DECLARADO' if t in SEM_TETO
                      else 'SÉRIE CURTA — sem faixa' if 'série curta' in r.get('motor', '')
                      else f'margem além de ±{LIM_MARGEM*100:.0f}%')
            print(f"{t:>7} {MOTOR.get(t,'—'):>5}   ⛔ RECUSADO — {motivo}")
            continue
        if not r or not r['justo'] or r['justo'] <= 0:
            print(f"{t:>7} {MOTOR.get(t,'—'):>5}   — motor manual (NAV/shopping) ou dado insuficiente")
            continue
        cot = A[max(A)].get('preco')
        # A guarda antiga (rebaixar convicção quando a margem passava de |100%|) foi
        # SUBSTITUÍDA por _sanidade(), que recusa em vez de rebaixar. Rebaixar mantinha o
        # número na tela com três estrelas vazias; o leitor via "R$ 51,72 ★☆☆" e lia um preço.
        # A recusa é a única forma de a tabela dizer "não sei" em vez de "vale isto, mais ou
        # menos". Ver LIM_MARGEM.
        fx = r.get('faixa')
        lo = fx[0] if (fx and fx[0] and fx[0] > 0) else r['justo']
        hi = fx[1] if (fx and fx[1] and fx[1] > 0) else r['justo']
        if r.get('teto_suprimido'):
            # A faixa vai para a tabela; o teto de compra, não. Ver _sanidade / LIM_LARGURA.
            r.update(teto=None, faixaLo=round(lo, 2), faixaHi=round(hi, 2),
                     largura=round(r.get('largura', 0), 3), cot=cot, seg=None)
            out[t] = r
            print(f"{t:>7} {MOTOR.get(t,'—'):>5} {r['justo']:>9.2f} {lo:>9.2f} {hi:>9.2f} "
                  f"{r.get('largura', 0)*100:>5.0f}% {cot:>8.2f}   sem teto")
            continue
        teto = lo
        r.update(teto=round(teto, 2), faixaLo=round(lo, 2), faixaHi=round(hi, 2),
                 largura=round(r.get('largura', 0), 3), cot=cot,
                 seg=(teto-cot)/teto*100 if cot else None)
        out[t] = r
        print(f"{t:>7} {MOTOR.get(t,'—'):>5} {r['justo']:>9.2f} {lo:>9.2f} {hi:>9.2f} "
              f"{r.get('largura', 0)*100:>5.0f}% {cot:>8.2f} {r['seg']:>6.0f}%")
    json.dump(out, open('analise/tetos.json', 'w'), ensure_ascii=False, indent=1)
    print(f"\n{len(out)} tetos calculados → analise/tetos.json")
