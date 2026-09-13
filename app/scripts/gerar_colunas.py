#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# GERADOR DAS COLUNAS DE LUCRO DO RADAR — auditoria de 06/09/2026
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pedido do usuário: "valide todos os campos da tabela e garanta que todos estejam de um motor
# com racional declarado e que não tem nada na mão. E que esteja tudo preenchido."
#
# A auditoria achou três coisas, e as três eram piores que "faltou tooltip":
#
#  1. O RÓTULO DA COLUNA 4 MENTIA. Ela diz "Lucro 2025 REAL" e 20 das 30 linhas traziam o
#     lucro LTM de 2026. PETR4 (R$133,76 bi), VALE3 (R$8,69 bi), KLBN11 (R$0,54 bi), SAUD3,
#     AXIA3 e AURE3 batem exatamente com o TTM 2T26, não com o exercício de 2025. Quem lesse
#     a coluna como "o que a empresa ganhou em 2025" lia errado em dois terços da tabela.
#
#  2. A COLUNA 5 MISTURAVA DUAS DEFINIÇÕES. Em algumas linhas era projeção de 2026 (CPFE3
#     R$6,10 bi contra LTM de R$6,29 bi); em outras era lucro NORMALIZADO de meio de ciclo
#     (VALE3 R$43,26 bi contra LTM de R$8,69 bi — cinco vezes; KLBN11 R$2,51 bi contra
#     R$0,54 bi). Duas grandezas diferentes empilhadas na mesma coluna e ordenáveis juntas.
#
#  3. 29 DAS 30 LINHAS TINHAM `data-lucro-manual`. Eram números digitados, curados em datas
#     diferentes, sem motor comum — exatamente o que o usuário mandou eliminar.
#
# O QUE ESTE SCRIPT FAZ: regenera as colunas 4, 5, 6, 7, 9 e 10 a partir de duas fontes, e
# só duas — HIST_SEED (Partnr/B3/CVM) e o lucro normalizado de data/tir.data.js, que tem
# motor declarado por setor (METODOLOGIA_ANALISE.md seção 10). Nenhum número digitado.
#
#   col 4  Lucro LTM         = lucrolin do último exercício da base (TTM 2T26)
#   col 5  Lucro normalizado = motor por setor (receita × margem mediana · ROE × PL · FFO ·
#                              lucro recorrente), o mesmo que alimenta a TIR real
#   col 6  Δ normalizado/LTM = quanto o resultado atual está acima ou abaixo do normalizado
#   col 7  LPA normalizado   = lucro normalizado ÷ papéis negociados (units já resolvidas)
#   col 9  Div./Ação         = LPA × payout (seção 22)
#   col 10 DY                = Div./Ação ÷ cotação
#
# ⚠️ A COLUNA 6 MUDA DE SIGNIFICADO. Era "crescimento projetado"; passa a ser a DISTÂNCIA
# entre o resultado corrente e o normalizado. Não é previsão: é diagnóstico de ciclo. KLBN11
# com −83% não vai cair 83%; ela está 83% abaixo do que a própria série sugere como normal.
import json, re, statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
src = (RAIZ / 'scripts/motor_teto.py').read_text()
M = {}
exec(src[:src.index("if __name__")], M)
H = M['carregar']()
M['H_GLOBAL'] = H

# lucro normalizado + motor declarado, de data/tir.data.js (seção 10 da metodologia)
tir = (RAIZ / 'data/tir.data.js').read_text()

# Série anual de dividend yield, 2016-2026, coletada da Partnr em 13/09/2026. Substituiu duas
# fontes que brigavam pela mesma célula: um texto digitado à mão (várias linhas citando
# StatusInvest, a do ITUB3 usando o DY da ITUB4) e um bloco de runtime que sobrescrevia com a
# API. Agora as duas colunas de DY realizado — a de 2025 e a mediana de 10 anos — saem daqui.
DYH = json.loads((RAIZ / 'analise/dy_historico.json').read_text())['tickers']

def dy_ano(t, ano):
    v = DYH.get(t, {}).get(str(ano))
    return v if (v and v > 0) else None      # zero na base = dado ausente, não dividendo zero

