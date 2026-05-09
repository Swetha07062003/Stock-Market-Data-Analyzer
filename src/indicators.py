import sqlite3
import pandas as pd

from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


# ----------------------------------------
# COMPUTE INDICATORS
# ----------------------------------------

def compute_indicators(
    ticker="AAPL",
    db_path="db/market.db"
):

    print(f"\nCalculating indicators for {ticker}...\n")

    # Connect database
    conn = sqlite3.connect(db_path)

    # Read stock prices
    query = """
        SELECT date, close
        FROM candles_daily
        WHERE ticker = ?
        ORDER BY date
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(ticker,)
    )

    # Check data
    if df.empty:
        print("No stock data found!")
        return

    # ----------------------------------------
    # SMA
    # ----------------------------------------

    df["sma20"] = SMAIndicator(
        close=df["close"],
        window=20
    ).sma_indicator()

    df["sma50"] = SMAIndicator(
        close=df["close"],
        window=50
    ).sma_indicator()

    # ----------------------------------------
    # RSI
    # ----------------------------------------

    df["rsi14"] = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    # ----------------------------------------
    # MACD
    # ----------------------------------------

    macd = MACD(close=df["close"])

    df["macd"] = macd.macd()

    df["macd_signal"] = macd.macd_signal()

    df["macd_hist"] = macd.macd_diff()

    # ----------------------------------------
    # Bollinger Bands
    # ----------------------------------------

    bb = BollingerBands(
        close=df["close"],
        window=20,
        window_dev=2
    )

    df["bb_upper"] = bb.bollinger_hband()

    df["bb_mid"] = bb.bollinger_mavg()

    df["bb_lower"] = bb.bollinger_lband()

    # Remove NULL rows
    df.dropna(inplace=True)

    print("\nIndicator Preview:\n")

    print(df.head())

    # ----------------------------------------
    # SAVE TO DATABASE
    # ----------------------------------------

    cursor = conn.cursor()

    print("\nSaving indicators into database...\n")

    for row in df.itertuples(index=False):

        cursor.execute("""
            INSERT OR REPLACE INTO indicators_daily
            (
                ticker,
                date,
                sma20,
                sma50,
                rsi14,
                macd,
                macd_signal,
                macd_hist,
                bb_upper,
                bb_mid,
                bb_lower
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            row.date,
            row.sma20,
            row.sma50,
            row.rsi14,
            row.macd,
            row.macd_signal,
            row.macd_hist,
            row.bb_upper,
            row.bb_mid,
            row.bb_lower
        ))

    conn.commit()

    conn.close()

    print(f"\nIndicators saved successfully for {ticker}!")


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":

    compute_indicators("AAPL")