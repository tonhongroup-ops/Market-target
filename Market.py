import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Money Flow Macro Radar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme CSS ปรับแต่งให้หน้าจอคลีนและสบายตา ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Global Macro Money Flow Radar")
st.markdown("เรดาร์ภาพใหญ่กระแสเงินทุนเคลื่อนย้ายของโลก (สเกลเทียบจุดเริ่มต้น 0%) เพื่อดูว่าสภาพคล่องกำลังไหลเข้าสินทรัพย์หรือ Sector ไหนแบบเคลียร์ๆ")

# --- กำหนดเฉพาะสินทรัพย์ภาพใหญ่ (ไม่เอาหุ้นรายตัวมารก) ---
macro_assets = {
    "Technology (XLK)": "XLK",
    "Healthcare (XLV)": "XLV",
    "Industrials (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "Energy (XLE)": "XLE",
    "Gold (GC=F)": "GC=F",
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Global Bond (TLT)": "TLT"
}

time_period = st.sidebar.selectbox("เลือกช่วงเวลาภาพใหญ่:", ["3mo", "6mo", "1y", "ytd"], index=1)

@st.cache_data(ttl=3600)
def fetch_macro_flow(tickers_dict, period):
    data_frames = {}
    for name, symbol in tickers_dict.items():
        df = yf.download(symbol, period=period, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            # คำนวณ % Return สะสมเทียบจุดเริ่มต้น
            data_frames[name] = ((df['Close'] / df['Close'].iloc[0]) - 1) * 100
    return pd.DataFrame(data_frames)

with st.spinner("กำลังประมวลผลข้อมูลภาพใหญ่ของโลก..."):
    df_macro = fetch_macro_flow(macro_assets, time_period)

if not df_macro.empty:
    # สร้างกราฟด้วย Plotly
    fig = go.Figure()

    for col in df_macro.columns:
        fig.add_trace(go.Scatter(
            x=df_macro.index, 
            y=df_macro[col], 
            mode='lines', 
            name=col,
            hovertemplate='%{y:.2f}%<extra></extra>' # ตัดข้อมูลขยะออก ให้เหลือแค่ตัวเลข % คลีนๆ
        ))

    # ย้าย Legend ลงมาไว้ด้านล่างกราฟ และจัดระเบียบ Hover ให้ไม่เกะกะ
    fig.update_layout(
        template="plotly_dark",
        title="Macro Asset Flow Comparison (% Return)",
        xaxis_title="วันที่",
        yaxis_title="ผลตอบแทนสะสม (%)",
        hovermode="x unified",
        legend=dict(
            orientation="h",          # จัดเรียงแนวนอน
            yanchor="top",
            y=-0.25,                  # ดันลงมาไว้ใต้กราฟ
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=80)             # เว้นพื้นที่ด้านล่างให้ Legend ไม่ชนขอบ
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 ตารางสรุปผลตอบแทนสะสมล่าสุด (%)")
    st.dataframe(df_macro.tail(1).T.rename(columns={df_macro.index[-1]: "Return (%)"}), use_container_width=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
