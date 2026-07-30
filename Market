import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Smart Money & Sector Flow Radar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme CSS ตกแต่งให้เข้มข้นสไตล์สายเทรดเดอร์โปร ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stAlert { background-color: #1f242d; color: #c9d1d9; border: 1px solid #383f4a; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: ควบคุมเรดาร์ ---
st.sidebar.title("🛠️ Control Panel")
st.sidebar.markdown("---")

analysis_mode = st.sidebar.radio(
    "เลือกโหมดวิเคราะห์:",
    ["📊 Sector Rotation & Asset Flow", "🚨 Volume Change & Smart Money Radar", "💡 Patent & Innovation Moat Watchlist"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **คำแนะนำจากเพื่อน:** โค้ดนี้ใช้ดึงข้อมูลราคาและวอลุ่มดิบจากตลาดโลก เพื่อสแกนหาจังหวะเล่นรอบตามรอยกองทุนใหญ่!")

# --- ฟังก์ชันดึงข้อมูลราคาและคำนวณ Volume Change ---
@st.cache_data(ttl=3600)
def fetch_market_data(tickers, period="3mo"):
    data = yf.download(tickers, period=period, group_by="ticker", auto_adjust=True)
    return data

# --- โหมดที่ 1: Sector Rotation & Asset Flow ---
if analysis_mode == "📊 Sector Rotation & Asset Flow":
    st.title("📊 Global Sector Rotation & Cross-Asset Flow")
    st.markdown("ติดตามการไหลเวียนของเงินทุนระหว่าง S&P 500 Sub-Sectors, ทองคำ และ Bitcoin เพื่อจับทิศทางตลาดรอบนี้")

    # กำหนดกลุ่มสินทรัพย์
    assets = {
        "Technology (XLK)": "XLK",
        "Communication Services (XLC)": "XLC",
        "Healthcare (XLV)": "XLV",
        "Industrials (XLI)": "XLI",
        "Energy & Grid (XLE)": "XLE",
        "Gold (GC=F)": "GC=F",
        "Bitcoin (BTC-USD)": "BTC-USD"
    }

    selected_asset_name = st.selectbox("เลือก Sector หรือสินทรัพย์ที่ต้องการเจาะลึก:", list(assets.keys()))
    ticker_symbol = assets[selected_asset_name]

    # ดึงข้อมูลย้อนหลัง 6 เดือน
    df_asset = yf.download(ticker_symbol, period="6mo", auto_adjust=True)
    
    if not df_asset.empty:
        # จัดการโครงสร้าง DataFrame ของ yfinance
        if isinstance(df_asset.columns, pd.MultiIndex):
            df_asset = df_asset.xs(ticker_symbol, axis=1, level=1) if ticker_symbol in df_asset.columns.levels[1] else df_asset

        # คำนวณผลตอบแทนสะสมและ Volume Change
        df_asset['Return_%'] = df_asset['Close'].pct_change() * 100
        df_asset['Vol_MA20'] = df_asset['Volume'].rolling(window=20).mean()
        df_asset['Vol_Spike'] = df_asset['Volume'] / df_asset['Vol_MA20']

        col1, col2, col3 = st.columns(3)
        current_price = float(df_asset['Close'].iloc[-1])
        prev_price = float(df_asset['Close'].iloc[-2])
        price_change = ((current_price - prev_price) / prev_price) * 100
        vol_spike_val = float(df_asset['Vol_Spike'].iloc[-1])

        col1.metric("ราคาปัจจุบัน (USD)", f"${current_price:,.2f}", f"{price_change:+.2f}%")
        col2.metric("วอลุ่มเทียบค่าเฉลี่ย 20 วัน", f"{vol_spike_val:.2f}x", "Volume Multiplier")
        col3.metric("สถานะสภาพคล่อง", "High Inflow" if vol_spike_val > 1.2 else "Normal Flow")

        st.markdown("### 📈 กราฟราคาและวอลุ่มย้อนหลัง")
        fig = px.line(df_asset, x=df_asset.index, y='Close', title=f"Price Trend: {selected_asset_name}")
        fig.update_layout(template="plotly_dark", xaxis_title="วันที่", yaxis_title="ราคา (USD)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")

# --- โหมดที่ 2: Volume Change & Smart Money Radar ---
elif analysis_mode == "🚨 Volume Change & Smart Money Radar":
    st.title("🚨 Volume Change & Smart Money Radar")
    st.markdown("สแกนหุ้นนวัตกรรมและเทคโนโลยีระดับโลกที่กำลังมี **Volume Spike** ผิดปกติ ซึ่งเป็นร่องรอยการสะสมของกองทุนสถาบัน")

    watchlist = ["ISRG", "FLNC", "META", "GOOGL", "NVDA", "GE", "TSLA", "AAPL"]
    
    scan_data = []
    for t in watchlist:
        stock = yf.Ticker(t)
        hist = stock.history(period="1mo")
        if not hist.empty and len(hist) >= 20:
            last_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].rolling(window=20).mean().iloc[-1]
            vol_ratio = last_vol / avg_vol if avg_vol > 0 else 0
            price_chg = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            
            scan_data.append({
                "Ticker": t,
                "Close Price ($)": round(float(hist['Close'].iloc[-1]), 2),
                "Daily Change (%)": round(float(price_chg), 2),
                "Volume Ratio (vs 20D MA)": round(float(vol_ratio), 2),
                "Signal Status": "🔥 Smart Money Accumulation" if vol_ratio > 1.5 else "⏳ Normal Trading"
            })

    df_scan = pd.DataFrame(scan_data)
    st.dataframe(df_scan, use_container_width=True)
    st.info("📌 **วิธีอ่านค่า:** ถ้า Volume Ratio พุ่งทะลุ 1.5x ขึ้นไป แปลว่ามีแรงซื้อขายหนาแน่นผิดปกติ (Block Trade / Institutional Footprint) ให้เช็กข่าวด่วนว่ามีประเด็นสิทธิบัตรหรือผลประกอบการอะไรหนุน!")

# --- โหมดที่ 3: Patent & Innovation Moat Watchlist ---
else:
    st.title("💡 Patent & Innovation Moat Watchlist")
    st.markdown("ส่องพอร์ตหุ้นนวัตกรรมที่มี **กำแพงสิทธิบัตร (IP Moat)** หนาแน่น ลอกเลียนแบบยาก และเป็นเป้าหมายของกองทุนระยะยาว")

    moat_stocks = {
        "ISRG (Intuitive Surgical)": "ผูกขาดตลาดหุ่นยนต์ผ่าตัด da Vinci และ Recurring Revenue จากอุปกรณ์ใช้แล้วทิ้ง",
        "FLNC (Fluence Energy)": "เจ้าพ่อระบบกักเก็บพลังงาน BESS และซอฟต์แวร์บริหารกริดแก้คอขวด AI Data Center",
        "GE (GE Aerospace)": "ราชาเครื่องยนต์เจ็ทและวัสดุศาสตร์คอมโพสิตขั้นสูง ผูกขาดตลาดการบินโลก",
        "NVDA (NVIDIA)": "เจ้าตลาดชิป AI และแพลตฟอร์มจำลองโลกฟิสิกส์ (Physical AI & Omniverse)"
    }

    for stock, desc in moat_stocks.items():
        with st.expander(f"🔹 {stock}"):
            st.write(f"**จุดแข็งเชิงนวัตกรรมและสิทธิบัตร:** {desc}")
            t_symbol = stock.split(" ")[0]
            tk = yf.Ticker(t_symbol)
            inf = tk.info
            col1, col2, col3 = st.columns(3)
            col1.metric("Market Cap", f"${inf.get('marketCap', 0):,}" if inf.get('marketCap') else "N/A")
            col2.metric("Trailing P/E", f"{inf.get('trailingPE', 'N/A')}")
            col3.metric("Profit Margin", f"{inf.get('profitMargins', 0)*100:.2f}%" if inf.get('profitMargins') else "N/A")

