import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import random
import base64
import os

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Everyday Moments", 
    page_icon="icon.png", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- 🍎 專治 iPhone 主畫面圖示 ---
def add_apple_touch_icon(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            apple_touch_icon_html = f"""
            <link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,{encoded_string}">
            <link rel="icon" type="image/png" href="data:image/png;base64,{encoded_string}">
            """
            st.markdown(apple_touch_icon_html, unsafe_allow_html=True)
    except Exception as e:
        pass

add_apple_touch_icon("icon.png")

# --- CSS 優化 ---
st.markdown("""
    <style>
    /* 隱藏預設元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background-color: rgba(0,0,0,0); z-index: 999;}
    
    /* 手機版面調整 */
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 5rem !important;
    }
    
    /* 輸入框與文字 */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        height: 50px !important;
    }
    
    /* 下拉選單 */
    div[data-baseweb="select"] > div {
        background-color: #fff9c4 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        height: 50px !important; 
        align-items: center;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
        font-size: 18px !important; 
    }
    
    /* 按鈕通用 */
    div.stButton > button {
        width: 100%; height: 3.8em; font-size: 20px !important; font-weight: bold;
        border-radius: 15px; border: none; margin-top: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.98); }

    .save-btn > button { background: linear-gradient(135deg, #FF6B6B 0%, #FF4B4B 100%); color: white; }
    .del-btn > button { background-color: #6c757d; color: white; }
    .gift-btn > button { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: white; }
    
    /* 使用按鈕 */
    .use-btn > button { 
        background-color: #4CAF50 !important; 
        color: white !important; 
        height: 100% !important; 
        min-height: 80px !important;
        font-size: 18px !important;
        margin-top: 0px !important;
        border-radius: 12px !important;
    }
    
    /* 信件內容樣式 */
    .letter-box {
        background-color: #fff;
        border: 1px dashed #FF4B4B;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        color: #555;
        margin-top: 10px;
        white-space: pre-wrap;
    }

    /* Toast 通知 */
    div[data-testid="stToast"] { 
        position: fixed !important; top: 50% !important; left: 50% !important;       
        transform: translate(-50%, -50%) !important; 
        width: auto !important; min-width: 300px !important; max-width: 80vw !important;  
        border-radius: 20px !important; background-color: rgba(255, 255, 255, 0.98) !important; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.2) !important; border: 2px solid #FF4B4B !important;
        text-align: center !important; padding: 10px !important; z-index: 999999 !important; 
    }
    div[data-testid="stToast"] * { font-size: 20px !important; color: #000000 !important; justify-content: center !important; }
    
    .game-status { font-size: 20px; font-weight: bold; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 19px; font-weight: bold; color: #2196F3 !important; margin-bottom: 2px; }
    .card-note { font-size: 14px; color: inherit; opacity: 0.8; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; line-height: 1.5; }
    .quote-box { background-color: #f0f2f6; border-left: 5px solid #FF4B4B; padding: 12px; margin-bottom: 15px; border-radius: 8px; font-style: italic; color: #555; text-align: center; font-size: 15px; }
    .footer { text-align: center; font-size: 12px; color: #cccccc; margin-top: 30px; margin-bottom: 20px; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 初始化狀態 ---
if "delete_verify_idx" not in st.session_state: st.session_state["delete_verify_idx"] = None

st.title("Everyday Moments")

# --- 隨機勉勵短語 ---
if "current_quote" not in st.session_state:
    quotes = ["🌱 每一筆省下的錢，都是未來的自由。", "💪 記帳不是為了省錢，而是為了更聰明地花錢。", "✨ 今天的自律，是為了明天的選擇權。", "🧱 財富是像堆積木一樣，一點一點累積起來的。", "🌟 你不理財，財不理你；用心生活，歲月靜好。", "🎯 透過記帳，看見真實的自己。", "🌈 能夠控制慾望的人，才能掌控人生。", "🌻 每一塊錢都有它的使命。", "🚀 投資自己，是報酬率最高的投資。", "❤️ 簡單生活，富足心靈。", "🏡 家的溫暖，建立在安穩的經濟基礎之上。"]
    st.session_state["current_quote"] = random.choice(quotes)
st.markdown(f'<div class="quote-box">{st.session_state["current_quote"]}</div>', unsafe_allow_html=True)

# --- 連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 讀取記帳資料 ---
try:
    df = conn.read(worksheet="Expenses", ttl=600)
    if df.empty: df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    else:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date_dt"].dt.strftime("%Y-%m")
        df["Note"] = df["Note"].fillna("")
except:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    st.toast("⚠️ 連線忙碌中，請稍後再試")

taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

current_spent = df[df["Month"] == current_month_str]["Amount"].sum() if not df.empty else 0
last_month_end = taiwan_date.replace(day=1) - timedelta(days=1)
last_month_spent = df[df["Month"] == last_month_end.strftime("%Y-%m")]["Amount"].sum() if not df.empty else 0

# --- 🔥 連勝計算邏輯 ---
def calculate_streak(df):
    if df.empty: return 0
    dates = df["Date_dt"].dt.date.dropna().unique()
    dates.sort()
    
    if len(dates) == 0: return 0
    
    # 從最新的日期開始往回數
    if dates[-1] != taiwan_date and dates[-1] != (taiwan_date - timedelta(days=1)):
        return 0
        
    check_date = dates[-1]
    streak = 1
    
    for i in range(
