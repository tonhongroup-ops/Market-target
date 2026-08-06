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
    .top3-box { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #f0883e; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors, Macro Liquidity & Innovation Flow** บทวิเคราะห์สิทธิบัตรและเกมการเงินจากเพื่อนคู่คิดของคุณ")

# --- Sidebar สำหรับปรับแต่ง Timeframe ---
st.sidebar.markdown("### ⚙️ ตั้งค่าเรดาร์ (Radar Settings)")
timeframe_option = st.sidebar.selectbox(
    "เลือกช่วงเวลาของกราฟ (Timeframe):",
    options=["1mo", "3mo", "6mo", "1y"],
    index=2, # ค่าเริ่มต้นที่ 6 เดือน
    format_func=lambda x: {"1mo": "1 เดือน", "3mo": "3 เดือน", "6mo": "6 เดือน", "1y": "1 ปี"}[x]
)

# --- รวบรวม Sector นวัตกรรม และสินทรัพย์สะท้อนสภาพคล่องครบถ้วน ---
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
def fetch_multi_period_volume_flow(assets_dict, period_str):
    table_data = []
    chart_raw_data = {}
    
    for name, symbol in assets_dict.items():
        try:
            df = yf.download(symbol, period=period_str, auto_adjust=True, progress=False)
            if df is not None and not df.empty:
                # แก้ปัญหา MultiIndex ของ yfinance ให้ปลอดภัย
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 25:
                        vol_sma20 = vol.rolling(window=20).mean()
                        vol_sma40 = vol.rolling(window=40).mean() if len(vol) >= 40 else vol_sma20
                        vol_sma60 = vol.rolling(window=60).mean() if len(vol) >= 60 else vol_sma20
                        
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
                        
                        if 'Close' in df.columns:
                            close_series = df['Close'].squeeze()
                            if isinstance(close_series, pd.DataFrame):
                                close_series = close_series.iloc[:, 0]
                            normalized = (close_series / close_series.iloc[0]) * 100
                            chart_raw_data[name] = normalized
        except Exception as e:
            continue
            
    return pd.DataFrame(table_data), pd.DataFrame(chart_raw_data)

with st.spinner(f'กำลังดึงข้อมูลตลาดและประมวลผลเรดาร์ (Timeframe: {timeframe_option})...'):
    df_result, df_chart = fetch_multi_period_volume_flow(radar_assets, timeframe_option)

st.markdown(f"### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา (Timeframe: {timeframe_option})")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- กราฟรวมทุก Sector พร้อมกัน (จัดเลย์เอาต์เว้นขวา 10%) ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบทิศทางราคา 'ทุก Sector & Macro Assets พร้อมกัน' (Normalized Growth Comparison)")
    st.markdown("💡 *กราฟนี้ปรับฐานราคาเริ่มต้นที่ 100 เพื่อให้เห็นการเคลื่อนตัวของทองคำ Bitcoin และทุก Sector พร้อมกันอย่างชัดเจน*")
    
    if not df_chart.empty:
        chart_col, spacer_col = st.columns([9, 1])
        with chart_col:
            st.line_chart(df_chart, use_container_width=True, height=500)
        with spacer_col:
            st.markdown("")
    
    # --- ส่วนวิเคราะห์เชิงลึกสไตล์เซียนหุ้นนวัตกรรม & Macro Liquidity ---
    st.markdown("---")
    st.markdown("### 🧠 วิเคราะห์สภาพตลาดเชิงลึก: Macro Flow, Patent Moat & Playbook หุ้นเล่นรอบ")
    
    st.markdown("""
    <div class="analysis-box">
    <h4>🔥 ถอดรหัสสภาพตลาด & เซกเตอร์ที่น่าสนใจในรอบนี้:</h4>
    <p>จากข้อมูลตารางและสภาพกระแสเงินทุนรอบนี้ เราแบ่งการวิเคราะห์ออกเป็น 3 แกนหลักเพื่อให้เห็นภาพการเล่นรอบที่คมชัดที่สุดเพื่อน:</p>
    
    <div class="stock-pick-box">
        <b>1. แกนมหภาค & สภาพคล่อง (Macro & Safe Haven Signal):</b><br>
        <i>นัยสำคัญจากทองคำ (Gold) และ Bitcoin:</i> การที่วอลุ่มทองคำพุ่งทะยานรุนแรง (Volume Spike) สะท้อนชัดเจนว่ากองทุนใหญ่และธนาคารกลางกำลังตั้งรับความเสี่ยงภูมิรัฐศาสตร์ (Geopolitical Risk) ขณะที่บิตคอยน์ทำหน้าที่เป็นตัววัดสภาพคล่องส่วนเกิน ถ้าย่อตัวลงแปลว่าสมาร์ตมันนี่เลือกตั้งรับความปลอดภัยชั่วคราว<br>
    </div>

    <div class="stock-pick-box-secondary">
        <b>2. เซกเตอร์นวัตกรรมที่น่าสนใจที่สุด (Top Sectors to Watch):</b><br>
        <ul>
            <li><b>Semiconductors & Patent Moat (SMH / XLK):</b> แม้บางช่วงวอลุ่มจะชะลอตัวเพื่อสร้างฐาน (Base Building) แต่เชิงโครงสร้างระยะยาว นี่คือเซกเตอร์ที่มีสิทธิบัตรผูกขาดทางเทคโนโลยีแกร่งที่สุดในโลก (เช่น สถาปัตยกรรมชิป AI ของ NVDA และการผลิตระดับพรีเมียมของ TSM) เหมาะกับการรอจังหวะสะสมเมื่อราคาย่อตัว</li>
            <li><b>Clean Energy & Smart Grid (XLE / XLI):</b> ได้อานิสงส์จากดีล Data Center ที่ต้องการพลังงานสะอาดป้อนระบบ 24/7 หุ้นอย่าง <b>FLNC</b> (ระบบกักเก็บพลังงาน) ที่มี Backlog ล้นมือ ถือเป็นหุ้น Turnaround ที่น่าจับตาการเล่นรอบ</li>
        </ul>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # --- ส่วนสรุปหุ้นเด่น 3 ตัวที่กำลังเกาะเทรนด์ (ตามรีเควส) ---
    st.markdown("---")
    st.markdown("### 🎯 สรุปหุ้นเด่น 3 ตัวเกาะเทรนด์นวัตกรรม & สิทธิบัตร (Top 3 Trend-Following Stocks)")
    st.markdown("💡 *สรุปสั้นกระชับสำหรับนำไปส่งต่อและวางแผนเล่นรอบตามกระแสสมาร์ตมันนี่*")

    st.markdown("""
    <div class="top3-box">
        <b>1. Broadcom Inc. (NASDAQ: AVGO) — เจ้าพ่อ Custom AI Silicon & High-Speed Networking</b><br>
        * <b>เทรนด์และสิทธิบัตร:</b> ผูกขาดสิทธิบัตรระบบเครือข่ายความเร็วสูง (Networking) และการออกแบบชิป AI เฉพาะกิจ (Custom ASIC) ให้กับคลาวด์ยักษ์ใหญ่<br>
        * <b>มุมมองการเล่นรอบ:</b> งบการเงินแข็งแกร่ง กระแสเงินสดอิสระสูง เหมาะกับการรอจังหวะย่อตัวเข้าสะสมที่แนวรับหลักเมื่อวอลุ่มฝั่งขายแห้ง
    </div>

    <div class="top3-box" style="border-left-color: #335dff;">
        <b>2. Arista Networks, Inc. (NASDAQ: ANET) — กระดูกสันหลัง AI Data Center Fabric</b><br>
        * <b>เทรนด์และสิทธิบัตร:</b> เจ้าของสิทธิบัตรซอฟต์แวร์จัดการโครงข่าย Low Latency (CloudVision & EOS) ที่จำเป็นต้องใช้ในการเชื่อมโยงคลัสเตอร์ AI ขนาดมหึมา<br>
        * <b>มุมมองการเล่นรอบ:</b> งบเติบโตต่อเนื่อง ไร้หนี้กวนใจ ทรงกราฟแข็งแกร่งกว่าตลาด เหมาะกับกลยุทธ์เล่นรอบแบบ Breakout ตามกรอบสะสม
    </div>

    <div class="top3-box" style="border-left-color: #f0883e;">
        <b>3. Vertiv Holdings Co. (NYSE: VRT) — ผู้นำระบบระบายความร้อน AI Data Center (Liquid Cooling)</b><br>
        * <b>เทรนด์และสิทธิบัตร:</b> ถือสิทธิบัตรระบบบริหารจัดการความร้อนและพลังงานแรงดันสูงสำหรับตู้แร็คเซิร์ฟเวอร์ AI ยุคใหม่ ซึ่งเป็นคอขวดสำคัญของอุตสาหกรรม<br>
        * <b>มุมมองการเล่นรอบ:</b> แบ็กล็อกงานในมือล้นทะลัก รับอานิสงส์การสร้างดาต้าเซ็นเตอร์ทั่วโลก เล่นรอบตามจังหวะรีบาวด์จากโซนแนวรับสำคัญ
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ กำลังเชื่อมต่อข้อมูลตลาด ลองกดรีเฟรชหน้าจออีกครั้งเพื่อน!")
    
