"""
scanner_service.py
==================
Main scan engine for QuantScan.
Scans NIFTY 500 stocks (in batches) and returns ranked results
using real fundamental + intrinsic + sentiment scoring.
"""

from data.nifty500 import NIFTY_500
from services.intrinsic_service  import calculate_intrinsic
from services.fundamental_service import get_fundamentals
from services.news_service        import get_news
from services.sentiment_service   import score_news
from services.valuation_service   import rank_stocks

import concurrent.futures


def analyze_single(symbol: str) -> dict | None:
    """Full analysis for one stock symbol."""
    try:
        intrinsic_data   = calculate_intrinsic(symbol)
        if not intrinsic_data:
            return None

        fundamental_data = get_fundamentals(symbol)
        headlines        = get_news(symbol, max_items=8)
        sentiment_data   = score_news(headlines)

        return {
            "symbol":             symbol,
            "price":              intrinsic_data["price"],
            "intrinsic_value":    intrinsic_data["intrinsic_value"],
            "graham_value":       intrinsic_data["graham_value"],
            "dcf_value":          intrinsic_data["dcf_value"],
            "upside_pct":         intrinsic_data["upside_pct"],
            "signal":             intrinsic_data["signal"],
            # Fundamentals
            "pe":                 fundamental_data["pe"],
            "roe_pct":            fundamental_data["roe_pct"],
            "roce_pct":           fundamental_data["roce_pct"],
            "eps":                fundamental_data["eps"],
            "eps_growth_pct":     fundamental_data["eps_growth_pct"],
            "de_ratio":           fundamental_data["de_ratio"],
            "div_yield_pct":      fundamental_data["div_yield_pct"],
            "fundamental_score":  fundamental_data["fundamental_score"],
            "grade":              fundamental_data["grade"],
            # Sentiment
            "sentiment_score":    sentiment_data["sentiment_score"],
            "sentiment_label":    sentiment_data["label"],
            "sentiment_confidence": sentiment_data["confidence"],
            "positive_news":      sentiment_data["positive_count"],
            "negative_news":      sentiment_data["negative_count"],
            "headlines":          [d["headline"] for d in sentiment_data["details"][:5]],
        }

    except Exception as e:
        print(f"[scanner] {symbol} failed: {e}")
        return None


def scan_undervalued(limit: int = 50, min_upside: float = 5.0) -> list:
    """
    Scans first `limit` NIFTY 500 stocks.
    Returns top results sorted by composite QuantScan score.
    min_upside: only include stocks with upside > this %
    """
    symbols = NIFTY_500[:limit]
    results = []

    # Parallel fetch with thread pool (max 8 workers to avoid rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(analyze_single, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            if data and data["upside_pct"] >= min_upside:
                results.append(data)

    ranked = rank_stocks(results)
    return ranked[:30]


def quick_analyze(symbol: str) -> dict | None:
    """Single stock deep analysis (for /analyze endpoint)."""
    return analyze_single(symbol)
