import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Heatmap & Smart Money Radar Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme CSS สไตล์นักวิเคราะห์มือโปร ---
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .analysis-box { background-color: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Global Heatmap & Smart Money Sector Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors Heatmap** ครบทุกกลุ่ม ตัดจบเส้นกราฟตามตลาดปิดจริงล่าสุดแบบเป๊ะๆ ไม่มีเส้นเกิน")

# --- รวบรวมทุก Sector ทั้งหมดตาม Heatmap ดั้งเดิมและสินทรัพย์พิเศษ ---
radar_assets = {
    "Technology (XLK)": "XLK",
    "Semiconductors / Patent Moat (SMH)": "SMH",
    "Financials (XLF)": "XLF",
    "Healthcare / Biotech (XLV)": "XLV",
    "Industrials & Smart Grid (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "Consumer Staples (XLP)": "XLP",
    "Energy & Clean Tech (XLE)": "XLE",
    "Advanced Materials (XLB)": "XLB",
    "Utilities (XLU)": "XLU",
    "Gold / Safe Haven (GC=F)": "GC=F",
    "Bitcoin / Global Liquidity (BTC-USD)": "BTC-USD"
}

@st.cache_data(ttl=3600)
def fetch_all_sectors_flow(assets_dict):
    volume_frames = {}
    latest_values = {}
    
    for name, symbol in assets_dict.items():
        try:
            df = yf.download(symbol, period="3mo", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) > 20:
                        vol_sma = vol.rolling(window=20).mean()
                        vol_change = ((vol - vol_sma) / vol_sma) * 100
                        volume_frames[name] = vol_change
                        latest_values[name] = float(vol_change.iloc[-1])
                    else:
                        latest_values[name] = 0.0
                else:
                    latest_values[name] = 0.0
        except:
            latest_values[name] = 0.0
            
    return volume_frames, latest_values

# ทดลองแสดงผลสรุปค่าล่าสุดแบบเคลียร์ๆ เพื่อให้มึงเช็กความถูกต้อง
vol_frames, latest_vals = fetch_all_sectors_flow(radar_assets)

st.markdown("### 📊 ตารางสรุป % Volume Change ล่าสุดของทุก Sector (แบบสมจริง)")
if latest_vals:
    df_display = pd.DataFrame(list(latest_vals.items()), columns=['Sector / Asset', 'Volume Change (Latest %)'])
    df_display['Volume Change (Latest %)'] = df_display['Volume Change (Latest %)'].round(2)
    st.dataframe(df_display, use_container_width=True)
else:
    st.warning("⚠️ กำลังดึงข้อมูลจากตลาด ร่างระบบใหม่อยู่เพื่อน ลองรีเฟรชหน้าจออีกทีนะ!")
    
