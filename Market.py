import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Innovation & Patent Smart Money Radar",
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
    
    for name, symbol in assets_dict.items():
        try:
            df = yf.download(symbol, period="3mo", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 30:
                        vol_sma20 = vol.rolling(window=20).mean()
                        
                        v_latest = float(((vol.iloc[-1] - vol_sma20.iloc[-1]) / vol_sma20.iloc[-1]) * 100)
                        v_3d = float(((vol.iloc[-3:].mean() - vol_sma20.iloc[-3:].mean()) / vol_sma20.iloc[-3:].mean()) * 100)
                        v_1w = float(((vol.iloc[-5:].mean() - vol_sma20.iloc[-5:].mean()) / vol_sma20.iloc[-5:].mean()) * 100)
                        v_2w = float(((vol.iloc[-10:].mean() - vol_sma20.iloc[-10:].mean()) / vol_sma20.iloc[-10:].mean()) * 100)
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

# รันฟังก์ชันดึงข้อมูล
with st.spinner('กำลังเชื่อมต่อฐานข้อมูลตลาดและประมวลผลกระแสเงินทุน...'):
    df_result = fetch_multi_period_volume_flow(radar_assets)

st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (เทียบกับค่าเฉลี่ยปกติ)")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- ส่วนวิเคราะห์เชิงลึกสไตล์เพื่อนรักนักลงทุน ---
    st.markdown("---")
    st.markdown("### 🧠 มุมมองวิเคราะห์เกมทุน สิทธิบัตร และรอบข่าวสาร (AI & Partner Insights)")
    
    # ตรวจสอบพฤติกรรมทองคำและกลุ่มเทคจากข้อมูลล่าสุดเพื่อจำลองการวิเคราะห์อัตโนมัติ
    gold_row = df_result[df_result['Sector / Asset'].str.contains('Gold')]
    tech_row = df_result[df_result['Sector / Asset'].str.contains('Semiconductors')]
    
    is_gold_panic = False
    if not gold_row.empty:
        latest_gold_val = gold_row['Latest (%)'].values[0]
        if latest_gold_val > 100:
            is_gold_panic = True

    if is_gold_panic:
        st.warning("🚨 **ตรวจพบสัญญาณ Panic & Safe Haven Flow:** เม็ดเงินก้อนใหญ่กำลังไหลทะลักเข้าสู่ทองคำและสินทรัพย์ปลอดภัยอย่างรุนแรง สะท้อนความกังวลเชิงมหภาค ทำให้กลุ่มหุ้นนวัตกรรมและเทคโดนดูดสภาพคล่องระยะสั้น")
    else:
        st.info("⚖️ **ภาวะตลาดทั่วไป:** กระแสเงินทุนเคลื่อนตัวตามรอบปกติ นักลงทุนกำลังให้น้ำหนักกับการติดตามงบการเงินและข่าวสารการจดสิทธิบัตรรายตัว")

    st.markdown("""
    <div class="analysis-box">
    <h4>💡 คำแนะนำเชิงกลยุทธ์การเล่นรอบ (Action Plan):</h4>
    <ul>
        <li><b>สำหรับกลุ่มนวัตกรรม & สิทธิบัตร (Tech / AI / SMH):</b> ช่วงที่วอลุ่มซึมตัวหรือโดนดึงสภาพคล่องออกไปชั่วคราว ถือเป็นจังหวะทองในการนั่งทำการบ้าน แกะรอยงบการเงิน และเช็กสตอรี่สิทธิบัตรเชิงลึก อย่าเพิ่งรีบไล่ราคา ให้รอจังหวะย่อตัวสะสมที่แนวรับ</li>
        <li><b>การจับตา Catalyst:</b> ติดตามข่าวสารการประกาศผลประกอบการและทิศทางการลงทุนในโครงสร้างพื้นฐานเทคโนโลยี เพราะเมื่อไหร่ที่เงินทุนเริ่มหมุนกลับ (Risk-On) หุ้นที่มี Patent Moat แกร่งจะดีดตัวแรงที่สุด</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    


เพิ่มจากโค้ดนี้นะ เป็น %volchangeโดยแสดงผลเป็นค่าที่คิดจากปัจจุบัน  เพิ่ม timeframe  อีก 2และ3 เดือน
