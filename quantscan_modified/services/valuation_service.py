"""
valuation_service.py
====================
Composite QuantScan Score (0-100):
  40%  Fundamental score
  40%  Intrinsic value upside
  20%  Sentiment score

rank_stocks(results: list) -> list sorted by composite score
"""

import math


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def composite_score(fundamental_score: float,
                    upside_pct: float,
                    sentiment_score: float) -> float:
    """
    fundamental_score : 0-100
    upside_pct        : any % (capped -50 to +100)
    sentiment_score   : -1 to +1
    Returns 0-100
    """
    # Normalize upside to 0-100
    upside_norm = _clamp((upside_pct + 50) / 150 * 100, 0, 100)

    # Normalize sentiment to 0-100
    sentiment_norm = _clamp((sentiment_score + 1) / 2 * 100, 0, 100)

    score = (
        0.40 * fundamental_score +
        0.40 * upside_norm +
        0.20 * sentiment_norm
    )
    return round(score, 1)


def get_recommendation(score: float, upside_pct: float) -> str:
    """Returns human-readable recommendation based on composite score."""
    if score >= 75 and upside_pct >= 20:
        return "STRONG BUY"
    elif score >= 60 and upside_pct >= 5:
        return "BUY"
    elif score >= 50:
        return "WATCH"
    elif score >= 35:
        return "HOLD"
    elif upside_pct <= -20:
        return "STRONG SELL"
    else:
        return "SELL"


def rank_stocks(results: list) -> list:
    """
    Accepts list of dicts each containing:
      fundamental_score, upside_pct, sentiment_score
    Adds composite_score and recommendation, returns sorted list.
    """
    for r in results:
        fs  = r.get("fundamental_score", 50)
        up  = r.get("upside_pct", 0)
        ss  = r.get("sentiment_score", 0)
        cs  = composite_score(fs, up, ss)
        r["composite_score"] = cs
        r["recommendation"]  = get_recommendation(cs, up)

    return sorted(results, key=lambda x: x["composite_score"], reverse=True)
