const INV10_IDS = {
  ALOS3: { t: 656, c: 171 },
};

async function fetchFromInvestidor10(ticker) {
  const ids = INV10_IDS[ticker];
  if (!ids) return null;
  const proxy = url => `https://corsproxy.io/?${encodeURIComponent(url)}`;
  const base = 'https://investidor10.com.br/api';
  try {
    const [cotRes, indRes, dreRes] = await Promise.all([
      fetch(proxy(`${base}/cotacao/ticker/${ids.t}`),                          {signal: AbortSignal.timeout(12000)}).then(r=>r.json()),
      fetch(proxy(`${base}/historico-indicadores/${ids.t}/5/?v=2`),            {signal: AbortSignal.timeout(12000)}).then(r=>r.json()),
      fetch(proxy(`${base}/balancos/balancoresultados/chart/${ids.c}/5/yearly/`), {signal: AbortSignal.timeout(12000)}).then(r=>r.json()),
    ]);

    const preco = cotRes?.price ?? null;

    // Indicadores — index 0 é "Atual"; usar arr[0].key (snake_case) como chave
    const ind = {};
    for (const [, arr] of Object.entries(indRes || {})) {
      if (Array.isArray(arr) && arr[0]?.year === 'Atual') ind[arr[0].key] = arr[0].value;
    }

    // DRE — coluna LTM = row[1] (array de 2 elementos para monetários)
    const parseMoney = s => {
      if (!s || s === 'R$ -' || s === '-') return null;
      const v = parseFloat(s.replace('R$ ', '').replace(/\./g, '').replace(',', '.').trim());
      return isNaN(v) ? null : v;
    };
    const dreMap = {};
    if (Array.isArray(dreRes)) {
      dreRes.slice(1).forEach(row => {
        dreMap[row[0]] = Array.isArray(row[1]) ? row[1][1] : (row[1] ?? null);
      });
    }
    const dv = k => dreMap[k] ?? null;
    const ni = k => (typeof ind[k] === 'number' ? ind[k] : null);

    // Se proxy falhou (403/bloqueado), ind e dreMap ficam vazios e preco=null — cai para fallback
    if (!preco && Object.keys(ind).length === 0 && Object.keys(dreMap).length === 0) return null;

    return {
      preco,
      pl:       ni('p_l'),
      pvp:      ni('p_vp'),
      dy:       ni('dividend_yield_last_12_months'),
      roe:      ni('roe'),
      roic:     ni('roic'),
      mgLiq:    ni('net_margin'),
      mgBruta:  ni('gross_margin'),
      mgEbitda: ni('ebitda_margin'),
      evEbitda:  ni('ev_ebitda'),
      lpa:       ni('lpa'),
      divEbitda: ni('net_debt_ebitda'),
      receita:    parseMoney(dv('Receita Líquida - (R$)')),
      custos:     parseMoney(dv('Custos - (R$)')),
      lucrobruto: parseMoney(dv('Lucro Bruto - (R$)')),
      ebitda:     parseMoney(dv('EBITDA - (R$)')),
      ebit:       parseMoney(dv('EBIT - (R$)')),
      imposto:    parseMoney(dv('Imposto - (R$)')),
      lucrolin:   parseMoney(dv('Lucro Líquido - (R$)')),
      divbruta:   parseMoney(dv('Dívida Bruta - (R$)')),
      divliq:     parseMoney(dv('Dívida Líquida - (R$)')),
    };
  } catch(e) {
    console.warn('[Inv10]', ticker, e);
    return null;
  }
}

