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
st.markdown("เรดาร์สแกนกระแสเงินทุนครบเครื่อง: ตารางครบทุกช่วงเวลา + ฟิลเตอร์สรุปตัวแกร่ง + กราฟรวมทุกสินทรัพย์เทียบสเกล % (+/-) เปิดปิดเส้นได้อิสระ")

# --- รวบรวม Sector, Innovation, SET100 ตัวแทน, Gold, Bitcoin ---
radar_assets = {
    "Technology & AI (XLK)": "XLK",
    "Semiconductors / Patent Moat (SMH)": "SMH",
    "Healthcare / Biotech (XLV)": "XLV",
    "Industrials & Smart Grid (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "Consumer Staples (XLP)": "XLP",
    "Energy & Clean Tech (XLE)": "XLE",
    "Advanced Materials (XLB)": "XLB",
    "Utilities (XLU)": "XLU",
    "SET100 Index (SET.BK)": "^SET.BK",
    "Gold / Safe Haven (GC=F)": "GC=F",
    "Bitcoin / Global Liquidity (BTC-USD)": "BTC-USD"
}

@st.cache_data(ttl=3600)
def fetch_and_normalize_radar(assets_dict):
    table_data = []
    normalized_prices = {} 
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
                        # แปลงราคาให้อยู่ในรูป % Change จากจุดเริ่มต้น (Normalized ให้จุดแรกเริ่มที่ 0% หรือเทียบสเกล +/- ได้ทันที)
                        # หรือใช้สูตรเทียบกับราคาปิดวันแรกในช่วงเวลา เพื่อให้เห็นความชันบวก/ลบชัดเจน
                        pct_change_series = ((close_series - close_series.iloc[0]) / close_series.iloc[0]) * 100
                        normalized_prices[name] = pct_change_series
                        
                        # คำนวณความแข็งแกร่งเทียบ SMA20
                        sma20 = close_series.rolling(window=20).mean().iloc[-1]
                        current_price = close_series.iloc[-1]
                        price_score = (current_price - sma20) / sma20 * 100

                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 70:
                        vol_sma20 = vol.rolling(window=20).mean()
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
                        
                        # กรองตัวที่แข็งแกร่ง
                        if v_1w > 0 and price_score > 0 and "Gold" not in name and "Bitcoin" not in name:
                            total_score = v_1w + price_score
                            scored_assets.append({"name": name, "score": total_score})
                            
        except Exception:
            continue
            
    scored_assets = sorted(scored_assets, key=lambda x: x['score'], reverse=True)
    return pd.DataFrame(table_data), normalized_prices, scored_assets

# รันฟังก์ชัน
with st.spinner('กำลังประมวลผลข้อมูลตลาดทั้งหมด...'):
    df_result, price_normalized, strong_picks = fetch_and_normalize_radar(radar_assets)

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

# --- 2. ตารางข้อมูล Volume Change ทุกช่วงเวลา ---
st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- 3. กราฟรวมทุกสินทรัพย์ พร้อมเปิด/ปิดเส้นได้เอง และสเกล % (+/-) ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบทุกสินทรัพย์ร่วมกัน (Normalized % Performance สเกล +/- แกน Y)")
    
    if price_normalized:
        df_norm = pd.DataFrame(price_normalized)
        
        if not df_norm.empty:
            # ให้มึงเลือกเปิด/ปิดเส้นราย Sector / Asset ได้เองตามใจชอบ (ค่าเริ่มต้นเลือกตัวหลักๆ ไว้ให้)
            default_selected = [k for k in radar_assets.keys() if k in df_norm.columns][:5]
            selected_assets_for_chart = st.multiselect(
                "🎛️ ติ๊กเลือก / เอาออก เพื่อเปิด-ปิดเส้นในกราฟ:",
                options=list(df_norm.columns),
                default=default_selected
            )
            
            if selected_assets_for_chart:
                # จัดการเรื่องเว้นพื้นที่ว่างขวา 10%
                last_date = df_norm.index[-1]
                total_days = (df_norm.index[-1] - df_norm.index[0]).days
                padding_days = max(int(total_days * 0.10), 5) 
                future_end_date = last_date + pd.Timedelta(days=padding_days)
                
                future_index = pd.date_range(start=last_date + pd.Timedelta(days=1), end=future_end_date, freq='B')
                df_padded = pd.DataFrame(index=df_norm.index.union(future_index))
                df_combined = df_padded.join(df_norm[selected_assets_for_chart]).ffill() 
                
                # พล้อตกราฟรวมที่แปลงเป็น % Change (แกน Y มี 0 เป็นจุดกึ่งกลาง วิ่งบวกและลบเห็นความชันชัดเจน)
                st.line_chart(df_combined, use_container_width=True)
                st.caption("💡 กราฟแสดงผลตอบแทนสะสม (%) เทียบจากจุดเริ่มต้น โดยมีแกน 0 เป็นเส้นกึ่งกลาง ทำให้เห็นความชัน (Slope) พุ่งขึ้น (+) หรือดิ่งลง (-) ของแต่ละตัวได้ชัดเจน พร้อมเว้นพื้นที่ขวา 10% สำรวจอนาคต")
            else:
                st.info("👈 กรุณาเลือกอย่างน้อย 1 สินทรัพย์จากกล่องด้านบนเพื่อแสดงกราฟ")

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    
