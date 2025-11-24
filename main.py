import requests
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

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
target_table = tables[3]

df = pd.read_html(str(target_table))[0]

print(df.head())