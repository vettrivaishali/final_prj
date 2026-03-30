from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.stock_router    import router as stock_router
from routers.screener_router import router as screener_router
from routers.ticker_router   import router as ticker_router

app = FastAPI(title="QuantScan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_router)
app.include_router(screener_router)
app.include_router(ticker_router)

@app.get("/")
def home():
    return {"msg": "QuantScan Backend Running", "version": "2.0"}
