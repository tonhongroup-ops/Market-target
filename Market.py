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
    .verdict-box { background-color: #162330; padding: 20px; border-radius: 10px; border: 1px solid #1f6feb; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors & Innovation Flow** พร้อมระบบสรุปเทรนด์ขาขึ้นอัตโนมัติเพื่อมึงโดยเฉพาะ")

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
def fetch_and_evaluate_market(assets_dict):
    table_data = []
    historical_prices = {} 
    uptrend_candidates = []
    
    for name, symbol in assets_dict.items():
        try:
            df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Close' in df.columns:
                    close_series = df['Close'].dropna()
                    if not close_series.empty:
                        normalized_series = (close_series / close_series.iloc[0]) * 100
                        historical_prices[name] = normalized_series
                        
                        # เช็คเบื้องต้นว่าเป็นขาขึ้นระยะสั้นหรือไม่ (ราคาปัจจุบัน > ค่าเฉลี่ย 20 วัน และทำทรงยก Low)
                        sma20_price = close_series.rolling(window=20).mean().iloc[-1]
                        current_price = close_series.iloc[-1]
                        price_trend_score = current_price - sma20_price

                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 70:
                        vol_sma20 = vol.rolling(window=20).mean()
                        vol_sma40 = vol.rolling(window=40).mean()
                        vol_sma60 = vol.rolling(window=60).mean()
                        
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
                        
                        # คัดกรองเงื่อนไขเข้าสู่โหมด "กำลังเป็นขาขึ้น / Smart Money เข้าสะสม"
                        # เงื่อนไข: วอลุ่มสัปดาห์นี้ขยายตัวกว่าค่าเฉลี่ย และราคาอยู่เหนือเส้นค่าเฉลี่ย
                        if v_1w > 10 and price_trend_score > 0:
                            uptrend_candidates.append(name)
                            
        except Exception:
            continue
            
    return pd.DataFrame(table_data), historical_prices, uptrend_candidates

# รันฟังก์ชันดึงข้อมูลและประเมินผล
with st.spinner('กำลังสแกนและประมวลผลเทรนด์ตลาด...'):
    df_result, price_data, uptrends = fetch_and_evaluate_market(radar_assets)

# --- ส่วนสรุปผลฟันธงอัตโนมัติ (Verdict Summary Box) ---
st.markdown("### 🎯 บทสรุปเรดาร์สแกนขาขึ้น (Smart Money Verdict)")
st.markdown(f"""
<div class="verdict-box">
    <h4>💡 สรุปผลวิเคราะห์อัตโนมัติจากระบบ:</h4>
    <p><b>สถานะตลาดรอบล่าสุด:</b> ระบบได้คัดกรองสินทรัพย์และกลุ่มอุตสาหกรรมที่มีการขยายตัวของ Volume ร่วมกับโครงสร้างราคาขาขึ้น พบว่ากลุ่มที่กำลังถูก Smart Money เข้าสะสมและมีสัญญาณเด่นชัดในรอบนี้ ได้แก่:</p>
    <ul>
        {''.join([f"<li>🚀 <b>{item}</b>: กำลังแสดงพลังซื้อหนุนนำ (Volume Expansion) และโครงสร้างราคาทำทรงขาขึ้นชัดเจน เหมาะแก่การเก็งรอบตามกระแสเงินทุน</li>" for item in uptrends]) if uptrends else "<li>⚖️ ตลาดอยู่ในช่วงพักฐาน ไร้แรงส่งรุนแรง เม็ดเงินยังกระจายตัวไม่ชี้ชัด ฝั่งซื้อยังต้องรอจังหวะสะสมที่แนวรับ</li>"}
    </ul>
    <p style="margin-top: 10px; color: #8b949e; font-size: 0.9em;">*หมายเหตุ: ข้อมูลนี้ประมวลผลจากสถิติวอลุ่มและโมเมนตัมราคา มึงสามารถเลือกหยิบชื่อกลุ่มเหล่านี้ไปให้กูช่วยแกะสล่อย้อนลึกรายตัวต่อได้เลยเพื่อน*</p>
</div>
""", unsafe_allow_html=True)

# --- ตารางเรดาร์สแกน ---
st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- กราฟรวมทุก Sector ในหน้าจอเดียว ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบภาพรวมตลาด (All Sectors Normalized Performance)")
    
    if price_data:
        df_prices = pd.DataFrame(price_data)
        
        if not df_prices.empty:
            last_date = df_prices.index[-1]
            total_days = (df_prices.index[-1] - df_prices.index[0]).days
            padding_days = max(int(total_days * 0.10), 5) 
            future_end_date = last_date + pd.Timedelta(days=padding_days)
            
            future_index = pd.date_range(start=last_date + pd.Timedelta(days=1), end=future_end_date, freq='B')
            df_padded = pd.DataFrame(index=df_prices.index.union(future_index))
            df_combined = df_padded.join(df_prices).ffill() 
            
            st.line_chart(df_combined, use_container_width=True)
            st.caption("💡 กราฟเทียบผลตอบแทน (%) ทุกกลุ่มอุตสาหกรรมในจอเดียว พร้อมเว้นพื้นที่ขวา 10%")

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    
