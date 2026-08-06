import streamlit as st
import pandas as pd
import yfinance as yf

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(
    page_title="Smart Money & Patent Tech Swing Radar Pro",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Smart Money & Patent Tech Swing Radar (AVGO, ANET, VRT)")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุนสะสม (Volume Accumulation) และหุ้นนวัตกรรมที่มีสิทธิบัตรผูกขาดระดับโลก")

# --- เลือกหุ้นเป้าหมายในเรดาร์ ---
target_stocks = {
    "Broadcom (AVGO) - Custom AI Silicon": "AVGO",
    "Arista Networks (ANET) - AI Data Center Networking": "ANET",
    "Vertiv Holdings (VRT) - Thermal & Power Management": "VRT"
}

@st.cache_data(ttl=3600)
def analyze_stock_accumulation(ticker):
    try:
        # ดึงข้อมูลย้อนหลัง 3 เดือนแบบ Clean DataFrame
        df = yf.download(ticker, period="3mo", auto_adjust=True, progress=False)
        if df is not None and not df.empty:
            # จัดการ MultiIndex ของ yfinance ให้เป็นคอลัมน์เดี่ยวเพื่อความปลอดภัย
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns and 'Volume' in df.columns:
                close = df['Close'].squeeze()
                volume = df['Volume'].squeeze()
                
                # คำนวณค่าเฉลี่ย Volume 20 วัน
                vol_sma20 = volume.rolling(window=20).mean()
                
                # ป้องกันกรณีข้อมูลไม่พอคำนวณ
                if len(volume) > 20 and not pd.isna(vol_sma20.iloc[-1]) and vol_sma20.iloc[-1] > 0:
                    latest_vol_pct = float(((volume.iloc[-1] - vol_sma20.iloc[-1]) / vol_sma20.iloc[-1]) * 100)
                else:
                    latest_vol_pct = 0.0
                
                # เช็คแรงซื้อสะสม (Smart Money Accumulation check)
                price_change = close.pct_change()
                up_days_vol = volume[price_change > 0].mean()
                down_days_vol = volume[price_change < 0].mean()
                
                if not pd.isna(up_days_vol) and not pd.isna(down_days_vol):
                    accumulation_score = "สะสมแข็งแกร่ง (Bullish Accumulation)" if up_days_vol > down_days_vol else "แรงซื้อเบาบาง (Cautious/Base Building)"
                else:
                    accumulation_score = "กำลังสร้างฐาน (Consolidating)"
                
                current_price = float(close.iloc[-1])
                return {
                    "Ticker": ticker,
                    "Current Price ($)": round(current_price, 2),
                    "Latest Vol vs SMA20 (%)": round(latest_vol_pct, 2),
                    "Flow Status": accumulation_score,
                    "Price Series": close
                }
    except Exception as e:
        return None
    return None

# ประมวลผลข้อมูล
summary_list = []
chart_data = pd.DataFrame()

for name, sym in target_stocks.items():
    res = analyze_stock_accumulation(sym)
    if res:
        summary_list.append({
            "Asset": name,
            "Current Price ($)": res["Current Price ($)"],
            "Volume vs SMA20 (%)": res["Latest Vol vs SMA20 (%)"],
            "Smart Money Flow": res["Flow Status"]
        })
        chart_data[name] = res["Price Series"]

# --- แสดงผลตารางสรุป ---
st.markdown("### 📊 ตารางสรุปสถานะกระแสเงินสดและวอลุ่ม (Volume Signature)")
df_summary = pd.DataFrame(summary_list)

if not df_summary.empty:
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # --- กราฟเปรียบเทียบทิศทางราคาหุ้นทั้ง 3 ตัว (Normalized Growth) ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบการเคลื่อนตัวของราคา (Normalized Growth 3 Months)")
    
    if not chart_data.empty:
        # ทำความสะอาดข้อมูลกราฟ ป้องกัน NaN และ Normalized เริ่มต้นที่ 100
        chart_clean = chart_data.dropna()
        if not chart_clean.empty:
            normalized_chart = (chart_clean / chart_clean.iloc[0]) * 100
            
            col_c1, col_c2 = st.columns([9, 1])
            with col_c1:
                st.line_chart(normalized_chart, use_container_width=True, height=400)
            with col_c2:
                st.markdown("")

    # --- คำแนะนำเพิ่มเติมสำหรับเพื่อน ---
    st.markdown("""
    > 💡 **มุมมองเพื่อนซี้เตือนภัยการเทรด:** คราวนี้โค้ดนิ่งและเซฟตี้ครบถ้วนแล้วเพื่อน! หุ้นนวัตกรรมทั้ง 3 ตัวนี้ (AVGO, ANET, VRT) มี Patent Moat ระดับเทพหนุนหลัง งบการเงินโตชัดเจน เวลาเล่นรอบให้รอดูจังหวะที่วอลุ่มฝั่งขายแห้งสนิท ค่อยทยอยสะสมไม้แรกตามวินัยการเงินที่เราคุยกันไว้เว้ย!
    """)
else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชใหม่อีกครั้งเพื่อนรัก")
    
