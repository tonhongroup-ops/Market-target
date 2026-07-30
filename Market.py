import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Heatmap & Smart Money Radar",
    page_icon="⚡",
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

st.title("⚡ Global Heatmap & Smart Money Sector Radar")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุน **All Sectors Heatmap** ครบทุกกลุ่ม พร้อมปุ่มเปิด/ปิดเส้นกราฟอิสระ และบทวิเคราะห์เจาะลึกเฉพาะ Sector ขาขึ้นตัวจริงที่มีของ")

# --- รวบรวมทุก Sector ทั้งหมดตาม Heatmap ดั้งเดิมและสินทรัพย์พิเศษ ---
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
def fetch_all_sectors_flow(assets_dict):
    volume_frames = {}
    for name, symbol in assets_dict.items():
        df = yf.download(symbol, period="1y", auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            if 'Volume' in df.columns:
                vol_sma = df['Volume'].rolling(window=20).mean()
                vol_change = ((df['Volume'] - vol_sma) / vol_sma) * 100
                vol_change = vol_change.clip(lower=-80, upper=300)
                volume_frames[name] = vol_change
            else:
                volume_frames[name] = pd.Series(0, index=df.index)
                
    df_vol = pd.DataFrame(volume_frames)
    df_vol = df_vol.ffill().bfill()
    return df_vol

with st.spinner("กำลังประมวลผลข้อมูล All Sectors Heatmap..."):
    df_flow = fetch_all_sectors_flow(radar_assets)

if not df_flow.empty:
    # --- ฟีเจอร์ปุ่มกดเปิด/ปิดเส้นกราฟทุก Sector แบบเลือกได้อิสระ ---
    st.markdown("### 🎛️ ปุ่มควบคุมการแสดงผลเส้นกราฟ (Toggle Sectors)")
    
    keys = list(radar_assets.keys())
    row1 = keys[:4]
    row2 = keys[4:8]
    row3 = keys[8:]
    
    selected_sectors = {}
    
    for row in [row1, row2, row3]:
        cols = st.columns(len(row))
        for i, col_name in enumerate(row):
            with cols[i]:
                selected_sectors[col_name] = st.checkbox(col_name, value=True)

    last_date = df_flow.index[-1]
    first_date = df_flow.index[0]
    total_days = (last_date - first_date).days
    
    padding_days = int(total_days * 0.15)
    max_x_limit = last_date + timedelta(days=padding_days)

    fig = go.Figure()

    for col in df_flow.columns:
        is_visible = True if selected_sectors.get(col, True) else 'legendonly'
        
        fig.add_trace(go.Scatter(
            x=df_flow.index, 
            y=df_flow[col], 
            mode='lines',
            line=dict(width=1.8),
            name=col,
            visible=is_visible,
            connectgaps=True
        ))

    fig.update_layout(
        template="plotly_dark",
        title="All Sectors Heatmap & Assets % Volume Change Flow",
        xaxis_title="วันที่",
        yaxis_title="% Volume Change (vs 20D MA)",
        xaxis=dict(range=[first_date, max_x_limit]),
        yaxis=dict(range=[-60, 250]),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=160)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 ตารางสรุป % Volume Change ล่าสุดของทุก Sector")
    # แก้ไขจุดที่พังโดยเอาพารามิเตอร์เกินออก เหลือแค่ use_container_width=True ตามมาตรฐาน Streamlit
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "% Volume Change (Latest)"}), use_container_width=True)

    # --- ส่วนบทวิเคราะห์: คัดเฉพาะ Sector ขาขึ้นตัวจริงที่มีของ มาชำแหละให้เห็นจะๆ ---
    st.markdown("""
    <div class="analysis-box">
    <h2>🧬 บทวิเคราะห์เจาะลึก: คัดหัวกะทิเฉพาะ Sector ขาขึ้นที่มี "ของจริง"</h2>
    <p><i>จากภาพรวม All Sectors ด้านบน กูคัดเฉพาะกลุ่มที่สมาร์ทมันนี่กำลังทุ่มเงินเข้าจริง งบแกร่ง และมีสิทธิบัตร (Patent Moat) คุ้มครอง มาชำแหละตัวเด็ดให้มึงลุย</i></p>
    <hr style="border-color: #30363d;">
    
    ### 🔥 1. กลุ่ม Semiconductors & Patent Moat (SMH) — ขาขึ้นตัวจริงสาย Deep Tech
    * **วิเคราะห์งบและสิทธิบัตร:** Gross Margin ยืนระยะสูงปรี๊ด 60-80% มีสิทธิบัตรสถาปัตยกรรมชิปและเครื่องพิมพ์ EUV ที่ไม่มีใครลอกเลียนแบบได้ เป็นหัวใจหลักของยุค AI Infrastructure
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `NVDA (Nvidia)` — เจ้าตลาดฮาร์ดแวร์ประมวลผล AI วอลุ่มเข้าสะสมหนาแน่นรอบใหญ่
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `ASML (ASML Holding)` — ผูกขาดเครื่องพิมพ์ EUV รายเดียวในโลก รายได้มั่นคงจากแบ็กล็อกข้ามปี

    ### ⚡ 2. กลุ่ม Industrials & Smart Grid (XLI) — ขาขึ้นจากวิกฤตพลังงานและ Data Center
    * **วิเคราะห์งบและสิทธิบัตร:** งบโตแบบก้าวกระโดดตามคำสั่งซื้อ (Backlog) ระบบส่งไฟฟ้าและกริดอัจฉริยะที่รองรับการแห่สร้าง Data Center ทั่วโลก สิทธิบัตรด้านวิศวกรรมไฟฟ้าแรงสูงคือเกราะคุ้มกันชั้นดี
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `GE Vernova (GEV)` — กังหันก๊าซและกริดไฟฟ้า ยอดจองล้นทะลัก วอลุ่มพุ่งแรง
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Eaton Corp (ETN)` — ผู้นำสวิตช์เกียร์และหม้อแปลงไฟฟ้าอัจฉริยะ งบการเงินนิ่งและแข็งแกร่งมาก

    ### 🔋 3. กลุ่ม Energy & Clean Tech (XLE) — ขาขึ้นจากนวัตกรรมกักเก็บพลังงาน (BESS)
    * **วิเคราะห์งบและสิทธิบัตร:** งบเร่งตัวจากการลงทุนระบบกักเก็บพลังงานและเซลล์เชื้อเพลิงป้อนโรงไฟฟ้า สิทธิบัตรเคมีแบตเตอรี่เฉพาะตัวทำให้ได้งานโปรเจกต์ใหญ่ระดับเมกะโปรเจกต์
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Bloom Energy (BE)` — ผู้นำเซลล์เชื้อเพลิงผลิตไฟฟ้านอกกริด วอลุ่มเหวี่ยงทำกำไรดีเยี่ยม
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Fluence Energy (FLNC)` — เบอร์ใหญ่ระบบ BESS โลก มีซอฟต์แวร์ควบคุมกริดลิขสิทธิ์

    ### 💰 4. กลุ่ม Bitcoin (BTC-USD) & Gold (GC=F) — ขาขึ้นจากสภาพคล่องมหภาค
    * **วิเคราะห์งบและสิทธิบัตร:** ไม่มีงบการเงินบริษัท แต่วัดกันที่สภาพคล่องโลก (Global Liquidity) และกระแสเงินสำรองปลอดภัย
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Bitcoin (BTC)` — สินทรัพย์ดูดสภาพคล่องไวและรุนแรงที่สุดเมื่อตลาดเปิดรับความเสี่ยง
    * 💎 **ของดีพรีเมียม (Core Safe Haven):** `Gold (GC=F)` — สินทรัพย์ปลอดภัยดั้งเดิม เสถียรและป้องกันความเสี่ยงระดับมหภาคได้ยอดเยี่ยม
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