def dy_mediana(t, n=10, ate=2025):
    anos = {int(y): v for y, v in DYH.get(t, {}).items()
            if ate - n + 1 <= int(y) <= ate and v and v > 0}
    if len(anos) < 3:
        return None, anos
    return st.median(anos.values()), anos
LN = {k: (float(v), mo) for k, v, mo in
      re.findall(r"(\w+):\s*\{[^}]*lucroNorm:(-?[\d.]+)[^}]*motor:'([^']*)'", tir)}
FIN = {k for k, v in M['MOTOR'].items() if v in ('FIN', 'NAV')}

# Taxa de crescimento por ticker, de data/tir.data.js. Registro a registro, não por regex solto
# sobre o arquivo inteiro: `gCagr:` é null em metade dos tickers, e um `.*?` preguiçoso pula o
# null e pega o gCagr do PRÓXIMO ticker — 10 empresas saíram com a taxa da vizinha antes de eu
# perceber.
_REG = {m.group(1): m.group(2) for m in re.finditer(r'(\w+):\s*\{([^}]*)\}', tir)}

def _tircampo(t, c):
    b = _REG.get(t)
    if not b: return None
    m = re.search(r'\b%s:\s*(-?[\d.]+|null)' % c, b)
    return None if (not m or m.group(1) == 'null') else float(m.group(1))

CRESC_CAP = 25.0   # projeção de UM ano; o cap de 15% do motor é para perpetuidade de 10 anos

def crescimento(t):
    """(taxa %, origem) para projetar 2026 a partir de 2025.

    Pedido do usuário: "utilize o lucro recorrente pra calcular a taxa de crescimento". É o
    `gCagr` que gerar_tir.py já produz — REGRESSÃO LOG sobre a série de lucro recorrente de
    data/fluxo.json. A escolha do estimador está justificada em cagr_recorrente(): média
    aritmética tem viés de Jensen e explodiu a ALOS3 para 59,7% por causa do ano da fusão;
    mediana das variações esconde queda monotônica e salvava a PASS3 indevidamente; CAGR de
    pontas usa 2 pontos e ignora o meio. A regressão usa todos.

    ⚠️ O motor ANULA gCagr para financeira, holding e cíclica de commodity — lucro recorrente
    não é conceito aplicável ali. São 21 dos 32 tickers. Nesses vale ROE × retenção, que é o
    crescimento que a empresa sustenta com o lucro que não distribui, e é o que o próprio motor
    usa como a outra metade do `g`.
    """
    g = _tircampo(t, 'gCagr')
    if g is not None:
        return max(-CRESC_CAP, min(g, CRESC_CAP)), ('CAGR do lucro recorrente por regressão log', g)
    g = _tircampo(t, 'gRoe')
    if g is not None:
        return max(-CRESC_CAP, min(g, CRESC_CAP)), ('ROE × retenção — o lucro recorrente não se '
                                                    'aplica a banco, seguradora, holding ou cíclica', g)
    return None, (None, None)


