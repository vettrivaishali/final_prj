"""
fundamental_service.py
======================
Fetches full fundamental data from yfinance and computes a
0-100 fundamental score across 8 metrics:

  P/E ratio         (lower = better, capped at 40)
  Forward P/E       (lower = better)
  PEG ratio         (< 1 is great)
  ROE               (higher = better, 15%+ is good)
  ROCE proxy        (EBIT / Total Assets)
  EPS growth        (positive = good)
  Debt/Equity       (lower = better)
  Dividend Yield    (bonus points)
"""

import yfinance as yf
import math


def _safe(val, default=0.0):
    try:
        v = float(val)
        return v if math.isfinite(v) else default
    except (TypeError, ValueError):
        return default


def score_metric(value, low_good=True, good_thresh=None, bad_thresh=None, max_score=12):
    """Generic scorer: returns 0..max_score"""
    if value == 0:
        return 0
    if low_good:
        if good_thresh and value <= good_thresh:
            return max_score
        if bad_thresh and value >= bad_thresh:
            return 0
        if good_thresh and bad_thresh:
            ratio = (bad_thresh - value) / (bad_thresh - good_thresh)
            return round(max(0, min(max_score, ratio * max_score)), 1)
    else:
        if good_thresh and value >= good_thresh:
            return max_score
        if bad_thresh and value <= bad_thresh:
            return 0
        if good_thresh and bad_thresh:
            ratio = (value - bad_thresh) / (good_thresh - bad_thresh)
            return round(max(0, min(max_score, ratio * max_score)), 1)
    return max_score / 2


def get_fundamentals(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info   = ticker.info

    price       = _safe(info.get("currentPrice") or info.get("regularMarketPrice"))
    pe          = _safe(info.get("trailingPE"))
    fwd_pe      = _safe(info.get("forwardPE"))
    peg         = _safe(info.get("pegRatio"))
    roe         = _safe(info.get("returnOnEquity")) * 100     # to %
    eps         = _safe(info.get("trailingEps"))
    eps_growth  = _safe(info.get("earningsGrowth"), 0) * 100
    de_ratio    = _safe(info.get("debtToEquity"))
    div_yield   = _safe(info.get("dividendYield"), 0) * 100   # to %
    market_cap  = _safe(info.get("marketCap"))
    pb          = _safe(info.get("priceToBook"))
    revenue_g   = _safe(info.get("revenueGrowth"), 0) * 100

    # ROCE proxy: operatingCashflow / totalAssets
    total_assets = _safe(info.get("totalAssets"))
    op_cf        = _safe(info.get("operatingCashflow"))
    roce = (op_cf / total_assets * 100) if total_assets > 0 else 0.0

    # ── Scoring (total 100 pts) ──────────────────────────────────────
    # P/E: good < 20, bad > 40
    s_pe       = score_metric(pe,       low_good=True,  good_thresh=20,  bad_thresh=40,  max_score=15) if pe > 0 else 0
    # Fwd P/E: good < 18, bad > 35
    s_fwd_pe   = score_metric(fwd_pe,   low_good=True,  good_thresh=18,  bad_thresh=35,  max_score=10) if fwd_pe > 0 else 0
    # PEG: < 1 great, > 2 bad
    s_peg      = score_metric(peg,      low_good=True,  good_thresh=1,   bad_thresh=2,   max_score=10) if peg > 0 else 0
    # ROE %: > 15 good, < 5 bad
    s_roe      = score_metric(roe,      low_good=False, good_thresh=15,  bad_thresh=5,   max_score=15)
    # ROCE %: > 15 good, < 5 bad
    s_roce     = score_metric(roce,     low_good=False, good_thresh=15,  bad_thresh=5,   max_score=15)
    # EPS growth %: > 15 good, < 0 bad
    s_eps_g    = score_metric(eps_growth, low_good=False, good_thresh=15, bad_thresh=0,  max_score=15)
    # D/E: < 0.5 good, > 2 bad
    s_de       = score_metric(de_ratio, low_good=True,  good_thresh=0.5, bad_thresh=2,   max_score=10) if de_ratio >= 0 else 5
    # Dividend: > 2% good
    s_div      = score_metric(div_yield, low_good=False, good_thresh=2,  bad_thresh=0,   max_score=10)

    total_score = round(s_pe + s_fwd_pe + s_peg + s_roe + s_roce + s_eps_g + s_de + s_div, 1)

    # Grade
    if total_score >= 75:
        grade = "A+"
    elif total_score >= 60:
        grade = "A"
    elif total_score >= 45:
        grade = "B"
    elif total_score >= 30:
        grade = "C"
    else:
        grade = "D"

    return {
        "symbol":        symbol,
        "price":         round(price, 2),
        "pe":            round(pe, 2),
        "fwd_pe":        round(fwd_pe, 2),
        "peg":           round(peg, 2),
        "roe_pct":       round(roe, 2),
        "roce_pct":      round(roce, 2),
        "eps":           round(eps, 2),
        "eps_growth_pct": round(eps_growth, 2),
        "de_ratio":      round(de_ratio, 2),
        "div_yield_pct": round(div_yield, 2),
        "pb":            round(pb, 2),
        "revenue_growth_pct": round(revenue_g, 2),
        "market_cap":    market_cap,
        "fundamental_score": total_score,
        "grade":         grade,
        "score_breakdown": {
            "pe_score":      s_pe,
            "fwd_pe_score":  s_fwd_pe,
            "peg_score":     s_peg,
            "roe_score":     s_roe,
            "roce_score":    s_roce,
            "eps_growth_score": s_eps_g,
            "de_score":      s_de,
            "dividend_score": s_div,
        }
    }