// Fetch fundamentais: brapi.dev (com token) → fundamentus.com.br → fetchCotacao (só preço)
async function fetchFundamentais(tickerSA) {
  const ticker = tickerSA.replace('.SA','');

  // ── Estratégia 0: brapi.dev com token (mais rápido, retorna tudo) ──────────
  try {
    const res = await fetch(
      `https://brapi.dev/api/quote/${ticker}?modules=defaultKeyStatistics,financialData&token=${BRAPI_TOKEN}`,
      {signal: AbortSignal.timeout(10000)}
    );
    if (res.ok) {
      const json = await res.json();
      const r = json?.results?.[0];
      if (r?.regularMarketPrice) {
        const fd  = r.financialData        || {};
        const dks = r.defaultKeyStatistics || {};
        const mcap = r.marketCap;
        const mcapStr = mcap
          ? (mcap>=1e12?`R$${(mcap/1e12).toFixed(2).replace('.',',')}T`
            :mcap>=1e9?`R$${(mcap/1e9).toFixed(1).replace('.',',')}B`
            :mcap>=1e6?`R$${(mcap/1e6).toFixed(0)}M`:'—')
          : null;
        const pct = v => (v!=null && !isNaN(v)) ? v*100 : null;
        return {
          preco:    r.regularMarketPrice,
          pl:       r.priceEarnings   || dks.trailingPE  || null,
          pvp:      dks.priceToBook                       || null,
          dy:       pct(dks.dividendYield),
          roe:      pct(fd.returnOnEquity),
          mgLiq:    pct(fd.profitMargins),
          evEbitda: dks.enterpriseToEbitda                || null,
          divPl:    fd.debtToEquity                       || null,
          lpa:      dks.trailingEps   || r.earningsPerShare || null,
          varDia:   r.regularMarketChangePercent          || null,
          mcapStr,
          min52:    r.fiftyTwoWeekLow                     || null,
          max52:    r.fiftyTwoWeekHigh                    || null,
          marketCap: mcap || null,
          // DRE
          receita:    fd.totalRevenue    || null,
          custos:     null,
          lucrobruto: fd.grossProfits    || null,
          ebitda:     fd.ebitda          || null,
          ebit:       fd.operatingIncome || null,
          imposto:    null,
          lucrolin:   null,
          // Balanço
          divbruta: fd.totalDebt || null,
          divliq:   null,
          // Margens
          mgBruta:  pct(fd.grossMargins),
          mgEbitda: pct(fd.ebitdaMargins),
          // Rentabilidade
          roic: pct(fd.returnOnCapitalEmployed) || null,
        };
      }
    }
  } catch {}

  // ── Estratégia 1: fundamentus.com.br ──────────────────────────────────────
  const fundUrl = `https://www.fundamentus.com.br/detalhes.php?papel=${ticker}`;
  const fundProxies = [
    `https://corsproxy.io/?${encodeURIComponent(fundUrl)}`,
    `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(fundUrl)}`,
  ];
  for (const proxy of fundProxies) {
    try {
      const res = await fetch(proxy, {signal: AbortSignal.timeout(12000)});
      if (!res.ok) continue;
      const html = await res.text();
      if (!html.includes('fundamentus')) continue;

      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Constrói mapa label→valor a partir de span.txt:
      // A página alterna label|valor|label|valor; os rótulos de oscilação (Dia, Mês…)
      // não têm valor numérico imediatamente após — apenas pulamos esses.
      const NUMRE = /^-?[\d.,]+%?$/;
      const spans = Array.from(doc.querySelectorAll('span.txt')).map(s => s.textContent.trim());
      const map = {};
      for (let i = 0; i < spans.length - 1; i++) {
        if (NUMRE.test(spans[i+1])) { map[spans[i]] = spans[i+1]; i++; }
      }

      const parseBR = s => {
        if (!s) return null;
        const v = parseFloat(s.replace('%','').replace(/\./g,'').replace(',','.').trim());
        return isNaN(v) ? null : v;
      };
      const findVal = (...keys) => {
        for (const k of keys) {
          const entry = Object.entries(map).find(([lbl]) => lbl.includes(k));
          if (entry) return parseBR(entry[1]);
        }
        return null;
      };

      const preco = findVal('ota');     // Cotação (iso-8859-1 → "Cota??o")
      if (!preco) continue;

      const mcapRaw = findVal('Valor de mercado');
      const mcap    = mcapRaw || null;
      const mcapStr = mcap
        ? (mcap>=1e12?`R$${(mcap/1e12).toFixed(2).replace('.',',')}T`
          :mcap>=1e9 ?`R$${(mcap/1e9) .toFixed(1).replace('.',',')}B`
          :mcap>=1e6 ?`R$${(mcap/1e6) .toFixed(0)}M`:'—')
        : null;

      const evEbitdaVal = findVal('EV / EBITDA');
      const valorFirma  = findVal('Valor da firma');      // EV em BRL
      const divLiqAbs   = findVal('v. L');                // "D?v. L?quida" (BRL absoluto)
      // Dív.Líq/EBITDA = Dív.Líq / (EV / EV_EBITDA)
      const divEbitda = (valorFirma && evEbitdaVal && evEbitdaVal > 0 && divLiqAbs != null)
        ? divLiqAbs / (valorFirma / evEbitdaVal)
        : null;

      return {
        preco,
        pl:        findVal('P/L'),
        pvp:       findVal('P/VP'),
        dy:        findVal('Div. Yield'),
        roe:       findVal('ROE'),
        mgLiq:     findVal('Marg. L'),
        evEbitda:  evEbitdaVal,
        divPl:     findVal('v L'),
        divEbitda,
        lpa:       findVal('LPA'),
        varDia:    null,
        mcapStr,
        min52:     findVal('Min 52'),
        max52:     findVal('Max 52'),
        marketCap: mcap,
        receita:null, custos:null, lucrobruto:null,
        ebitda:null, ebit:null, imposto:null, lucrolin:null,
        divbruta:null, divliq:null,
        mgBruta:null, mgEbitda:null, roic:null,
      };
    } catch { continue; }
  }

  // ── Estratégia 2: brapi.dev básico com token — retorna preço + campos parciais ──
  try {
    const br = await fetch(`https://brapi.dev/api/quote/${ticker}?token=${BRAPI_TOKEN}`, {signal: AbortSignal.timeout(8000)});
    if (br.ok) {
      const j = await br.json();
      const r = j?.results?.[0];
      if (r?.regularMarketPrice) {
        const mcap = r.marketCap;
        const mcapStr = mcap
          ? (mcap>=1e12?`R$${(mcap/1e12).toFixed(2).replace('.',',')}T`
            :mcap>=1e9?`R$${(mcap/1e9).toFixed(1).replace('.',',')}B`
            :mcap>=1e6?`R$${(mcap/1e6).toFixed(0)}M`:'—')
          : null;
        return {preco:r.regularMarketPrice,pl:r.priceEarnings||null,pvp:null,dy:null,
                roe:null,mgLiq:null,evEbitda:null,divPl:null,divEbitda:null,
                lpa:r.earningsPerShare||null,varDia:r.regularMarketChangePercent||null,
                mcapStr,min52:r.fiftyTwoWeekLow||null,max52:r.fiftyTwoWeekHigh||null,
                marketCap:mcap||null,
                receita:null,custos:null,lucrobruto:null,ebitda:null,ebit:null,
                imposto:null,lucrolin:null,divbruta:null,divliq:null,
                mgBruta:null,mgEbitda:null,roic:null};
      }
    }
  } catch {}

  // ── Estratégia 3: só preço via Yahoo (último recurso) ─────────────────────
  try {
    const p = await fetchCotacao(tickerSA);
    if(p) return {preco:p,pl:null,pvp:null,dy:null,roe:null,mgLiq:null,evEbitda:null,
                  divPl:null,divEbitda:null,varDia:null,mcapStr:null,min52:null,max52:null,lpa:null,marketCap:null,
                  receita:null,custos:null,lucrobruto:null,ebitda:null,ebit:null,
                  imposto:null,lucrolin:null,divbruta:null,divliq:null,
                  mgBruta:null,mgEbitda:null,roic:null};
  } catch {}
  return null;
}

// Renderiza uma linha com os dados fundamentais
