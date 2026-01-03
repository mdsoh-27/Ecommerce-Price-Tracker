"""
Flipkart web scraper with retry logic and error handling
"""
import requests
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)

def scrape_flipkart(product_name, timeout=10, max_retries=3, retry_delay=2):
    """
    Scrape product prices from Flipkart with retry logic
    
    Args:
        product_name: Product search query
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        List of product dictionaries with name and price
    """
    query = product_name.replace(" ", "+")
    url = f"https://www.flipkart.com/search?q={query}"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[SCRAPER] Fetching Flipkart data for '{product_name}' (attempt {attempt + 1}/{max_retries})")
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Try multiple CSS selectors as fallback
                product_blocks = soup.select("div._75nlfW, div._1AtVbE, div.cPHDOP")
                
                if not product_blocks:
                    logger.warning(f"[SCRAPER] No product blocks found for '{product_name}'")
                    return []
                
                results = []
                for block in product_blocks:
                    # Try multiple selectors for name
                    name_element = block.select_one(
                        "a.IRpwTa, a.s1Q9rs, div.KzDlHZ, ._4rR01T, a.wjcEIp"
                    )
                    
                    # Try multiple selectors for price
                    price_element = block.select_one(
                        "div._30jeq3, div.Nx9bqj, div._1_WHN1, div._25b18c"
                    )
                    
                    if name_element and price_element:
                        try:
                            price_text = price_element.text.replace("₹", "").replace(",", "").strip()
                            # Extract numeric value
                            price_value = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                            
                            if price_value:
                                results.append({
                                    "name": name_element.text.strip(),
                                    "price": price_value
                                })
                        except Exception as e:
                            logger.warning(f"[SCRAPER] Error parsing product data: {e}")
                            continue
                
                logger.info(f"[SCRAPER] Found {len(results)} products from Flipkart")
                return results[:10]  # Limit for performance
            
            elif response.status_code == 429:
                # Rate limited
                logger.warning(f"[SCRAPER] Rate limited by Flipkart (429). Retrying after {retry_delay * 2}s...")
                time.sleep(retry_delay * 2)
                continue
            
            else:
                logger.error(f"[SCRAPER] Failed to fetch Flipkart page (status: {response.status_code})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return []
        
        except requests.exceptions.Timeout:
            logger.error(f"[SCRAPER] Request timeout for '{product_name}'")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return []
        
        except requests.exceptions.ConnectionError:
            logger.error(f"[SCRAPER] Connection error for '{product_name}'")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return []
        
        except Exception as e:
            logger.error(f"[SCRAPER] Unexpected error while scraping Flipkart: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return []
    
    logger.error(f"[SCRAPER] All retry attempts failed for '{product_name}'")
    return []
