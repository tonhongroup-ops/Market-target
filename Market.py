import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Money Sniper Pro", layout="wide")

st.title("🎯 Smart Money Sniper: Innovation & Patent Radar")
st.markdown("คัดเฉพาะตัวที่เงินไหลเข้า (High Accel Volume) + กราฟวิเคราะห์รอบ")

radar_assets = {
    "Technology & AI (XLK)": "XLK",
    "Semiconductors (SMH)": "SMH",
    "Healthcare/Biotech (XLV)": "XLV",
    "Industrials/Smart Grid (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "Energy & Clean Tech (XLE)": "XLE"
}

@st.cache_data(ttl=3600)
def analyze_smart_money(assets_dict):
    table_data = []
    plot_data = {}
    sniper_picks = []
    
    for name, symbol in assets_dict.items():
        df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
        if df.empty: continue
        
        # กราฟเปรียบเทียบ %Performance (Normalizing)
        close = df['Close']
        perf = ((close - close.iloc[0]) / close.iloc[0]) * 100
        plot_data[name] = perf
        
        # คำนวณ Smart Money Score (Volume Acceleration)
        vol = df['Volume']
        v_sma20 = vol.rolling(20).mean()
        
        # อัตราเร่งของวอลุ่มเทียบกับค่าเฉลี่ย 20 วัน
        accel_1d = ((vol.iloc[-1] - v_sma20.iloc[-1]) / v_sma20.iloc[-1]) * 100
        accel_3d = ((vol.iloc[-3:].mean() - v_sma20.iloc[-3:].mean()) / v_sma20.iloc[-3:].mean()) * 100
        accel_1w = ((vol.iloc[-5:].mean() - v_sma20.iloc[-5:].mean()) / v_sma20.iloc[-5:].mean()) * 100
        accel_3w = ((vol.iloc[-15:].mean() - v_sma20.iloc[-15:].mean()) / v_sma20.iloc[-15:].mean()) * 100
        accel_1m = ((vol.iloc[-20:].mean() - v_sma20.iloc[-20:].mean()) / v_sma20.iloc[-20:].mean()) * 100
        
        table_data.append({
            "Asset": name, "1D Accel (%)": round(accel_1d, 2), "3D Accel (%)": round(accel_3d, 2),
            "1W Accel (%)": round(accel_1w, 2), "3W Accel (%)": round(accel_3w, 2), "1M Accel (%)": round(accel_1m, 2)
        })
        
        # เงื่อนไข Sniper: 1D และ 3D ต้องเป็นบวกและเหนือเกณฑ์ (แสดงว่าเงินพึ่งเข้า)
        price_ma20 = df['Close'].rolling(20).mean().iloc[-1]
        if accel_1d > 20 and accel_3d > 10 and df['Close'].iloc[-1] > price_ma20:
            sniper_picks.append({"name": name, "score": accel_1d + accel_3d})

    return pd.DataFrame(table_data), plot_data, sniper_picks

df_stats, plot_data, picks = analyze_smart_money(radar_assets)

# --- 1. แสดงผล Sniper Picks ---
st.subheader("🚀 Smart Money Alert: ตัวที่เงินไหลเข้าหนักๆ")
if picks:
    for p in picks:
        st.success(f"พบสัญญาณ Smart Money ใน {p['name']} - วอลุ่มกระชากและราคายืนเหนือเส้นค่าเฉลี่ย!")
else:
    st.info("ตลาดกำลังพักตัว: ยังไม่มีสินทรัพย์ไหนผ่านเงื่อนไข Smart Money รอบนี้")

# --- 2. กราฟเทพ (เส้นเต็ม + เว้นระยะขวา 10%) ---
st.subheader("📈 Performance Comparison")
fig = go.Figure()
for name, data in plot_data.items():
    fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', name=name, line=dict(width=2)))

# ตั้งระยะห่างขวา 10%
last_date = list(plot_data.values())[0].index[-1]
padding = (last_date - list(plot_data.values())[0].index[0]) * 0.1
fig.update_layout(
    xaxis=dict(range=[list(plot_data.values())[0].index[0], last_date + padding]),
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
    hovermode="x unified", legend=dict(orientation="h", y=-0.2)
)
st.plotly_chart(fig, use_container_width=True)

# --- 3. ตารางข้อมูลแบบละเอียด ---
st.subheader("📊 Volume Acceleration Table")
st.dataframe(df_stats, use_container_width=True)
