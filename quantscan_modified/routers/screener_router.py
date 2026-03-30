from fastapi import APIRouter, Query
from services.scanner_service import scan_undervalued

router = APIRouter()

@router.get("/scan")
def scan(
    limit: int = Query(default=50, ge=10, le=500, description="Number of NIFTY 500 stocks to scan"),
    min_upside: float = Query(default=5.0, description="Minimum upside % to include")
):
    """
    Scan NIFTY 500 stocks and return undervalued ones ranked by QuantScan composite score.
    """
    return scan_undervalued(limit=limit, min_upside=min_upside)
