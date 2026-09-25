import asyncio
import os
import re
from datetime import datetime, timezone
from apify import Actor
import httpx
from bs4 import BeautifulSoup


async def main():
    async with Actor:
        actor_input = await Actor.get_input()
        max_results = actor_input.get('maxResults', 50)
        sector = actor_input.get('sector', 'All')
        min_market_cap = actor_input.get('minMarketCap', 0)
        max_pe = actor_input.get('maxPE', 50)
        min_dividend_yield = actor_input.get('minDividendYield', 0)
        min_roe = actor_input.get('minROE', 0)
        
        # Build screen URL based on filters (use All-Stocks as base, filter in-memory)
        screen_url = 'https://www.screener.in/screens/1/All-Stocks/'
        
        # Setup proxy
        proxy_password = os.environ.get("APIFY_PROXY_PASSWORD")
        proxy_url = f"http://auto:{proxy_password}@proxy.apify.com:8000" if proxy_password else None
        
        # Create HTTP client
        client_kwargs = {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'timeout': 30.0,
            'follow_redirects': True
        }
        if proxy_url:
            client_kwargs['proxy'] = proxy_url
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            # Fetch screen page
            resp = await client.get(screen_url)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract company links from table
            company_links = []
            for link in soup.find_all('a', href=re.compile(r'/company/[^/]+/')):
                href = link.get('href')
                if href and href.startswith('/company/'):
                    full_url = f"https://www.screener.in{href}"
                    if full_url not in company_links:
                        company_links.append(full_url)
            
            count = 0
            scraped_companies = []
            
            for company_url in company_links:
                if count >= max_results:
                    break
                
                try:
                    # Rate limiting - delay between requests
                    await asyncio.sleep(2)
                    
                    # Fetch company detail page
                    detail_resp = await client.get(company_url)
                    detail_resp.raise_for_status()
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    
                    # Extract company name
                    h1 = detail_soup.find('h1')
                    company_name = h1.get_text(strip=True) if h1 else None
                    
                    # Extract key metrics
                    metrics = {}
                    for span in detail_soup.find_all('span', class_='name'):
                        metric_name = span.get_text(strip=True)
                        # Find value (next sibling or parent)
                        parent = span.parent
                        if parent:
                            value_span = parent.find('span', class_='number')
                            if value_span:
                                metrics[metric_name] = value_span.get_text(strip=True)
                    
                    # Extract quarterly results table
                    quarterly_results = []
                    for table in detail_soup.find_all('table', class_='data-table'):
                        headers_row = table.find('thead')
                        if headers_row:
                            headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
                            if 'Sales' in headers or 'Net Profit' in headers:
                                for row in table.find('tbody').find_all('tr')[:4]:  # Last 4 quarters
                                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                                    if cells and len(cells) == len(headers):
                                        quarterly_results.append(dict(zip(headers, cells)))
                                break
                    
                    # Parse numeric values for filtering
                    market_cap_str = metrics.get('Market Cap', '0')
                    market_cap_val = float(re.sub(r'[^\d.]', '', market_cap_str.split('Cr')[0]) if 'Cr' in market_cap_str else '0')
                    
                    pe_str = metrics.get('Stock P/E', '0')
                    pe_val = float(re.sub(r'[^\d.]', '', pe_str)) if pe_str and pe_str != '-' else 999
                    
                    div_str = metrics.get('Dividend Yield', '0')
                    div_val = float(re.sub(r'[^\d.]', '', div_str.replace('%', ''))) if div_str and div_str != '-' else 0
                    
                    roe_str = metrics.get('ROCE', '0')
                    roe_val = float(re.sub(r'[^\d.]', '', roe_str.replace('%', ''))) if roe_str and roe_str != '-' else 0
                    
                    # Apply filters
                    if market_cap_val < min_market_cap:
                        continue
                    if pe_val > max_pe:
                        continue
                    if div_val < min_dividend_yield:
                        continue
                    if roe_val < min_roe:
                        continue
                    
                    # Push result
                    result = {
                        'url': company_url,
                        'companyName': company_name,
                        'marketCap': metrics.get('Market Cap'),
                        'currentPrice': metrics.get('Current Price'),
                        'stockPE': metrics.get('Stock P/E'),
                        'bookValue': metrics.get('Book Value'),
                        'dividendYield': metrics.get('Dividend Yield'),
                        'roe': metrics.get('ROCE'),
                        'quarterlyResults': quarterly_results[:4] if quarterly_results else None,
                        'scrapedAt': datetime.now(timezone.utc).isoformat()
                    }
                    
                    await Actor.push_data(result)
                    count += 1
                    
                except Exception as e:
                    Actor.log.error(f"Error scraping {company_url}: {e}")
                    continue
            
            Actor.log.info(f"Scraped {count} companies")
