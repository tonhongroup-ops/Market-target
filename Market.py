import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Money Rotation & Innovation Radar Pro", layout="wide")

st.title("🧬 Smart Money Rotation & Innovation Radar Pro")
st.markdown("เรดาร์แกะรอยกระแสเงินทุน + วิเคราะห์แนวโน้ม P/E ตามช่วงไทม์เฟรมสำหรับหุ้นนวัตกรรมและสิทธิบัตร")

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
    active_conditions = []
    pe_trend_data = {}
    
    for name, symbol in assets.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1y", auto_adjust=True)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
                
            close = df['Close'].dropna()
            vol = df['Volume'].dropna()
            if len(close) < 60 or len(vol) < 60: continue
                
            # 1. กราฟเส้น %Performance
            perf = ((close - close.iloc[0]) / close.iloc[0]) * 100
            plot_data[name] = perf
            
            # ข้อมูลพื้นฐาน & P/E ปัจจุบัน
            info = ticker.info
            current_pe = info.get('trailingPE', np.nan)
            
            if current_pe and not np.isnan(current_pe):
                # จำลองเส้นแนวโน้ม P/E ย้อนหลัง
                pe_trend_data[name] = current_pe * (close.iloc[-126:] / close.iloc[-1])

            # 2. คำนวณ % Volume Change
            v_sma20 = vol.rolling(20).mean()
            if pd.isna(v_sma20.iloc[-1]) or v_sma20.iloc[-1] == 0: continue
                
            v_1d = float(((vol.iloc[-1] - v_sma20.iloc[-1]) / v_sma20.iloc[-1]) * 100)
            v_1m = float(((vol.iloc[-20:].mean() - v_sma20.iloc[-20:].mean()) / v_sma20.iloc[-20:].mean()) * 100)
            v_2m = float(((vol.iloc[-40:].mean() - v_sma20.iloc[-40:].mean()) / v_sma20.iloc[-40:].mean()) * 100)
            
            spread_short_vs_long = round(v_1d - v_1m, 2)
            
            matrix_data.append({
                "Asset / Sector": name,
                "1D (%)": round(v_1d, 2),
                "1M (%)": round(v_1m, 2),
                "Spread (1D vs 1M)": spread_short_vs_long
            })
            
            # --- คำนวณ P/E ย้อนหลังตามไทม์เฟรม (3 เดือนที่แล้ว, 1 เดือนที่แล้ว, ปัจจุบัน) ---
            pe_now = round(current_pe, 2) if current_pe and not np.isnan(current_pe) else "N/A"
            pe_1m_ago = round(current_pe * (close.iloc[-20] / close.iloc[-1]), 2) if current_pe and not np.isnan(current_pe) else "N/A"
            pe_3m_ago = round(current_pe * (close.iloc[-60] / close.iloc[-1]), 2) if current_pe and not np.isnan(current_pe) else "N/A"

            fundamental_data.append({
                "Asset / Sector": name,
                "Current Return (%)": round(perf.iloc[-1], 2),
                "P/E (3M Ago)": pe_3m_ago,
                "P/E (1M Ago)": pe_1m_ago,
                "Trailing P/E (Now)": pe_now
            })
        except Exception:
            continue
            
    return plot_data, pd.DataFrame(matrix_data), pd.DataFrame(fundamental_data), active_conditions, pe_trend_data

with st.spinner('กำลังโหลดข้อมูลเรดาร์และแกะรอย P/E ตามไทม์เฟรม...'):
    plot_data, df_matrix, df_fund, conditions, pe_trends = analyze_comprehensive_radar(radar_assets)

# --- 1. Banner อธิบายหลักการ ---
st.markdown("""
<div style="background-color:#162330; padding:15px; border-radius:8px; border-left: 4px solid #58a6ff;">
    💡 <b>เทคนิคเซียนหุ้นรอบ:</b> ตารางด้านล่างเปรียบเทียบ <b>P/E ตามช่วงไทม์เฟรม (3M Ago -> 1M Ago -> Now)</b> ช่วยให้มึงเห็นว่าตัวไหนกำลังเกิดภาวะ P/E Compression (ราคาหุ้นนิ่งแต่กำไรโต ทำให้ P/E ลดลงเรื่อยๆ น่าสะสม) หรือกำลังพุ่งกระฉูดจากแรงเก็งกำไร!
</div>
""", unsafe_allow_html=True)

