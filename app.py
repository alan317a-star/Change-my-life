import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import requests

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 (iPhone 黑字與卡片樣式優化) ---
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; margin-top: 10px;
    }
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .card-title { font-size: 18px; font-weight: bold; color: #333; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("Everyday Moments")

# --- 2. 建立連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 處理資料 ---
try:
    df = conn.read(worksheet="Expenses", ttl=0)
    if df.empty:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    else:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date_dt"].dt.strftime("%Y-%m")
except Exception:
    st.warning("⚠️ 請檢查 Secrets 設定中的 Google Sheets 金鑰")
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# --- 時間校正 (UTC+8) ---
taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

# --- 4. 側邊欄：手動天氣與紀念日 ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    love_days = (taiwan_date - date(2019, 6, 15)).days
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    
    st.divider()
    st.header("🌤️ 當地天氣")
    # 提供城市切換，完美避開 GPS 崩潰報錯
    location = st.selectbox("切換城市", ["台中西屯", "福岡 (日本)"])
    lat, lon = (24.16, 120.68) if location == "台中西屯" else (33.59, 130.40)
    
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        st.metric(f"{location} 氣溫", f"{w_res['current_weather']['temperature']} °C")
    except:
        st.write("天氣讀取中...")

    st.divider()
    monthly_budget = st.number_input("本月錢包預算", value=30000, step=1000)

# --- 5. 🛡️ 錢包防禦戰 (主介面) ---
current_spent = df[df["Month"] == current_month_str]["Amount"].sum() if not df.empty else 0
remaining = monthly_budget - current_spent
percent = min(current_spent / monthly_budget, 1.0) if monthly_budget > 0 else 0

st.subheader("🛡️ 錢包防禦戰")
col_m1, col_m2 = st.columns([2, 1])
with col_m1:
    st.progress(percent)
    st.caption(f"本月已支出比例: {percent:.1%}")
with col_m2:
    st.metric("剩餘預算", f"${remaining:,.0f}")

st.write("---")

# --- 📂 分頁切換 ---
tab1, tab2, tab3 = st.tabs(["📝 記帳", "📊 分析", "📋 列表"])

with tab1:
    with st.form("entry_form", clear_on_submit=True):
        d_val = st.date_input("📅 日期", taiwan_date)
        c_val = st.selectbox("📂 分類", ["🍔 飲食", "🛒 日用", "🚗 交通", "🇯🇵 旅遊", "👶 子女", "💸 其他"])
        a_val = st.number_input("💲 金額", min_value=0, step=1)
        n_val = st.text_input("📝 備註")
        
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        if st.form_submit_button("💾 儲存紀錄"):
            if a_val > 0:
                new_row = pd.DataFrame([{"Date": str(d_val), "Category": c_val, "Amount": a_val, "Note": n_val}])
                conn.update(worksheet="Expenses", data=pd.concat([conn.read(worksheet="Expenses", ttl=0), new_row], ignore_index=True))
                st.success("✅ 存入雲端成功！")
                time.sleep(1)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if not df.empty and total_spent := df[df["Month"] == current_month_str]["Amount"].sum():
        fig = px.pie(df[df["Month"] == current_month_str], values="Amount", names="Category", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("本月尚無數據可分析")

with tab3:
    st.subheader("📋 最近 15 筆紀錄")
    if not df.empty:
        for _, row in df.sort_values("Date", ascending=False).head(15).iterrows():
            with st.container(border=True):
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f'<div class="card-title">{row["Category"]}</div>', unsafe_allow_html=True)
                    st.caption(f"{row['Date']} | {row['Note']}")
                with col_c2:
                    st.markdown(f'<div class="card-amount">${row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
