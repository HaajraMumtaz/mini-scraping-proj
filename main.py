import requests
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.strip()
    
    # remove citation markers like [12]
    text = re.sub(r"\[.*?\]", "", text)
    
    # remove weird spaces
    text = text.replace("\xa0", " ")
    
    return text
def clean_country(text: str) -> str:
    text = clean_text(text)
    
    # remove text inside parentheses
    text = re.sub(r"\(.*?\)", "", text)
    
    return text.strip()
def clean_number(text: str):
    text = clean_text(text)
    text = text.replace(",", "")
    
    # handle missing values
    if text in ["", "—", "-", "N/A"]:
        return None
    
    try:
        return int(text)
    except ValueError:
        return None

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_page(url):
    headers = {
    "User-Agent": "...",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

    response = requests.get(url, timeout=10,headers=headers)
    response.raise_for_status()
    return response.text

def find_table_by_caption(soup, target_keywords):
    tables = soup.find_all("table")
    for table in tables:
        caption = table.find("caption")
        if caption:
            text = caption.get_text(strip=True).lower()
            if any(keyword in text for keyword in target_keywords):
                print("FOUND TABLE:", caption.get_text(strip=True))
                return table
    raise Exception("No matching table found.")

def parse_gdp_table(table):
    rows = table.find_all("tr")
    data = []
    ix=0
    # Extract header positions dynamically
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all("th")]

    rank_idx = headers.index("rank") if "rank" in headers else None
    country_idx = None
    gdp_idx = None

    # Detect country and gdp columns
    for i, h in enumerate(headers):
        if "country" in h:
            country_idx = i
        if "gdp" in h and ("million" in h or "$" in h):
            gdp_idx = i


    for row in rows[1:]:  
        cols = row.find_all(["td", "th"])
        cols = [c.get_text(" ", strip=True) for c in cols]

        if len(cols) < 3:
            continue

        rank = ix
        ix+=1
        country = cols[0]
        gdp_raw = cols[2]

        # Clean GDP number
        gdp_clean = ''.join(ch for ch in gdp_raw if ch.isdigit())

        data.append({
            "rank": rank,
            "country": country,
            "gdp_usd_million": int(gdp_clean) if gdp_clean else None
        })

    for item in data[1:10]:
        print(item)

url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
html = fetch_page(url)
soup = BeautifulSoup(html, "html.parser")

table = find_table_by_caption(
    soup,
    ["gdp", "nominal", "million"]  # keywords
)

results = parse_gdp_table(table)


