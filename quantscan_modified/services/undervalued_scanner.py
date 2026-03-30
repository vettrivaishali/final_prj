from services.intrinsic_service import calculate_intrinsic
import pandas as pd

def scan_undervalued():

    df = pd.read_csv("data/nifty500.csv")

    results = []

    for symbol in df["Symbol"].head(50):   # limit first 50 for speed

        sym = symbol + ".NS"

        data = calculate_intrinsic(sym)

        if data and data["undervalued_pct"] > 10:
            results.append(data)

    results = sorted(results, key=lambda x: x["undervalued_pct"], reverse=True)

    return results