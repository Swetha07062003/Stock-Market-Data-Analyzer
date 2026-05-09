import sqlite3
import pandas as pd
import numpy as np


# ----------------------------------------
# RUN BACKTEST
# ----------------------------------------

def run_backtest(
    ticker="AAPL",
    db_path="db/market.db",
    fee_bps=5
):

    print(f"\nRunning backtest for {ticker}...\n")

    conn = sqlite3.connect(db_path)

    # ----------------------------------------
    # LOAD DATA
    # ----------------------------------------

    query = """
        SELECT
            c.date,
            c.close,
            i.sma20,
            i.sma50
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

    # Check data
    if df.empty:
        print("No data found!")
        return

    # ----------------------------------------
    # CREATE SIGNALS
    # ----------------------------------------

    # 1 = BUY
    # 0 = SELL

    df["signal"] = np.where(
        df["sma20"] > df["sma50"],
        1,
        0
    )

    # Position for next day
    df["position"] = df["signal"].shift(1)

    # Daily returns
    df["market_return"] = df["close"].pct_change()

    # Strategy returns
    df["strategy_return"] = (
        df["position"] * df["market_return"]
    )

    # Remove NaN
    df.dropna(inplace=True)

    # ----------------------------------------
    # TRANSACTION COST
    # ----------------------------------------

    df["trade"] = df["position"].diff().abs()

    transaction_cost = fee_bps / 10000

    df["strategy_return"] = (
        df["strategy_return"]
        - (df["trade"] * transaction_cost)
    )

    # ----------------------------------------
    # EQUITY CURVE
    # ----------------------------------------

    df["equity_curve"] = (
        1 + df["strategy_return"]
    ).cumprod()

    # ----------------------------------------
    # PERFORMANCE METRICS
    # ----------------------------------------

    pnl = (
        df["equity_curve"].iloc[-1] - 1
    ) * 100

    sharpe = (
        np.sqrt(252)
        * (
            df["strategy_return"].mean()
            /
            df["strategy_return"].std()
        )
    )

    rolling_max = (
        df["equity_curve"].cummax()
    )

    drawdown = (
        df["equity_curve"]
        /
        rolling_max
        - 1
    )

    max_drawdown = drawdown.min() * 100

    trades = int(df["trade"].sum())

    winning_trades = (
        df[df["strategy_return"] > 0]
    )

    win_rate = (
        len(winning_trades)
        /
        len(df)
    ) * 100

    # ----------------------------------------
    # PRINT RESULTS
    # ----------------------------------------

    print("BACKTEST RESULTS")
    print("-" * 40)

    print(f"Profit/Loss      : {pnl:.2f}%")
    print(f"Sharpe Ratio     : {sharpe:.2f}")
    print(f"Max Drawdown     : {max_drawdown:.2f}%")
    print(f"Total Trades     : {trades}")
    print(f"Win Rate         : {win_rate:.2f}%")

    # ----------------------------------------
    # SAVE RESULTS
    # ----------------------------------------

    results = pd.DataFrame({
        "Metric": [
            "Profit/Loss",
            "Sharpe Ratio",
            "Max Drawdown",
            "Trades",
            "Win Rate"
        ],
        "Value": [
            pnl,
            sharpe,
            max_drawdown,
            trades,
            win_rate
        ]
    })

    results.to_csv(
        "outputs/backtest_results.csv",
        index=False
    )

    # Save equity curve
    df.to_csv(
        "outputs/backtest_equity_curve.csv",
        index=False
    )

    conn.close()

    print("\nBacktest completed successfully!")

    return df


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":

    run_backtest("AAPL")