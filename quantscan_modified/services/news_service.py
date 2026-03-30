"""
news_service.py
===============
Fetches real financial news headlines for a given stock symbol.
Uses Google News RSS (no API key needed).
Returns list of headline strings.
"""

import requests
import xml.etree.ElementTree as ET
import urllib.parse


def get_news(symbol: str, max_items: int = 10) -> list:
    """
    Fetches latest news headlines for the given stock symbol.
    Strips .NS / .BO suffix for better search results.
    """
    clean = symbol.replace(".NS", "").replace(".BO", "")
    query = urllib.parse.quote(f"{clean} stock NSE India")
    url   = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    headlines = []

    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()

        root = ET.fromstring(r.content)
        channel = root.find("channel")
        if channel is None:
            return headlines

        for item in channel.findall("item")[:max_items]:
            title_el = item.find("title")
            if title_el is not None and title_el.text:
                # Strip source attribution " - Source Name"
                text = title_el.text.split(" - ")[0].strip()
                headlines.append(text)

    except Exception as e:
        print(f"[news_service] {symbol} fetch error: {e}")

    return headlines if headlines else ["No recent news found"]
