import yfinance as yf

def get_stock_history(symbol: str):
    try:
        df = yf.download(
            symbol,
            period="6mo",      # IMPORTANT FIX
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df is None or df.empty:
            print(f"❌ No data for {symbol}")
            return None

        return df

    except Exception as e:
        print(f"❌ Stock fetch error for {symbol}: {e}")
        return None