import pandas as pd

def load_nifty500():
    df = pd.read_csv("data/nifty500.csv")
    return [s + ".NS" for s in df["Symbol"].tolist()]