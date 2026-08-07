import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Money Sniper Pro", layout="wide")

st.title("🎯 Smart Money Sniper: Innovation & Patent Radar")
st.markdown("คัดเฉพาะตัวที่เงินไหลเข้า (High Accel Volume) + กราฟเส้นทึบ เว้นขวา 10% จบมุมมองโปร")

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
        try:
            df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
            if df is None or df.empty: 
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            if 'Close' not in df.columns or 'Volume' not in df.columns:
                continue
                
            close = df['Close'].dropna()
            vol = df['Volume'].dropna()
            
            if len(close) < 30 or len(vol) < 30:
                continue
                
            # กราฟเปรียบเทียบ %Performance (Normalizing จากจุดเริ่มต้น)
            perf = ((close - close.iloc[0]) / close.iloc[0]) * 100
            plot_data[name] = perf
            
            # คำนวณ Smart Money Score (Volume Acceleration)
            v_sma20 = vol.rolling(20).mean()
            
            if pd.isna(v_sma20.iloc[-1]) or v_sma20.iloc[-1] == 0:
                continue
                
            accel_1d = float(((vol.iloc[-1] - v_sma20.iloc[-1]) / v_sma20.iloc[-1]) * 100)
            accel_3d = float(((vol.iloc[-3:].mean() - v_sma20.iloc[-3:].mean()) / v_sma20.iloc[-3:].mean()) * 100)
            accel_1w = float(((vol.iloc[-5:].mean() - v_sma20.iloc[-5:].mean()) / v_sma20.iloc[-5:].mean()) * 100)
            accel_3w = float(((vol.iloc[-15:].mean() - v_sma20.iloc[-15:].mean()) / v_sma20.iloc[-15:].mean()) * 100)
            accel_1m = float(((vol.iloc[-20:].mean() - v_sma20.iloc[-20:].mean()) / v_sma20.iloc[-20:].mean()) * 100)
            
            table_data.append({
                "Asset": name, 
                "1D Accel (%)": round(accel_1d, 2), 
                "3D Accel (%)": round(accel_3d, 2),
                "1W Accel (%)": round(accel_1w, 2), 
                "3W Accel (%)": round(accel_3w, 2), 
                "1M Accel (%)": round(accel_1m, 2)
            })
            
            # เงื่อนไขคัดกรอง Smart Money (กรองให้แคบและคมขึ้น)
            price_ma20 = close.rolling(20).mean().iloc[-1]
            if accel_1d > 15 and accel_3d > 8 and close.iloc[-1] > price_ma20:
                sniper_picks.append({"name": name, "score": round(accel_1d + accel_3d, 2)})
        except Exception:
            continue

    return pd.DataFrame(table_data), plot_data, sniper_picks

# รันฟังก์ชันวิเคราะห์
with st.spinner('กำลังสแกนหาจังหวะ Smart Money...'):
    df_stats, plot_data, picks = analyze_smart_money(radar_assets)

# --- 1. แสดงผล Sniper Picks ---
st.subheader("🚀 Smart Money Alert: ตัวที่เงินไหลเข้าหนักๆ")
if picks:
    for p in picks:
        st.success(f"🎯 ตรวจพบกระแสเงินทุนหนาแน่นใน **{p['name']}** (Score: {p['score']}) — วอลุ่มเร่งตัวและราคายืนเหนือเส้นค่าเฉลี่ยแข็งแกร่ง")
else:
    st.info("💡 รอบนี้ยังไม่มี Sector ไหนเข้าเกณฑ์เร่งตัวแบบจัดเต็ม ตลาดอยู่ในโหมดรอดูสถานการณ์")

# --- 2. กราฟเทพ (เส้นทึบ 100% + เว้นระยะขวา 10%) ---
st.subheader("📈 Performance Comparison (Solid Lines & 10% Right Padding)")

if plot_data:
    fig = go.Figure()
    
    # วาดเส้นกราฟทีละตัว บังคับให้เป็นเส้นทึบ (dash='solid')
    for name, data in plot_data.items():
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data, 
            mode='lines', 
            name=name, 
            line=dict(width=2.5, dash='solid')
        ))

    # คำนวณช่วงเวลาเพื่อเว้นขวา 10% และตัดจบที่ตลาดปิด
    first_key = list(plot_data.keys())[0]
    all_dates = plot_data[first_key].index
    last_date = all_dates[-1]
    start_date = all_dates[0]
    
    # คำนวณระยะเวลาเพิ่ม 10% ทางขวา
    time_span = last_date - start_date
    right_padding_date = last_date + (time_span * 0.1)

    fig.update_layout(
        xaxis=dict(
            range=[start_date, right_padding_date],
            showgrid=True,
            gridcolor="#30363d",
            type="date"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#30363d",
            zeroline=True,
            zerolinecolor="#8b949e",
            zerolinewidth=1.5
        ),
        plot_bgcolor="#0e1117", 
        paper_bgcolor="#0e1117", 
        font_color="white",
        hovermode="x unified", 
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        height=550
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
else:
    st.warning("⚠️ ไม่พบข้อมูลกราฟในรอบนี้")

# --- 3. ตารางข้อมูลแบบละเอียด ---
st.subheader("📊 Volume Acceleration Table")
if not df_stats.empty:
    st.dataframe(df_stats, use_container_width=True, hide_index=True)
else:
    st.info("กำลังโหลดข้อมูลตาราง...")
    
