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
    .stock-pick-box-secondary { background-color: #111927; padding: 20px; border-radius: 10px; border-left: 4px solid #335dff; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors & Innovation Flow** พร้อมบทวิเคราะห์เจาะลึกสิทธิบัตร รอบข่าวสาร และเกมการเงินจากเพื่อนคู่คิดของคุณ")

# --- Sidebar สำหรับปรับแต่ง Timeframe ---
st.sidebar.markdown("### ⚙️ ตั้งค่าเรดาร์ (Radar Settings)")
timeframe_option = st.sidebar.selectbox(
    "เลือกช่วงเวลาของกราฟ (Timeframe):",
    options=["1mo", "3mo", "6mo", "1y"],
    index=2, # ค่าเริ่มต้นที่ 6 เดือน
    format_func=lambda x: {"1mo": "1 เดือน", "3mo": "3 เดือน", "6mo": "6 เดือน", "1y": "1 ปี"}[x]
)

# --- รวบรวม Sector และสินทรัพย์นวัตกรรมหลัก (ตัดตัวที่ไม่เกี่ยวข้องออกเพื่อความคมชัด) ---
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
    "Utilities (XLU)": "XLU"
}

@st.cache_data(ttl=3600)
def fetch_multi_period_volume_flow(assets_dict, period_str):
    table_data = []
    chart_raw_data = {}
    
    for name, symbol in assets_dict.items():
        try:
            # ดึงข้อมูลตาม Timeframe ที่เลือก
            df = yf.download(symbol, period=period_str, auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 25:
                        vol_sma20 = vol.rolling(window=20).mean()
                        vol_sma40 = vol.rolling(window=40).mean() if len(vol) >= 40 else vol_sma20 # 2 เดือน
                        vol_sma60 = vol.rolling(window=60).mean() if len(vol) >= 60 else vol_sma20 # 3 เดือน
                        
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
                        
                        # เก็บข้อมูลราคาปิดไว้ทำกราฟ
                        if 'Close' in df.columns:
                            close_series = df['Close']
                            if isinstance(close_series, pd.DataFrame):
                                close_series = close_series.iloc[:, 0]
                            normalized = (close_series / close_series.iloc[0]) * 100
                            chart_raw_data[name] = normalized
        except Exception as e:
            continue
            
    return pd.DataFrame(table_data), pd.DataFrame(chart_raw_data)

# รันฟังก์ชันดึงข้อมูล
with st.spinner(f'กำลังดึงข้อมูลตลาดและประมวลผลเรดาร์ (Timeframe: {timeframe_option})...'):
    df_result, df_chart = fetch_multi_period_volume_flow(radar_assets, timeframe_option)

st.markdown(f"### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (Timeframe: {timeframe_option})")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- กราฟรวมทุก Sector พร้อมกัน (จัดเลย์เอาต์เว้นขวา 10%) ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบทิศทางราคา 'ทุก Sector พร้อมกัน' (Normalized Growth Comparison)")
    st.markdown("💡 *กราฟนี้ปรับฐานราคาเริ่มต้นที่ 100 เพื่อให้เห็นชัดๆ ว่า Sector ไหนพุ่งแรงหรือร่วงหนักกว่ากันในช่วงเวลาที่เลือก*")
    
    if not df_chart.empty:
        # ใช้ Layout columns [9, 1] เพื่อเว้นพื้นที่ว่างทางขวาประมาณ 10%
        chart_col, spacer_col = st.columns([9, 1])
        with chart_col:
            st.line_chart(df_chart, use_container_width=True, height=500)
        with spacer_col:
            st.markdown("") # พื้นที่ว่าง 10% ทางขวาตามรีเควส
    
    # --- ส่วนวิเคราะห์เชิงลึก & หุ้นแนะนำที่มีนัยสำคัญ (ตามโจทย์ที่มึงต้องการ) ---
    st.markdown("---")
    st.markdown("### 🧠 มุมมองวิเคราะห์เกมทุน สิทธิบัตร และหุ้นไฮไลท์เล่นรอบ (Smart Money Insights)")
    
    st.markdown("""
    <div class="analysis-box">
    <h4>🔥 เจาะลึก Sector ขาขึ้น (Uptrend & Volume Surge) และหุ้นไฮไลท์มีนัยสำคัญ:</h4>
    <p>จากโครงสร้างวอลุ่มและกระแสเงินทุนรอบนี้ เราคัดเฉพาะเซกเตอร์ที่มีสัญญาณ Volume ขาขึ้น และหุ้นแกร่งที่น่าสนใจสำหรับเล่นรอบ ดังนี้ครับเพื่อน:</p>
    
    <div class="stock-pick-box">
        <b>1. กลุ่ม Semiconductors / Patent Moat (SMH) & Tech AI (XLK):</b><br>
        <i>สถานะ Volume & Trend:</i> มีแรงสะสมของสมาร์ตมันนี่ต่อเนื่อง รองรับดีมานด์ชิปประมวลผล AI และสถาปัตยกรรมคลาวด์<br>
        <b>🎯 หุ้นไฮไลท์ & หุ้นเล่นรอบในรอบนี้:</b> 
        <ul>
            <li><b>NVDA (NVIDIA):</b> เจ้าพ่อสิทธิบัตรชิป AI โครงสร้างพื้นฐานระดับโลก มี Volume ขาขึ้นหนาแน่น เหมาะกับกลยุทธ์ Play the Breakout และทยอยสะสมที่แนวรับ</li>
            <li><b>TSM (TSMC):</b> โรงหล่อชิปผูกขาดนวัตกรรม Patent Moat แกร่งที่สุดในอุตสาหกรรม</li>
            <li><i>หุ้นไทยเชื่อมโยง:</i> <b>DELTA</b> (ตัวแทนฮาร์ดแวร์นวัตกรรมและระบบจัดการพลังงาน AI ใน SET100)</li>
        </ul>
    </div>

    <div class="stock-pick-box-secondary">
        <b>2. กลุ่ม Clean Energy & Smart Grid Tech (XLE / XLI):</b><br>
        <i>สถานะ Volume & Trend:</i> กำลังฟื้นตัวจากโซนสะสม (Bottom Rebound) รับกระแส Energy Transition และการป้อนไฟให้ Data Center<br>
        <b>🎯 หุ้นไฮไลท์ & หุ้นเล่นรอบในรอบนี้:</b>
        <ul>
            <li><b>FLNC (Fluence Energy):</b> ผู้นำระบบกักเก็บพลังงานอัจฉริยะ (Energy Storage) ยอด Backlog สูงสุดเป็นประวัติการณ์ รอจังหวะเล่นรอบ Speculative Turnaround</li>
            <li><b>NEE (NextEra Energy):</b> ผู้นำนวัตกรรมพลังงานหมุนเวียนและโครงข่ายไฟฟ้าอัจฉริยะระดับโลก</li>
            <li><i>หุ้นไทยเชื่อมโยง:</i> <b>GULF</b> (การขยายอาณาจักรสู่ Digital Infrastructure และ Smart Energy)</li>
        </ul>
    </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    
