#!/usr/bin/env python3
"""Consolida o lucro TRIMESTRAL das respostas do MCP Partnr em analise/trimestrais.json.

POR QUE EXISTE — 14/09/2026. O usuário pediu para "garantir que estamos estimando o lucro
projetado certo". A auditoria encontrou o IRBR3 com R$ 330 mi declarados para 2026 contra
R$ 90 mi realizados no 1º semestre, com PREJUÍZO no 2T26. O número vinha do relatório de
25/08/2026 e ninguém tinha como saber que ele havia envelhecido: `LUCRO_2026_DECLARADO` é
uma constante digitada, e constante digitada não avisa quando o fato muda.

Este coletor + `checar_lucro_declarado.py` fecham esse buraco: o trimestre publicado passa a
ser confrontado com o número declarado, e a divergência aparece.

USO — as respostas do Partnr são grandes demais para o contexto, então o harness as salva em
arquivo. Rode a ferramenta por ticker e passe os arquivos:

    companies_reports(symbol=TICKER, section=INCOME_STATEMENT,
                      frequency=QUARTERLY, latest_by_reference_date=True)
    python3 scripts/coletar_trimestrais.py IRBR3=arq1.txt BBSE3=arq2.txt ...

⚠️ O TICKER É INFORMADO POR FORA, nunca deduzido do conteúdo. Foi a lição do coletor de P/L
(seção 33): deduzir ticker do payload fez a VIVA3 herdar a série da BBSE3.
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DEST = RAIZ / 'analise/trimestrais.json'
# A linha de lucro muda de nome conforme o setor (banco, seguradora, indústria). A ordem é
# de preferência: o lucro ATRIBUÍVEL AO CONTROLADOR é o que o acionista recebe.
CHAVES = ['CONTROLLING_NET_INCOME', 'NET_INCOME', 'NET_PROFIT']


def ler(arq):
    d = json.load(open(arq))
    out = {}
    for r in d:
        if r.get('frequency') != 'QUARTERLY' or r.get('aggregation') != 'CONSOLIDATED':
            continue
        dados = r.get('data') or {}
        for k in CHAVES:
            if dados.get(k) is not None:
                out[r['reference_date'][:10]] = dados[k]
                break
    return out


def main(args):
    try:
        base = json.loads(DEST.read_text())
    except Exception:
        base = {'fonte': 'MCP Partnr — companies_reports INCOME_STATEMENT QUARTERLY CONSOLIDATED',
                'tickers': {}}
    for a in args:
        if '=' not in a:
            raise SystemExit(f'esperado TICKER=arquivo, veio {a!r}')
        t, arq = a.split('=', 1)
        tri = ler(arq)
        if not tri:
            print(f'{t}: nenhum trimestre consolidado no arquivo — pulado')
            continue
        base['tickers'][t] = {'trimestres': dict(sorted(tri.items()))}
        ult = sorted(tri)[-1]
        print(f'{t}: {len(tri)} trimestres, último {ult} = R$ {tri[ult]/1e6:.1f} mi')
    from datetime import date
    base['coletado_em'] = date.today().isoformat()
    DEST.write_text(json.dumps(base, ensure_ascii=False, indent=1))
    print(f'\n{len(base["tickers"])} tickers → {DEST.relative_to(RAIZ)}')


if __name__ == '__main__':
    main(sys.argv[1:])
