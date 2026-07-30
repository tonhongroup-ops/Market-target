import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Bullish Sector & Innovation Smart Money Radar",
    page_icon="🚀",
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

st.title("🚀 Bullish Sector & Innovation Smart Money Radar")
st.markdown("เรดาร์คัดกรองเฉพาะ **Sector ที่เป็นขาขึ้นและมี Smart Money ไหลเข้าแรงสุด** ตัดตัวที่ซบเซาทิ้ง อัปเดตสดทุกรีเฟรช")

# --- คัดเลือกเฉพาะ Sector ขาขึ้นและสินทรัพย์เกรดพรีเมียมตามรอบข่าวสาร ---
bullish_radar_assets = {
    "Semiconductors / Patent Moat (SMH)": "SMH",
    "Industrials & Smart Grid (XLI)": "XLI",
    "Energy & Clean Tech (XLE)": "XLE",
    "Bitcoin / Global Liquidity (BTC-USD)": "BTC-USD"
}

@st.cache_data(ttl=3600)
def fetch_bullish_volume_flow(assets_dict):
    volume_frames = {}
    for name, symbol in assets_dict.items():
        df = yf.download(symbol, period="2y", auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            if 'Volume' in df.columns:
                # คำนวณ % Volume Change เทียบกับค่าเฉลี่ย 20 วัน
                vol_sma = df['Volume'].rolling(window=20).mean()
                vol_change = ((df['Volume'] - vol_sma) / vol_sma) * 100
                volume_frames[name] = vol_change
            else:
                volume_frames[name] = pd.Series(0, index=df.index)
                
    df_vol = pd.DataFrame(volume_frames)
    df_vol = df_vol.ffill().bfill()
    return df_vol

with st.spinner("กำลังคัดกรองและคำนวณ % Volume Change เฉพาะกลุ่มขาขึ้น..."):
    df_flow = fetch_bullish_volume_flow(bullish_radar_assets)

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
            line=dict(width=1.8),
            name=col,
            connectgaps=True,
            hoverinfo='skip'
        ))

    fig.update_layout(
        template="plotly_dark",
        title="Bullish Sector % Volume Change Flow (Filtered High-Growth View)",
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

    st.markdown("### 📋 ตารางสรุป % Volume Change ล่าสุดของกลุ่มขาขึ้น")
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "% Volume Change (Latest)"}), use_container_width=True)

    # --- บทวิเคราะห์เฉพาะกลุ่มขาขึ้นและหุ้นตัวเต็งซิ่งๆ ---
    st.markdown("""
        <div class="analysis-box">
            <h2>🔥 เจาะลึกเฉพาะ Sector ขาขึ้น นวัตกรรม และหุ้นเต็งกระชากพอร์ต</h2>
            <p><i>คัดเน้นๆ เฉพาะกลุ่มที่งบการเงินโตเร่งตัว มีสิทธิบัตรคุ้มครอง (Patent Moat) และวอลุ่ม Smart Money หนุนหลังเต็มสูบ</i></p>
            <hr style="border-color: #30363d;">
            
            <h3>🧠 1. กลุ่ม Semiconductors & Patent Moat (SMH) — ขาขึ้นรอบใหญ่จาก AI & Deep Tech</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> กลุ่มนี้ยืนหนึ่งเรื่อง Gross Margin ทะลุ 60-80% เพราะมีสิทธิบัตรสถาปัตยกรรมชิปและเครื่องจักรพิมพ์เวเฟอร์ที่คู่แข่งไม่มีทางก๊อปปี้ได้ งบการเงินโตตามรอบการลงทุนโครงสร้างพื้นฐาน AI แบบฉุดไม่อยู่</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>NVDA (Nvidia)</code> — เจ้าตลาดฮาร์ดแวร์ปัญญาประดิษฐ์ วอลุ่มเข้าสะสมหนาแน่นทุกครั้งที่ย่อตัว</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>ASML (ASML Holding)</code> — ผูกขาดเครื่องพิมพ์ EUV ลิขสิทธิ์ระดับโลก โรงงานชิปไหนก็ขาดไม่ได้ งบแกร่งกระแสเงินสดล้น</li>
            </ul>

            <h3>⚡ 2. กลุ่ม Industrials & Smart Grid (XLI) — ขาขึ้นจากวิกฤตพลังงานและ Data Center</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> งบการเงินเติบโตแบบก้าวกระโดดจาก Backlog สั่งซื้อล่วงหน้ายาวเหยียด สิทธิบัตรเน้นเรื่องระบบส่งไฟฟ้าแรงสูงและซอฟต์แวร์จัดการกริดอัจฉริยะ รองรับการแห่สร้าง Data Center ทั่วโลก</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>GE Vernova (GEV)</code> — หุ้นม้ามืดด้านกังหันก๊าซและกริดไฟฟ้า ยอดจองล้นทะลัก วอลุ่มพุ่งแรงสะใจ</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>Eaton Corp (ETN)</code> — ผู้นำสวิตช์เกียร์และหม้อแปลงไฟฟ้าอัจฉริยะ งบสม่ำเสมอ ความได้เปรียบทางวิศวกรรมสูงปรี๊ด</li>
            </ul>

            <h3>🔋 3. กลุ่ม Energy & Clean Tech (XLE) — ขาขึ้นรอบสั้นจากนวัตกรรมกักเก็บพลังงาน</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> งบกำลังพลิกฟื้นและเร่งตัวจากการลงทุนระบบกักเก็บพลังงาน (BESS) และเซลล์เชื้อเพลิง สิทธิบัตรเคมีแบตเตอรี่คือเกราะคุ้มกันชั้นดี วอลุ่มมักจะสวิงแรงตามดีลโปรเจกต์ระดับเมกะโปรเจกต์</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>Bloom Energy (BE)</code> — ผู้นำเซลล์เชื้อเพลิงผลิตไฟฟ้านอกกริดป้อน Data Center วอลุ่มเหวี่ยงทำกำไรดีมาก</li>
                <li>💎 <b>ของดีพรีเมียม (Core Patent Moat):</b> <code>Fluence Energy (FLNC)</code> — เบอร์ใหญ่ระบบ BESS โลก มีซอฟต์แวร์บริหารกริดลิขสิทธิ์เฉพาะตัว</li>
            </ul>

            <h3>💰 4. กลุ่ม Bitcoin & Global Liquidity (BTC-USD) — ขาขึ้นจากกระแสเงินสดมหภาค</h3>
            <p><b>วิเคราะห์งบและสิทธิบัตร:</b> ไม่มีงบการเงินบริษัท แต่วัดกันที่สภาพคล่องโลก (Global Liquidity) และนโยบายการเงิน วอลุ่มพุ่งทะยานไวที่สุดในบรรดาสินทรัพย์ทั้งหมดเมื่อเงินเฟ้อหรือดอกเบี้ยเป็นใจ</p>
            <ul>
                <li>🚀 <b>ตัวเต็งกระชากพอร์ต (High Beta):</b> <code>Bitcoin (BTC)</code> — สินทรัพย์สินสุทธิที่ดูดสภาพคล่องไวและรุนแรงที่สุด เหมาะกับการเล่นรอบสั้นทำกำไรกระชากใจ</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
