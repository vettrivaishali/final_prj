"""
ticker_router.py
Live ticker endpoint — returns price + change% for top 30 stocks
Used by the dashboard ticker tape for real-time scrolling data
"""
from fastapi import APIRouter
import yfinance as yf
from data.nifty500 import NIFTY_500
import concurrent.futures

router = APIRouter()

TICKER_SYMBOLS = NIFTY_500[:40]  # top 40 for speed

def _fetch_one(sym):
    try:
        t = yf.Ticker(sym)
        info = t.fast_info
        price = round(float(info.last_price), 2)
        prev  = round(float(info.previous_close), 2)
        chg   = round((price - prev) / prev * 100, 2) if prev else 0
        return {"symbol": sym.replace(".NS",""), "price": price, "change": chg}
    except:
        return None

@router.get("/ticker")
def live_ticker():
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(_fetch_one, s): s for s in TICKER_SYMBOLS}
        for f in concurrent.futures.as_completed(futures):
            d = f.result()
            if d:
                results.append(d)
    results.sort(key=lambda x: abs(x["change"]), reverse=True)
    return results[:30]
