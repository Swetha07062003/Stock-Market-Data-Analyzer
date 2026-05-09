from fastapi import FastAPI
import sqlite3
import pandas as pd

from src.ingest import fetch_daily, save_to_database
from src.indicators import compute_indicators
from src.backtest import run_backtest

app = FastAPI(
    title="Stock Market Data Analyzer API",
    description="Financial Analytics Backend API",
    version="1.0"
)

DB_PATH = "db/market.db"


# ----------------------------------------
# HOME ROUTE
# ----------------------------------------

@app.get("/")
def home():

    return {
        "message": "Stock Market Data Analyzer API Running"
    }


# ----------------------------------------
# REFRESH STOCK DATA
# ----------------------------------------

@app.get("/refresh/{ticker}")
def refresh_stock(ticker: str):

    ticker = ticker.upper()

    # Download stock data
    df = fetch_daily(ticker)

    # Save data
    save_to_database(df, ticker)

    # Compute indicators
    compute_indicators(ticker)

    return {
        "status": "success",
        "message": f"{ticker} data refreshed successfully"
    }


# ----------------------------------------
# GET CHART DATA
# ----------------------------------------

@app.get("/chart/{ticker}")
def get_chart_data(ticker: str):

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            c.date,
            c.close,
            i.sma20,
            i.sma50,
            i.rsi14,
            i.macd
        FROM candles_daily c
        JOIN indicators_daily i
        ON c.ticker = i.ticker
        AND c.date = i.date
        WHERE c.ticker = ?
        ORDER BY c.date
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(ticker.upper(),)
    )

    conn.close()

    return df.to_dict(orient="records")


# ----------------------------------------
# RUN BACKTEST
# ----------------------------------------

@app.get("/backtest/{ticker}")
def backtest(ticker: str):

    run_backtest(ticker.upper())

    results = pd.read_csv(
        "outputs/backtest_results.csv"
    )

    return results.to_dict(orient="records")