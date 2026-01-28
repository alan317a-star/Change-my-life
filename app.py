import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

# --- 1. 頁面設定 (修改點：瀏覽器標題) ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stSelectbox, .stDateInput { font-size: 18px !important; }
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; border: none; margin-top: 10px;
    }
    /* 綠色確認按鈕 */
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .save-btn > button:hover { background-color: #E03A3A; color: white; }
    
    /* 灰色刪除按鈕 */
    .del-btn > button { background-color: #6c757d; color: white; }
    .del-btn > button:hover { background-color: #5a6268; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- (修改點：主標題) ---
st.title("Everyday Moments")

# --- 2. 建立連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 讀取與處理資料 ---
try:
    df = conn.read(worksheet="Expenses", ttl=0)
    if df.empty:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    else:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date_dt"].dt.strftime("%Y-%m")
        df["Note"] = df["Note"].fillna("")
except Exception:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# --- 時間校正 (台灣時區 UTC+8) ---
taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()

# --- 4. 記帳輸入區 ---
with st.expander("📝 新增一筆支出", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("📅 日期", taiwan_date)
        with col2:
            cat_val = st.selectbox("📂 分類", [
                "👶 育兒 (尿布/奶粉)", "✈️ 日本行 (機票/住宿)", "🍣 日本行 (吃喝玩樂)", 
                "🚗 交通/加油", "🏠 家用雜支", "👔 個人/治裝", "💰 其他"
            ])
            
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input
