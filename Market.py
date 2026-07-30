import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Smart Money & Patent Moat Radar",
    page_icon="🧬",
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

st.sidebar.title("🧬 Smart Money & IP Radar")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "เลือกมุมมองวิเคราะห์:",
    ["🔬 วิเคราะห์หุ้นนวัตกรรม & สิทธิบัตรผูกขาด (IP Moat)", "📊 สแกนรอบเงินทุน & ข่าวสารเปลี่ยนโลก (Sector Swing)"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **มุมมองเพื่อนซี้:** กองทุนใหญ่ไม่เคยซื้อหุ้นตามกราฟเทคนิคอย่างเดียว เขากว้านซื้อหุ้นที่มี 'สิทธิบัตรผูกขาด' และงบการเงินรองรับการเติบโต 3-5 ปีข้างหน้า มาดูกันว่าตัวไหนซ่อนอยู่ในเรดาร์เราบ้าง!")

# --- โหมดที่ 1: วิเคราะห์หุ้นนวัตกรรม & สิทธิบัตรผูกขาด (IP Moat) ---
if app_mode == "🔬 วิเคราะห์หุ้นนวัตกรรม & สิทธิบัตรผูกขาด (IP Moat)":
    st.title("🔬 หุ้นนวัตกรรมเชิงลึก & กำแพงสิทธิบัตร (IP Moat Analyzer)")
    st.markdown("เจาะลึกบริษัทเทคโนโลยีและเครื่องมือแพทย์ระดับโลกที่กุมสิทธิบัตรผูกขาด ลอกเลียนแบบยาก และเป็นเป้าหมายของกองทุนระยะยาว")

    # คลังหุ้นนวัตกรรมที่มีสิทธิบัตรหนาแน่น
    moat_stocks = {
        "ISRG (Intuitive Surgical)": {
            "ticker": "ISRG",
            "sector": "MedTech / Robotic Surgery",
            "moat": "ผูกขาดตลาดหุ่นยนต์ผ่าตัด da Vinci สิทธิบัตรนับพันฉบับ และรายได้ประจำ (Recurring Revenue) จากอุปกรณ์ใช้แล้วทิ้ง",
            "outlook": "สังคมผู้สูงอายุทั่วโลกผลักดันให้โรงพยาบาลต้องซื้อระบบหุ่นยนต์เพิ่มขึ้นต่อเนื่อง"
        },
        "FLNC (Fluence Energy)": {
            "ticker": "FLNC",
            "sector": "Grid Energy Storage & AI Infrastructure",
            "moat": "เจ้าตลาดระบบกักเก็บพลังงานแบตเตอรี่ (BESS) และซอฟต์แวร์บริหารจัดการกริดอัจฉริยะ แก้คอขวดให้ AI Data Center",
            "outlook": "ได้อานิสงส์เต็มๆ จากการบูมของดาต้าเซ็นเตอร์ที่ต้องการพลังงานเสถียร 24 ชั่วโมง"
        },
        "NVDA (NVIDIA)": {
            "ticker": "NVDA",
            "sector": "AI Computing & Physical AI",
            "moat": "ผูกขาดทั้งฮาร์ดแวร์ชิป AI และซอฟต์แวร์ CUDA ที่นักพัฒนาทั่วโลกต้องพึ่งพา รวมถึงสิทธิบัตรสถาปัตยกรรมชิปขั้นสูง",
            "outlook": "ครองส่วนแบ่งตลาดโครงสร้างพื้นฐาน AI ของโลกอย่างไร้คู่แข่งในระยะกลาง"
        },
        "ASML (ASML Holding)": {
            "ticker": "ASML",
            "sector": "Semiconductor Lithography",
            "moat": "ผู้ผลิตเครื่องพิมพ์เวเฟอร์ Extreme Ultraviolet (EUV) รายเดียวในโลกที่สร้างชิปไฮend ได้ ไม่มีใครแทนที่ได้",
            "outlook": "คอขวดสำคัญที่สุดของห่วงโซ่อุปทานชิปโลก ใครจะผลิตชิปเบอร์เล็กต้องง้อ ASML"
        }
    }

    selected_stock_name = st.selectbox("เลือกบริษัทนวัตกรรมที่ต้องการส่องงบและสิทธิบัตร:", list(moat_stocks.keys()))
    info_dict = moat_stocks[selected_stock_name]
    ticker_symbol = info_dict["ticker"]

    st.markdown(f"### 📌 ภาพรวมและกำแพงสิทธิบัตรของ **{selected_stock_name}**")
    st.success(f"**ประเภท Sector:** {info_dict['sector']}\n\n**IP Moat (ความได้เปรียบทางสิทธิบัตร):** {info_dict['moat']}\n\n**มุมมองอนาคต:** {info_dict['outlook']}")

    # ดึงข้อมูลเชิงงบการเงินและราคาจาก yfinance
    tk = yf.Ticker(ticker_symbol)
    fin_info = tk.info

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", f"${fin_info.get('marketCap', 0):,}" if fin_info.get('marketCap') else "N/A")
    col2.metric("Trailing P/E", f"{fin_info.get('trailingPE', 'N/A')}")
    col3.metric("Profit Margin", f"{fin_info.get('profitMargins', 0)*100:.2f}%" if fin_info.get('profitMargins') else "N/A")
    col4.metric("ROE", f"{fin_info.get('returnOnEquity', 0)*100:.2f}%" if fin_info.get('returnOnEquity') else "N/A")

    st.markdown("---")
    st.markdown(f"### 📈 กราฟราคาหุ้นรอบใหญ่ย้อนหลัง 2 ปีของ `{ticker_symbol}` (ส่องจังหวะสมาร์ทมันนี่สะสมของ)")
    
    df_hist = yf.download(ticker_symbol, period="2y", auto_adjust=True)
    if not df_hist.empty:
        if isinstance(df_hist.columns, pd.MultiIndex):
            df_hist = df_hist.xs(ticker_symbol, axis=1, level=1) if ticker_symbol in df_hist.columns.levels[1] else df_hist

        fig_stock = px.line(df_hist, x=df_hist.index, y='Close', title=f"Price Action & Trend: {ticker_symbol}")
        fig_stock.update_layout(template="plotly_dark", xaxis_title="วันที่", yaxis_title="ราคา (USD)")
        st.plotly_chart(fig_stock, use_container_width=True)
    else:
        st.warning("กำลังดึงข้อมูลกราฟ...")

# --- โหมดที่ 2: สแกนรอบเงินทุน & ข่าวสารเปลี่ยนโลก (Sector Swing) ---
else:
    st.title("📊 สแกนรอบเงินทุนมหภาค & ข่าวสารขับเคลื่อนตลาด (Sector Swing)")
    st.markdown("ติดตามการไหลเวียนของเงินทุนใน Sector หลัก เพื่อดูว่ากองทุนกำลังหมุนเงิน (Sector Rotation) ไปเล่นรอบที่กลุ่มไหนตามกระแสข่าวโลก")

    macro_sectors = {
        "Technology / AI Infrastructure (XLK)": "XLK",
        "Healthcare / MedTech (XLV)": "XLV",
        "Industrials & Grid (XLI)": "XLI",
        "Energy & Nuclear/BESS (XLE)": "XLE",
        "Gold / Safe Haven (GC=F)": "GC=F",
        "Bitcoin / Liquidity Sponge (BTC-USD)": "BTC-USD"
    }

    @st.cache_data(ttl=3600)
    def fetch_sector_rotation(sectors_dict):
        data_frames = {}
        for name, symbol in sectors_dict.items():
            df = yf.download(symbol, period="1y", auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df
                # คำนวณ % Return สะสมในรอบ 1 ปี เพื่อดูความแรงของรอบปัจจุบัน
                data_frames[name] = ((df['Close'] / df['Close'].iloc[0]) - 1) * 100
        return pd.DataFrame(data_frames)

    with st.spinner("กำลังสแกนทิศทางเงินทุนราย Sector..."):
        df_sec = fetch_sector_rotation(macro_sectors)

    if not df_sec.empty:
        fig_sec = px.line(df_sec, title="Sector Rotation Momentum (1-Year Return %)")
        fig_sec.update_layout(
            template="plotly_dark",
            xaxis_title="วันที่",
            yaxis_title="ผลตอบแทนสะสมเทียบจุดเริ่มต้น (%)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
            margin=dict(b=80)
        )
        st.plotly_chart(fig_sec, use_container_width=True)

        st.markdown("### 📋 สรุปโมเมนตัมและทิศทางเงินทุนล่าสุด")
        st.dataframe(df_sec.tail(1).T.rename(columns={df_sec.index[-1]: "Return (%)"}), use_container_width=True)
    else:
        st.error("ไม่สามารถดึงข้อมูล Sector ได้ในขณะนี้")
        
