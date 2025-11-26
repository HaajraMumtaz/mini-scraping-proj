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

def fetch_page(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            logging.error(f"Failed to fetch {url}: HTTP {response.status_code}")
            return None

        logging.info(f"Successfully fetched {url}")
        return response.text

    except requests.RequestException as e:
        logging.error(f"Request error for {url}: {e}")
        return None


html = fetch_page("https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)")

soup =BeautifulSoup(html,"html.parser")
tables=soup.find_all("table",{"class": "wikitable"})
target_table = None
for t in tables:
    cap = t.find("caption")
    if cap and "GDP" in cap.get_text():
        target_table = t
        break

if target_table is None:
    raise Exception("Could not find GDP table on the page.")
results=[]
rows=target_table.find_all("tr")
data_rows=rows[1:]
for row in data_rows:
    cells = row.find_all("td")
    if len(cells) < 3:
        continue
    rank = clean_number(cells[0].get_text())
    country = clean_country(cells[1].get_text())
    gdp = clean_number(cells[2].get_text())

    if country and gdp:
        results.append({
            "rank": rank,
            "country": country,
            "gdp_usd_million": gdp
        })

# Preview first few
for r in results[:5]:
    print(r)


