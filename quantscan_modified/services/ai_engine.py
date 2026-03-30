import yfinance as yf


def analyze_stock(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo", auto_adjust=True)

        if hist is None or hist.empty or "Close" not in hist.columns:
            return {"error": "No data"}

        price = float(hist["Close"].iloc[-1])
        start = float(hist["Close"].iloc[0])

        if start == 0:
            return {"error": "Invalid starting price"}

        growth = (price - start) / start
        avg_price = float(hist["Close"].mean())

        intrinsic = price * (1 + growth)
        signal = "BUY" if intrinsic > price else "SELL"

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "avg_price": round(avg_price, 2),
            "intrinsic": round(intrinsic, 2),
            "growth_3m": round(growth * 100, 2),
            "signal": signal
        }
    except Exception as e:
        return {"error": f"Stock analysis failed: {e}"}