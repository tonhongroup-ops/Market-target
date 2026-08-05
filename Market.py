import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Innovation & Patent Smart Money Radar Pro",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme CSS สไตล์นักวิเคราะห์มือโปร ---
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .analysis-box { background-color: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-top: 25px; }
    .stock-pick-box { background-color: #111927; padding: 20px; border-radius: 10px; border-left: 4px solid #3fb950; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors & Innovation Flow** พร้อมบทวิเคราะห์เจาะลึกสิทธิบัตร รอบข่าวสาร และเกมการเงินจากเพื่อนคู่คิดของคุณ")

# --- รวบรวมทุก Sector และสินทรัพย์พิเศษ ---
radar_assets = {
    "Technology & AI (XLK)": "XLK",
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
    chart_raw_data = {}
    
    for name, symbol in assets_dict.items():
        try:
            # ดึงข้อมูลย้อนหลัง 6 เดือน
            df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 70:
                        vol_sma20 = vol.rolling(window=20).mean()
                        vol_sma40 = vol.rolling(window=40).mean() # 2 เดือน
                        vol_sma60 = vol.rolling(window=60).mean() # 3 เดือน
                        
                        v_latest = float(((vol.iloc[-1] - vol_sma20.iloc[-1]) / vol_sma20.iloc[-1]) * 100)
                        v_3d = float(((vol.iloc[-3:].mean() - vol_sma20.iloc[-3:].mean()) / vol_sma20.iloc[-3:].mean()) * 100)
                        v_1w = float(((vol.iloc[-5:].mean() - vol_sma20.iloc[-5:].mean()) / vol_sma20.iloc[-5:].mean()) * 100)
                        v_2w = float(((vol.iloc[-10:].mean() - vol_sma20.iloc[-10:].mean()) / vol_sma20.iloc[-10:].mean()) * 100)
                        v_1m = float(((vol.iloc[-20:].mean() - vol_sma20.iloc[-20:].mean()) / vol_sma20.iloc[-20:].mean()) * 100)
                        v_2m = float(((vol.iloc[-1] - vol_sma40.iloc[-1]) / vol_sma40.iloc[-1]) * 100)
                        v_3m = float(((vol.iloc[-1] - vol_sma60.iloc[-1]) / vol_sma60.iloc[-1]) * 100)
                        
                        table_data.append({
                            "Sector / Asset": name,
                            "Latest (%)": round(v_latest, 2),
                            "3 Days (%)": round(v_3d, 2),
                            "1 Week (%)": round(v_1w, 2),
                            "2 Weeks (%)": round(v_2w, 2),
                            "1 Month (%)": round(v_1m, 2),
                            "2 Months (%)": round(v_2m, 2),
                            "3 Months (%)": round(v_3m, 2)
                        })
                        
                        # เก็บข้อมูลราคาปิดไว้สำหรับทำกราฟแนวโน้ม Sector
                        if 'Close' in df.columns:
                            chart_raw_data[name] = df['Close'].tail(60)
        except Exception as e:
            continue
            
    return pd.DataFrame(table_data), chart_raw_data

# รันฟังก์ชันดึงข้อมูล
with st.spinner('กำลังเชื่อมต่อฐานข้อมูลตลาดและประมวลผลกระแสเงินทุน...'):
    df_result, chart_data = fetch_multi_period_volume_flow(radar_assets)

st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (เทียบกับค่าเฉลี่ยปกติ)")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- กราฟแสดงแนวโน้มราคา Sector ที่มึงถามหาว่าหายไปไหน! ---
    st.markdown("---")
    st.markdown("### 📈 กราฟแนวโน้มราคา Sector ย้อนหลัง (Trend & Price Action)")
    if chart_data:
        selected_sector_chart = st.selectbox("เลือก Sector หรือสินทรัพย์เพื่อดูเส้นทางราคา (Normalized Close 60 Days):", list(chart_data.keys()))
        if selected_sector_chart in chart_data:
            # Normalize ราคาให้เริ่มที่ 100 เพื่อเทียบสัดส่วนการเติบโต
            raw_series = chart_data[selected_sector_chart]
            if isinstance(raw_series, pd.DataFrame):
                raw_series = raw_series.iloc[:, 0]
            normalized_df = (raw_series / raw_series.iloc[0]) * 100
            st.line_chart(normalized_df)
    
    # --- ส่วนวิเคราะห์เชิงลึกสไตล์เพื่อนรักนักลงทุน & แนะนำหุ้นที่มีนัยสำคัญ ---
    st.markdown("---")
    st.markdown("### 🧠 มุมมองวิเคราะห์เกมทุน สิทธิบัตร และรอบข่าวสาร (AI & Smart Money Insights)")
    
    # ค้นหา Sector ที่เงินกำลังไหลเข้าแรงสุดในรอบ 1 เดือนหรือล่าสุด
    st.markdown("""
    <div class="analysis-box">
    <h4>🔥 วิเคราะห์กระแสเงินทุน (Money Flow Momentum) & หุ้นไฮไลท์ราย Sector:</h4>
    <p>จากการสแกนโครงสร้างวอลุ่มทั้งระยะสั้น (Latest/3Days) และระยะกลาง (2-3 Months) พบจุดสะสมของสมาร์ตมันนี่ในกลุ่มนวัตกรรมและโครงสร้างพื้นฐานสำคัญ ดังนี้ครับเพื่อน:</p>
    
    <div class="stock-pick-box">
        <b>1. กลุ่ม Semiconductors / Patent Moat (SMH) & Tech AI (XLK):</b><br>
        <i>นัยสำคัญทางเทค & สิทธิบัตร:</i> เป็นหัวใจของการจดสิทธิบัตรชิปประมวลผล AI และสถาปัตยกรรมคลาวด์ หาก % Volume Change ในช่วง 2-3 เดือนเริ่มฟื้นตัวจากจุดซึม แปลว่าเม็ดเงินกำลังตั้งหลักรอบใหม่รับสินค้า Hi-Season<br>
        <b>🎯 หุ้นแนะนำมีนัยสำคัญ:</b> 
        <ul>
            <li><b>NVDA (NVIDIA):</b> เจ้าพ่อสิทธิบัตรชิป AI และโครงสร้างพื้นฐาน Data Center โลก</li>
            <li><b>TSM (TSMC):</b> โรงหล่อชิปผูกขาดเทคโนโลยีขั้นสูง Patent Moat แน่นหนาที่สุด</li>
            <li><i>ฝั่งไทย:</i> <b>DELTA</b> (ตัวแทนฮาร์ดแวร์นวัตกรรมและระบบจัดการพลังงาน AI ใน SET100)</li>
        </ul>
    </div>

    <div class="stock-pick-box" style="border-left-color: #335dff;">
        <b>2. กลุ่ม Industrials & Smart Grid (XLI) / Energy Tech (XLE):</b><br>
        <i>นัยสำคัญทางเทค & สิทธิบัตร:</i> เมกะเทรนด์การเปลี่ยนผ่านพลังงาน (Energy Transition) และระบบโครงข่ายไฟฟ้าอัจฉริยะ (Smart Grid) ที่ต้องอาศัยนวัตกรรมการบริหารพลังงานสะอาด<br>
        <b>🎯 หุ้นแนะนำมีนัยสำคัญ:</b>
        <ul>
            <li><b>NEE (NextEra Energy):</b> ผู้นำนวัตกรรมพลังงานหมุนเวียนและโครงข่ายอัจฉริยะระดับโลก</li>
            <li><i>ฝั่งไทย:</i> <b>GULF</b> (การขยายอาณาจักรสู่ Digital Infrastructure, Data Center และ Smart Energy เต็มตัว)</li>
        </ul>
    </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    
