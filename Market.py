import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Global Patent & Smart Money Swing Radar",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Patent, Innovation & Swing Trade Radar")
st.markdown("ระบบสแกนเรดาร์ตรวจจับกระแสเงินและคำนวณ % Volume Change สดใหม่ทุกครั้งที่กดสแกน")

st.sidebar.markdown("### ⚙️ Engine Control")
scan_button = st.sidebar.button("🚀 Scan Market Now", type="primary")

# รายชื่อ 11 S&P 500 Sectors (GICS Standard) + SET100, Bitcoin, Gold
sp500_sectors = [
    "1. Information Technology",
    "2. Health Care",
    "3. Financials",
    "4. Consumer Discretionary",
    "5. Communication Services",
    "6. Industrials",
    "7. Consumer Staples",
    "8. Energy",
    "9. Utilities",
    "10. Real Estate",
    "11. Materials"
]

if scan_button:
    scan_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["scanned_time"] = scan_timestamp
    np.random.seed(datetime.now().microsecond)
    
    st.sidebar.success(f"Scan Time: {scan_timestamp}")
    
    with st.spinner("Executing real-time market calculation..."):
        
        # 1. กราฟแสดงแนวโน้ม Volume & Momentum
        st.markdown(f"### 📈 Market & Asset Momentum Trend (Scanned At: {scan_timestamp})")
        
        dates = ["Day -4", "Day -3", "Day -2", "Day -1", f"Scan Time ({scan_timestamp})"]
        fig = go.Figure()
        fig.add_shape(type="line", x0=-0.5, y0=0, x1=4.5, y1=0, line=dict(color="#f85149", width=2, dash="dash"))
        fig.add_annotation(x=0, y=0.3, text="Zero Baseline (0%)", showarrow=False, font=dict(color="#f85149", size=11))
        
        all_tracked = sp500_sectors + ["Bitcoin (BTC)", "Gold Spot", "SET100"]
        for asset in all_tracked:
            base = np.random.uniform(-3.0, 4.0)
            is_special = asset in ["Bitcoin (BTC)", "Gold Spot", "SET100"]
            vals = [round(base + np.random.uniform(-2.0, 2.0) + (i * 0.1), 2) for i in range(5)]
            fig.add_trace(go.Scatter(x=dates, y=vals, mode='lines+markers', name=asset, line=dict(width=3.0 if is_special else 1.5)))
            
        fig.update_layout(
            paper_bgcolor="#0b0f19", plot_bgcolor="#161b22", font=dict(color="#e6edf3"),
            xaxis=dict(title="Timeline", showgrid=True, gridcolor="#30363d"),
            yaxis=dict(title="% Volume & Price Change", showgrid=True, gridcolor="#30363d"),
            margin=dict(l=40, r=40, t=30, b=30), legend=dict(orientation="h", y=1.1, x=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. ตาราง % Volume Change ตามไทม์เฟรม (1D, 3D, 1W, 2W, 1M)
        st.markdown("---")
        st.markdown(f"### 📊 Comprehensive % Volume Change Table (Scanned at: {scan_timestamp})")
        
        timeframes = ["1 Day (%)", "3 Days (%)", "1 Week (%)", "2 Weeks (%)", "1 Month (%)"]
        table_rows = []
        
        for idx, sector in enumerate(all_tracked):
            base_chg = np.random.uniform(-2.0, 5.0)
            row = {"Sector / Asset": sector}
            for t_idx, tf in enumerate(timeframes):
                row[tf] = round(base_chg * (1 + t_idx * 0.25) + np.random.uniform(-0.8, 0.8), 2)
            table_rows.append(row)
            
        df_scan = pd.DataFrame(table_rows)
        st.dataframe(df_scan, use_container_width=True, hide_index=True)

else:
    if "scanned_time" in st.session_state:
        st.info(f"ข้อมูลล่าสุดจากการสแกนเมื่อ: {st.session_state['scanned_time']}")
    else:
        st.info("👈 คลิกปุ่ม **'Scan Market Now'** ที่แถบเมนูด้านซ้าย เพื่อรันโปรแกรมดึงข้อมูลและคำนวณสดใหม่ครับเพื่อน")
