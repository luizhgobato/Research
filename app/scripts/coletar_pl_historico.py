#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════════════════════════════
# COLETOR DO P/L DE 10 ANOS — analise/pl_historico.json
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pedido do usuário: "eu gostaria do P/L de 10 anos para empresas maduras, mesmo que tenhamos
# que pegar de outra fonte". Não precisou de outra fonte: a Partnr TEM a série longa, em
# `companies_valuationRatios` com frequency=TTM — o que ela não tem é ANNUAL (404) nem
# QUARTERLY (404). O TTM devolve UMA REVISÃO POR DIA, o que dá respostas de 0,5 a 2,7 MB por
# empresa e estourava o limite da ferramenta.
#
# A saída: cada resposta é salva num .txt pelo próprio harness, e este script lê os arquivos
# do disco, extrai o ÚLTIMO registro de cada ano civil e grava um JSON pequeno. O conteúdo
# gigante nunca entra no contexto.
#
# ⚠️ IDENTIFICAÇÃO POR CONTEÚDO, NÃO POR ORDEM DE CHAMADA. Os arquivos não carregam o símbolo
# da empresa, e casar por ordem de chamada ou por data de modificação quebra em silêncio na
# primeira vez que uma chamada falhar no meio do lote. Cada arquivo é identificado casando o
# P/L de 2025 e 2026 com o que o HIST_SEED já tem — se não casar com ninguém dentro da
# tolerância, o arquivo é reportado como não identificado em vez de ser atribuído a alguém.
#
# ⚠️ CLASSE DE AÇÃO. A API separa PRICE_TO_EARNINGS_CS (ordinária) e _PS (preferencial), e a
# escolha errada coloca o múltiplo da PN sobre o preço da ON. O casamento por conteúdo resolve
# isso sozinho: a série que bate com o HIST_SEED do ticker é a da classe certa.
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / 'analise' / 'pl_historico.json'
TOL = 0.06          # 6% de tolerância no casamento (a base arredonda em 2 casas)


def series_do_arquivo(p):
    """{chave_da_classe: {ano: valor}} — último registro de cada ano civil."""
    try:
        d = json.loads(Path(p).read_text(encoding='utf-8').strip())
    except Exception:
        return {}
    out = {}
    for chave, freqs in d.items():
        serie = next(iter(freqs.values()), [])
        por = {}
        for it in serie:
            v = it.get('value')
            if v is None or not (0 < v < 200):
                continue
            rd = it['reference_date'][:10]
            ano = int(rd[:4])
            if ano not in por or rd > por[ano][0]:
                por[ano] = (rd, v)
        if por:
            out[chave] = {a: round(por[a][1], 2) for a in sorted(por)}
    return out


def main():
    """Uso: coletar_pl_historico.py TICKER=arquivo.txt [TICKER=arquivo.txt ...]

    ⚠️ O TICKER É INFORMADO, NÃO INFERIDO. A primeira versão tentava descobrir de quem era
    cada arquivo casando o P/L com o HIST_SEED, e errou de três formas diferentes: a VIVA3
    (com um único ano de P/L na base) reivindicou a série da BBSE3; a série _PS do arquivo do
    ITUB — que é a ITUB4, nem está no Radar — foi atribuída à MULT3; e a _CS do arquivo da
    BBSE foi parar na PSSA3. Séries de P/L de empresas diferentes se parecem o bastante para
    o casamento numérico ser uma má ideia. Quem chama a API sabe o que pediu; basta dizer.

    O que CONTINUA sendo decidido por conteúdo é a CLASSE DE AÇÃO: a resposta traz
    PRICE_TO_EARNINGS_CS (ordinária) e _PS (preferencial), e escolher errado põe o múltiplo
    da PN sobre o preço da ON. Fica a série cujo P/L de 2026 chega mais perto do que o
    HIST_SEED já tem para aquele ticker — que é o mesmo dado, pela mesma fonte, do mesmo ano.
    """
    src = (RAIZ / 'scripts/motor_teto.py').read_text(encoding='utf-8')
    M = {}
    exec(src[:src.index('if __name__')], M)
    H = M['carregar']()

    antigo = {}
    if SAIDA.exists():
        antigo = json.loads(SAIDA.read_text(encoding='utf-8')).get('tickers', {})

    novos, avisos = [], []
    for arg in sys.argv[1:]:
        t, _, caminho = arg.partition('=')
        if t not in H:
            avisos.append(f'{t}: não está no HIST_SEED'); continue
        # ⚠️ ANCORA NO ANO FECHADO (2025), não em 2026. O HIST_SEED registra o P/L do
        # FECHAMENTO do ano; a série TTM de 2026 tem data-base 30/06 e o preço mudou desde
        # então. No PETR4 a diferença era de 11% em 2026 (4,20 contra 4,67) e ZERO em 2025
        # (5,41 nos dois) — âncora num ano incompleto reprovava a série certa.
        ano_ref = 2025 if (H[t].get(2025) or {}).get('pl') else 2026
        ref = (H[t].get(ano_ref) or {}).get('pl')
        series = series_do_arquivo(caminho)
        if not series:
            avisos.append(f'{t}: arquivo vazio ou ilegível ({Path(caminho).name})'); continue
        # classe certa = a que reproduz o P/L que a base já registra para este ticker
        melhor, dist_melhor = None, None
        for chave, serie in series.items():
            alvo = serie.get(ano_ref)
            if alvo is None or ref is None:
                continue
            d = abs(alvo - ref) / abs(ref)
            if dist_melhor is None or d < dist_melhor:
                melhor, dist_melhor = (chave, serie), d
        if not melhor:
            avisos.append(f'{t}: nenhuma série utilizável'); continue
        chave, serie = melhor
        # A TOLERÂNCIA SERVE PARA ESCOLHER ENTRE CLASSES. Quando a empresa só tem uma classe
        # (BBSE3, por exemplo, só tem ON), não há o que escolher e recusar a série por ela
        # divergir do HIST_SEED joga fora o dado por causa de uma diferença de definição ou de
        # data de coleta entre duas fontes da mesma API. Nesse caso grava e AVISA.
        if dist_melhor > TOL:
            if len(series) > 1:
                avisos.append(f'⚠️ {t}: {len(series)} classes e a mais próxima ({chave}) diverge '
                              f'{dist_melhor*100:.0f}% do P/L da base — NÃO gravado, risco de '
                              f'pegar a classe errada')
                continue
            avisos.append(f'ℹ️ {t}: série única ({chave}), diverge {dist_melhor*100:.0f}% do P/L '
                          f'de {ano_ref} do HIST_SEED — gravada mesmo assim')
        antigo[t] = {'id': chave, 'anos': {str(a): v for a, v in serie.items()}}
        novos.append((t, chave, serie))

    SAIDA.write_text(json.dumps({
        'fonte': 'MCP Partnr (B3/CVM) · companies_valuationRatios · frequency=TTM · '
                 'último registro de cada ano civil',
        'coletado_em': '2026-09-14',
        'tickers': antigo}, ensure_ascii=False, indent=1), encoding='utf-8')

    print(f'{len(novos)} gravados nesta passada · {len(antigo)} no arquivo')
    for t, chave, serie in novos:
        vals = sorted(serie.values())
        print(f"  {t:8} {chave:26} {len(serie):>2} anos  {min(serie)}-{max(serie)}  "
              f"mediana {vals[len(vals)//2]:.1f}x")
    for a in avisos:
        print('  ' + a)


if __name__ == '__main__':
    main()
