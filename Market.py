import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Money Sniper & Innovation Radar", layout="wide")

st.title("🧬 Smart Money Sniper & Innovation Patent Radar Pro")
st.markdown("เรดาร์สแกนหุ้นนวัตกรรม สิทธิบัตร + ตารางกรอง % Volume Acceleration + กราฟเทคนิคระดับโปร")

# --- กลุ่มสินทรัพย์และนวัตกรรมเชิงลึก ---
radar_assets = {
    "Technology & AI (XLK)": "XLK",
    "Semiconductors / Patent Moat (SMH)": "SMH",
    "Healthcare / Biotech (XLV)": "XLV",
    "Advanced Materials (XLB)": "XLB",
    "Industrials / Smart Grid (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "SET100 Index (SET.BK)": "^SET.BK",
    "Gold / Safe Haven (GC=F)": "GC=F",
    "Bitcoin / Global Liquidity (BTC-USD)": "BTC-USD"
}

@st.cache_data(ttl=3600)
def fetch_smart_money_radar(assets):
    plot_data = {}
    table_data = []
    fundamental_data = []
    sniper_picks = []
    
    for name, symbol in assets.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", auto_adjust=True)
            if df.empty: continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            close = df['Close'].dropna()
            vol = df['Volume'].dropna()
            
            if len(close) < 30 or len(vol) < 30:
                continue
                
            # 1. ข้อมูลกราฟ %Performance
            perf = ((close - close.iloc[0]) / close.iloc[0]) * 100
            plot_data[name] = perf
            
            # 2. คำนวณ % Volume Acceleration (ตามที่มึงต้องการให้กรองแคบลงและคมขึ้น)
            v_sma20 = vol.rolling(20).mean()
            if pd.isna(v_sma20.iloc[-1]) or v_sma20.iloc[-1] == 0:
                continue
                
            accel_1d = float(((vol.iloc[-1] - v_sma20.iloc[-1]) / v_sma20.iloc[-1]) * 100)
            accel_3d = float(((vol.iloc[-3:].mean() - v_sma20.iloc[-3:].mean()) / v_sma20.iloc[-3:].mean()) * 100)
            accel_1w = float(((vol.iloc[-5:].mean() - v_sma20.iloc[-5:].mean()) / v_sma20.iloc[-5:].mean()) * 100)
            accel_3w = float(((vol.iloc[-15:].mean() - v_sma20.iloc[-15:].mean()) / v_sma20.iloc[-15:].mean()) * 100)
            accel_1m = float(((vol.iloc[-20:].mean() - v_sma20.iloc[-20:].mean()) / v_sma20.iloc[-20:].mean()) * 100)
            
            table_data.append({
                "Asset / Sector": name,
                "1D Accel (%)": round(accel_1d, 2),
                "3D Accel (%)": round(accel_3d, 2),
                "1W Accel (%)": round(accel_1w, 2),
                "3W Accel (%)": round(accel_3w, 2),
                "1M Accel (%)": round(accel_1m, 2)
            })
            
            # เงื่อนไขคัดกรอง Smart Money (จับจังหวะเงินเข้าแบบเน้นๆ)
            price_ma20 = close.rolling(20).mean().iloc[-1]
            if accel_1d > 12 and accel_3d > 5 and close.iloc[-1] > price_ma20 and "Gold" not in name and "Bitcoin" not in name:
                sniper_picks.append({"name": name, "score": round(accel_1d + accel_3d, 2)})

            # 3. ข้อมูลพื้นฐานย่อ
            info = ticker.info
            pe = info.get('trailingPE', np.nan)
            div_yield = info.get('dividendYield', 0)
            div_pct = f"{div_yield * 100:.2f}%" if div_yield and not np.isnan(div_yield) else "N/A"
            
            fundamental_data.append({
                "Asset / Sector": name,
                "Current Return (%)": round(perf.iloc[-1], 2),
                "Trailing PE": round(pe, 2) if pe and not np.isnan(pe) else "N/A",
                "Div Yield": div_pct
            })
            
        except Exception:
            continue
            
    return plot_data, pd.DataFrame(table_data), pd.DataFrame(fundamental_data), sniper_picks

with st.spinner('กำลังประมวลผลระบบสแกน Smart Money...'):
    plot_data, df_vol_accel, df_fund, picks = fetch_smart_money_radar(radar_assets)

# --- 1. Smart Money Sniper Alert ---
st.subheader("🎯 Smart Money Sniper Alert (จับจังหวะเงินไหลเข้า)")
if picks:
    for p in picks:
        st.success(f"🔥 ตรวจพบกระแสเงินทุนหนาแน่นใน **{p['name']}** (Score: {p['score']}) — วอลุ่มเร่งตัวเหนือค่าเฉลี่ยและราคายืนเหนือ SMA20")
else:
    st.info("💡 ตอนนี้ยังไม่มี Sector ไหนเข้าเกณฑ์เร่งตัวแบบจัดเต็ม ตลาดกำลังอยู่ในโหมดพักตัวหรือรอดูข่าวเชิงมหภาค")

# --- 2. กราฟเทคนิค (เส้นทึบหนา, เว้นขวา 10%, ซูมได้, กดปิดเส้นได้) ---
st.subheader("📈 Performance & Trend Comparison (Interactive Pro Chart)")

if plot_data:
    fig = go.Figure()
    
    for name, data in plot_data.items():
        is_innovation = any(x in name for x in ["XLK", "SMH", "XLV", "XLB"])
        width = 3.0 if is_innovation else 1.5
        
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data, 
            mode='lines', 
            name=name, 
            line=dict(width=width, dash='solid')
        ))

    first_key = list(plot_data.keys())[0]
    all_dates = plot_data[first_key].index
    last_date = all_dates[-1]
    start_date = all_dates[0]
    right_padding = last_date + ((last_date - start_date) * 0.1)

    fig.update_layout(
        xaxis=dict(range=[start_date, right_padding], showgrid=True, gridcolor="#30363d", type="date"),
        yaxis=dict(showgrid=True, gridcolor="#30363d", zeroline=True, zerolinecolor="#8b949e", zerolinewidth=1.5),
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        hovermode="x unified", legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
    st.caption("💡 ทริค: คลิกที่ชื่อ Sector ด้านล่างเพื่อซ่อน/โชว์เส้น, ลากเมาส์ครอบเพื่อซูมดูช่วงเวลาข่าวออกได้เลย")

# --- 3. ตาราง % Volume Acceleration ที่มึงตามหา ---
st.subheader("📊 Volume Acceleration Table (%Vol Change เทียบค่าเฉลี่ย 20 วัน)")
if not df_vol_accel.empty:
    st.dataframe(df_vol_accel.sort_values(by="1D Accel (%)", ascending=False), use_container_width=True, hide_index=True)
else:
    st.warning("กำลังดึงข้อมูลตาราง Volume...")

# --- 4. ตารางงบการเงินและ Valuation พื้นฐาน ---
st.subheader("📋 Fundamental & Valuation Snapshot")
if not df_fund.empty:
    st.dataframe(df_fund.sort_values(by="Current Return (%)", ascending=False), use_container_width=True, hide_index=True)
    
