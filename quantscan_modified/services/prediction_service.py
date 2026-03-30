"""
prediction_service.py
=====================
Ensemble price prediction using 3 models:
  1. Linear Regression (trend)
  2. Exponential Smoothing (momentum)
  3. Bollinger Band mean-reversion target

Returns 7-day, 30-day price predictions + confidence + support/resistance
"""

import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import math

def _ema(prices, span):
    """Exponential moving average."""
    alpha = 2 / (span + 1)
    ema = [prices[0]]
    for p in prices[1:]:
        ema.append(alpha * p + (1 - alpha) * ema[-1])
    return np.array(ema)

def predict_prices(symbol: str) -> dict:
    try:
        df = yf.download(symbol, period="1y", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or df.empty or len(df) < 30:
            return None

        closes = df["Close"].values.flatten().astype(float)
        n = len(closes)

        # ── 1. Linear Regression (next 7 & 30 days) ─────────────────
        X = np.arange(n).reshape(-1, 1)
        y = closes
        lr = LinearRegression().fit(X, y)
        pred_7d  = float(lr.predict([[n + 7]])[0])
        pred_30d = float(lr.predict([[n + 30]])[0])

        # ── 2. EMA momentum adjustment ───────────────────────────────
        ema20 = _ema(closes, 20)
        ema50 = _ema(closes, 50)
        last_price = closes[-1]
        ema_momentum = (ema20[-1] - ema50[-1]) / ema50[-1]  # positive = bullish

        # Blend: 60% LR + 40% EMA-momentum adjusted
        momentum_7d  = last_price * (1 + ema_momentum * 0.5)
        momentum_30d = last_price * (1 + ema_momentum * 2.0)
        blended_7d   = round(0.6 * pred_7d  + 0.4 * momentum_7d,  2)
        blended_30d  = round(0.6 * pred_30d + 0.4 * momentum_30d, 2)

        # ── 3. Bollinger Bands (support/resistance) ──────────────────
        window = 20
        rolling_mean = np.mean(closes[-window:])
        rolling_std  = np.std(closes[-window:])
        upper_band   = round(rolling_mean + 2 * rolling_std, 2)
        lower_band   = round(rolling_mean - 2 * rolling_std, 2)

        # ── 4. RSI ───────────────────────────────────────────────────
        deltas = np.diff(closes[-15:])
        gains  = deltas[deltas > 0].mean() if len(deltas[deltas > 0]) else 0
        losses = abs(deltas[deltas < 0].mean()) if len(deltas[deltas < 0]) else 0.001
        rs     = gains / losses
        rsi    = round(100 - (100 / (1 + rs)), 1)

        # ── 5. Confidence (R² of linear model) ───────────────────────
        r2          = lr.score(X, y)
        confidence  = round(max(40, min(95, r2 * 100)), 1)

        # ── Historical closes for sparkline (last 30 days) ───────────
        sparkline = [round(float(v), 2) for v in closes[-30:]]

        return {
            "symbol":        symbol,
            "current_price": round(last_price, 2),
            "pred_7d":       blended_7d,
            "pred_30d":      blended_30d,
            "change_7d_pct": round((blended_7d - last_price) / last_price * 100, 2),
            "change_30d_pct": round((blended_30d - last_price) / last_price * 100, 2),
            "upper_band":    upper_band,
            "lower_band":    lower_band,
            "ema20":         round(float(ema20[-1]), 2),
            "ema50":         round(float(ema50[-1]), 2),
            "rsi":           rsi,
            "confidence":    confidence,
            "sparkline":     sparkline,
        }

    except Exception as e:
        print(f"[prediction_service] {symbol}: {e}")
        return None