def normalizado(t, A, usar_cache=True):
    """Lucro normalizado + nome do motor.

    ⚠️ `usar_cache` existe por causa de um CICLO, achado em 13/09/2026 quando o usuário
    perguntou por que o lucro normalizado da TIM (R$ 3,38 bi) estava abaixo do lucro de 2025:
    `gerar_tir.py` chamava esta função para CALCULAR o lucroNorm que ele grava em
    data/tir.data.js — e esta função começa lendo o lucroNorm de data/tir.data.js. O gerador
    lia a própria saída anterior. Uma vez escrito, o número nunca mais mudava, por mais que a
    base andasse. A TIM estava três regerações atrasada (3,38 contra 3,85 recalculado).
    Quem ESCREVE o cache passa usar_cache=False; quem só LÊ a planilha continua no padrão.

    ⚠️ MEDIANA COM TENDÊNCIA, não mediana simples. Também da pergunta da TIM: a margem líquida
    dela foi 7,8% → 11,9% → 12,4% → 16,2% → 15,8%. Isso não oscila, isso SOBE — e a mediana de
    6 anos (14,1%) ancorava no pior período e punia a empresa por ter melhorado. É exatamente o
    defeito que `mediana_com_tendencia` foi escrita para corrigir no ROE dos bancos (seção do
    motor), e que aqui nunca tinha sido aplicado. Com ela, a margem usada vira 15,8%.
    """
    if usar_cache and t in LN:
        return LN[t][0], LN[t][1], 'data/tir.data.js'
    val, q = M['anos_validos'](A)
    c = A[max(A)]
    if t in FIN:
        # ⚠️ O PATRIMÔNIO VEM DA CONTABILIDADE, NÃO DO PREÇO. Até 13/09/2026 esta linha fazia
        # `vpa() × papeis()`, e vpa() é preço ÷ P/VP — ou seja, o lucro NORMALIZADO, que é um
        # número de fundamento, se mexia quando a ação subia ou caía. Pior: o P/VP da base não
        # reconcilia com o par lucro/ROE da mesma base. O usuário achou pelo Itaú, cujo lucro
        # normalizado saía em R$ 40,1 bi contra R$ 45,9 bi de lucro real em 2025 — o P/VP
        # dizia patrimônio de R$ 190,9 bi e o ROE dizia R$ 228,0 bi, 16% de diferença. A
        # varredura achou o mesmo em quase todo o grupo: BMEB4 −12%, BRSR6 +11%, e a SAUD3
        # com +244%, que é a incorporação de 2026 batendo em cheio no P/VP.
        # Patrimônio = lucro ÷ ROE resolve: os dois campos são contábeis, da mesma fonte e do
        # mesmo exercício, e o preço sai da conta. Na prática a fórmula vira
        # `lucro_atual × (ROE típico ÷ ROE de hoje)` — escala o lucro pela distância entre a
        # rentabilidade normal do banco e a de agora, que é exatamente o que normalizar quer
        # dizer.
        roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
        roe_hoje, lucro_hoje = c.get('roe'), c.get('lucrolin')
        if roes and roe_hoje and roe_hoje > 0 and lucro_hoje and lucro_hoje > 0:
            pl_contabil = lucro_hoje / (roe_hoje / 100)
            roe, _nota = M['mediana_com_tendencia'](roes, limiar_abs=2.0)
            return roe/100*pl_contabil, 'ROE mediano × patrimônio líquido', 'calculado agora'
    mg = [A[y]['lucrolin']/A[y]['receita'] for y in val
          if A[y].get('receita') and A[y].get('lucrolin')]
    if mg and c.get('receita'):
        m, _nota = M['mediana_com_tendencia'](mg)
        return m*c['receita'], 'receita × margem líquida mediana', 'calculado agora'
    return None, None, None


def br(v, casas=2):
    return f"{v:,.{casas}f}".replace(',', '§').replace('.', ',').replace('§', '.')


def dinheiro(v):
    if v is None: return None
    a = abs(v)
    if a >= 1e9:  return ('-' if v < 0 else '') + f'R$ {br(a/1e9)} bi'
    if a >= 1e6:  return ('-' if v < 0 else '') + f'R$ {br(a/1e6, 0)} mi'
    return ('-' if v < 0 else '') + f'R$ {br(a)}'


VAZIO = '<span class="muted">—</span>'


def cel(txt, tip):
    return f'{txt}<span class="col-tip" data-tip="{tip}">ⓘ</span>'


