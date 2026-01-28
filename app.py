import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import requests
from streamlit_js_eval import get_geolocation

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 (包含 iPhone 黑字優化與卡片樣式) ---
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
    }
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 20px !important; font-weight: bold;
        border-radius: 10px; background-color: #FF4B4B; color: white;
    }
    .card-container {
        border: 1px solid #eee; border-radius: 10px; padding: 15px;
        margin-bottom: 10px; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .card-title { font-size: 18px; font-weight: bold; color: #333; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 建立連線與資料處理 ---
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(worksheet="Expenses", ttl=0)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date_dt"].dt.strftime("%Y-%m")
except:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# 時間校正
taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()

# --- 🌤️ 天氣函式 ---
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=5).json()
        temp = res['current_weather']['temperature']
        return f"🌡️ {temp}°C"
    except:
        return "N/A"

# --- ⏳ 側邊欄：GPS 與 重要時刻 ---
with st.sidebar:
    st.header("📍 目前位置")
    # 雲端修正：使用 checkbox 確保手機瀏覽器能正確觸發 GPS 授權
    enable_gps = st.checkbox("開啟定位偵測", value=True)
    
    weather_text = "偵測中..."
    location_name = "偵測中"
    
    if enable_gps:
        loc = get_geolocation()
        if loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            location_name = "📍 您的位置"
            weather_text = get_weather(lat, lon)
        else:
            # GPS 抓不到時，預設顯示台中西屯天氣
            location_name = "🏠 台中西屯 (預設)"
            weather_text = get_weather(24.16, 120.68)
            st.caption("提示：若想定位，請點選瀏覽器「允許位置存取」")
    
    st.metric(location_name, weather_text)
    
    st.divider()
    st.header("⏳ 重要時刻")
    love_days = (taiwan_date - date(2019, 6, 15)).days
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    
    st.info(f"👩‍❤️‍👨 在一起 **{love_days}** 天")
    st.success(f"👶 承淅來到地球 **{baby_days}** 天")
    
    st.divider()
    monthly_budget = st.number_input("本月預算", value=30000, step=1000)

# --- 🛡️ 錢包防禦戰 (主畫面) ---
current_month_spent = df[df["Month"] == taiwan_now.strftime("%Y-%m")]["Amount"].sum() if not df.empty else 0
remaining = monthly_budget - current_month_spent
st.subheader("🛡️ 錢包防禦戰")
col_m1, col_m2 = st.columns(2)
col_m1.metric("剩餘血量", f"${remaining:,.0f}")
col_m2.progress(min(current_month_spent/monthly_budget, 1.0) if monthly_budget > 0 else 0)

# --- 📂 分頁功能 ---
tab1, tab2, tab3 = st.tabs(["📝 記帳", "📊 分析", "📋 列表"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date_v = c1.date_input("日期", taiwan_date)
        cat_v = c2.selectbox("分類", ["🍔 飲食", "🛒 日用", "👶 寶寶", "🚗 交通", "🇯🇵 旅遊", "💸 其他"])
        amt_v = st.number_input("金額", min_value=0, step=1)
        note_v = st.text_input("備註")
        if st.form_submit_button("儲存紀錄"):
            new_row = pd.DataFrame([{"Date": str(date_v), "Category": cat_v, "Amount": amt_v, "Note": note_v}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Expenses", data=updated_df)
            st.success("儲存成功！")
            time.sleep(1)
            st.rerun()

with tab3:
    st.subheader("📋 最近紀錄")
    if not df.empty:
        for _, row in df.sort_values("Date", ascending=False).head(15).iterrows():
            st.markdown(f"""
            <div class="card-container">
                <div style="display: flex; justify-content: space-between;">
                    <span class="card-title">{row['Category']}</span>
                    <span class="card-amount">${row['Amount']:,.0f}</span>
                </div>
                <div class="card-note">{row['Date']} | {row['Note']}</div>
            </div>
            """, unsafe_allow_html=True)
