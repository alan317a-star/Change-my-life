import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime, timedelta
import requests
from streamlit_js_eval import get_geolocation

# --- 1. 頁面與樣式設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

st.markdown("""
    <style>
    .card-container {
        border: 1px solid #eee; border-radius: 10px; padding: 15px;
        margin-bottom: 10px; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .card-title { font-size: 18px; font-weight: bold; color: #333; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心計算：重要時刻 ---
taiwan_now = datetime.utcnow() + timedelta(hours=8)
today = taiwan_now.date()
love_days = (today - date(2019, 6, 15)).days
baby_days = (today - date(2025, 9, 12)).days

# --- 3. 天氣函式 ---
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=5).json()
        temp = res['current_weather']['temperature']
        return f"🌡️ {temp}°C"
    except:
        return "N/A"

# --- 4. 側邊欄：重要時刻與穩定版天氣 ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    st.info(f"👩‍❤️‍👨 在一起 **{love_days}** 天")
    st.success(f"👶 承淅來到地球 **{baby_days}** 天")
    
    st.divider()
    
    st.header("📍 定位與天氣")
    # 預設座標：台中西屯區
    default_lat, default_lon = 24.16, 120.68
    
    # 雲端保險：只有點下按鈕才要求 GPS，避免網頁崩潰
    if st.button("更新手機當地天氣"):
        loc = get_geolocation()
        if loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.metric("當前定位氣溫", get_weather(lat, lon))
        else:
            st.warning("正在取得授權，請稍候...")
    else:
        # 預設顯示西屯
        st.metric("🏠 台中西屯 (預設)", get_weather(default_lat, default_lon))
        st.caption("提示：日本旅遊時請點上方按鈕更新當地天氣")

# --- 5. 錢包防禦戰與記帳 (原本功能不變) ---
st.title("🛡️ 錢包防禦戰")
# ... 此處維持您原本的記帳與列表代碼 ...