def gerar():
    p = RAIZ / 'data/radar-rows.data.js'
    h = p.read_text()
    log = []
    for t in sorted(H):
        if f'{t}.SA"' not in h:
            continue
        A = H[t]; c = A[max(A)]
        ano = max(A)
        ltm = c.get('lucrolin')
        ln, motor, fonte = normalizado(t, A)   # segue alimentando a TIR; não é mais coluna
        pap = M['papeis'](t, A)
        po, npo, pf = M['payout_final'](t, A, H)
        l25 = (A.get(2025) or {}).get('lucrolin')
        g, (origem_g, g_bruto) = crescimento(t)
        proj = l25 * (1 + g/100) if (l25 and l25 > 0 and g is not None) else None

        # ⚠️ 13/09/2026 — O LPA PASSOU A SAIR DO LUCRO PROJETADO, não do normalizado.
        # O usuário: "o LPA você está utilizando o lucro normalizado mas não tem mais essa
        # coluna". Estava — e o problema não era só a tooltip citar uma coluna que sumiu: a
        # cadeia inteira (LPA → dividendo → DY) pendurava num número que não aparecia em lugar
        # nenhum da tela. No Itaú o LPA de R$ 4,76 vinha de R$ 46,65 bi, que não é nem o lucro
        # de 2025 (R$ 45,85 bi) nem o projetado (R$ 50,54 bi). Não havia como conferir.
        # Agora a linha fecha e cada passo é visível: 2025 → projetado 2026 → ÷ papéis = LPA
        # → × payout = dividendo → ÷ cotação = DY.
        # ⚠️ O CUSTO, declarado: o normalizado existia para tirar o CICLO da conta. A VALE3 cai
        # de LPA 3,89 para 2,67 porque a projeção extrapola a queda do minério em vez de
        # suavizá-la. Para dividendo de UM ano isso é defensável — empresa no fundo do ciclo
        # paga menos mesmo —, mas quem ler o DY da VALE3 está lendo fundo de ciclo, não média.
        lpa = (proj/pap) if (proj and pap and proj > 0) else None
        dps = (lpa*po) if (lpa and po) else None
        preco = c.get('preco')
        dy = (dps/preco*100) if (dps and preco) else None

        base = (f'Fonte: MCP Partnr (B3/CVM), exercício {ano} — série TTM com data-base '
                f'30/06/2026. Nenhum valor digitado à mão: gerado por scripts/gerar_colunas.py.')
        cells = {}

        # ── Coluna 4 · LUCRO DO EXERCÍCIO FECHADO DE 2025 ────────────────────────────────
        # Pedido do usuário em 13/09/2026, e ela responde uma pergunta que o LTM sozinho não
        # responde: o LTM atravessa dois exercícios (2S25 + 1S26), então quando ele sobe não
        # dá para saber se foi o semestre novo que veio forte ou o velho que era fraco. Com o
        # ano fechado ao lado, a comparação fica direta.
        cells[4] = cel(dinheiro(l25) or VAZIO,
            'LUCRO LÍQUIDO — EXERCÍCIO FECHADO DE 2025&#10;&#10;'
            'Fonte: MCP Partnr (B3/CVM), 1º de janeiro a 31 de dezembro de 2025.&#10;&#10;'
            'A coluna ao lado é o LTM, que vai de 01/07/2025 a 30/06/2026 e portanto mistura '
            'dois exercícios. Esta aqui é o ano civil fechado, sem mistura.')

        # ── Coluna 5 · LUCRO PROJETADO 2026 ─────────────────────────────────────────────
        origem, bruto = origem_g, g_bruto
        cortado = (g is not None and bruto is not None and abs(bruto - g) > 0.05)
        # ── Coluna 6 · TAXA DE CRESCIMENTO 2025 → 2026 ──────────────────────────────────
        # Pedido do usuário. Ela já existia embutida na projeção, mas só aparecia na tooltip —
        # e é o único número que separa a coluna de 2025 da de 2026. Exposta, a linha inteira
        # fica conferível de cabeça: lucro × (1 + taxa) = projetado.
        cells[6] = cel(
            (f'<span style="color:{"#0a5c35" if g >= 0 else "#9c1c1c"};font-weight:600;">'
             f'{"+" if g >= 0 else ""}{br(g,1)}%</span>'
             + (f' <span style="color:#b45309;font-size:11px;">({"+" if bruto >= 0 else ""}'
                f'{br(bruto,1)}%)</span>' if cortado else '')) if g is not None else VAZIO,
            (f'CRESCIMENTO APLICADO = {br(g,1)}%&#10;&#10;{origem}.&#10;'
             if g is not None else
             'SEM TAXA DE CRESCIMENTO&#10;&#10;A empresa não tem série de lucro recorrente nem '
             'ROE utilizável na base.&#10;')
            + (f'&#10;⚠️ VALOR BRUTO {br(bruto,1)}% — o número entre parênteses. Limitado a '
               f'±{br(CRESC_CAP,0)}% porque projetar mais que isso em um ano, a partir de série '
               f'de 5 pontos, é chute com casa decimal.&#10;' if cortado else '')
            + '&#10;É esta taxa que leva a coluna Lucro 2025 à coluna Lucro Projetado 2026.&#10;'
            + base)

        cells[5] = cel(dinheiro(proj) or VAZIO,
            (f'LUCRO PROJETADO 2026 = lucro 2025 R$ {br((l25 or 0)/1e9)} bi × (1 + {br(g)}%)'
             if proj else 'LUCRO PROJETADO 2026 — não calculável')
            + '&#10;&#10;'
            + (f'Taxa: {origem}.&#10;' if origem else
               'Sem taxa de crescimento: a empresa não tem série de lucro recorrente nem ROE '
               'utilizável na base.&#10;')
            + (f'⚠️ VALOR BRUTO {br(bruto)}% — limitado a ±{br(CRESC_CAP,0)}%. Projetar mais que '
               f'isso em um ano a partir de série curta é chute com casa decimal.&#10;' if cortado else '')
            + (('' if l25 and l25 > 0 else
                'Lucro de 2025 ausente ou negativo: sem base positiva não existe percentual de '
                'crescimento com significado.&#10;'))
            + '&#10;⚠️ É PROJEÇÃO, não medida. Não entra no preço justo nem no ranking: o backtest '
              '(scripts/backtest_ranking.py) mostrou que somar crescimento ao earnings yield '
              'PIOROU o poder de ordenar em 8,9 p.p. Está aqui para leitura.&#10;' + base)

        cells[7] = cel(f'R$ {br(lpa)}' if lpa else VAZIO,
            (f'LUCRO POR AÇÃO = lucro projetado 2026 R$ {br(proj/1e9)} bi ÷ {pap/1e6:.0f} mi papéis'
             if lpa else 'LUCRO POR AÇÃO — sem lucro projetado 2026')
            + '&#10;&#10;Papéis NEGOCIADOS: a contagem é derivada de lucro ÷ LPA da própria base, '
              'ancorada no ano mais recente e usando só os anos cuja contagem fica a ±25% dele — '
              'assim um desdobramento não mistura bases (a SBSP3 fez 5:1 e a contagem foi de '
              '705 mi para 3.519 mi) nem um ano de lucro perto de zero explode a divisão.&#10;'
              'Units já resolvidas (KLBN11 ÷5, SANB11 ÷2, BPAC11 ÷3): o número é POR PAPEL '
              'negociado, na mesma base do preço e do dividendo.&#10;' + base)

        rot = {'piso': 'piso da política', 'teto': 'teto da política',
               'estatutario': 'realizado (a política é só o mínimo legal)',
               'outra_base': 'realizado (a política não é % do lucro)',
               'nao_paga': 'a empresa não paga dividendos',
               'pares': 'payout mediano dos pares — não é da empresa',
               'realizado': 'realizado da própria série'}.get(pf[0], pf[0])
        cells[9] = cel(f'R$ {br(dps)}' if dps else VAZIO,
            (f'DIVIDENDO POR AÇÃO = LPA R$ {br(lpa)} × payout {po*100:.0f}%'
             if dps else 'DIVIDENDO POR AÇÃO — sem LPA ou sem payout')
            + f'&#10;&#10;Payout: {rot} (detalhe na coluna Payout).&#10;'
              'É FUNDAMENTO, não deriva do preço: até 06/09/2026 o DPS era calculado como '
              '"DY × cotação", o que fazia o dividendo por ação subir quando a AÇÃO subia. '
              'A relação foi invertida — o DPS sai do lucro, e o DY é que deriva dele.&#10;' + base)

        cells[10] = cel(f'{br(dy,2)}%' if dy else VAZIO,
            (f'DIVIDEND YIELD = Div./Ação R$ {br(dps)} ÷ cotação R$ {br(preco)}'
             if dy else 'DIVIDEND YIELD — sem dividendo por ação calculável')
            + '&#10;&#10;Recalculado a cada atualização de cotação: o dividendo é fixo (vem do '
              'lucro) e o yield é que se move com o preço, como deve ser.&#10;' + base)

        # ── Coluna 11 · DIVIDEND YIELD REALIZADO DE 2025 ────────────────────────────────
        # Pedido do usuário: "troque a DY LTM por DY 2025". A coluna antiga era digitada à mão
        # — várias linhas citavam StatusInvest como fonte e a do ITUB3 usava o DY da ITUB4,
        # "mais líquida" — e ainda era reescrita em runtime pela API do Partnr. Dois números de
        # fora da base, brigando pela mesma célula. Este sai de data/historico.data.js, igual
        # ao resto da tabela, e é fato consumado: serve para conferir o DY projetado ao lado.
        dy25 = (A.get(2025) or {}).get('dy')
        # ── Coluna 11 · DY REALIZADO DE 2025 · Coluna 12 · MEDIANA DE 10 ANOS ───────────
        d25 = dy_ano(t, 2025)
        cells[11] = cel(
            (f'<span style="{"color:#059669;font-weight:600" if d25 >= 8 else ("" if d25 >= 4 else "color:#dc2626")}">'
             f'{br(d25,2)}%</span>') if d25 else VAZIO,
            (f'DIVIDEND YIELD REALIZADO DE 2025 = {br(d25,2)}%&#10;&#10;'
             'Proventos do exercício de 2025 ÷ preço da data-base.&#10;'
             if d25 else
             'DY DE 2025 — sem dado&#10;&#10;A base devolve yield ausente ou zero para este '
             'ticker em 2025, e zero aqui significa dado faltando, não dividendo zero.&#10;')
            + '&#10;É FATO, não projeção. A coluna à esquerda é o DY projetado (lucro de 2026 × '
              'payout ÷ cotação) e a da direita é a mediana de 10 anos — as três juntas mostram '
              'se a projeção está dentro do que a empresa costuma pagar.&#10;'
              'Fonte: MCP Partnr (B3/CVM), analise/dy_historico.json.')

        med10, usados = dy_mediana(t)
        cells[12] = cel(
            (f'<span style="{"color:#059669;font-weight:600" if med10 >= 8 else ("" if med10 >= 4 else "color:#dc2626")}">'
             f'{br(med10,2)}%</span>') if med10 else VAZIO,
            (f'DY MEDIANO DE 10 ANOS = {br(med10,2)}%&#10;&#10;'
             f'{len(usados)} exercícios com dado, de {min(usados)} a {max(usados)}.&#10;'
             f'Faixa: {br(min(usados.values()),2)}% a {br(max(usados.values()),2)}%.&#10;'
             f'Média dos mesmos anos: {br(sum(usados.values())/len(usados),2)}%.&#10;&#10;'
             'MEDIANA e não média: a PETR4 pagou 65% em 2022 e a BRAP4 47,9% em 2021 — '
             'extraordinários que levam a média da PETR4 a 16,4% contra 10,6% da mediana. '
             'A mediana descreve o ano típico.&#10;'
             if med10 else
             'DY MEDIANO DE 10 ANOS — não calculável&#10;&#10;Menos de 3 exercícios com dado '
             'utilizável na janela. Empresa recém-listada ou sem histórico de proventos na base.&#10;')
            + '&#10;⚠️ Anos com yield zero saem da conta: zero na base significa dado ausente.&#10;'
              '⚠️ 10 anos podem abranger mais de uma empresa — a ALOS3 era Aliansce até 2023.&#10;'
              'Fonte: MCP Partnr (B3/CVM), analise/dy_historico.json.')

        i = h.index(f'{t}.SA"'); m = h.find('<tr', i); end = m if m > 0 else len(h)
        blk = h[i:end]
        for idx in sorted(cells, reverse=True):
            tds = [x for x in re.finditer(r'<td\b[^>]*>.*?</td>', blk, re.S)]
            if idx >= len(tds): continue
            td = tds[idx]
            ini = re.match(r'<td\b[^>]*>', td.group(0)).group(0)
            blk = blk[:td.start()] + ini + cells[idx] + '</td>' + blk[td.end():]
        # LPA LTM por papel — alimenta a coluna P/L (js/fundamentos.js). Antes vinha curado à
        # mão e ficava defasado; agora sai da mesma base. Negativo é mantido de propósito: a
        # coluna de P/L precisa saber que houve prejuízo para declarar isso em vez de calar.
        lpa_ltm = (ltm/pap) if (ltm and pap) else None
        tag_end = blk.find('>')
        tag = blk[:tag_end]
        if lpa_ltm is not None:
            fonte_lpa = (f'LPA LTM = lucro dos últimos 12 meses R$ {br(ltm/1e9)} bi ÷ '
                         f'{pap/1e6:.0f} mi papéis negociados (units resolvidas). '
                         f'Fonte: MCP Partnr (B3/CVM), TTM 2T26. Gerado por scripts/gerar_colunas.py.')
            tag = (re.sub(r'data-lpa-ltm="[^"]*"', f'data-lpa-ltm="{lpa_ltm:.4f}"', tag)
                   if 'data-lpa-ltm=' in tag
                   else tag.replace(' data-veredicto=', f' data-lpa-ltm="{lpa_ltm:.4f}" data-veredicto=', 1))
            tag = (re.sub(r'data-lpa-fonte="[^"]*"', f'data-lpa-fonte="{fonte_lpa}"', tag)
                   if 'data-lpa-fonte=' in tag
                   else tag.replace(' data-veredicto=', f' data-lpa-fonte="{fonte_lpa}" data-veredicto=', 1))
        if 'data-lpa-manual=' not in tag:
            tag = tag.replace(' data-veredicto=', ' data-lpa-manual="true" data-veredicto=', 1)

        # ⚠️ 13/09/2026 — data-dy-proj PASSA A SER GERADO AQUI. Ele estava congelado de uma
        # geração antiga e divergia da própria coluna de DY em 28 das 30 linhas, às vezes pela
        # metade: SBSP3 mostrava 5,07% com o atributo em 10,67%, BRAP4 3,78% contra 9,53%,
        # PETR4 13,91% contra 6,24%. E não é enfeite — é ele que alimenta o Retorno Total e a
        # perna de dividendos da TIR real, então a tabela decidia com um número e exibia outro.
        # js/calculos.js já refazia a conta em runtime (atualizarDivDY), mas só DEPOIS de
        # "Atualizar Cotações"; em quem abre a página e não clica, o valor velho valia.
        # Escrever na geração deixa o arquivo coerente antes de qualquer JS rodar.
        if dy is not None:
            tag = (re.sub(r'data-dy-proj="[^"]*"', f'data-dy-proj="{dy/100:.4f}"', tag)
                   if 'data-dy-proj=' in tag
                   else tag.replace(' data-veredicto=', f' data-dy-proj="{dy/100:.4f}" data-veredicto=', 1))
        blk = tag + blk[tag_end:]
        h = h[:i] + blk + h[end:]
        log.append((t, ltm, ln, lpa, po, dps, dy))
    p.write_text(h)
    return log


if __name__ == '__main__':
    log = gerar()
    print(f"{'ativo':8}{'LTM':>10}{'normaliz':>10}{'LPA':>8}{'pay':>6}{'DPS':>8}{'DY':>8}")
    for t, ltm, ln, lpa, po, dps, dy in log:
        print(f"{t:8}{(f'{ltm/1e9:.2f}' if ltm else '—'):>10}{(f'{ln/1e9:.2f}' if ln else '—'):>10}"
              f"{(f'{lpa:.2f}' if lpa else '—'):>8}{(f'{po*100:.0f}%' if po is not None else '—'):>6}"
              f"{(f'{dps:.2f}' if dps else '—'):>8}{(f'{dy:.1f}%' if dy else '—'):>8}")
    print(f"\n{len(log)} linhas regeneradas — colunas 4,5,6,7,9,10,11,12")
