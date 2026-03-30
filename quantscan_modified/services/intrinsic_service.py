"""
intrinsic_service.py
====================
Two real valuation models:
  1. Graham Number  ->  sqrt(22.5 x EPS x BVPS)
  2. DCF (simplified)  ->  EPS x (8.5 + 2g) x 4.4 / Y
     where g = expected growth rate, Y = current AAA bond yield proxy

Returns upside % = (intrinsic - price) / price x 100
"""

import yfinance as yf
import math

RISK_FREE_RATE = 7.2   # India 10Y G-Sec yield proxy %


def _safe(val, default=0):
    try:
        v = float(val)
        return v if math.isfinite(v) else default
    except (TypeError, ValueError):
        return default


def calculate_intrinsic(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info

        price   = _safe(info.get("currentPrice") or info.get("regularMarketPrice"))
        eps     = _safe(info.get("trailingEps"))
        bvps    = _safe(info.get("bookValue"))
        pe      = _safe(info.get("trailingPE"))
        fwd_pe  = _safe(info.get("forwardPE"))
        peg     = _safe(info.get("pegRatio"))
        roe     = _safe(info.get("returnOnEquity"))
        growth  = _safe(info.get("earningsGrowth") or info.get("revenueGrowth"), 0.10) * 100

        if price <= 0:
            return None

        # 1. Graham Number
        graham = 0.0
        if eps > 0 and bvps > 0:
            graham = math.sqrt(22.5 * eps * bvps)

        # 2. Benjamin Graham DCF: V = EPS x (8.5 + 2g) x 4.4 / Y
        dcf = 0.0
        g_cap = max(0.0, min(25.0, growth))
        if eps > 0:
            dcf = eps * (8.5 + 2 * g_cap) * 4.4 / RISK_FREE_RATE

        # 3. Composite intrinsic = average of valid models
        valid = [v for v in [graham, dcf] if v > 0]
        intrinsic = sum(valid) / len(valid) if valid else price

        upside_pct = round((intrinsic - price) / price * 100, 2)

        if upside_pct >= 20:
            signal = "STRONG BUY"
        elif upside_pct >= 5:
            signal = "BUY"
        elif upside_pct <= -20:
            signal = "STRONG SELL"
        elif upside_pct <= -5:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "symbol":          symbol,
            "price":           round(price, 2),
            "eps":             round(eps, 2),
            "bvps":            round(bvps, 2),
            "pe":              round(pe, 2),
            "fwd_pe":          round(fwd_pe, 2),
            "peg":             round(peg, 2),
            "roe_pct":         round(roe * 100, 2),
            "growth_pct":      round(g_cap, 2),
            "graham_value":    round(graham, 2),
            "dcf_value":       round(dcf, 2),
            "intrinsic_value": round(intrinsic, 2),
            "upside_pct":      upside_pct,
            "undervalued_pct": upside_pct,
            "signal":          signal,
        }

    except Exception as e:
        print(f"[intrinsic_service] {symbol} error: {e}")
        return None
