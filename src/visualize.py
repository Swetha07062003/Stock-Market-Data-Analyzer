import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------------------
# LOAD DATA
# ----------------------------------------

def load_data(
    ticker="AAPL",
    db_path="db/market.db"
):

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            c.date,
            c.close,
            i.sma20,
            i.sma50,
            i.rsi14,
            i.macd,
            i.macd_signal
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
        params=(ticker,)
    )

    conn.close()

    df["date"] = pd.to_datetime(df["date"])

    return df


# ----------------------------------------
# PRICE + SMA CHART
# ----------------------------------------

def plot_price_chart(df, ticker):

    plt.figure(figsize=(14, 7))

    plt.plot(
        df["date"],
        df["close"],
        label="Closing Price"
    )

    plt.plot(
        df["date"],
        df["sma20"],
        label="SMA20"
    )

    plt.plot(
        df["date"],
        df["sma50"],
        label="SMA50"
    )

    plt.title(f"{ticker} Price & Moving Averages")

    plt.xlabel("Date")

    plt.ylabel("Price")

    plt.legend()

    plt.grid(True)

    plt.savefig(
        f"images/{ticker}_price_sma_chart.png"
    )

    plt.show()


# ----------------------------------------
# RSI CHART
# ----------------------------------------

def plot_rsi(df, ticker):

    plt.figure(figsize=(14, 5))

    plt.plot(
        df["date"],
        df["rsi14"],
        label="RSI14"
    )

    plt.axhline(
        70,
        linestyle="--"
    )

    plt.axhline(
        30,
        linestyle="--"
    )

    plt.title(f"{ticker} RSI Indicator")

    plt.xlabel("Date")

    plt.ylabel("RSI")

    plt.legend()

    plt.grid(True)

    plt.savefig(
        f"images/{ticker}_rsi_chart.png"
    )

    plt.show()


# ----------------------------------------
# MACD CHART
# ----------------------------------------

def plot_macd(df, ticker):

    plt.figure(figsize=(14, 5))

    plt.plot(
        df["date"],
        df["macd"],
        label="MACD"
    )

    plt.plot(
        df["date"],
        df["macd_signal"],
        label="Signal Line"
    )

    plt.title(f"{ticker} MACD Indicator")

    plt.xlabel("Date")

    plt.ylabel("MACD")

    plt.legend()

    plt.grid(True)

    plt.savefig(
        f"images/{ticker}_macd_chart.png"
    )

    plt.show()


# ----------------------------------------
# EQUITY CURVE
# ----------------------------------------

def plot_equity_curve():

    df = pd.read_csv(
        "outputs/backtest_equity_curve.csv"
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        df.index,
        df["equity_curve"],
        label="Equity Curve"
    )

    plt.title("Backtest Equity Curve")

    plt.xlabel("Trading Days")

    plt.ylabel("Portfolio Growth")

    plt.legend()

    plt.grid(True)

    plt.savefig(
        "images/equity_curve_chart.png"
    )

    plt.show()


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":

    ticker = "AAPL"

    data = load_data(ticker)

    print("\nGenerating charts...\n")

    plot_price_chart(data, ticker)

    plot_rsi(data, ticker)

    plot_macd(data, ticker)

    plot_equity_curve()

    print("\nCharts generated successfully!")