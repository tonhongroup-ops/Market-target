import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Heatmap & Multi-Period Volume Radar Pro",
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

st.title("⚡ Multi-Period Volume Flow Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors Heatmap** พร้อมเจาะลึก % Vol Change แบบเทียบหลายช่วงเวลา (3 วัน, 1 สัปดาห์, 2 สัปดาห์, 1 เดือน)")

# --- รวบรวมทุก Sector และสินทรัพย์พิเศษ ---
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
def fetch_multi_period_volume_flow(assets_dict):
    table_data = []
    
    for name, symbol in assets_dict.items():
        try:
            # ดึงข้อมูลย้อนหลัง 3 เดือน เพื่อให้มีข้อมูลพอคำนวณค่าเฉลี่ยและช่วงเวลาต่างๆ
            df = yf.download(symbol, period="3mo", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 30:
                        # คำนวณค่าเฉลี่ย Volume 20 วัน (SMA 20) เป็นฐาน
                        vol_sma20 = vol.rolling(window=20).mean()
                        
                        # คำนวณ % Vol Change เทียบกับค่าเฉลี่ยย้อนหลังในแต่ละจุด
                        # 1. ล่าสุด (Latest)
                        v_latest = float(((vol.iloc[-1] - vol_sma20.iloc[-1]) / vol_sma20.iloc[-1]) * 100)
                        # 2. ย้อนหลัง 3 วัน (เฉลี่ย 3 วันล่าสุดเทียบ SMA)
                        v_3d = float(((vol.iloc[-3:].mean() - vol_sma20.iloc[-3:].mean()) / vol_sma20.iloc[-3:].mean()) * 100)
                        # 3. ย้อนหลัง 1 สัปดาห์ / 5 วัน
                        v_1w = float(((vol.iloc[-5:].mean() - vol_sma20.iloc[-5:].mean()) / vol_sma20.iloc[-5:].mean()) * 100)
                        # 4. ย้อนหลัง 2 สัปดาห์ / 10 วัน
                        v_2w = float(((vol.iloc[-10:].mean() - vol_sma20.iloc[-10:].mean()) / vol_sma20.iloc[-10:].mean()) * 100)
                        # 5. ย้อนหลัง 1 เดือน / 20 วัน
                        v_1m = float(((vol.iloc[-20:].mean() - vol_sma20.iloc[-20:].mean()) / vol_sma20.iloc[-20:].mean()) * 100)
                        
                        table_data.append({
                            "Sector / Asset": name,
                            "Latest (%)": round(v_latest, 2),
                            "3 Days (%)": round(v_3d, 2),
                            "1 Week (%)": round(v_1w, 2),
                            "2 Weeks (%)": round(v_2w, 2),
                            "1 Month (%)": round(v_1m, 2)
                        })
        except Exception as e:
            continue
            
    return pd.DataFrame(table_data)

# รันฟังก์ชันดึงข้อมูลและแสดงผล
with st.spinner('กำลังประมวลผลกระแสเงินทุนและคำนวณสถิติย้อนหลังทุก Sector...'):
    df_result = fetch_multi_period_volume_flow(radar_assets)

st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (เทียบกับค่าเฉลี่ยปกติ)")
if not df_result.empty:
    # จัดรูปแบบตารางให้ดูง่าย
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 💡 มุมมองวิเคราะห์เกมทุน (Multi-Timeframe Flow Insights)")
    st.info("📌 **วิธีอ่านค่า:** หากช่อง **Latest** หรือ **3 Days** พุ่งสูงขึ้นสวนทางกับช่อง **1 Month** ที่ติดลบ แปลว่ากำลังมีเม็ดเงินก้อนใหม่ไหลทะลักเข้ามาเปลี่ยนเทรนด์อย่างฉับพลัน (เช่น กรณีกลุ่ม Safe Haven หรือทองคำที่เกิด Panic Flow เข้ากะทันหัน) ในทางกลับกัน ถ้าติดลบยาวทุกคอลัมน์แสดงว่าตลาดอยู่ในภาวะซึมตัวและไร้สภาพคล่อง")
else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    
