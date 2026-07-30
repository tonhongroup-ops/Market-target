import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Macro Money Flow Radar",
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
st.markdown("เรดาร์ภาพใหญ่กระแสเงินทุนเคลื่อนย้ายของโลก (ย้อนหลัง 2 ปี | จัดเรียงเส้นให้เนียนสนิท)")

# --- กำหนดเฉพาะสินทรัพย์ภาพใหญ่ ---
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

time_period = "2y"

@st.cache_data(ttl=3600)
def fetch_macro_flow(tickers_dict, period):
    data_frames = {}
    for name, symbol in tickers_dict.items():
        df = yf.download(symbol, period=period, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            # ดึงเฉพาะราคาปิด
            data_frames[name] = df['Close']
            
    # รวม DataFrame เข้าด้วยกัน
    df_combined = pd.DataFrame(data_frames)
    
    # เติมข้อมูลช่วงวันหยุด (Forward Fill) เพื่อไม่ให้เกิดช่องว่างข้อมูลที่ทำให้เส้นขาด
    df_combined = df_combined.ffill().bfill()
    
    # คำนวณ % Return สะสมเทียบจุดเริ่มต้น
    df_return = ((df_combined / df_combined.iloc[0]) - 1) * 100
    return df_return

with st.spinner("กำลังจัดระเบียบข้อมูลกระแสเงินทุนโลก..."):
    df_macro = fetch_macro_flow(macro_assets, time_period)

if not df_macro.empty:
    last_date = df_macro.index[-1]
    first_date = df_macro.index[0]
    total_days = (last_date - first_date).days
    
    padding_days = int(total_days * 0.15)
    max_x_limit = last_date + timedelta(days=padding_days)

    fig = go.Figure()

    for col in df_macro.columns:
        fig.add_trace(go.Scatter(
            x=df_macro.index, 
            y=df_macro[col], 
            mode='lines',            
            line=dict(width=2.5),    # เส้นทึบหนาเต็มตา
            name=col,
            connectgaps=True,        # คำสั่งบังคับเชื่อมช่องว่างข้อมูลให้ต่อกันสนิท
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))

    fig.update_layout(
        template="plotly_dark",
        title="Macro Asset Flow Comparison (Solid & Connected Lines)",
        xaxis_title="วันที่",
        yaxis_title="ผลตอบแทนสะสม (%)",
        hovermode="x unified",
        xaxis=dict(
            range=[first_date, max_x_limit],
            type='date'
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=80)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 ตารางสรุปผลตอบแทนสะสมล่าสุด (%) ในรอบ 2 ปี")
    st.dataframe(df_macro.tail(1).T.rename(columns={df_macro.index[-1]: "Return (%)"}), use_container_width=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
