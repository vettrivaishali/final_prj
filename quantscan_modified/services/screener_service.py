from services.nifty_loader import load_nifty500
from services.ai_engine import analyze_stock

def scan_nifty500():
    symbols = load_nifty500()
    results=[]

    for s in symbols[:50]:   # limit first test
        r = analyze_stock(s)
        if r and "error" not in r:
            results.append(r)

    return sorted(
        results,
        key=lambda x: x.get("intrinsic", 0) - x.get("avg_price", 0),
        reverse=True
    )