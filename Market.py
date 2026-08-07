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
    .pick-box { background-color: #162330; padding: 20px; border-radius: 10px; border: 1px solid #1f6feb; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์สแกนหาหุ้น/สินทรัพย์ตัวที่แข็งแกร่งและน่าสนใจที่สุดในรอบนี้แบบอัตโนมัติ")

# --- ข้อมูล Sector และตัวแทนสินทรัพย์หลัก (หรือจะใส่หุ้นรายตัวในกลุ่มนวัตกรรม/สิทธิบัตรก็ได้) ---
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
def fetch_and_filter_strong_picks(assets_dict):
    table_data = []
    historical_prices = {} 
    scored_assets = []
    
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
                        
                        # คำนวณความแข็งแกร่งของราคา (Price Momentum Score)
                        sma20 = close_series.rolling(window=20).mean().iloc[-1]
                        current_price = close_series.iloc[-1]
                        price_score = (current_price - sma20) / sma20 * 100

                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 70:
                        vol_sma20 = vol.rolling(window=20).mean()
                        v_latest = float(((vol.iloc[-1] - vol_sma20.iloc[-1]) / vol_sma20.iloc[-1]) * 100)
                        v_1w = float(((vol.iloc[-5:].mean() - vol_sma20.iloc[-5:].mean()) / vol_sma20.iloc[-5:].mean()) * 100)
                        
                        table_data.append({
                            "Sector / Asset": name,
                            "Latest (%)": round(v_latest, 2),
                            "1 Week (%)": round(v_1w, 2),
                            "Price vs SMA20 (%)": round(price_score, 2)
                        })
                        
                        # ใช้เงื่อนไข if-else คัดกรองตัวที่เข้าเกณฑ์ "แข็งแกร่งและน่าสนใจ" (Volume หนุน + ราคาอยู่เหนือค่าเฉลี่ย)
                        if v_1w > 0 and price_score > 0:
                            # คำนวณคะแนนความฟิตรวม (Score = Vol Growth + Price Momentum)
                            total_score = v_1w + price_score
                            scored_assets.append({"name": name, "score": total_score})
                            
        except Exception:
            continue
            
    # เรียงลำดับจากตัวที่คะแนนความแข็งแกร่งสูงสุดลงมา
    scored_assets = sorted(scored_assets, key=lambda x: x['score'], reverse=True)
    return pd.DataFrame(table_data), historical_prices, scored_assets

# รันฟังก์ชัน
with st.spinner('กำลังประมวลผลและคัดกรองตัวที่แข็งแกร่งที่สุด...'):
    df_result, price_data, strong_picks = fetch_and_filter_strong_picks(radar_assets)

# --- กล่องแสดงผลตัวที่น่าสนใจและแข็งแกร่งที่สุด (Filtered Top Picks) ---
st.markdown("### 🎯 ตัวที่น่าสนใจและแข็งแกร่งที่สุดในรอบนี้ (Filtered Strong Picks)")
st.markdown(f"""
<div class="pick-box">
    <h4>🔥 ผลการคัดกรองตามเงื่อนไขความแข็งแกร่ง (Smart Money Filter):</h4>
    <ul>
        {''.join([f"<li>🏆 <b>{item['name']}</b> (คะแนนความแกร่ง: <code>{item['score']:.2f}</code>) — ผ่านเกณฑ์ Volume ขยายตัวและยืนเหนือเส้นค่าเฉลี่ยอย่างมั่นคง เป็นเป้าหมายที่ Smart Money กำลังสะสม</li>" for item in strong_picks]) if strong_picks else "<li>⚠️ ไม่มีตัวไหนผ่านเกณฑ์ความแข็งแกร่งขั้นสุดในรอบนี้ ตลาดอยู่ในโหมดพักตัว</li>"}
    </ul>
</div>
""", unsafe_allow_html=True)

# --- ตารางเรดาร์สแกน ---
st.markdown("### 📊 ตารางแสดงค่าสถิติวอลุ่มและราคา")
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
    
