import yfinance as yf
import pandas as pd
import sqlite3
import datetime as dt

# ----------------------------------------
# FETCH STOCK DATA
# ----------------------------------------

def fetch_daily(ticker, start="2020-01-01", end=None):

    print(f"\nDownloading stock data for {ticker}...\n")

    df = yf.download(
        ticker,
        start=start,
        end=end or dt.date.today().isoformat(),
        progress=False
    )

    # Check if data exists
    if df.empty:
        print("No stock data found!")
        return pd.DataFrame()

    # Reset index
    df.reset_index(inplace=True)

    # Fix column names
    new_columns = []

    for col in df.columns:

        # Handle tuple columns
        if isinstance(col, tuple):
            new_columns.append(col[0].lower().replace(" ", "_"))
        else:
            new_columns.append(col.lower().replace(" ", "_"))

    df.columns = new_columns

    # Rename adjusted close column if needed
    if "adj_close" not in df.columns and "adj close" in df.columns:
        df.rename(columns={"adj close": "adj_close"}, inplace=True)

    # Format date column
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)

    # Required columns
    required_columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume"
    ]

    # Keep only existing columns
    available_columns = [col for col in required_columns if col in df.columns]

    df = df[available_columns]

    print("\nStock Data Preview:\n")
    print(df.head())

    return df


# ----------------------------------------
# SAVE DATA TO DATABASE
# ----------------------------------------

def save_to_database(df, ticker, db_path="db/market.db"):

    if df.empty:
        print("No data to save.")
        return

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    print("\nSaving data into database...\n")

    for row in df.itertuples(index=False):

        cursor.execute("""
            INSERT OR REPLACE INTO candles_daily
            (
                ticker,
                date,
                open,
                high,
                low,
                close,
                adj_close,
                volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            row.date,
            row.open,
            row.high,
            row.low,
            row.close,
            getattr(row, "adj_close", row.close),
            row.volume
        ))

    conn.commit()

    conn.close()

    print(f"\nData saved successfully for {ticker}!")


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":

    ticker = "AAPL"

    stock_df = fetch_daily(ticker)

    if not stock_df.empty:

        # Save CSV backup
        stock_df.to_csv(
            f"data/{ticker}_stock_data.csv",
            index=False
        )

        # Save to database
        save_to_database(stock_df, ticker)

        print("\nStock ingestion completed successfully!")