import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Money Rotation & Innovation Radar Pro", layout="wide")

st.title("🧬 Smart Money Rotation & Innovation Radar Pro")
st.markdown("เรดาร์แกะรอยกระแสเงินทุน (Capital Rotation) + ตาราง %Vol Change ครบทุกไทม์เฟรม (ส่องจังหวะงบการเงินและสิทธิบัตร)")

# --- สินทรัพย์นวัตกรรม สิทธิบัตร และ SET100 ---
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
def analyze_comprehensive_radar(assets):
    plot_data = {}
    matrix_data = []
    fundamental_data = []
    rotation_signals = []
    
    for name, symbol in assets.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", auto_adjust=True)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
                
            close = df['Close'].dropna()
            vol = df['Volume'].dropna()
            if len(close) < 60 or len(vol) < 60: continue
                
            # 1. กราฟเส้น %Performance
            perf = ((close - close.iloc[0]) / close.iloc[0]) * 100
            plot_data[name] = perf
            
            # 2. คำนวณ % Volume Change เทียบค่าเฉลี่ย 20 วัน ครบทุกระยะ (1D, 3D, 1W, 3W, 1M, 2M, 3M)
            v_sma20 = vol.rolling(20).mean()
            if pd.isna(v_sma20.iloc[-1]) or v_sma20.iloc[-1] == 0: continue
                
            v_1d = float(((vol.iloc[-1] - v_sma20.iloc[-1]) / v_sma20.iloc[-1]) * 100)
            v_3d = float(((vol.iloc[-3:].mean() - v_sma20.iloc[-3:].mean()) / v_sma20.iloc[-3:].mean()) * 100)
            v_1w = float(((vol.iloc[-5:].mean() - v_sma20.iloc[-5:].mean()) / v_sma20.iloc[-5:].mean()) * 100)
            v_3w = float(((vol.iloc[-15:].mean() - v_sma20.iloc[-15:].mean()) / v_sma20.iloc[-15:].mean()) * 100)
            v_1m = float(((vol.iloc[-20:].mean() - v_sma20.iloc[-20:].mean()) / v_sma20.iloc[-20:].mean()) * 100)
            v_2m = float(((vol.iloc[-40:].mean() - v_sma20.iloc[-40:].mean()) / v_sma20.iloc[-40:].mean()) * 100)
            v_3m = float(((vol.iloc[-60:].mean() - v_sma20.iloc[-60:].mean()) / v_sma20.iloc[-60:].mean()) * 100)
            
            spread_short_vs_long = round(v_1d - v_1m, 2)
            
            matrix_data.append({
                "Asset / Sector": name,
                "1D (%)": round(v_1d, 2),
                "3D (%)": round(v_3d, 2),
                "1W (%)": round(v_1w, 2),
                "3W (%)": round(v_3w, 2),
                "1M (%)": round(v_1m, 2),
                "2M (%)": round(v_2m, 2),
                "3M (%)": round(v_3m, 2),
                "Spread (1D vs 1M)": spread_short_vs_long
            })
            
            # เช็คสัญญาณพิเศษ
            price_ma20 = close.rolling(20).mean().iloc[-1]
            if name == "SET100 Index (SET.BK)" and v_1d > 10 and spread_short_vs_long > 10:
                rotation_signals.append({
                    "name": name,
                    "msg": f"🚨 สัญญาณเงินเข้า SET100! 1D Vol พุ่งไปที่ `{v_1d}%` (Spread ห่างจากค่าเฉลี่ย 1 เดือน `{spread_short_vs_long}%`) จับตาการหมุนเงินกลับตลาดไทย!"
                })
            elif "XL" in symbol and v_1d > 15 and spread_short_vs_long > 15 and close.iloc[-1] > price_ma20:
                rotation_signals.append({
                    "name": name,
                    "msg": f"🔥 Smart Money โหมโรงใน **{name}** (1D Vol: `{v_1d}%`, Spread: `{spread_short_vs_long}%`)"
                })

            # 3. ข้อมูลพื้นฐาน
            info = ticker.info
            pe = info.get('trailingPE', np.nan)
            fundamental_data.append({
                "Asset / Sector": name,
                "Current Return (%)": round(perf.iloc[-1], 2),
                "Trailing PE": round(pe, 2) if pe and not np.isnan(pe) else "N/A"
            })
        except Exception:
            continue
            
    return plot_data, pd.DataFrame(matrix_data), pd.DataFrame(fundamental_data), rotation_signals

with st.spinner('กำลังดึงข้อมูลและคำนวณตารางระยะยาว...'):
    plot_data, df_matrix, df_fund, signals = analyze_comprehensive_radar(radar_assets)

# --- 1. Rotation Alert ---
st.subheader("🎯 Capital Rotation & Smart Money Alert")
if signals:
    for s in signals:
        if "SET100" in s['name']:
            st.error(s['msg'])
        else:
            st.success(s['msg'])
else:
    st.info("💡 ตลาดอยู่ในโหมดทรงตัว ติดตามการประกาศงบและรอบข่าวสิทธิบัตรอย่างใกล้ชิด")

# --- 2. กราฟเทคนิค (เส้นทึบหนา, เว้นขวา 10%, เอา Float ออกสะอาดเอี่ยม) ---
st.subheader("📈 Performance Comparison (Clean Interactive Chart)")

if plot_data:
    fig = go.Figure()
    for name, data in plot_data.items():
        is_focus = any(x in name for x in ["XLK", "SMH", "SET100"])
        width = 3.0 if is_focus else 1.5
        fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', name=name, line=dict(width=width, dash='solid')))

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
    # ซ่อน ModeBar และเครื่องมือลอยเกะกะทิ้งทั้งหมดตามที่สั่ง
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

# --- 3. ตาราง Volume Change ครบทุกระยะ (รวม 2M และ 3M ที่มึงต้องการ) ---
st.subheader("📊 Volume Change Matrix (ครบทุกไทม์เฟรม 1D ถึง 3M สำหรับเทียบรอบงบการเงิน)")
if not df_matrix.empty:
    st.dataframe(df_matrix.sort_values(by="Spread (1D vs 1M)", ascending=False), use_container_width=True, hide_index=True)
    st.caption("📌 **ทริควิเคราะห์:** ใช้ช่อง 2M และ 3M เทียบกับระยะสั้น (1D/3D) เพื่อดูว่าช่วงก่อนประกาศงบหรือหลังงบออก วอลุ่มสะสมหนาแน่นขึ้นหรือแผ่วลงขนาดไหน")
else:
    st.warning("กำลังประมวลผลตาราง...")

# --- 4. ตารางพื้นฐาน ---
st.subheader("📋 Fundamental & Valuation Snapshot")
if not df_fund.empty:
    st.dataframe(df_fund.sort_values(by="Current Return (%)", ascending=False), use_container_width=True, hide_index=True)
    
