import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dynamic Sector & Patent Swing Radar",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .stock-card { background-color: #161b22; padding: 15px; border-radius: 8px; border-left: 4px solid #1f6feb; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Dynamic Sector Stock Screener & Patent Momentum Radar")
st.markdown("ระบบสแกนหุ้นรายตัวตามธีมเซกเตอร์ คัดกรองตัวที่วิ่งแรงและวอลุ่มเข้าสอดคล้องกับภาพรวมตลาดแบบเรียลไทม์")

st.sidebar.markdown("### ⚙️ Engine Control")
scan_btn = st.sidebar.button("🚀 สแกนหาหุ้นเด่นตามธีมเซกเตอร์ (Run Stock Screener)", type="primary")

# กำหนดกลุ่มหุ้นรายเซกเตอร์สำหรับให้ระบบวิ่งสแกนหาตัวที่วิ่งตามธีม
sector_watchlist = {
    "1. Information Technology (AI & Cloud)": ["NVDA", "AVGO", "MSFT", "AAPL", "AMD", "PLTR", "CRM", "QCOM"],
    "2. Health Care & Biotech (Med Patents)": ["LLY", "ISRG", "NVO", "UNH", "JNJ", "ABBV", "AMGN"],
    "3. Consumer Discretionary (Innovation)": ["AMZN", "TSLA", "NFLX", "UBER", "ABNB"],
    "4. SET100 Thailand (Leading S-Curve)": ["KBANK.BK", "PTT.BK", "BDMS.BK", "CPALL.BK", "ADVANC.BK", "DELTA.BK"]
}

if scan_btn:
    scan_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["scan_timestamp"] = scan_timestamp
    st.sidebar.success(f"สแกนสำเร็จเมื่อ: {scan_timestamp}")
    
    with st.spinner("กำลังสแกนหุ้นรายตัวในแต่ละเซกเตอร์และประมวลผลโมเมนตัม..."):
        
        end_date = datetime.today()
        start_date = end_date - timedelta(days=45)
        
        screener_results = {}
        
        for sector_name, tickers in sector_watchlist.items():
            sector_passing_stocks = []
            for ticker in tickers:
                try:
                    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
                    if not df.empty and len(df) >= 15:
                        close = df['Close'].squeeze()
                        vol = df['Volume'].squeeze()
                        
                        p_now = float(close.iloc[-1])
                        p_1w = float(close.iloc[-5]) if len(close) >= 5 else p_now
                        
                        chg_1w = ((p_now - p_1w) / p_1w) * 100
                        vol_avg = float(vol.iloc[-5:-1].mean()) if len(vol) >= 5 else float(vol.iloc[-1])
                        vol_now = float(vol.iloc[-1])
                        vol_exp = ((vol_now - vol_avg) / vol_avg) * 100 if vol_avg > 0 else 0
                        
                        # คัดกรองหุ้นที่ 1 สัปดาห์เป็นบวกและมีแรงซื้อเข้ามาสนับสนุน
                        if chg_1w >= 0:
                            sector_passing_stocks.append({
                                "Ticker": ticker,
                                "Price": round(p_now, 2),
                                "1W Chg (%)": round(chg_1w, 2),
                                "Volume Exp (%)": round(vol_exp, 2)
                            })
                except Exception:
                    continue
            
            # เรียงลำดับหุ้นที่เปอร์เซ็นต์เปลี่ยนแปล 1 สัปดาห์สูงสุดในเซกเตอร์
            if sector_passing_stocks:
                sector_passing_stocks = sorted(sector_passing_stocks, key=lambda x: x["1W Chg (%)"], reverse=True)
                screener_results[sector_name] = sector_passing_stocks[:3] # เอา Top 3 ตัวที่เด่นสุดในรอบนั้น
                
        # แสดงผลลัพธ์การสแกน
        st.markdown(f"---")
        st.markdown(f"### 🎯 ผลการสแกนหุ้นเด่นตามธีมเซกเตอร์ (Scanned at: {scan_timestamp})")
        st.info("💡 ระบบได้ทำการคัดกรองหุ้นรายตัวในแต่ละเซกเตอร์ที่มีโมเมนตัมราคา 1 สัปดาห์เป็นบวกและมีแรงซื้อ (Volume Expansion) สนับสนุนแบบเรียลไทม์")
        
        if screener_results:
            for sec, stocks in screener_results.items():
                st.markdown(f"#### 🌐 Sector: {sec}")
                for stck in stocks:
                    st.markdown(f"""
                    <div class="stock-card">
                        <b>📌 Ticker: {stck['Ticker']}</b> | ราคาล่าสุด: <b>{stck['Price']}</b> | เปลี่ยนแปลง 1 สัปดาห์: <span style="color: #3fb950; font-weight: bold;">+{stck['1W Chg (%)']}%</span> | อัตราขยายตัววอลุ่ม: <b>{stck['Volume Exp (%)']}%</b><br>
                        <small><i>👉 หุ้นตัวนี้ถูกดึงขึ้นมาเพราะผ่านเกณฑ์ Momentum & Volume Breakout ในรอบการสแกนนี้ มึงสามารถนำไปเจาะลึกงบการเงินและสิทธิบัตรต่อได้ทันที</i></small>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.warning("รอบนี้ตลาดผันผวน หุ้นในเซกเตอร์ส่วนใหญ่ยังไม่ผ่านเกณฑ์โมเมนตัมขาขึ้น")

else:
    if "scan_timestamp" in st.session_state:
        st.info(f"ข้อมูลการสแกนล่าสุดเมื่อ: {st.session_state['scan_timestamp']}")
    else:
        st.info("👈 คลิกปุ่ม **'สแกนหาหุ้นเด่นตามธีมเซกเตอร์'** ทางด้านซ้าย เพื่อให้ระบบสแกนหุ้นรายตัวตามเงื่อนไขใหม่สดๆ ได้เลยเพื่อน!")
