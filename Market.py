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
st.markdown("เรดาร์ตรวจจับกระแสเงินทุนครบเครื่อง ทั้งตารางข้อมูลย้อนหลังทุกช่วงเวลา กล่องฟิลเตอร์สรุปตัวแกร่ง และกราฟเลือกดูรายตัวแบบเว้นพื้นที่ขวา 10%")

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
def fetch_complete_radar_data(assets_dict):
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
                        historical_prices[name] = close_series
                        
                        # คำนวณความแข็งแกร่งเทียบ SMA20
                        sma20 = close_series.rolling(window=20).mean().iloc[-1]
                        current_price = close_series.iloc[-1]
                        price_score = (current_price - sma20) / sma20 * 100

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
                        
                        # กรองตัวที่แข็งแกร่ง (Volume สัปดาห์นี้เป็นบวก + ราคาอยู่เหนือเส้นค่าเฉลี่ย)
                        if v_1w > 0 and price_score > 0:
                            total_score = v_1w + price_score
                            scored_assets.append({"name": name, "score": total_score})
                            
        except Exception:
            continue
            
    scored_assets = sorted(scored_assets, key=lambda x: x['score'], reverse=True)
    return pd.DataFrame(table_data), historical_prices, scored_assets

# รันฟังก์ชันดึงข้อมูล
with st.spinner('กำลังเชื่อมต่อข้อมูลตลาดและประมวลผลเรดาร์...'):
    df_result, price_data, strong_picks = fetch_complete_radar_data(radar_assets)

# --- 1. กล่องสรุปผลคัดกรองตัวที่แข็งแกร่งที่สุดอัตโนมัติ ---
st.markdown("### 🎯 ตัวที่น่าสนใจและแข็งแกร่งที่สุดในรอบนี้ (Filtered Strong Picks)")
st.markdown(f"""
<div class="pick-box">
    <h4>🔥 ผลการคัดกรองตามเงื่อนไข Smart Money Filter:</h4>
    <ul>
        {''.join([f"<li>🏆 <b>{item['name']}</b> (คะแนนความแกร่ง: <code>{item['score']:.2f}</code>) — ผ่านเกณฑ์ Volume ขยายตัวและยืนเหนือเส้นค่าเฉลี่ยอย่างมั่นคง</li>" for item in strong_picks]) if strong_picks else "<li>⚠️ ไม่มีตัวไหนผ่านเกณฑ์ความแข็งแกร่งขั้นสุดในรอบนี้ ตลาดอยู่ในโหมดพักตัว</li>"}
    </ul>
</div>
""", unsafe_allow_html=True)

# --- 2. ตารางข้อมูล Volume Change ทุกช่วงเวลาแบบจัดเต็ม ---
st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (เทียบกับค่าเฉลี่ยปกติ)")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- 3. กราฟเลือกดูรายตัว พร้อมเว้นพื้นที่ขวา 10% ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเส้นแนวโน้มราคา (Trend Line & Future Padding View)")
    
    if price_data:
        selected_chart_asset = st.selectbox("เลือก Sector หรือสินทรัพย์เพื่อดูเส้นแนวโน้ม:", list(price_data.keys()))
        
        if selected_chart_asset in price_data:
            target_series = price_data[selected_chart_asset].dropna()
            
            if not target_series.empty:
                last_date = target_series.index[-1]
                total_days = (target_series.index[-1] - target_series.index[0]).days
                padding_days = max(int(total_days * 0.10), 5) 
                future_end_date = last_date + pd.Timedelta(days=padding_days)
                
                future_index = pd.date_range(start=last_date + pd.Timedelta(days=1), end=future_end_date, freq='B')
                df_padded = pd.DataFrame(index=target_series.index.union(future_index))
                df_padded[selected_chart_asset] = target_series
                df_combined = df_padded.ffill()
                
                st.line_chart(df_combined[selected_chart_asset], use_container_width=True)
                st.caption(f"💡 กราฟแสดงราคาของ {selected_chart_asset} ย้อนหลัง พร้อมเว้นพื้นที่ว่างทางขวา 10% สำหรับประเมินทิศทาง Smart Money")

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    ไ
