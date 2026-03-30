# QuantScan — Setup & Run Guide

## 1. Install dependencies
```bash
pip install -r requirements.txt
python -m textblob.download_corpora   # downloads NLP data for sentiment
```

## 2. Start backend
```bash
uvicorn app:app --reload
# Runs on http://127.0.0.1:8000
```

## 3. Open frontend
Open `dashboard.html` directly in your browser (or serve via Live Server in VS Code).

## 4. API Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /analyze/{symbol}` | Full analysis for one stock e.g. `/analyze/TCS.NS` |
| `GET /scan` | Scan NIFTY 500, returns ranked undervalued stocks |
| `GET /scan?limit=100&min_upside=10` | Custom scan parameters |

---

## How the Scoring Works

### Intrinsic Value (intrinsic_service.py)
Two real valuation models averaged together:

**Graham Number** = √(22.5 × EPS × Book Value Per Share)
- Classic Benjamin Graham formula
- Valid when EPS > 0 and BVPS > 0

**DCF (Graham Formula)** = EPS × (8.5 + 2g) × 4.4 / Y
- g = earnings growth rate (capped 0–25%)
- Y = India 10Y G-Sec yield proxy (7.2%)
- 8.5 = base P/E for zero-growth company

### Fundamental Score (fundamental_service.py)
0–100 points across 8 metrics:
| Metric | Weight | Good Threshold |
|--------|--------|---------------|
| P/E Ratio | 15pts | < 20 |
| Forward P/E | 10pts | < 18 |
| PEG Ratio | 10pts | < 1.0 |
| ROE | 15pts | > 15% |
| ROCE | 15pts | > 15% |
| EPS Growth | 15pts | > 15% |
| Debt/Equity | 10pts | < 0.5 |
| Dividend Yield | 10pts | > 2% |

**Grades**: A+ (75+), A (60+), B (45+), C (30+), D (<30)

### Sentiment Score (sentiment_service.py)
- Real NLP using **TextBlob** polarity analysis
- Blended with financial keyword lexicon (60/40 mix)
- Per-headline scoring with overall label: POSITIVE / NEUTRAL / NEGATIVE

### QuantScan Composite Score (valuation_service.py)
```
Composite = 40% × Fundamental Score
          + 40% × Upside % (normalized)
          + 20% × Sentiment Score (normalized)
```

**Signals**: STRONG BUY (≥75, upside≥20%) → BUY → WATCH → HOLD → SELL → STRONG SELL
