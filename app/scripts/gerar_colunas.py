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
LN = {k: (float(v), mo) for k, v, mo in
      re.findall(r"(\w+):\s*\{[^}]*lucroNorm:(-?[\d.]+)[^}]*motor:'([^']*)'", tir)}
FIN = {k for k, v in M['MOTOR'].items() if v in ('FIN', 'NAV')}


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
        ln, motor, fonte = normalizado(t, A)
        pap = M['papeis'](t, A)
        po, npo, pf = M['payout_final'](t, A, H)
        lpa = (ln/pap) if (ln and pap and ln > 0) else None
        dps = (lpa*po) if (lpa and po) else None
        preco = c.get('preco')
        dy = (dps/preco*100) if (dps and preco) else None
        delta = (ltm/ln - 1)*100 if (ltm and ln and ln > 0) else None

        base = (f'Fonte: MCP Partnr (B3/CVM), exercício {ano} — série TTM com data-base '
                f'30/06/2026. Nenhum valor digitado à mão: gerado por scripts/gerar_colunas.py.')
        cells = {}

        # ── Coluna 4 · LUCRO DO EXERCÍCIO FECHADO DE 2025 ────────────────────────────────
        # Pedido do usuário em 13/09/2026, e ela responde uma pergunta que o LTM sozinho não
        # responde: o LTM atravessa dois exercícios (2S25 + 1S26), então quando ele sobe não
        # dá para saber se foi o semestre novo que veio forte ou o velho que era fraco. Com o
        # ano fechado ao lado, a comparação fica direta.
        l25 = (A.get(2025) or {}).get('lucrolin')
        cells[4] = cel(dinheiro(l25) or VAZIO,
            'LUCRO LÍQUIDO — EXERCÍCIO FECHADO DE 2025&#10;&#10;'
            'Fonte: MCP Partnr (B3/CVM), 1º de janeiro a 31 de dezembro de 2025.&#10;&#10;'
            'A coluna ao lado é o LTM, que vai de 01/07/2025 a 30/06/2026 e portanto mistura '
            'dois exercícios. Esta aqui é o ano civil fechado, sem mistura.')

        cells[5] = cel(dinheiro(ltm) or VAZIO,
            f'LUCRO LÍQUIDO LTM (últimos 12 meses)&#10;&#10;{base}&#10;&#10;'
            f'⚠️ Esta coluna já se chamou "Lucro 2025 REAL" e o rótulo estava errado em 20 das '
            f'30 linhas — elas traziam o LTM de 2026, não o exercício fechado de 2025. '
            f'Agora o rótulo e o conteúdo são a mesma coisa em todas.')

        if ln and ln > 0:
            cells[6] = cel(dinheiro(ln),
                f'LUCRO NORMALIZADO — {motor}&#10;&#10;'
                f'NÃO é projeção de 2026. É quanto a empresa ganha num ano REPRESENTATIVO, '
                f'calculado pelo motor do setor: indústria e serviço usam receita atual × margem '
                f'líquida MEDIANA da série; financeira usa ROE mediano × patrimônio; shopping usa '
                f'FFO (FCO − capex); e onde o Partnr publica lucro recorrente, ele é usado direto.'
                f'&#10;&#10;Existe para tirar o ciclo e o não-recorrente da conta: a VALE3 tem '
                f'LTM de R$8,69 bi e normalizado de R$62,03 bi porque o LTM pegou o fundo do '
                f'minério; a KLBN11 idem na celulose.&#10;&#10;Origem: {fonte}. Motor documentado '
                f'em METODOLOGIA_ANALISE.md seção 10.&#10;{base}')
        else:
            cells[6] = cel(VAZIO,
                'LUCRO NORMALIZADO — não calculável&#10;&#10;'
                + ('A margem líquida mediana da série é NEGATIVA (prejuízo em mais da metade dos '
                   'anos válidos), então não existe "ano representativo" positivo para normalizar. '
                   if ln is not None else
                   'A empresa não tem série suficiente na base para nenhum dos motores de '
                   'normalização (menos de 2 anos válidos).')
                + 'Célula vazia é melhor que número errado.&#10;' + base)

        cells[7] = cel(
            (f'<span class="tag {"tag-green" if delta>=0 else "tag-red"}">'
             f'{"+" if delta>=0 else ""}{delta:.0f}%</span>') if delta is not None else VAZIO,
            'DISTÂNCIA DO NORMALIZADO = lucro LTM ÷ lucro normalizado − 1&#10;&#10;'
            '⚠️ MUDOU DE SIGNIFICADO em 06/09/2026. Esta coluna era "crescimento projetado", '
            'comparando dois números que estavam em bases diferentes. Agora é DIAGNÓSTICO DE '
            'CICLO, não previsão.&#10;&#10;'
            'Positivo = a empresa está ganhando ACIMA do que a própria série sugere como normal '
            '(pode ser melhora estrutural, pode ser pico de ciclo). Negativo = está abaixo.&#10;'
            'A KLBN11 com −83% não vai cair 83%: ela está 83% abaixo do seu próprio padrão.&#10;'
            + base)

        cells[8] = cel(f'R$ {br(lpa)}' if lpa else VAZIO,
            (f'LPA NORMALIZADO = lucro normalizado R$ {br(ln/1e9)} bi ÷ {pap/1e6:.0f} mi papéis'
             if lpa else 'LPA NORMALIZADO — sem lucro normalizado positivo')
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
        cells[10] = cel(f'R$ {br(dps)}' if dps else VAZIO,
            (f'DIVIDENDO POR AÇÃO = LPA normalizado R$ {br(lpa)} × payout {po*100:.0f}%'
             if dps else 'DIVIDENDO POR AÇÃO — sem LPA normalizado ou sem payout')
            + f'&#10;&#10;Payout: {rot} (detalhe na coluna Payout).&#10;'
              'É FUNDAMENTO, não deriva do preço: até 06/09/2026 o DPS era calculado como '
              '"DY × cotação", o que fazia o dividendo por ação subir quando a AÇÃO subia. '
              'A relação foi invertida — o DPS sai do lucro, e o DY é que deriva dele.&#10;' + base)

        cells[11] = cel(f'{br(dy,2)}%' if dy else VAZIO,
            (f'DIVIDEND YIELD = Div./Ação R$ {br(dps)} ÷ cotação R$ {br(preco)}'
             if dy else 'DIVIDEND YIELD — sem dividendo por ação calculável')
            + '&#10;&#10;Recalculado a cada atualização de cotação: o dividendo é fixo (vem do '
              'lucro) e o yield é que se move com o preço, como deve ser.&#10;' + base)

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
    print(f"\n{len(log)} linhas regeneradas — colunas 4,5,6,7,8,10,11")
