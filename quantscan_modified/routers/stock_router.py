from fastapi import APIRouter, HTTPException
from services.scanner_service import quick_analyze
from services.prediction_service import predict_prices

router = APIRouter()

@router.get("/analyze/{symbol}")
def analyze(symbol: str):
    symbol = symbol.upper()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol += ".NS"
    result = quick_analyze(symbol)
    if not result:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    # Attach prediction data
    pred = predict_prices(symbol)
    if pred:
        result["prediction"] = pred
    return result
