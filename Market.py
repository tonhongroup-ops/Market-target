import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Heatmap & Innovation Volume Radar",
    page_icon="📈",
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

st.title("📈 Global Heatmap Sector & Innovation Volume Radar")
st.markdown("เรดาร์ติดตามกระแสปริมาณการซื้อขาย (% Volume Change) สะท้อนการไหลเข้าของ Smart Money แบบเรียลไทม์ (ย้อนหลัง 2 ปี | ขยายขวา 15% | ไม่มี Hover Info กวนใจ)")

# --- รวบรวม Sector ตาม Heatmap + สินทรัพย์พิเศษตามสั่ง ---
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
def fetch_volume_change_flow(assets_dict):
    data_frames = {}
    volume_frames = {}
    
    for name, symbol in assets_dict.items():
        df = yf.download(symbol, period="2y", auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
            data_frames[name] = df['Close']
            if 'Volume' in df.columns:
                # คำนวณ % Volume Change เทียบกับค่าเฉลี่ย 20 วันย้อนหลัง
                vol_sma = df['Volume'].rolling(window=20).mean()
                vol_change = ((df['Volume'] - vol_sma) / vol_sma) * 100
                volume_frames[name] = vol_change
            else:
                volume_frames[name] = pd.Series(0, index=df.index)
                
    df_vol = pd.DataFrame(volume_frames)
    df_vol = df_vol.ffill().bfill()
    return df_vol

with st.spinner("กำลังประมวลผล % Volume Change ของ Smart Money..."):
    df_flow = fetch_volume_change_flow(radar_assets)

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
            line=dict(width=1.5),
            name=col,
            connectgaps=True,
            hoverinfo='skip' # ปิดกล่องข้อความตอนเอาเมาส์จิ้มตามสั่ง
        ))

    fig.update_layout(
        template="plotly_dark",
        title="Sector & Innovation % Volume Change Flow (2-Year Clean View)",
        xaxis_title="วันที่",
        yaxis_title="% Volume Change (vs 20D MA)",
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

    st.markdown("### 📋 ตารางสรุป % Volume Change ล่าสุดของแต่ละ Sector")
    st.dataframe(df_flow.tail(1).T.rename(columns={df_flow.index[-1]: "% Volume Change (Latest)"}), use_container_width=True)

else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    
