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
    historical_prices = {} 
    
    for name, symbol in assets_dict.items():
        try:
            df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Close' in df.columns:
                    historical_prices[name] = df['Close']

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
        except Exception:
            continue
            
    return pd.DataFrame(table_data), historical_prices

# --- ฟังก์ชันวิเคราะห์เจาะลึก Smart Money Trend แบบไดนามิก (รันใหม่ทุกรอบ) ---
def generate_smart_money_analysis(df_res):
    if df_res.empty:
        return "กำลังดึงข้อมูลเพื่อประมวลผลกระแสเงินทุน..."

    # ดึงค่าเฉลี่ยหรือตัวชี้วัดสำคัญมาประกอบการวิเคราะห์
    tech_row = df_res[df_res['Sector / Asset'].str.contains('Technology')]
    semi_row = df_res[df_res['Sector / Asset'].str.contains('Semiconductors')]
    gold_row = df_res[df_res['Sector / Asset'].str.contains('Gold')]
    crypto_row = df_res[df_res['Sector / Asset'].str.contains('Bitcoin')]
    health_row = df_res[df_res['Sector / Asset'].str.contains('Healthcare')]

    tech_latest = tech_row['Latest (%)'].values[0] if not tech_row.empty else 0.0
    semi_latest = semi_row['Latest (%)'].values[0] if not semi_row.empty else 0.0
    gold_latest = gold_row['Latest (%)'].values[0] if not gold_row.empty else 0.0
    crypto_latest = crypto_row['Latest (%)'].values[0] if not crypto_row.empty else 0.0
    health_latest = health_row['Latest (%)'].values[0] if not health_row.empty else 0.0

    analysis_text = f"""
    <div class="analysis-box">
    <h4>🧠 บทวิเคราะห์เจาะลึกกระแสเงินทุน (Smart Money Flow & Macro Catalyst)</h4>
    <p><b>สภาวะกระแสเงินทุนรอบล่าสุด:</b> ระบบได้ตรวจวัดความผิดปกติและทิศทางของ Volume ข้ามกลุ่มอุตสาหกรรม เพื่อแกะรอยว่ากลุ่มทุนใหญ่กำลังโยกย้ายเงินไปซุ่มเก็บที่ไหน โดยมีประเด็นสำคัญดังนี้:</p>
    <ul>
        <li><b>กลุ่มเทคโนโลยีและนวัตกรรม (Tech / AI / Semiconductors):</b> 
            ค่า Volume ชี้วัดล่าสุดอยู่ที่ Tech ({tech_latest}%) และ Semi ({semi_latest}%). 
            {' 👉 สภาพคล่องกำลังไหลทะลักเข้าสะสมในกลุ่มนวัตกรรมที่มี Patent Moat แกร่ง สะท้อนมุมมองเชิงบวกต่อรอบข่าวสารการออกผลิตภัณฑ์ใหม่และการจดสิทธิบัตรเชิงโครงสร้าง' if tech_latest > 0 or semi_latest > 0 else ' 👉 สภาพคล่องในกลุ่มเทคฯ เริ่มซึมตัวและถูกลดความเสี่ยง (Risk-Off) สถาบันการเงินอาจกำลังรอดูงบการเงินไตรมาสถัดไปหรือรอความชัดเจนจากนโยบายมหภาค'}
        </li>
        <li><b>สินทรัพย์ปลอดภัยและสภาพคล่องทางเลือก (Gold / Bitcoin):</b> 
            Gold ({gold_latest}%), Bitcoin ({crypto_latest}%). 
            {' ⚠️ ตรวจพบแรงซื้อสะสมในสินทรัพย์ป้องกันความเสี่ยง (Safe Haven) ซึ่งอาจบ่งบอกถึงความกังวลระยะสั้นต่อความผันผวนของตลาดทุน หรือการเตรียมรับมือกับตัวเลขเศรษฐกิจมหภาคสำคัญ' if gold_latest > 20 or crypto_latest > 20 else ' ⚖️ กระแสเงินในสินทรัพย์ปลอดภัยยังเคลื่อนไหวในกรอบปกติ ไม่มีสัญญาณ Panic ดึงเม็ดเงินออกจากตลาดหุ้น'}
        </li>
        <li><b>กลุ่มนวัตกรรมชีวภาพและการแพทย์ (Healthcare / Biotech):</b> 
            ค่า Volume อยู่ที่ {health_latest}%. กลุ่มนี้มักเป็นหลุมหลบภัยชั้นดีเมื่อตลาดผันผวน เนื่องจากมูลค่ากิจการถูกขับเคลื่อนด้วยสิทธิบัตรยาและอุปกรณ์การแพทย์ผูกขาด (High Barrier to Entry)</li>
    </ul>
    <h4>💡 คำแนะนำเชิงกลยุทธ์การเล่นรอบ (Action Plan):</h4>
    <ul>
        <li><b>เกมหุ้นรายตัวตาม Catalyst:</b> โฟกัสบริษัทที่มีงบการเงินแข็งแกร่ง (Free Cash Flow เป็นบวก, หนี้ต่ำ) และมีสตอรี่การจดสิทธิบัตรนวัตกรรมใหม่ที่จะบล็อกคู่แข่งในอีก 1-3 ปีข้างหน้า</li>
        <li><b>จังหวะเข้าทำ:</b> อย่าเพิ่งไล่ราคาในวันที่วอลุ่มพุ่งรุนแรงอย่างไร้เหตุผล ให้ใช้ตารางนี้ส่องดูจังหวะที่ Smart Money ย่อตัวสะสม แล้วทยอยเก็บตามแนวรับสำคัญ</li>
    </ul>
    </div>
    """
    return analysis_text

# รันฟังก์ชันดึงข้อมูล
with st.spinner('กำลังเชื่อมต่อฐานข้อมูลตลาดและประมวลผลกระแสเงินทุน...'):
    df_result, price_data = fetch_multi_period_volume_flow(radar_assets)

st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (เทียบกับค่าเฉลี่ยปกติ)")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- แสดงบทวิเคราะห์ Smart Money รันใหม่ทุกรอบ ---
    st.markdown("---")
    st.markdown(generate_smart_money_analysis(df_result), unsafe_allow_html=True)

    # --- ส่วนพล็อตเส้นกราฟราคา พร้อมเว้นที่ว่างขวา 10% ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเส้นแนวโน้มราคา (Trend Line & Future Padding View)")
    
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
            
            selected_chart_asset = st.selectbox("เลือก Sector หรือสินทรัพย์เพื่อดูเส้นแนวโน้ม:", list(price_data.keys()))
            
            if selected_chart_asset in df_combined.columns:
                st.line_chart(df_combined[selected_chart_asset], use_container_width=True)
                st.caption(f"💡 กราฟแสดงราคาของ {selected_chart_asset} ย้อนหลัง พร้อมเว้นพื้นที่ว่างทางขวา 10% สำหรับการคาดการณ์และประเมินทิศทาง Smart Money")

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
