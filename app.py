import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime, timedelta
import requests
import time

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- 2. CSS 美化 (iPhone 黑字與卡片樣式優化) ---
st.markdown("""
    <style>
    /* 輸入框黑字優化 */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    /* 卡片式列表樣式 */
    .card-container {
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: white;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .card-title { font-size: 18px; font-weight: bold; color: #333; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
    .card-note { font-size: 14px; color: #666; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 核心計算：重要時刻 ---
# 自動校正為台灣時間 (UTC+8)
taiwan_now = datetime.utcnow() + timedelta(hours=8)
today = taiwan_now.date()
love_days = (today - date(2019, 6, 15)).days
baby_days = (today - date(2025, 9, 12)).days

# --- 4. 側邊欄：手動天氣與紀念日 ---
with st.sidebar:
    st.header("⏳ 重要時刻")
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
        temp = w_res['current_weather']['temperature']
        st.metric(f"{location} 氣溫", f"{temp} °C")
    except:
        st.write("天氣更新中...")

    st.divider()
    monthly_budget = st.number_input("本月錢包總血量 (預算)", value=30000, step=1000)

# --- 5. 主介面：錢包防禦戰 ---
st.title("🛡️ 錢包防禦戰")

# 建立 Google Sheets 連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Expenses", ttl=0)
    
    # 預算進度條
    current_spent = df[pd.to_datetime(df["Date"]).dt.strftime("%Y-%m") == today.strftime("%Y-%m")]["Amount"].sum() if not df.empty else 0
    remaining = monthly_budget - current_spent
    
    col1, col2 = st.columns(2)
    col1.metric("本月剩餘預算", f"${remaining:,.0f}")
    col2.progress(min(current_spent/monthly_budget, 1.0) if monthly_budget > 0 else 0)

except Exception:
    st.warning("⚠️ 請在 Secrets 設定中檢查 Google Sheets 連線金鑰")
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# --- 6. 分頁功能 ---
tab1, tab2 = st.tabs(["📝 快速記帳", "📋 消費清單"])

with tab1:
    with st.form("entry_form", clear_on_submit=True):
        date_v = st.date_input("日期", today)
        cat_v = st.selectbox("分類", ["🍔
