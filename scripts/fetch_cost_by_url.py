#!/usr/bin/env python3
"""
Tata 1mg Medicine MRP Crawler
Fetches the MRP of a medicine from a 1mg product URL.

Usage:
    python 1mg_crawler.py <url>
    python 1mg_crawler.py https://www.1mg.com/drugs/dolo-650-tablet-81458

Requirements:
    pip install requests beautifulsoup4
    (Optional, for JS-rendered pages) pip install selenium webdriver-manager
"""

import sys
import re
import json
import argparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.1mg.com/",
}


# ─── Helper: recursively search a dict/list for a key ────────────────────────

def find_key(d, key):
    """Recursively search nested dicts/lists for a given key."""
    if isinstance(d, dict):
        if key in d:
            return d[key]
        for v in d.values():
            result = find_key(v, key)
            if result is not None:
                return result
    elif isinstance(d, list):
        for item in d:
            result = find_key(item, key)
            if result is not None:
                return result
    return None


# ─── Strategy 1: Parse HTML directly ─────────────────────────────────────────

def extract_mrp_from_html(soup: BeautifulSoup) -> str | None:
    """Try various extraction strategies used by 1mg."""

    # 1. __NEXT_DATA__ — most reliable; contains raw product data before rendering
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    if next_data_tag:
        try:
            data = json.loads(next_data_tag.string)
            page_props = data.get("props", {}).get("pageProps", {})
            mrp = find_key(page_props, "mrp") or find_key(page_props, "MRP")
            if mrp:
                return str(mrp)
        except (json.JSONDecodeError, AttributeError):
            pass

    # 2. JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    offers = item.get("offers", {})
                    if isinstance(offers, dict):
                        # Prefer highPrice (MRP) over price (discounted)
                        price = offers.get("highPrice") or offers.get("price")
                        if price:
                            return str(price)
                    elif isinstance(offers, list) and offers:
                        price = offers[0].get("highPrice") or offers[0].get("price")
                        if price:
                            return str(price)
        except (json.JSONDecodeError, AttributeError):
            continue

    # 3. Common 1mg CSS class names (may change over time)
    selectors = [
        {"class": re.compile(r"price-tag", re.I)},
        {"class": re.compile(r"DrugHeader__price", re.I)},
        {"class": re.compile(r"ProductCard__price", re.I)},
        {"class": re.compile(r"style__price-tag", re.I)},
        {"class": re.compile(r"PriceBox", re.I)},
        {"itemprop": "price"},
    ]
    for sel in selectors:
        tag = soup.find(attrs=sel)
        if tag:
            text = tag.get_text(strip=True)
            match = re.search(r"[\u20B9₹]?\s*(\d[\d,]*(?:\.\d{1,2})?)(?!\d|%)", text)
            if match:
                return match.group(1).replace(",", "")

    # 4. Scan all text for "MRP ₹xxx" pattern
    full_text = soup.get_text()
    match = re.search(
        r"MRP\s*[:\-]?\s*[\u20B9₹]?\s*(\d[\d,]*(?:\.\d{1,2})?)(?!\d|%)",
        full_text,
        re.I,
    )
    if match:
        return match.group(1).replace(",", "")

    # 5. Generic ₹ price scan — last resort
    # Negative lookahead (?!\d|%) prevents "149.02" from bleeding into "149.029%"
    prices = re.findall(r"[\u20B9₹]\s*(\d[\d,]*(?:\.\d{1,2})?)(?!\d|%)", full_text)
    if prices:
        return prices[0].replace(",", "")

    return None


# ─── Strategy 2: Selenium fallback (for JS-rendered content) ──────────────────

def extract_mrp_with_selenium(url: str) -> str | None:
    """Use headless Chrome via Selenium if requests doesn't work."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print(
            "[!] Selenium not installed. Run:\n"
            "    pip install selenium webdriver-manager"
        )
        return None

    print("[*] Trying Selenium (headless Chrome)...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'MRP')]"))
            )
        except Exception:
            pass  # Continue even if wait times out

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        return extract_mrp_from_html(soup)
    finally:
        driver.quit()


# ─── Main crawler ──────────────────────────────────────────────────────────────

def get_mrp(url: str, use_selenium: bool = False) -> dict:
    """
    Fetch the MRP of a medicine from a 1mg URL.

    Args:
        url: Full 1mg product URL
        use_selenium: Force Selenium even if requests succeeds

    Returns:
        dict with keys: url, medicine_name, mrp, currency, source, error
    """
    if not url.startswith("http"):
        url = "https://" + url

    result = {
        "url": url,
        "medicine_name": url.rstrip("/").split("/")[-1].replace("-", " ").title(),
        "mrp": None,
        "currency": "INR (₹)",
        "source": None,
        "error": None,
    }

    # ── Try requests first ──
    if not use_selenium:
        print(f"[*] Fetching: {url}")
        try:
            session = requests.Session()
            # Hit homepage first to get cookies (mimics a real browser session)
            session.get("https://www.1mg.com", headers=HEADERS, timeout=10)
            resp = session.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            title_tag = soup.find("title")
            if title_tag:
                result["medicine_name"] = title_tag.get_text(strip=True).split("|")[0].strip()

            mrp = extract_mrp_from_html(soup)
            if mrp:
                result["mrp"] = mrp
                result["source"] = "requests + BeautifulSoup"
                return result
            else:
                print("[!] Could not find MRP in static HTML. Page may be JS-rendered.")
        except requests.RequestException as e:
            result["error"] = str(e)
            print(f"[!] Request failed: {e}")

    # ── Fallback to Selenium ──
    mrp = extract_mrp_with_selenium(url)
    if mrp:
        result["mrp"] = mrp
        result["source"] = "Selenium (headless Chrome)"
        result["error"] = None
    else:
        result["error"] = (
            result.get("error") or "MRP not found. Page structure may have changed."
        )

    return result


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Crawl Tata 1mg to get the MRP of a medicine."
    )
    parser.add_argument("url", help="1mg product URL")
    parser.add_argument(
        "--selenium",
        action="store_true",
        help="Use Selenium (headless Chrome) instead of requests",
    )
    args = parser.parse_args()

    result = get_mrp(args.url, use_selenium=args.selenium)

    print("\n" + "=" * 50)
    print(f"  Medicine : {result['medicine_name']}")
    if result["mrp"]:
        print(f"  MRP      : ₹{result['mrp']}")
        print(f"  Currency : {result['currency']}")
        print(f"  Source   : {result['source']}")
    else:
        print(f"  MRP      : Not found")
        print(f"  Error    : {result['error']}")
    print(f"  URL      : {result['url']}")
    print("=" * 50)

    return 0 if result["mrp"] else 1


if __name__ == "__main__":
    sys.exit(main())