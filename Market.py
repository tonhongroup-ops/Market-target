import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Heatmap & Innovation Theme Radar",
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
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Global Heatmap Sector & Innovation Radar")
st.markdown("เรดาร์ติดตามกระแสเงินทุนภาพใหญ่: Heatmap Sectors + Gold + Bitcoin + Grid + Patent Moat + Clean Tech + Advanced Materials (ย้อนหลัง 2 ปี | เผื่อขวา 15%)")

# --- รวบรวม Sector ตาม Heatmap + สินทรัพย์พิเศษที่มึงสั่ง ---
radar_assets = {
    # Heatmap Core Sectors (US SPDR ETFs)
    "Technology (XLK)": "XLK",
    "Semiconductors / Patent Moat (SMH)": "SMH",
    "Financials (XLF)": "XLF",
    "Healthcare / Biotech (XLV)": "XLV",
    "Industrials & Grid (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "Consumer Staples (XLP)": "XLP",
    "Energy & Clean Tech (XLE)": "XLE",
    "Advanced Materials (XLB)": "XLB",
    "Utilities (XLU)": "XLU",
    # Custom Assets ตามสั่ง
    "Gold / Safe Haven (GC=F)": "GC=F",
    "Bitcoin / Global Liquidity (BTC-USD)": "BTC-USD"
}

@st.cache_data(ttl=3600)
def fetch_custom_net_flow(assets_dict):
    data_frames = {}
    for name, symbol in assets_dict.items():
        df = yf.download(symbol, period="2y", auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            data_frames[name] = df['Close']
    
    df_combined = pd.DataFrame(data_frames)
    df_combined = df_combined.ffill().bfill()
    # คำนวณมูลค่าสะสมเทียบจุดเริ่มต้น (Base 0%)
    df_net_value = ((df_combined / df_combined.iloc[0]) - 1) * 100
    return df_net_value

with st.spinner("กำลังประมวลผลกระแสเงินทุนแบบจัดเต็ม..."):
    df_flow = fetch_custom_net_flow(radar_assets)

if not df_flow.empty:
    last_date = df_flow.index[-1]
    first_date = df_flow.index[0]
    total_days = (last_date - first_date).days
    
    # เว้นพื้นที่ว่างด้านขวาของกราฟไว้ 15% ตามสั่ง
    padding_days = int(total_days * 0.15)
    max_x_limit = last_date + timedelta(days=padding_days)

    fig = go.Figure()

    for col in df_flow.columns:
        fig.add_trace(go.Scatter(
            x=df_flow.index, 
            y=df_flow[col], 
            mode='lines',
            line=dict(width=2),
            name=col,
            connectgaps=True,         # เส้นทึบเชื่อมเนียนกริบ
            hoverinfo='skip'          # ปิดกล่องข้อความตอนเมาส์จิ้มตามสั่ง
        ))

    fig.update_layout(
        template="plotly_dark",
        title="Heatmap & Innovation Asset Net Value Flow (2-Year Clean View)",
        xaxis_title="วันที่",
        yaxis_title="มูลค่าสะสมเทียบจุดเริ่มต้น (%)",
        xaxis=dict(
            range=[first_date, max_x_limit] # ขยายขวา 15%
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.4,                   # ย้าย Legend มาไว้ด้านล่าง เปิด-ปิดสะดวก
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=120)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 ตารางสรุปมูลค่าสะสมล่าสุด (%) ของแต่ละ Sector")
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "Net Value Flow (%)"}), use_container_width=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
