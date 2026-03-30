from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class StockAnalysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    intrinsic = Column(Float)
    avg_price = Column(Float)
    future_price = Column(Float)
    sentiment = Column(String)
    signal = Column(String)