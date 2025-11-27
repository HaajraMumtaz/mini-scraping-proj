import requests
import logging
from bs4 import BeautifulSoup
import pandas as pd
import re

# ---------------------------------------
# Logging Configuration
# ---------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ---------------------------------------
#  Text Cleaning Helpers
# ---------------------------------------
def clean_text(text: str) -> str:
    """
    Clean generic text by:
      - removing citation markers (e.g., [12])
      - removing non-breaking spaces
      - stripping whitespace
    """
    if not text:
        return ""
    
    logging.debug(f"Cleaning text: {text}")

    text = text.strip()
    text = re.sub(r"\[.*?\]", "", text)      # Remove citations like [12]
    text = text.replace("\xa0", " ")         # Replace weird spaces
    return text


def clean_country(text: str) -> str:
    """
    Clean country names by:
      - cleaning text
      - removing parentheses content (e.g., 'China (Mainland)' → 'China')
    """
    logging.debug(f"Cleaning country: {text}")
    text = clean_text(text)
    text = re.sub(r"\(.*?\)", "", text)      # Remove text inside parentheses
    return text.strip()


def clean_number(text: str):
    """
    Convert a string to an integer:
      - removes commas
      - converts to int
      - returns None for invalid or missing values
    """
    logging.debug(f"Cleaning number: {text}")
    text = clean_text(text).replace(",", "")

    if text in ["", "—", "-", "N/A"]:
        return None

    try:
        return int(text)
    except ValueError:
        return None


# ---------------------------------------
# Fetching Web Page
# ---------------------------------------
def fetch_page(url: str) -> str:
    """
    Fetch an HTML page using HTTP GET with headers.
    Raises an exception if the request fails.
    """
    logging.info(f"Fetching URL: {url}")

    headers = {
        "User-Agent": "...",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()

    logging.info("Page fetched successfully.")
    return response.text


# ---------------------------------------
# Detect Table by Caption
# ---------------------------------------
def find_table_by_caption(soup, target_keywords):
    """
    Find the first table whose caption contains ANY of the given keywords.
    Returns the <table> element.
    """
    logging.info("Searching for target table...")

    tables = soup.find_all("table")
    for table in tables:
        caption = table.find("caption")
        if caption:
            text = caption.get_text(strip=True).lower()
            if any(keyword in text for keyword in target_keywords):
                logging.info(f"Matched table caption: {caption.get_text(strip=True)}")
                return table

    raise Exception("No matching table found.")


# ---------------------------------------
# Parse GDP Table
# ---------------------------------------
def parse_gdp_table(table):
    """
    Parse a GDP table by dynamically detecting:
      - country column
      - GDP column
      - rank column (if present)

    Extracts rows into a list of dictionaries:
      {
        "rank": int,
        "country": str,
        "gdp_usd_million": int or None
      }
    """

    logging.info("Parsing GDP table...")

    rows = table.find_all("tr")
    data = []

    # Extract headers
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all("th")]
    logging.debug(f"Detected headers: {headers}")

    rank_idx = headers.index("rank") if "rank" in headers else None
    country_idx = None
    gdp_idx = None

    # Detect column indexes
    for i, h in enumerate(headers):
        if "country" in h:
            country_idx = i
        if "gdp" in h:
            gdp_idx = i

    logging.info(f"Detected country column: {country_idx}, GDP column: {gdp_idx}")

    for ix, row in enumerate(rows[1:], start=1):
        cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]

        if len(cols) < 3:
            continue

        country = clean_country(cols[country_idx if country_idx is not None else 0])
        gdp_val = clean_number(cols[gdp_idx if gdp_idx is not None else 2])

        entry = {
            "rank": ix,
            "country": country,
            "gdp_usd_million": gdp_val
        }

        data.append(entry)

    logging.info(f"Parsed {len(data)} rows.")

    # Preview first 10:
    for item in data[:10]:
        logging.debug(item)

    return data


# ---------------------------------------
# Main Execution
# ---------------------------------------
url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
html = fetch_page(url)
soup = BeautifulSoup(html, "html.parser")

table = find_table_by_caption(
    soup,
    ["gdp", "nominal", "million"]
)

results = parse_gdp_table(table)
