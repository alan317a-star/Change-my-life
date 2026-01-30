import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import random

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Everyday Moments", 
    page_icon="icon.png",  # <--- 這裡會讀取您上傳的 512x512 貓咪圖片
    layout="centered",
    initial_sidebar_state="expanded" # 側邊欄預設展開，不會收起來
)

# --- 初始化刪除確認狀態 ---
if "delete_verify_idx" not in st.session_state:
    st.session_state["delete_verify_idx"] = None

# --- CSS 極致 APP 化美化 ---
st.markdown("""
    <style>
    /* === 1. 隱藏 Streamlit 預設元素 === */
    #MainMenu {visibility: hidden;} /* 隱藏右上角三個點點選單 */
    footer {visibility: hidden;}    /* 隱藏底部 Made with Streamlit */
    
    /* [重要] 不要完全隱藏 header，改為背景透明 */
    /* 這樣手機左上角的「>」側邊欄按鈕才會出現 */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0); 
        z-index: 1;
    }
    
    /* 隱藏頂部的彩色橫條裝飾 */
    .stApp > header {
        background-color: transparent;
    }
    
    /* === 2. 手機版面調整 === */
    .block-container {
        padding-top: 3rem !important; /* 留空間給頂部按鈕 */
        padding-bottom: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* === 3. 輸入框與文字設定 === */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        height: 50px !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }
    
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
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* === 4. 按鈕設定 === */
    div.stButton > button {
        width: 100%; 
        height: 3.8em;
        font-size: 20px !important; 
        font-weight: bold;
        border-radius: 15px;
        border: none; 
        margin-top: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.98); }

    .save-btn > button { background: linear-gradient(135deg, #FF6B6B 0%, #FF4B4B 100%); color: white; }
    .del-btn > button { background-color: #6c757d; color: white; }
    .stButton > button[kind="secondary"] { 
        height: 100% !important; 
        margin-top: 0px !important; 
        font-size: 18px !important; 
        background-color: #f1f3f5 !important; 
        border: 1px solid #dee2e6 !important; 
        color: #495057 !important;
        border-radius: 10px !important;
    }
    
    /* === 5. 其他元件優化 === */
    .game-status { font-size: 20px; font-weight: bold; margin-bottom: 5px; text-align: center; }
    
    /* Toast 通知 */
    div[data-testid="stToast"] { 
        top: 10% !important; 
        left: 50% !important; 
        transform: translate(-50%, 0) !important; 
        width: 90vw !important; 
        border-radius: 50px !important; 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important; 
        border: 1px solid #FF4B4B !important;
    }
    div[data-testid="stToast"] * { font-size: 18px !important; color: #000000 !important; }
    
    /* 卡片樣式 */
    .card-title { font-size: 19px; font-weight: bold; color: #2196F3 !important; margin-bottom: 2px; }
    .card-note { font-size: 14px; color: inherit; opacity: 0.8; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; line-height: 1.5; }
    
    /* 金句樣式 */
    .quote-box { background-color: #f0f2f6; border-left: 5px solid #FF4B4B; padding: 12px; margin-bottom: 15px; border-radius: 8px; font-style: italic; color: #555; text-align: center; font-size: 15px; }
    .footer { text-align: center; font-size: 12px; color: #cccccc; margin-top: 30px; margin-bottom: 20px; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("Everyday Moments")

# --- 隨機勉勵短語 (固定 Session) ---
if "current_quote" not in st.session_state:
    quotes = [
        "🌱 每一筆省下的錢，都是未來的自由。", "💪 記帳不是為了省錢，而是為了更聰明地花錢。", "✨ 今天的自律，是為了明天的選擇權。",
        "🧱 財富是像堆積木一樣，一點一點累積起來的。", "🌟 你不理財，財不理你；用心生活，歲月靜好。", "🎯 透過記帳，看見真實的自己。",
        "🌈 能夠控制慾望的人，才能掌控人生。", "🌻 每一塊錢都有它的使命，別讓它白白流失。", "🚀 投資自己，是報酬率最高的投資。",
        "❤️ 簡單生活，富足心靈。", "💧 涓涓細流，終成大海；小錢不省，大錢難留。", "🛑 想要不等於需要，下單前多想三秒鐘。",
        "📅 記帳是給未來的自己一封情書。", "⚖️ 理財就是理生活，平衡才是王道。", "🗝️ 財富不是人生的目的，而是實現夢想的工具。",
        "🦁 省錢不需要像苦行僧，只需要像獵人一樣精準。", "⏳ 時間就是金錢，善用每一分資源。", "🛡️ 建立緊急預備金，是給生活穿上防彈衣。",
        "👣 千里之行，始於足下；百萬資產，始於記帳。", "🚫 遠離精緻窮，擁抱踏實富。", "💎 真正的富有，是擁有支配時間的權利。",
        "🧘‍♀️ 心若富足，生活處處是寶藏。", "📈 每天進步 1%，一年後你會感謝現在的自己。", "🌤️ 存錢不是為了過苦日子，而是為了迎接好日子。",
        "🔍 記帳不只是紀錄數字，更是檢視生活軌跡。", "🎁 最好的禮物，是一個無後顧之憂的未來。", "🚦 克制一時的衝動，換來長久的安穩。",
        "🧠 投資大腦，永遠不會虧損。", "🕊️ 財務自由的第一步，從了解你的現金流開始。", "🏡 家的溫暖，建立在安穩的經濟基礎之上。"
    ]
    st.session_state["current_quote"] = random.choice(quotes)
st.markdown(f'<div class="quote-box">{st.session_state["current_quote"]}</div>', unsafe_allow_html=True)

# --- 連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 讀取資料 (極速快取模式 TTL=600) ---
try:
    df = conn.read(worksheet="Expenses", ttl=600)
    
    if df.empty:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    else:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date_dt"].dt.strftime("%Y-%m")
        df["Note"] = df["Note"].fillna("")
except Exception:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    st.toast("⚠️ 連線忙碌中，請稍後再試")

taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

current_spent = 0
last_month_spent = 0
if not df.empty:
    current_spent = df[df["Month"] == current_month_str]["Amount"].sum()
    first_day_current = taiwan_date.replace(day=1)
    last_month_end = first_day_current - timedelta(days=1)
    last_month_str = last_month_end.strftime("%Y-%m")
    last_month_spent = df[df["Month"] == last_month_str]["Amount"].sum()

# --- 側邊欄 (保持展開) ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    love_days = (taiwan_date - date(2019, 6, 15)).days
    if love_days > 0: st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    if baby_days > 0: st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    elif baby_days == 0: st.success("🎂 就是今天！寶寶誕生啦！")
    else: st.warning(f"👶 距離寶寶出生還有 **{-baby_days}** 天")
    st.write("---")

    st.header("📊 帳務概況")
    diff = current_spent - last_month_spent
    delta_label = f"比上月{'多' if diff > 0 else '少'}花 ${abs(diff):,.0f}"
    st.metric(label="💸 本月已花費", value=f"${current_spent:,.0f}", delta=delta_label, delta_color="inverse")
    
    st.write("") 
    st.markdown("##### 📜 歷史查詢")
    if not df.empty:
        month_options = ["🏆 歷史總花費"] + sorted(df["Month"].dropna().unique().tolist(), reverse=True)
        selected_query = st.selectbox("選擇月份", month_options, label_visibility="collapsed")
        if selected_query == "🏆 歷史總花費":
            query_amount = df["Amount"].sum()
            query_label = "累積總支出"
        else:
            query_amount = df[df["Month"] == selected_query]["Amount"].sum()
            query_label = f"{selected_query} 總支出"
        st.info(f"{query_label}: **${query_amount:,.0f}**")
    else: st.caption("尚無歷史資料")