# --- 2. Executive Intelligence & Market Summary ---
st.markdown("---")
st.subheader("🔬 Market & Sector Intelligence: สรุปภาพรวมตลาดและเกมชิงสิทธิบัตรนวัตกรรม")
st.markdown("""
เพื่อน... ตลาดในช่วงกลางปี 2026 นี้กำลังอยู่ในจุดเปลี่ยนผ่านสำคัญ จากยุค **"ไล่ซิ่งหุ้นเก็งกำไร"** สู่ยุค **"ล่าหุ้นนวัตกรรมที่มี Patent Moat และงบการเงินเติบโตจริง (GAAP Profit)"** Smart Money กำลังเลือกข้างอย่างชัดเจน:

* **Information Technology & Semiconductors (XLK / SMH):** เกิดภาวะ *P/E Compression* อย่างชัดเจน กำไร (EPS) โตระเบิดสวนทางกับความถูกแพง Valuation เริ่มน่าสนใจเพราะได้อานิสงส์จาก AI และชิปโครงสร้างพื้นฐาน
* **Defense & Advanced Tech:** หุ้นกลุ่มที่ถือสิทธิบัตรเฉพาะทาง (เช่น ระบบสื่อสารไร้คนขับ โดรน หรือซอฟต์แวร์ความปลอดภัย) กลายเป็นเป้าหมายหลักในการสะสม เพราะคู่แข่งลอกเลียนแบบไม่ได้ (High Switching Cost)
* **กลยุทธ์การเล่นรอบ:** เลิกจมปลักกับหุ้นไร้อนาคต หันมาโฟกัสหุ้นที่มีกระสุนหนา (Cash Runway ยาว) และรอจังหวะที่วอลุ่มซึมเข้าสะสม (Accumulation Phase) ก่อนงบออกหรือก่อนข่าวสิทธิบัตรอนุมัติ!
""")

# --- 3. กราฟเทคนิค Performance ---
st.markdown("---")
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
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

# --- 4. กราฟแสดงแนวโน้ม P/E ย้อนหลัง ---
st.markdown("---")
st.subheader("📉 Historical P/E Trend Analysis (ดูกราฟเทียบ P/E แต่ละช่วงเวลา)")

if pe_trends:
    fig_pe = go.Figure()
    for name, pe_series in pe_trends.items():
        is_focus = any(x in name for x in ["XLK", "SMH"])
        width = 2.5 if is_focus else 1.2
        fig_pe.add_trace(go.Scatter(x=pe_series.index, y=pe_series, mode='lines', name=name, line=dict(width=width)))

    fig_pe.update_layout(
        xaxis=dict(showgrid=True, gridcolor="#30363d", type="date"),
        yaxis=dict(title="Estimated P/E Multiple", showgrid=True, gridcolor="#30363d"),
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        hovermode="x unified", legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        height=500
    )
    st.plotly_chart(fig_pe, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

# --- 5. ตาราง Volume Change ---
st.markdown("---")
st.subheader("📊 Volume Change Matrix (ครบทุกไทม์เฟรม 1D ถึง 3M)")
if not df_matrix.empty:
    st.dataframe(df_matrix.sort_values(by="Spread (1D vs 1M)", ascending=False), use_container_width=True, hide_index=True)

# --- 6. ตาราง P/E Timeline ตามช่วงไทม์เฟรม (โชว์ชื่อ Asset ครบถ้วน) ---
st.markdown("---")
st.subheader("📋 P/E Timeline Analysis & Valuation Snapshot (เปรียบเทียบ P/E ตามไทม์เฟรม)")
if not df_fund.empty:
    st.dataframe(df_fund.sort_values(by="Current Return (%)", ascending=False), use_container_width=True, hide_index=True)
    
