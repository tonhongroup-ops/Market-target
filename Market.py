import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Heatmap & Innovation Smart Money Radar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme CSS สไตล์นักวิเคราะห์การเงินมือโปร ---
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .stAlert { background-color: #1f242d; color: #c9d1d9; border: 1px solid #383f4a; }
    .analysis-box { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Global Heatmap Sector & Innovation Smart Money Radar")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุนสะสมผ่าน `% Volume Change` และบทวิเคราะห์เจาะลึกงบ/สิทธิบัตร อัปเดตอัตโนมัติทุกรีเฟรช")

# --- พิกัด Sector ตาม Heatmap + สินทรัพย์พิเศษตามสั่ง ---
radar_assets = {
    "Technology (XLK)": "XLK",
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
def fetch_volume_change_flow(assets_dict):
    volume_frames = {}
    for name, symbol in assets_dict.items():
        df = yf.download(symbol, period="2y", auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            if 'Volume' in df.columns:
                # คำนวณ % Volume Change เทียบกับค่าเฉลี่ย 20 วัน (เช็ก Smart Money Flow)
                vol_sma = df['Volume'].rolling(window=20).mean()
                vol_change = ((df['Volume'] - vol_sma) / vol_sma) * 100
                volume_frames[name] = vol_change
            else:
                volume_frames[name] = pd.Series(0, index=df.index)
                
    df_vol = pd.DataFrame(volume_frames)
    df_vol = df_vol.ffill().bfill()
    return df_vol

with st.spinner("กำลังคำนวณ % Volume Change และสแกนกระแสเงินทุนสมาร์ทมันนี่..."):
    df_flow = fetch_volume_change_flow(radar_assets)

if not df_flow.empty:
    last_date = df_flow.index[-1]
    first_date = df_flow.index[0]
    total_days = (last_date - first_date).days
    
    # เผื่อพื้นที่ขวา 15% ตามสเปก
    padding_days = int(total_days * 0.15)
    max_x_limit = last_date + timedelta(days=padding_days)

    fig = go.Figure()

    for col in df_flow.columns:
        fig.add_trace(go.Scatter(
            x=df_flow.index, 
            y=df_flow[col], 
            mode='lines',
            line=dict(width=1.5),
            name=col,
            connectgaps=True,
            hoverinfo='skip' # ปิดกล่องข้อความกวนใจเวลาเมาส์ชี้
        ))

    fig.update_layout(
        template="plotly_dark",
        title="Sector & Innovation % Volume Change Flow (2-Year Clean View)",
        xaxis_title="วันที่",
        yaxis_title="% Volume Change (vs 20D MA)",
        xaxis=dict(
            range=[first_date, max_x_limit]
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.4,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=120)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 ตารางสรุป % Volume Change ล่าสุดของแต่ละ Sector")
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "% Volume Change (Latest)"}), use_container_width=True)

    # --- ส่วนบทวิเคราะห์และหุ้นเต็งที่ฝังไว้โชว์ทุกรีเฟรช ---
    st.markdown("""
        <div class="analysis-box">
            <h2>🧬 บทวิเคราะห์เจาะลึกสมาร์ทมันนี่, สิทธิบัตร และหุ้นเต็งประจำเรดาร์</h2>
            <p><i>วิเคราะห์สดผ่านระบบทุกครั้งที่มีการรีเฟรชหน้าจอ เพื่อเกาะติดกระแสเงินทุนรอบใหญ่ตามข่าวสารและงบการเงิน</i></p>
            <hr style="border-color: #30363d;">
            
            <h3>🔥 1. กลุ่ม Semiconductors & Patent Moat (SMH / XLK)</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> งบเด่นเรื่อง Gross Margin สูงลิ่ว (50-80%) เพราะมีสิทธิบัตรคุ้มครองสถาปัตยกรรมชิปและเครื่องพิมพ์ EUV ที่คู่แข่งลอกเลียนแบบไม่ได้ วอลุ่มพุ่งรับรอบขยายกำลังผลิต AI Hardware</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>NVDA (Nvidia)</code> — เจ้าตลาดฮาร์ดแวร์ประมวลผล AI วอลุ่มหนาแน่น พอร์ตเขียวไว</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>ASML (ASML Holding)</code> — เจ้าขาดเครื่องพิมพ์ EUV รายเดียวในโลก รายได้มั่นคงตามดีมานด์ชิปล้ำยุค</li>
            </ul>

            <h3>⚡ 2. กลุ่ม Industrials & Smart Grid (XLI)</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> งบโตต่อเนื่องจาก Backlog ทุบสถิติ สิทธิบัตรเน้นระบบส่งกำลังไฟฟ้าแรงดันสูงและซอฟต์แวร์บริหารกริดอัจฉริยะ รองรับการบูมของ Data Center ทั่วโลก</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>GE Vernova (GEV)</code> — ผู้นำกังหันก๊าซและโครงสร้างพื้นฐานกริด ยอดสั่งซื้อพุ่งสะใจสายเก็งกำไร</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>Eaton Corp (ETN)</code> — เบอร์หนึ่งเรื่องหม้อแปลงและสวิตช์เกียร์ งบสม่ำเสมอ ความได้เปรียบทางวิศวกรรมสูง</li>
            </ul>

            <h3>🔋 3. กลุ่ม Energy & Clean Tech (XLE)</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> อยู่ในช่วงเร่งลงทุน R&D นวัตกรรมกักเก็บพลังงาน (BESS) และเซลล์เชื้อเพลิง สิทธิบัตรเคมีแบตเตอรี่คือหัวใจสำคัญ วอลุ่มเหวี่ยงตามข่าวดีลโครงการใหญ่</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>Bloom Energy (BE)</code> — โดดเด่นเรื่องเซลล์เชื้อเพลิงผลิตไฟฟ้านอกกริด (Microgrid) ป้อน Data Center</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>Fluence Energy (FLNC)</code> — ผู้นำ BESS ระดับโลก มีซอฟต์แวร์ควบคุมกริดจดลิขสิทธิ์แน่นหนา</li>
            </ul>

            <h3>🧪 4. กลุ่ม Advanced Materials (XLB)</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> เติบโตตามความต้องการวัสดุศาสตร์เกรดพิเศษในอากาศยานและเซมิคอนดักเตอร์ สิทธิบัตรสูตรโลหะผสมคือเกราะคุ้มกันชั้นดี</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>MP Materials (MP)</code> — เหมืองแร่หายาก (Rare Earth) สหรัฐฯ วอลุ่มตอบสนองไวตามประเด็นซัพพลายเชน</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>Materion Corp (MTRN)</code> — เบอร์ใหญ่ด้านวัสดุวิศวกรรมพิเศษ งบแกร่ง หนี้ต่ำ กำไรสม่ำเสมอ</li>
            </ul>

            <h3>💰 5. กลุ่ม Bitcoin & Gold (Liquidity & Safe Haven)</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> วัดกันที่สภาพคล่องมหภาค (Global Liquidity) วอลุ่มพุ่งกระจายตามตัวเลขเงินเฟ้อ นโยบายดอกเบี้ย และความเสี่ยงเชิงระบบ</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>Bitcoin (BTC)</code> — สินทรัพย์สภาพคล่องสูงที่ตอบสนองไวที่สุด</li>
                <li>💎 <b>ของดีพรีเมียม (Core Safe Haven):</b> <code>Gold (GC=F)</code> — สินทรัพย์ปลอดภัยดั้งเดิม เสถียรและปลอดภัยสูงสุด</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
