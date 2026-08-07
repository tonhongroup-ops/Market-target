import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- ตั้งค่าหน้าจอ Streamlit (Config) ---
st.set_page_config(
    page_title="Global Innovation & Patent Smart Money Radar Pro",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme CSS สไตล์นักวิเคราะห์มือโปร ---
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e6edf3; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .pick-box { background-color: #162330; padding: 20px; border-radius: 10px; border: 1px solid #1f6feb; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Innovation, Patent & Smart Money Radar Pro")
st.markdown("เรดาร์ตรวจจับกระแสเงินทุนครบเครื่อง: ตารางครบทุกช่วงเวลา + ฟิลเตอร์สรุปตัวแกร่ง + กราฟ Plotly Interactive ซูมขยายและกดเปิด-ปิดเส้นได้อิสระ")

# --- รวบรวม Sector, Innovation, SET100 ตัวแทน, Gold, Bitcoin ---
radar_assets = {
    "Technology & AI (XLK)": "XLK",
    "Semiconductors / Patent Moat (SMH)": "SMH",
    "Healthcare / Biotech (XLV)": "XLV",
    "Industrials & Smart Grid (XLI)": "XLI",
    "Consumer Discretionary (XLY)": "XLY",
    "Consumer Staples (XLP)": "XLP",
    "Energy & Clean Tech (XLE)": "XLE",
    "Advanced Materials (XLB)": "XLB",
    "Utilities (XLU)": "XLU",
    "SET100 Index (SET.BK)": "^SET.BK",
    "Gold / Safe Haven (GC=F)": "GC=F",
    "Bitcoin / Global Liquidity (BTC-USD)": "BTC-USD"
}

@st.cache_data(ttl=3600)
def fetch_and_normalize_radar(assets_dict):
    table_data = []
    normalized_prices = {} 
    scored_assets = []
    
    for name, symbol in assets_dict.items():
        try:
            df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if 'Close' in df.columns:
                    close_series = df['Close'].dropna()
                    if not close_series.empty and len(close_series) > 1:
                        pct_change_series = ((close_series - close_series.iloc[0]) / close_series.iloc[0]) * 100
                        normalized_prices[name] = pct_change_series
                        
                        sma20 = close_series.rolling(window=20).mean()
                        if not sma20.empty and not pd.isna(sma20.iloc[-1]):
                            current_price = close_series.iloc[-1]
                            price_score = float((current_price - sma20.iloc[-1]) / sma20.iloc[-1] * 100)
                        else:
                            price_score = 0.0

                if 'Volume' in df.columns:
                    vol = df['Volume'].dropna()
                    if len(vol) >= 40:
                        vol_sma20 = vol.rolling(window=20).mean()
                        if not vol_sma20.empty and not pd.isna(vol_sma20.iloc[-1]) and vol_sma20.iloc[-1] > 0:
                            v_latest = float(((vol.iloc[-1] - vol_sma20.iloc[-1]) / vol_sma20.iloc[-1]) * 100)
                            v_3d = float(((vol.iloc[-3:].mean() - vol_sma20.iloc[-3:].mean()) / vol_sma20.iloc[-3:].mean()) * 100)
                            v_1w = float(((vol.iloc[-5:].mean() - vol_sma20.iloc[-5:].mean()) / vol_sma20.iloc[-5:].mean()) * 100)
                            v_2w = float(((vol.iloc[-10:].mean() - vol_sma20.iloc[-10:].mean()) / vol_sma20.iloc[-10:].mean()) * 100)
                            v_1m = float(((vol.iloc[-20:].mean() - vol_sma20.iloc[-20:].mean()) / vol_sma20.iloc[-20:].mean()) * 100)
                            
                            table_data.append({
                                "Sector / Asset": name,
                                "Latest (%)": round(v_latest, 2) if not np.isnan(v_latest) else 0.0,
                                "3 Days (%)": round(v_3d, 2) if not np.isnan(v_3d) else 0.0,
                                "1 Week (%)": round(v_1w, 2) if not np.isnan(v_1w) else 0.0,
                                "2 Weeks (%)": round(v_2w, 2) if not np.isnan(v_2w) else 0.0,
                                "1 Month (%)": round(v_1m, 2) if not np.isnan(v_1m) else 0.0
                            })
                            
                            if v_1w > 0 and price_score > 0 and "Gold" not in name and "Bitcoin" not in name:
                                total_score = v_1w + price_score
                                scored_assets.append({"name": name, "score": total_score})
        except Exception:
            continue
            
    scored_assets = sorted(scored_assets, key=lambda x: x['score'], reverse=True)
    return pd.DataFrame(table_data), normalized_prices, scored_assets

# รันฟังก์ชัน
with st.spinner('กำลังประมวลผลข้อมูลตลาดทั้งหมด...'):
    df_result, price_normalized, strong_picks = fetch_and_normalize_radar(radar_assets)

# --- 1. กล่องสรุปผลคัดกรองตัวที่แข็งแกร่งที่สุดอัตโนมัติ ---
st.markdown("### 🎯 ตัวที่น่าสนใจและแข็งแกร่งที่สุดในรอบนี้ (Filtered Strong Picks)")
st.markdown(f"""
<div class="pick-box">
    <h4>🔥 ผลการคัดกรองตามเงื่อนไข Smart Money Filter:</h4>
    <ul>
        {''.join([f"<li>🏆 <b>{item['name']}</b> (คะแนนความแกร่ง: <code>{item['score']:.2f}</code>) — ผ่านเกณฑ์ Volume ขยายตัวและยืนเหนือเส้นค่าเฉลี่ยอย่างมั่นคง</li>" for item in strong_picks]) if strong_picks else "<li>⚠️ ไม่มีตัวไหนผ่านเกณฑ์ความแข็งแกร่งขั้นสุดในรอบนี้ หรือระบบกำลังดึงข้อมูลสำรอง ตลาดอยู่ในโหมดพักตัว</li>"}
    </ul>
</div>
""", unsafe_allow_html=True)

# --- 2. ตารางข้อมูล Volume Change ---
st.markdown("### 📊 ตารางเปรียบเทียบ % Volume Change ทุกช่วงเวลา")
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # --- 3. กราฟ Plotly Interactive (ซูมได้, เลื่อนช่วงเวลาได้, คลิกเปิด-ปิดเส้นได้) ---
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบทุกสินทรัพย์ (Plotly Interactive: ซูมขยาย / คลิกชื่อด้านล่างเพื่อซ่อน-แสดง)")
    
    if price_normalized:
        df_norm = pd.DataFrame(price_normalized)
        
        if not df_norm.empty:
            df_norm_reset = df_norm.reset_index()
            date_col = df_norm_reset.columns[0]
            df_melted = df_norm_reset.melt(id_vars=[date_col], var_name="Asset", value_name="Performance (%)")
            
            fig = px.line(
                df_melted, 
                x=date_col, 
                y="Performance (%)", 
                color="Asset",
                markers=False
            )
            
            fig.update_layout(
                paper_bgcolor="#0b0f19",
                plot_bgcolor="#161b22",
                font_color="#e6edf3",
                xaxis=dict(
                    showgrid=True, 
                    gridcolor="#30363d",
                    rangeslider=dict(visible=False),
                    type="date"
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor="#30363d", 
                    zeroline=True, 
                    zerolinecolor="#8b949e", 
                    zerolinewidth=2
                ),
                legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
                margin=dict(l=20, r=20, t=30, b=60),
                height=580,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
            st.caption("💡 มึงสามารถใช้เมาส์ลากครอบ (Box Zoom) หรือเลื่อนช่วงเวลาเพื่อซูมดูข้อมูลได้อิสระ คลิกที่ชื่อ Sector ด้านล่างเพื่อซ่อน/แสดงเส้นได้ตามใจชอบ")

else:
    st.warning("⚠️ กำลังดึงข้อมูลจากตลาด ลองกดรีเฟรชที่เบราว์เซอร์อีกทีเพื่อน รอบนี้ครบถ้วนสมบูรณ์แบบแน่นอน!")
    
