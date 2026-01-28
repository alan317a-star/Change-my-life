import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="家庭記帳本", layout="centered")
st.title("💰 家庭記帳本")

# --- 1. 記帳輸入區 (直接嵌在 App 裡，不用跳轉) ---
st.subheader("📝 新增一筆")

# [請將下方的網址換成您的 Google 表單網址]
# 記得網址後面要加上 ?embedded=true 這樣才會漂亮
google_form_url = "https://docs.google.com/forms/d/e/https://docs.google.com/spreadsheets/d/10bzPEsIqRdnjTiI9sr6wN9DVTpI7HbikYTNz1UzQ21A/edit?usp=sharing/viewform?embedded=true"

# 使用 iframe 將表單「種」在 App 裡面
components.iframe(google_form_url, height=600, scrolling=True)

# --- 2. 顯示結果區 (Streamlit 負責讀取) ---
st.write("---")
st.subheader("📊 最新記帳紀錄")

conn = st.connection("gsheets", type=GSheetsConnection)

if st.button("🔄 重新整理查看最新紀錄"):
    st.rerun()

try:
    # 讀取 Google 表單產生的那個分頁 (通常叫 "表單回應 1")
    df = conn.read(worksheet="表單回應 1", ttl=0)
    
    if not df.empty:
        # 簡單整理一下顯示順序 (最新的在最上面)
        st.dataframe(df.iloc[::-1], use_container_width=True)
    else:
        st.info("目前還沒有資料")
        
except Exception:
    st.warning("請確認 Google 表單是否已連結到這份試算表，且分頁名稱正確。")

