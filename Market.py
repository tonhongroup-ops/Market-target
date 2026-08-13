import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Money Rotation & Innovation Radar Pro", layout="wide")

st.title("🧬 Smart Money Rotation & Innovation Radar Pro")
st.markdown("เรดาร์แกะรอยกระแสเงินทุน (Capital Rotation) + ระบบวิเคราะห์ 2 กรณี (Accumulation vs Spike) + เจาะลึกงบการเงินและ Sector น่าเล่นฉบับเซียนหุ้นนวัตกรรม")

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
            
            # --- ตรวจสอบเงื่อนไข 2 กรณี (Accumulation vs Spike) ---
            price_ma20 = close.rolling(20).mean().iloc[-1]
            
            if v_1d > 20 and spread_short_vs_long > 15 and close.iloc[-1] > price_ma20:
                active_conditions.append({
                    "type": "SPIKE",
                    "name": name,
                    "msg": f"🚨 **[กรณีที่ 2: Spike & Momentum]** ตรวจพบวอลุ่มระเบิดใน **{name}**! 1D Vol พุ่งไปที่ `{v_1d}%` (Spread ห่าง `{spread_short_vs_long}%`) — สัญญาณเงินก้อนใหญ่ไล่ล่าราคาตามรอบข่าว/งบการเงิน รีบตามน้ำด่วน!"
                })
            elif v_1m > 5 and v_2m > 0 and abs(spread_short_vs_long) < 10:
                active_conditions.append({
                    "type": "ACCUM",
                    "name": name,
                    "msg": f"📦 **[กรณีที่ 1: Accumulation Phase]** **{name}** กำลังสะสมพลัง (1M: `{v_1m}%`, 2M: `{v_2m}%`) วอลุ่มค่อยๆ ซึมเข้าแบบไม่ตื่นตูม เหมาะกับการทยอยสะสมรอดอบประกาศงบหรือข่าวใหญ่"
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
            
    return plot_data, pd.DataFrame(matrix_data), pd.DataFrame(fundamental_data), active_conditions

with st.spinner('กำลังวิเคราะห์โครงสร้าง Smart Money และเงื่อนไขตลาด...'):
    plot_data, df_matrix, df_fund, conditions = analyze_comprehensive_radar(radar_assets)

# --- 1. Smart Money Condition Banner ---
st.subheader("🎯 Smart Money Executive Matrix (วิเคราะห์ 2 กรณีอัตโนมัติ)")
if conditions:
    for c in conditions[:3]: 
        if c["type"] == "SPIKE":
            st.error(c["msg"])
        else:
            st.info(c["msg"])
else:
    st.markdown("""
    <div style="background-color:#162330; padding:15px; border-radius:8px; border-left: 4px solid #8b949e;">
        💡 <b>สถานะตลาดปัจจุบัน:</b> อยู่ในช่วงรอดูท่าที (Consolidation) ไม่มีสินทรัพย์ไหนเข้าเกณฑ์ Spike หรือ Accumulation ชัดเจน รอจับตาวอลุ่มสัปดาห์นี้
    </div>
    """, unsafe_allow_html=True)

# --- NEW: วิเคราะห์เจาะลึก Sector Valuation & Innovation Moat ฉบับเซียน ---
st.markdown("---")
st.subheader("🔬 Executive Intelligence: วิเคราะห์เจาะลึก Sector และหุ้นนวัตกรรม (สิทธิบัตร & งบการเงิน)")

st.markdown("""
<div style="background-color:#0d1117; border:1px solid #30363d; padding:20px; border-radius:10px;">
    <h4 style="color:#58a6ff; margin-top:0;">📊 สรุปภาพรวม Sector ที่น่าเล่นที่สุดตอนนี้ (อ้างอิงข้อมูล Valuation & EPS ล่าสุด)</h4>
    <p>เพื่อน... จากข้อมูลการเปลี่ยนแปลงของกำไร (EPS Change) และความถูกแพงของ P/E ในตลาดตอนนี้ (ข้อมูล Bloomberg อัปเดต สอดยอดกับพอร์ตสาย Tech & Innovation ของเรา) กูสรุป 3 เซกเตอร์ที่น่าสนใจที่สุดดังนี้:</p>
    
    <ul>
        <li><b>1. Information Technology & Semiconductors (XLK / SMH) — <i>"ของถูกในร่างยักษ์เติบโต"</i></b><br>
            แม้ราคา YTD จะบวกขึ้นมาเด่นชัด แต่สังเกตมั้ยว่า <b>P/E Change ลดลงไปถึง -4.53</b> เพราะกำไร (EPS) โตระเบิดระเบอร์ถึง <b>+47.31%</b>! นี่คือลักษณะของหุ้นนวัตกรรมที่มี "Patent Moat" ชัดเจน กำไรโตเร็วกว่าราคาหุ้น ทำให้มูลค่าความแพง (Valuation) ลดลง <u><b>คำแนะนำ:</b> ย่อตัวคือโอกาสทองในการสะสมหุ้นกลุ่ม AI, หุ่นยนต์, และชิปโครงสร้างพื้นฐาน</u>
        </li>
        <li><b>2. Communication Services & Consumer Discretionary — <i>"หุ้นเติบโตซ่อนมูลค่า"</i></b><br>
            กลุ่มนี้ EPS โตสูงระดับ <b>+26.64%</b> และ <b>+17.41%</b> แต่ P/E หดตัวลงหนักมาก (-4.39 และ -3.45) แสดงว่าตลาดยังกลัวความเสี่ยงระยะสั้น แต่ไส้ในงบการเงินแกร่งจริง <u><b>คำแนะนำ:</b> เหมาะกับการทยอยสะสมหุ้นแพลตฟอร์ม, สื่อสารความเร็วสูง, และระบบคลาวด์</u>
        </li>
        <li><b>3. Energy & Materials (XLB / XLI) — <i>"กลุ่มวัฏจักรที่ได้อานิสงส์ความต้องการใช้โครงสร้างพื้นฐาน"</i></b><br>
            ด้วยอัตราการเติบโตของ EPS สูงถึง <b>+54.67%</b> (Energy) และ <b>+22.86%</b> (Materials) ทำให้ Valuation ถูกลงอย่างเห็นได้ชัด <u><b>คำแนะนำ:</b> เหมาะกับการเล่นรอบตามข่าวสิทธิบัตรวัสดุศาสตร์และพลังงานสะอาด</u>
        </li>
    </ul>
    
    <hr style="border-color:#30363d;">
    <h4 style="color:#f0883e; margin-top:10px;">💡 มุมมองเพื่อนซี้ (Action Strategy สำหรับสายหุ้นนวัตกรรมและสิทธิบัตร):</h4>
    <p>การเล่นหุ้นนวัตกรรมรอบนี้ อย่าดูแค่กราฟเทคนิคเดี่ยวๆ มึงต้องจับตาดู <b>"อัตราการเผาเงิน (Cash Runway)"</b> และ <b>"ความคืบหน้าของสิทธิบัตร (Patent Milestone)"</b> ควบคู่ไปด้วย ตัวไหนที่งบกำไรเริ่มพลิกเป็นบวกและ P/E เริ่มลดลงสวนทางกับราคา (ตามโมเดล Technology ด้านบน) ให้ใช้จังหวะ Volume Accumulation (Case 1) ทยอยเก็บเข้าพอร์ต แล้วรอจังหวะระเบิดของราคา (Case 2) เพื่อทำกำไรเป็นกอบเป็นกำ!</p>
</div>
""", unsafe_allow_html=True)

# --- 2. กราฟเทคนิค ---
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

# --- 3. ตาราง Volume Change ครบทุกระยะ ---
st.subheader("📊 Volume Change Matrix (ครบทุกไทม์เฟรม 1D ถึง 3M สำหรับเทียบนัยยะงบการเงิน)")
if not df_matrix.empty:
    st.dataframe(df_matrix.sort_values(by="Spread (1D vs 1M)", ascending=False), use_container_width=True, hide_index=True)
    st.caption("📌 **ทริควิเคราะห์สไตล์โปร:** ใช้ช่อง 2M และ 3M ดูฐานวอลุ่มเดิมก่อนงบออก เทียบกับช่อง 1D และ Spread เพื่อเช็คว่าทุนกำลังซึมเข้า (Case 1) หรือกำลังระเบิดลากราคา (Case 2)")
else:
    st.warning("กำลังประมวลผลตาราง...")

# --- 4. ตารางพื้นฐาน ---
st.subheader("📋 Fundamental & Valuation Snapshot")
if not df_fund.empty:
    st.dataframe(df_fund.sort_values(by="Current Return (%)", ascending=False), use_container_width=True, hide_index=True)
            
