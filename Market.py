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

# --- Theme CSS สไตล์นักวิเคราะห์มืออาชีพ ---
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .analysis-box { background-color: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Global Heatmap & Innovation Smart Money Radar (All Sectors)")
st.markdown("เรดาร์สแกนกระแสเงินทุน Smart Money ครบทุก Sector Heatmap, Smart Grid, Gold และ Bitcoin พร้อมระบบกรองสเกลกราฟให้มองเห็นง่ายชัดเจน และบทวิเคราะห์เจาะลึกงบ/สิทธิบัตร")

# --- รวบรวมทุก Sector ทั้งหมดตาม Heatmap ดั้งเดิมและสินทรัพย์พิเศษตามที่มึงต้องการ ---
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
                # ตัด Outlier ป้องกันสเกลพัง
                vol_change = vol_change.clip(lower=-80, upper=300)
                volume_frames[name] = vol_change
            else:
                volume_frames[name] = pd.Series(0, index=df.index)
                
    df_vol = pd.DataFrame(volume_frames)
    df_vol = df_vol.ffill().bfill()
    return df_vol

with st.spinner("กำลังประมวลผลข้อมูล All Sectors Heatmap และกระแส Smart Money..."):
    df_flow = fetch_all_sectors_flow(radar_assets)

if not df_flow.empty:
    last_date = df_flow.index[-1]
    first_date = df_flow.index[0]
    total_days = (last_date - first_date).days
    
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
            connectgaps=True
        ))

    fig.update_layout(
        template="plotly_dark",
        title="All Sectors Heatmap & Assets % Volume Change Flow (Clean View)",
        xaxis_title="วันที่",
        yaxis_title="% Volume Change (vs 20D MA)",
        xaxis=dict(range=[first_date, max_x_limit]),
        yaxis=dict(range=[-60, 250]), # ล็อกกรอบแกน Y ให้มองเห็นเส้นทุก Sector ชัดเจน ไม่แบนราบ
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
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "% Volume Change (Latest)"}), use_container_width=True)

    # --- ส่วนบทวิเคราะห์เจาะลึกครบทุกกลุ่มแบบจัดเต็ม ---
    st.markdown("""
    <div class="analysis-box">
    <h2>🧬 บทวิเคราะห์เจาะลึก All Sectors Heatmap, สิทธิบัตร และสมาร์ทมันนี่</h2>
    <p><i>วิเคราะห์งบการเงิน สิทธิบัตร (Patent Moat) และรอบการหมุนเวียนของเงินทุนในทุก Sector เพื่อให้มึงตามเจ้ามือทันทุกจังหวะ</i></p>
    <hr style="border-color: #30363d;">
    
    ### 🔥 1. กลุ่ม Semiconductors & Patent Moat (SMH / XLK)
    * **วิเคราะห์งบและสิทธิบัตร:** Gross Margin สูงระดับ 60-80% มีสิทธิบัตรคุ้มครองสถาปัตยกรรมชิปและเครื่องพิมพ์ EUV ลิขสิทธิ์เฉพาะตัว สมาร์ทมันนี่ชอบสะสมช่วงหุ้นซบเซาก่อนระเบิดรับรอบ AI
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `NVDA (Nvidia)` — เจ้าตลาดฮาร์ดแวร์ AI วอลุ่มเข้าแน่น
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `ASML (ASML Holding)` — ผูกขาดเครื่องพิมพ์ EUV รายเดียวในโลก งบแกร่งสุด

    ### ⚡ 2. กลุ่ม Industrials & Smart Grid (XLI)
    * **วิเคราะห์งบและสิทธิบัตร:** งบโตต่อเนื่องจาก Backlog สั่งซื้อล่วงหน้า สิทธิบัตรระบบส่งกำลังไฟฟ้าแรงดันสูงและซอฟต์แวร์กริดอัจฉริยะ รองรับการบูมของ Data Center
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `GE Vernova (GEV)` — กังหันก๊าซและโครงสร้างพื้นฐานกริด ยอดจองพุ่ง
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Eaton Corp (ETN)` — เบอร์หนึ่งเรื่องหม้อแปลงและสวิตช์เกียร์อัจฉริยะ

    ### 🔋 3. กลุ่ม Energy & Clean Tech (XLE)
    * **วิเคราะห์งบและสิทธิบัตร:** เร่งลงทุน R&D ระบบกักเก็บพลังงาน (BESS) และเซลล์เชื้อเพลิง สิทธิบัตรเคมีแบตเตอรี่คือเกราะคุ้มกันชั้นดี
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Bloom Energy (BE)` — เซลล์เชื้อเพลิงผลิตไฟฟ้านอกกริดป้อน Data Center
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Fluence Energy (FLNC)` — ผู้นำระบบ BESS ระดับโลก มีซอฟต์แวร์ควบคุมกริดลิขสิทธิ์

    ### 🧪 4. กลุ่ม Healthcare, Advanced Materials & Others (XLV / XLB / XLF / XLU / XLP / XLY)
    * **วิเคราะห์งบและสิทธิบัตร:** กลุ่มป้องกันความเสี่ยงและเติบโตตามวัฏจักรเศรษฐกิจ สิทธิบัตรยาเฉพาะทาง (เช่น Eli Lilly) ทำกำไรมหาศาล ขณะที่กลุ่มธนาคารและอุปโภคบริโภคมองกระแสเงินสดปันผล
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Eli Lilly (LLY)` / `MP Materials (MP)` — หุ้นนวัตกรรมยาและแร่หายากที่ทุนใหญ่ชอบเข้า
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** หุ้นกลุ่ม Defensive ที่งบการเงินนิ่งและมีกระแสเงินสดสม่ำเสมอ

    ### 💰 5. กลุ่ม Bitcoin (BTC-USD) & Gold (GC=F)
    * **วิเคราะห์งบและสิทธิบัตร:** วัดกันที่สภาพคล่องมหภาค (Global Liquidity) และกระแสเงินสดสำรองปลอดภัย
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Bitcoin (BTC)` — สินทรัพย์ดูดสภาพคล่องไวและรุนแรงที่สุด
    * 💎 **ของดีพรีเมียม (Core Safe Haven):** `Gold (GC=F)` — สินทรัพย์ปลอดภัยดั้งเดิม เสถียรสูงสุด
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
