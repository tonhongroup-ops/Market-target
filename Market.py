import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Innovation & Patent Smart Money Radar Pro", layout="wide")

st.title("🧬 Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์วิเคราะห์หุ้นนวัตกรรม สิทธิบัตร รอบข่าว และกระแสเงินสดระดับโปร")

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
def fetch_deep_analysis(assets):
    plot_data = {}
    fundamental_data = []
    
    for name, symbol in assets.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", auto_adjust=True)
            if df.empty: continue
            
            close = df['Close'].dropna()
            perf = ((close - close.iloc[0]) / close.iloc[0]) * 100
            plot_data[name] = perf
            
            # ดึงข้อมูลพื้นฐานและงบคร่าวๆ มาสกัด (ถ้ามี)
            info = ticker.info
            pe = info.get('trailingPE', np.nan)
            market_cap = info.get('marketCap', np.nan)
            div_yield = info.get('dividendYield', 0)
            div_pct = f"{div_yield * 100:.2f}%" if div_yield and not np.isnan(div_yield) else "N/A"
            
            fundamental_data.append({
                "Asset / Sector": name,
                "Current Return (%)": round(perf.iloc[-1], 2),
                "Trailing PE": round(pe, 2) if pe and not np.isnan(pe) else "N/A",
                "Div Yield": div_pct,
                "Market Cap (B$)": round(market_cap / 1e9, 2) if market_cap and not np.isnan(market_cap) else "N/A"
            })
        except Exception:
            continue
            
    return plot_data, pd.DataFrame(fundamental_data)

with st.spinner('กำลังเจาะลึกงบการเงินและคำนวณรอบกราฟ...'):
    plot_data, df_fund = fetch_deep_analysis(radar_assets)

# --- 1. Executive Summary & Market Catalyst ---
st.subheader("🎯 Smart Money & Innovation Catalyst Insight")
st.markdown("""
<div style="background-color:#162330; padding:20px; border-radius:10px; border-left: 5px solid #1f6feb; margin-bottom: 20px;">
    <h4>💡 มุมมองวิเคราะห์เชิงลึก (Rotation & Patent Play):</h4>
    <ul>
        <li><b>Semiconductors & AI (SMH / XLK):</b> ยังเป็นหัวใจหลักของกระแสสิทธิบัตรและนวัตกรรมโลก เงินทุน (Smart Money) มักจะพักตัวระยะสั้นก่อนลากรอบใหญ่ตามข่าวออกผลิตภัณฑ์หรือผลประกอบการ</li>
        <li><b>Healthcare / Biotech (XLV):</b> หลุมหลบภัยชั้นดีที่มี Patent Moat คุ้มครองสูง เหมาะกับการถือเล่นรอบเมื่อตลาดผันผวน</li>
        <li><b>Macro Context:</b> เปรียบเทียบผลตอบแทนกับ Gold และ Bitcoin เพื่อเช็คสภาพคล่องโลกว่าไหลเข้าสินทรัพย์เสี่ยงหรือสินทรัพย์ปลอดภัย</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- 2. กราฟเทคนิค (เส้นทึบหนา, เว้นขวา 10%, ซูมได้, กดปิดเส้นได้) ---
st.subheader("📈 Performance & Trend Comparison (Interactive Pro Chart)")

if plot_data:
    fig = go.Figure()
    
    for name, data in plot_data.items():
        # เน้นเส้นกลุ่มนวัตกรรมให้หนาพิเศษ กลุ่มอื่นบางลง
        is_innovation = any(x in name for x in ["XLK", "SMH", "XLV", "XLB"])
        width = 3.0 if is_innovation else 1.5
        
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data, 
            mode='lines', 
            name=name, 
            line=dict(width=width, dash='solid')
        ))

    # คำนวณช่วงเวลาเว้นขวา 10%
    first_key = list(plot_data.keys())[0]
    all_dates = plot_data[first_key].index
    last_date = all_dates[-1]
    start_date = all_dates[0]
    right_padding = last_date + ((last_date - start_date) * 0.1)

    fig.update_layout(
        xaxis=dict(
            range=[start_date, right_padding],
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
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
    st.caption("💡 ทริค: คลิกที่ชื่อ Sector ด้านล่างเพื่อซ่อน/โชว์เส้น, ลากเมาส์ครอบเพื่อซูมดูช่วงเวลาข่าวออกได้เลย")

# --- 3. ตารางงบการเงินและข้อมูลพื้นฐาน ---
st.subheader("📊 Fundamental & Valuation Snapshot")
if not df_fund.empty:
    st.dataframe(df_fund.sort_values(by="Current Return (%)", ascending=False), use_container_width=True, hide_index=True)
else:
    st.warning("กำลังดึงข้อมูลพื้นฐาน...")
    
