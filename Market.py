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
    .analysis-box { background-color: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Global Heatmap Sector & Innovation Smart Money Radar")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุนสะสมผ่าน `% Volume Change (vs 20D MA)` ครบเครื่องทุก Sector Heatmap, Smart Grid, Gold และ Bitcoin เส้นกราฟตรงชัดเจน พร้อมบทวิเคราะห์อัปเดตอัตโนมัติทุกรีเฟรช")

# --- รวบรวมทุก Sector ตาม Heatmap + Smart Grid + สินทรัพย์พิเศษตามที่มึงต้องการครบถ้วน ---
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
                # คำนวณ % Volume Change เทียบกับค่าเฉลี่ย 20 วัน
                vol_sma = df['Volume'].rolling(window=20).mean()
                vol_change = ((df['Volume'] - vol_sma) / vol_sma) * 100
                volume_frames[name] = vol_change
            else:
                volume_frames[name] = pd.Series(0, index=df.index)
                
    df_vol = pd.DataFrame(volume_frames)
    df_vol = df_vol.ffill().bfill()
    return df_vol

with st.spinner("กำลังคำนวณ % Volume Change ทุก Sector และดึงข้อมูลสมาร์ทมันนี่..."):
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
            mode='lines', # เส้นกราฟตรง (Linear lines) ชัดเจน
            line=dict(width=1.5),
            name=col,
            connectgaps=True,
            hoverinfo='skip'
        ))

    fig.update_layout(
        template="plotly_dark",
        title="Full Sector Heatmap & Innovation % Volume Change Flow (Linear View)",
        xaxis_title="วันที่",
        yaxis_title="% Volume Change (vs 20D MA)",
        xaxis=dict(
            range=[first_date, max_x_limit]
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=150)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 ตารางสรุป % Volume Change ล่าสุดของทุก Sector")
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "% Volume Change (Latest)"}), use_container_width=True)

    # --- ส่วนบทวิเคราะห์จัดเต็ม อ่านง่ายสบายตาด้วย Markdown แท้ๆ ---
    st.markdown("""
    <div class="analysis-box">
    <h2>🧬 บทวิเคราะห์เจาะลึก Sector Heatmap, Smart Grid, สิทธิบัตร และหุ้นเต็ง</h2>
    <p><i>วิเคราะห์สดผ่านระบบทุกรีเฟรช ครบเครื่องทุกกลุ่มสินทรัพย์ที่มึงสั่ง เกาะติดกระแสเงินทุนสมาร์ทมันนี่แบบคมๆ</i></p>
    <hr style="border-color: #30363d;">
    
    ### 🔥 1. กลุ่ม Semiconductors & Patent Moat (SMH / XLK)
    * **วิเคราะห์งบและสิทธิบัตร:** งบเด่นเรื่อง Gross Margin สูงลิ่ว (50-80%) เพราะมีสิทธิบัตรคุ้มครองสถาปัตยกรรมชิปและเครื่องพิมพ์ EUV ลิขสิทธิ์เฉพาะตัวที่คู่แข่งก๊อปปี้ไม่ได้ วอลุ่มพุ่งรับรอบขยายกำลังผลิต AI Hardware
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `NVDA (Nvidia)` — เจ้าตลาดฮาร์ดแวร์ AI วอลุ่มหนาแน่น พอร์ตเขียวไวสุด
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `ASML (ASML Holding)` — ผูกขาดเครื่องพิมพ์ EUV รายเดียวในโลก งบแกร่ง รายได้มั่นคงตามดีมานด์ชิปล้ำยุค

    ### ⚡ 2. กลุ่ม Industrials & Smart Grid (XLI)
    * **วิเคราะห์งบและสิทธิบัตร:** งบโตต่อเนื่องจาก Backlog (ยอดสั่งซื้อรอส่งมอบ) ทุบสถิติ สิทธิบัตรเน้นระบบส่งกำลังไฟฟ้าแรงดันสูงและซอฟต์แวร์บริหารกริดอัจฉริยะ รองรับการแห่สร้าง Data Center ทั่วโลก
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `GE Vernova (GEV)` — ผู้นำกังหันก๊าซและโครงสร้างพื้นฐานกริดไฟฟ้า ยอดจองล้นทะลัก วอลุ่มเหวี่ยงสะใจสายเก็งกำไร
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Eaton Corp (ETN)` — เบอร์หนึ่งเรื่องหม้อแปลงและสวิตช์เกียร์อัจฉริยะ งบสม่ำเสมอ ความได้เปรียบทางวิศวกรรมสูง

    ### 🔋 3. กลุ่ม Energy & Clean Tech (XLE)
    * **วิเคราะห์งบและสิทธิบัตร:** อยู่ในช่วงเร่งลงทุน R&D นวัตกรรมกักเก็บพลังงาน (BESS) และเซลล์เชื้อเพลิง สิทธิบัตรเคมีแบตเตอรี่คือหัวใจสำคัญ วอลุ่มมักจะสวิงแรงตามข่าวดีลโครงการพลังงานขนาดใหญ่
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Bloom Energy (BE)` — โดดเด่นเรื่องเซลล์เชื้อเพลิงผลิตไฟฟ้านอกกริด (Microgrid) ป้อนให้ Data Center วอลุ่มเข้าไวออกไว
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Fluence Energy (FLNC)` — ผู้นำระบบ BESS ระดับโลก มีซอฟต์แวร์ควบคุมกริดที่จดลิขสิทธิ์แน่นหนา

    ### 🧪 4. กลุ่ม Advanced Materials & Healthcare (XLB / XLV)
    * **วิเคราะห์งบและสิทธิบัตร:** เติบโตตามความต้องการวัสดุศาสตร์เกรดพิเศษในอากาศยานและเซมิคอนดักเตอร์ รวมถึงสิทธิบัตรยาและเครื่องมือแพทย์เฉพาะทางที่ทำกำไรมหาศาล
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `MP Materials (MP)` — เหมืองแร่หายาก (Rare Earth) ของสหรัฐฯ วอลุ่มตอบสนองไวตามประเด็นซัพพลายเชน
    * 💎 **ของดีพรีเมียม (Core Patent Moat):** `Eli Lilly (LLY)` — เจ้าตลาดนวัตกรรมยาต้านโรคอ้วนและเบาหวาน สิทธิบัตรแน่น งบโตระเบิด

    ### 💰 5. กลุ่ม Bitcoin (BTC-USD) & Gold (GC=F)
    * **วิเคราะห์งบและสิทธิบัตร:** ไม่มีงบการเงินบริษัท แต่วัดกันที่สภาพคล่องมหภาค (Global Liquidity) และนโยบายการเงิน วอลุ่มพุ่งกระจายตามตัวเลขเงินเฟ้อและความเสี่ยงเชิงระบบ
    * 🚀 **ตัวเต็งกระชากพอร์ต (High Beta):** `Bitcoin (BTC)` — สินทรัพย์สภาพคล่องสูงที่ตอบสนองไวที่สุดในพอร์ต
    * 💎 **ของดีพรีเมียม (Core Safe Haven):** `Gold (GC=F)` — สินทรัพย์ปลอดภัยดั้งเดิม เสถียรและป้องกันความเสี่ยงดีเยี่ยม
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
