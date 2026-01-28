import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime, timedelta
import requests

# --- 1. 頁面與樣式設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# iPhone 黑字與卡片樣式優化
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

# --- 2. 核心計算：重要時刻 ---
# 自動校正為台灣/日本時間 (UTC+8/9 差異不大，以 +8 為主)
taiwan_now = datetime.utcnow() + timedelta(hours=8)
today = taiwan_now.date()
love_days = (today - date(2019, 6, 15)).days
baby_days = (today - date(2025, 9, 12)).days

# --- 3. 側邊欄：固定天氣與重要時刻 ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    
    st.divider()
    
    st.header("🌤️ 當地天氣")
    # 提供手動切換，避免 GPS 權限報錯
    location = st.radio("切換城市", ["台中西屯", "福岡 (日本)"])
    if location == "台中西屯":
        lat, lon = 24.16, 120.68
    else:
        lat, lon = 33.59, 130.40 # 福岡座標
    
    # 抓取天氣 API
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(w_url, timeout=5).json()
        temp = res['current_weather']['temperature']
        st.metric(f"{location} 氣溫", f"{temp} °C")
    except:
        st.write("天氣連線中...")

    st.divider()
    monthly_budget = st.number_input("本月預算", value=30000, step=1000)

# --- 4. 主介面：錢包防禦戰與記帳 (Google Sheets 連線) ---
st.title("🛡️ 錢包防禦戰")
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(worksheet="Expenses", ttl=0)
    # 這裡加入您原本的記帳、分析與卡片列表程式碼...
    st.success("☁️ 雲端帳本連線正常")
except:
    st.error("⚠️ 請在 Secrets 設定中檢查 Google Sheets 連線密鑰")

# (以下接您原本的 tab1, tab2, tab3 邏輯)
