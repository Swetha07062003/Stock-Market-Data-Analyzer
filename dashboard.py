import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

from src.backtest import run_backtest
from src.ingest import fetch_daily, save_to_database
from src.indicators import compute_indicators


# =================================================
# PAGE CONFIG
# =================================================

st.set_page_config(
    page_title="Stock Market Data Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# CENTER TITLE
# =================================================

st.markdown(
    """
    <h1 style='
        text-align: center;
        color: white;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 10px;
    '>
        📈 Stock Market Data Analyzer
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='
        text-align: center;
        color: #94A3B8;
        font-size: 18px;
        margin-bottom: 40px;
    '>
        Professional FinTech Analytics Dashboard
    </p>
    """,
    unsafe_allow_html=True
)


# =================================================
# CUSTOM CSS
# =================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0B1120;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    /* Main title */
    h1 {
        color: white !important;
        font-size: 42px !important;
        font-weight: 700 !important;
    }

    h2, h3 {
        color: white !important;
    }

    /* KPI Cards */
    .metric-card {
        background-color: #1E293B;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #334155;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    }

    .metric-title {
        color: #94A3B8;
        font-size: 15px;
        margin-bottom: 10px;
        font-weight: 500;
    }

    .metric-value {
        color: white;
        font-size: 34px;
        font-weight: 700;
    }

    .metric-change-positive {
        color: #22C55E;
        font-size: 16px;
        font-weight: 600;
        margin-top: 8px;
    }

    .metric-change-negative {
        color: #EF4444;
        font-size: 16px;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)





# =================================================
# DATABASE
# =================================================

DB_PATH = "db/market.db"


# =================================================
# LOAD DATA
# =================================================

def load_data(ticker):

    conn = sqlite3.connect(DB_PATH)

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

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


# =================================================
# AUTO DOWNLOAD STOCK DATA
# =================================================

def process_stock(ticker):

    stock_df = fetch_daily(ticker)

    if stock_df.empty:
        return False

    save_to_database(stock_df, ticker)

    compute_indicators(ticker)

    return True


# =================================================
# SIDEBAR
# =================================================

st.sidebar.title("⚙ Dashboard Settings")

selected_stock = st.sidebar.selectbox(
    "Select Stock",
    ["AAPL", "TSLA", "MSFT", "NVDA"]
)

currency = st.sidebar.selectbox(
    "Currency",
    ["USD ($)", "INR (₹)"]
)


# =================================================
# LOAD STOCK DATA
# =================================================

stock_df = load_data(selected_stock)

if stock_df.empty:

    with st.spinner(f"Loading {selected_stock} data..."):

        process_stock(selected_stock)

        stock_df = load_data(selected_stock)

if stock_df.empty:
    st.error("Unable to load stock data")
    st.stop()


# =================================================
# CURRENCY HANDLING
# =================================================

USD_TO_INR = 83.0

currency_symbol = "$"

if currency == "INR (₹)":

    stock_df["close"] = stock_df["close"] * USD_TO_INR
    stock_df["sma20"] = stock_df["sma20"] * USD_TO_INR
    stock_df["sma50"] = stock_df["sma50"] * USD_TO_INR

    currency_symbol = "₹"


# =================================================
# KPI CALCULATIONS
# =================================================

latest_price = stock_df["close"].iloc[-1]

previous_price = stock_df["close"].iloc[-2]

price_change = latest_price - previous_price

price_change_percent = (price_change / previous_price) * 100

latest_rsi = stock_df["rsi14"].iloc[-1]

latest_macd = stock_df["macd"].iloc[-1]

latest_sma20 = stock_df["sma20"].iloc[-1]

latest_sma50 = stock_df["sma50"].iloc[-1]


# =================================================
# KPI SECTION
# =================================================

st.markdown("## 📊 Market Overview")

col1, col2, col3, col4 = st.columns(4)

change_class = (
    "metric-change-positive"
    if price_change_percent >= 0
    else "metric-change-negative"
)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Current Price</div>
            <div class="metric-value">
                {currency_symbol}{latest_price:,.2f}
            </div>
            <div class="{change_class}">
                {price_change_percent:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">RSI14</div>
            <div class="metric-value">
                {latest_rsi:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">SMA20</div>
            <div class="metric-value">
                {currency_symbol}{latest_sma20:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">SMA50</div>
            <div class="metric-value">
                {currency_symbol}{latest_sma50:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =================================================
# DATA TABLE
# =================================================

st.markdown("## 📋 Stock Market Dataset")

st.dataframe(
    stock_df.tail(15),
    use_container_width=True
)


# =================================================
# PRICE CHART
# =================================================

st.markdown("## 📈 Price & Moving Averages")

price_chart = go.Figure()

price_chart.add_trace(go.Scatter(
    x=stock_df["date"],
    y=stock_df["close"],
    mode="lines",
    name="Closing Price"
))

price_chart.add_trace(go.Scatter(
    x=stock_df["date"],
    y=stock_df["sma20"],
    mode="lines",
    name="SMA20"
))

price_chart.add_trace(go.Scatter(
    x=stock_df["date"],
    y=stock_df["sma50"],
    mode="lines",
    name="SMA50"
))

price_chart.update_layout(
    template="plotly_dark",
    height=600,
    xaxis_title="Date",
    yaxis_title=f"Price ({currency_symbol})",
    hovermode="x unified"
)

st.plotly_chart(
    price_chart,
    use_container_width=True
)


# =================================================
# RSI + MACD
# =================================================

left_col, right_col = st.columns(2)

with left_col:

    st.markdown("## 📉 RSI Indicator")

    rsi_chart = go.Figure()

    rsi_chart.add_trace(go.Scatter(
        x=stock_df["date"],
        y=stock_df["rsi14"],
        mode="lines",
        name="RSI14"
    ))

    rsi_chart.add_hline(
        y=70,
        line_dash="dash"
    )

    rsi_chart.add_hline(
        y=30,
        line_dash="dash"
    )

    rsi_chart.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(
        rsi_chart,
        use_container_width=True
    )

with right_col:

    st.markdown("## 📊 MACD Indicator")

    macd_chart = go.Figure()

    macd_chart.add_trace(go.Scatter(
        x=stock_df["date"],
        y=stock_df["macd"],
        mode="lines",
        name="MACD"
    ))

    macd_chart.add_trace(go.Scatter(
        x=stock_df["date"],
        y=stock_df["macd_signal"],
        mode="lines",
        name="Signal Line"
    ))

    macd_chart.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(
        macd_chart,
        use_container_width=True
    )


# =================================================
# BACKTEST
# =================================================

st.markdown("## 🤖 Quantitative Backtesting")

if st.button("Run SMA Backtest"):

    with st.spinner("Running backtest strategy..."):

        run_backtest(selected_stock)

        results = pd.read_csv(
            "outputs/backtest_results.csv"
        )

    st.success("Backtest Completed Successfully")

    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.markdown("### 📑 Backtest Metrics")

        st.dataframe(
            results,
            use_container_width=True
        )

    with result_col2:

        equity_df = pd.read_csv(
            "outputs/backtest_equity_curve.csv"
        )

        equity_chart = go.Figure()

        equity_chart.add_trace(go.Scatter(
            y=equity_df["equity_curve"],
            mode="lines",
            name="Equity Curve"
        ))

        equity_chart.update_layout(
            template="plotly_dark",
            title="Portfolio Equity Curve",
            height=420
        )

        st.plotly_chart(
            equity_chart,
            use_container_width=True
        )


# =================================================
# FOOTER
# =================================================

st.markdown("---")

