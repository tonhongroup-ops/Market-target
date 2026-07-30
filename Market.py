import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Money Flow Radar & Sector Rotation",
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
    "เลือกโหมดวิเคราะห์ภาพใหญ่:",
    ["🌍 Global Money Flow (รวมทุกเส้น ซ่อน/แสดงได้)", "📊 Sector Rotation & Asset Flow", "🚨 Volume Change & Smart Money Radar", "💡 Patent & Innovation Moat Watchlist"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **มุมมองเพื่อน:** ภาพใหญ่ของเงินโลกตอนนี้กำลังวิ่งหาความมั่นคงและนวัตกรรมที่มีสิทธิบัตรผูกขาด มาแกะรอยดูกันว่าเงินไหลไปไหนบ้าง!")

# --- โหมดที่ 0: Global Money Flow (รวมเส้นภาพใหญ่ทั้งหมดตามที่มึงต้องการ) ---
if analysis_mode == "🌍 Global Money Flow (รวมทุกเส้น ซ่อน/แสดงได้)":
    st.title("🌍 Global Money Flow Macro Radar")
    st.markdown("ภาพใหญ่กระแสเงินทุนของโลก (S&P 500 Sectors, ทองคำ, Bitcoin และหุ้นนวัตกรรม) มึงสามารถกดคลิกที่ชื่อใน Legend ด้านขวาเพื่อ **Hide (ซ่อน)** หรือ **Show (แสดง)** ทีละเส้นได้ตามใจชอบ เพื่อดูเปรียบเทียบความต่าง!")

    # ดึงข้อมูลสินทรัพย์หลักภาพใหญ่ (ใช้ผลตอบแทนสะสมเทียบจุดเริ่มต้น เพื่อให้อยู่สเกลเดียวกัน 0%)
    macro_tickers = {
        "Technology (XLK)": "XLK",
        "Healthcare (XLV)": "XLV",
        "Industrials (XLI)": "XLI",
        "Gold (GC=F)": "GC=F",
        "Bitcoin (BTC-USD)": "BTC-USD",
        "NVIDIA (NVDA)": "NVDA",
        "Fluence Energy (FLNC)": "FLNC"
    }

    @st.cache_data(ttl=3600)
    def fetch_multi_assets(tickers_dict, period="6mo"):
        data_frames = {}
        for name, symbol in tickers_dict.items():
            df = yf.download(symbol, period=period, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
                # คำนวณ % Return สะสมจากวันแรกในรอบ 6 เดือน เพื่อเทียบสเกลกันได้
                data_frames[name] = ((df['Close'] / df['Close'].iloc[0]) - 1) * 100
        return pd.DataFrame(data_frames)

    with st.spinner("กำลังดึงข้อมูลกระแสเงินทุนโลกทั้งหมด มาสับให้ดู..."):
        df_macro = fetch_multi_assets(macro_tickers)

    if not df_macro.empty:
        st.markdown("### 📈 กราฟเปรียบเทียบผลตอบแทนสะสม (%) - กดที่ชื่อ Legend เพื่อซ่อน/แสดงแต่ละเส้นได้ทันที")
        
        fig_macro = px.line(df_macro, title="Global Asset Flow Comparison (% Return Normalized)")
        fig_macro.update_layout(
            template="plotly_dark",
            xaxis_title="วันที่",
            yaxis_title="ผลตอบแทนสะสมเทียบจุดเริ่มต้น (%)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_macro, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📊 ตารางสรุปการเปลี่ยนแปลงล่าสุดของแต่ละสินทรัพย์")
        st.dataframe(df_macro.tail(1).T.rename(columns={df_macro.index[-1]: "ผลตอบแทนสะสมล่าสุด (%)"}), use_container_width=True)
    else:
        st.error("ไม่สามารถดึงข้อมูลภาพใหญ่ได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")

# --- โหมดที่ 1: Sector Rotation & Asset Flow ---
elif analysis_mode == "📊 Sector Rotation & Asset Flow":
    st.title("📊 Global Sector Rotation & Cross-Asset Flow")
    st.markdown("ติดตามการไหลเวียนของเงินทุนรายตัวเพื่อเจาะลึกแบบละเอียด")

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

    df_asset = yf.download(ticker_symbol, period="6mo", auto_adjust=True)
    if not df_asset.empty:
        if isinstance(df_asset.columns, pd.MultiIndex):
            df_asset = df_asset.xs(ticker_symbol, axis=1, level=1) if ticker_symbol in df_asset.columns.levels[1] else df_asset

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

        fig = px.line(df_asset, x=df_asset.index, y='Close', title=f"Price Trend: {selected_asset_name}")
        fig.update_layout(template="plotly_dark", xaxis_title="วันที่", yaxis_title="ราคา (USD)")
        st.plotly_chart(fig, use_container_width=True)

# --- โหมดที่ 2: Volume Change & Smart Money Radar ---
elif analysis_mode == "🚨 Volume Change & Smart Money Radar":
    st.title("🚨 Volume Change & Smart Money Radar")
    st.markdown("สแกนหุ้นนวัตกรรมและเทคโนโลยีระดับโลกที่มี Volume Spike ผิดปกติ")

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

# --- โหมดที่ 3: Patent & Innovation Moat Watchlist ---
else:
    st.title("💡 Patent & Innovation Moat Watchlist")
    st.markdown("ส่องพอร์ตหุ้นนวัตกรรมที่มีกำแพงสิทธิบัตร (IP Moat) หนาแน่น")

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
            
