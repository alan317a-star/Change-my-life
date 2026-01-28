import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import requests

# --- GPS 套件 ---
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    st.error("⚠️ 請先安裝 GPS 套件：在終端機輸入 `pip install streamlit-js-eval`")

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 (含卡片優化) ---
st.markdown("""
    <style>
    /* 輸入框與文字設定 (iPhone 黑字優化) */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #fff9c4 !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    div[data-baseweb="select"] svg {
        fill: #000000 !important;
    }
    
    /* 按鈕設定 */
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; border: none; margin-top: 10px;
    }
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .save-btn > button:hover { background-color: #E03A3A; color: white; }
    .del-btn > button { background-color: #6c757d; color: white; }
    .del-btn > button:hover { background-color: #5a6268; color: white; }
    
    /* 進度條文字 */
    .game-status {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    /* 跳窗設定 */
    div[data-testid="stToast"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 90vw !important;
        max-width: 500px !important;
        padding: 15px 25px !important;
        border-radius: 50px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 30px rgba(0,0,0,0.3) !important;
        text-align: center !important;
        z-index: 999999 !important;
        border: 2px solid #FF4B4B !important;
    }
    
    div[data-testid="stToast"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        font-family: sans-serif !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
    }
    
    /* 分頁籤 (Tabs) 字體放大 */
    button[data-baseweb="tab"] div p {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    /* 卡片式列表樣式 */
    .card-title {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }
    .card-note {
        font-size: 14px;
        color: #666;
    }
    .card-amount {
        font-size: 20px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

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
        df["Date_Only"] = df["Date_dt"].dt.date
        df["Note"] = df["Note"].fillna("")
except Exception:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# --- 時間校正 ---
taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

# --- 🌤️ 天氣功能 ---
@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia%2FTaipei"
        response = requests.get(url, timeout=5
