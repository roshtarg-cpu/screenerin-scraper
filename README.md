# Screener.in Stock Scraper - Indian Stock Market Data Extractor

Extract comprehensive financial data from Screener.in, India's premier stock screening platform. Built for AI agents, data analysts, and investors using Claude, ChatGPT, and automated workflows via Apify MCP.

## Features

- **Comprehensive Stock Data**: Market cap, P/E ratios, book value, dividend yield, ROE/ROCE metrics
- **Quarterly Financial Results**: Last 4 quarters of sales, profit, and operating metrics
- **Flexible Screening**: Works with any Screener.in screen URL - sector screens, custom filters, value stocks
- **AI-Ready Output**: Clean JSON format compatible with Claude Code, ChatGPT, and AI agent pipelines
- **Fast & Reliable**: HTTP-based extraction, no browser overhead, LIGHT protection

## Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `screenUrl` | String | Yes | Screener.in screen URL (e.g., `https://www.screener.in/screens/1/All-Stocks/`) |
| `maxResults` | Integer | Yes | Maximum number of stocks to scrape (1-500, default: 50) |
| `proxyConfiguration` | Object | No | Apify proxy settings (residential recommended) |

## Output Schema

```json
{
  "url": "https://www.screener.in/company/AQYLON/",
  "companyName": "Aqylon Nexus Ltd",
  "marketCap": "₹ 1,234 Cr.",
  "currentPrice": "₹ 456",
  "stockPE": "23.4",
  "bookValue": "₹ 123",
  "dividendYield": "1.2%",
  "roe": "15.3%",
  "quarterlyResults": [
    {"Period": "Mar 2026", "Sales": "234", "Net Profit": "45"},
    ...
  ],
  "scrapedAt": "2026-09-25T22:48:00.000Z"
}
```

## Use Cases

1. **AI-Powered Stock Research**: Feed data into Claude/ChatGPT for investment analysis and recommendations
2. **Portfolio Screening**: Identify undervalued stocks using P/E, book value, and ROE filters
3. **Quarterly Trend Analysis**: Track revenue and profit trends across sectors
4. **MCP Integration**: Use with Apify MCP server for real-time stock data in AI agent workflows
5. **Financial Dashboards**: Build automated reporting on Indian equity markets
6. **Value Investing**: Screen for low P/E, high dividend yield stocks
7. **Sector Comparison**: Compare metrics across IT, pharma, banking, and manufacturing sectors

## Popular Screener.in Screens

- **All Stocks**: `https://www.screener.in/screens/1/All-Stocks/`
- **Value Stocks**: `https://www.screener.in/screens/71940/value-stocks/`
- **High Dividend**: `https://www.screener.in/screens/71944/high-dividend/`
- **Low P/E**: `https://www.screener.in/screens/71947/low-pe-stocks/`
- **IT Sector**: `https://www.screener.in/screens/71952/it-sector/`

## Pricing

- **Per Stock**: $0.005 (5 cents per 1000 stocks)
- **Startup Fee**: $0.05 per run
- **Example**: 100 stocks = $0.05 + (100 × $0.005) = $0.55

## AI Agent Integration

### Claude Code / ChatGPT
```python
# Via Apify MCP
stocks = apify.run_actor("fervent_bus/screenerin-scraper", {
    "screenUrl": "https://www.screener.in/screens/1/All-Stocks/",
    "maxResults": 50
})

# Analyze with Claude
claude.ask(f"Which of these stocks are undervalued? {stocks}")
```

### API Call
```bash
curl -X POST "https://api.apify.com/v2/acts/fervent_bus~screenerin-scraper/runs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"screenUrl":"https://www.screener.in/screens/1/All-Stocks/","maxResults":50}'
```

## FAQ

**Q: Can I scrape custom screens?**  
A: Yes - any Screener.in URL works. Create your custom screen on screener.in, copy the URL, and pass it as `screenUrl`.

**Q: How current is the data?**  
A: Data is scraped live from Screener.in at runtime. Metrics reflect the current session's values.

**Q: Does it work with paid Screener.in accounts?**  
A: The scraper uses public Screener.in data. Premium features (detailed financials, alerts) require manual access.

**Q: Can I get historical data?**  
A: The actor extracts the last 4 quarters of financial results visible on company pages. For longer history, run periodically and store results.

**Q: Compatible with AI agents?**  
A: Yes - designed for Claude, ChatGPT, and MCP workflows. Output is clean JSON, no post-processing needed.

## Technical Details

- **Technology**: Python 3.11 + httpx + BeautifulSoup (no browser)
- **Protection Level**: LIGHT (government/financial site, stable selectors)
- **Proxy**: Apify residential proxy (auto-configured)
- **Runtime**: ~2-5 seconds per stock

## Support

Issues? Found a bug? Create an issue on [GitHub](https://github.com/roshtarg-cpu/screenerin-scraper) or contact via Apify platform.

---

*Compatible with Claude, ChatGPT & AI agents via Apify MCP. Built for automated stock research and investment analysis.*
