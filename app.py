import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time  # For adding delays to handle API rate limits

# ✅ Set up Streamlit Page
st.set_page_config(page_title="Stock Market Insights", layout="wide")
st.title("📊 Stock Market Insights Dashboard")

# ✅ Alpha Vantage Free API Key
API_KEY = "51O42CQZX7GDAV3G"  # Replace with your actual API key

# ✅ Function to Fetch Stock Data
@st.cache_data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    # 🚨 Check for Errors in API Response
    if "Error Message" in data:
        st.error(f"❌ Invalid stock symbol '{symbol}'. Please enter a valid one.")
        return None
    elif "Note" in data:
        st.warning("🚨 API request limit reached. Please wait and try again.")
        return None
    elif "Time Series (Daily)" not in data:
        st.error(f"❌ Unexpected API response for '{symbol}'. Please check the API key and try again.")
        return None

    # ✅ Convert JSON Data to Pandas DataFrame
    try:
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index", dtype=float)
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index, errors='coerce')  # Convert to datetime format
        return df.sort_index()
    except Exception as e:
        st.error(f"❌ Error processing data for '{symbol}': {e}")
        return None

# ✅ User Input for Stock Symbol
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, TSLA)", "AAPL").upper()

# ✅ Fetch Data When Button is Clicked
if st.button("🔍 Get Insights"):
    with st.spinner("Fetching stock data..."):
        # Add a delay to handle API rate limits
        time.sleep(12)  # Wait 12 seconds to avoid hitting the rate limit

        data = get_stock_data(symbol)

    if data is not None:
        # --- 🔹 1. Closing Price Trend ---
        st.subheader(f"📈 {symbol} Closing Price Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Closing Price", line=dict(color="blue")))
        fig.update_layout(title=f"{symbol} Closing Price", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

        # --- 🔹 2. Moving Averages ---
        st.subheader("📊 Moving Averages (SMA & EMA)")
        data["SMA_50"] = data["Close"].rolling(window=50).mean()
        data["SMA_200"] = data["Close"].rolling(window=200).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Closing Price", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=data.index, y=data["SMA_50"], mode="lines", name="50-Day SMA", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=data.index, y=data["SMA_200"], mode="lines", name="200-Day SMA", line=dict(color="red")))
        fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

        # --- 🔹 3. Bollinger Bands (Volatility) ---
        st.subheader("📉 Bollinger Bands (Volatility)")
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["UpperBB"] = data["MA20"] + 2 * data["Close"].rolling(window=20).std()
        data["LowerBB"] = data["MA20"] - 2 * data["Close"].rolling(window=20).std()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Closing Price", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=data.index, y=data["UpperBB"], mode="lines", name="Upper Bollinger Band", line=dict(color="red", dash="dot")))
        fig.add_trace(go.Scatter(x=data.index, y=data["LowerBB"], mode="lines", name="Lower Bollinger Band", line=dict(color="green", dash="dot")))
        fig.update_layout(title="Bollinger Bands", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

        # --- 🔹 4. Trading Volume ---
        st.subheader("📊 Trading Volume")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data.index, y=data["Volume"], name="Trading Volume", marker=dict(color="purple")))
        fig.update_layout(title="Trading Volume", xaxis_title="Date", yaxis_title="Volume")
        st.plotly_chart(fig, use_container_width=True)

        # --- 🔹 5. Relative Strength Index (RSI) ---
        st.subheader("📍 Relative Strength Index (RSI)")
        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data["RSI"] = 100 - (100 / (1 + rs))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["RSI"], mode="lines", name="RSI", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=data.index, y=[70]*len(data), mode="lines", name="Overbought (70)", line=dict(color="red", dash="dash")))
        fig.add_trace(go.Scatter(x=data.index, y=[30]*len(data), mode="lines", name="Oversold (30)", line=dict(color="green", dash="dash")))
        fig.update_layout(title="Relative Strength Index (RSI)", xaxis_title="Date", yaxis_title="RSI Value")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"❌ Unable to load stock data for '{symbol}'. Please check the symbol or try again later.")