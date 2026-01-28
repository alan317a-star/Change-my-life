import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 ---
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
        df["Note"] = df["Note"].fillna("")
except Exception:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# --- 時間校正 ---
taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

# --- ⏳ 側邊欄 ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    love_start = date(2019, 6, 15)
    love_days = (taiwan_date - love_start).days
    if love_days > 0:
        st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    
    baby_born = date(2025, 9, 12)
    baby_days = (taiwan_date - baby_born).days
    if baby_days > 0:
        st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    elif baby_days == 0:
        st.success("🎂 就是今天！寶寶誕生啦！")
    else:
        st.warning(f"👶 距離寶寶出生還有 **{-baby_days}** 天")

    st.write("---")
    st.header("⚙️ 遊戲設定 (預算)")
    monthly_budget = st.number_input("本月錢包總血量 (預算)", value=30000, step=1000)

# --- 🛡️ 錢包防禦戰 ---
if not df.empty:
    current_month_df = df[df["Month"] == current_month_str]
    current_spent = current_month_df["Amount"].sum()
else:
    current_spent = 0

if monthly_budget > 0:
    percent = current_spent / monthly_budget
else:
    percent = 0

st.subheader(f"🛡️ 錢包防禦戰")

_, last_day_of_month = calendar.monthrange(taiwan_date.year, taiwan_date.month)
days_remaining_in_month = last_day_of_month - taiwan_date.day + 1
remaining_budget = monthly_budget - current_spent
daily_budget = remaining_budget / days_remaining_in_month if days_remaining_in_month > 0 else 0

col_bar1, col_bar2, col_bar3 = st.columns([2, 1, 1])

with col_bar1:
    if percent < 0.5:
        status_text = "🟢 勇者狀態良好！"
    elif percent < 0.8:
        status_text = "🟡 遭遇小怪，受傷中..."
    elif percent < 1.0:
        status_text = "🔴 BOSS 戰預警！告急！"
    else:
        status_text = "☠️ 錢包已陣亡"
    st.markdown(f'<div class="game-status">{status_text}</div>', unsafe_allow_html=True)
    display_percent = min(percent, 1.0)
    st.progress(display_percent)

with col_bar2:
    st.metric("剩餘血量", f"${remaining_budget:,.0f}", delta=f"-${current_spent:,.0f}", delta_color="inverse")

with col_bar3:
    st.metric("📅 今日可用", f"${daily_budget:,.0f}", help="剩餘預算 ÷ 本月剩餘天數")

st.write("---")

# --- 📂 分頁切換 ---
tab1, tab2, tab3 = st.tabs(["📝 記帳", "📊 分析", "📋 列表"])

# === 分頁 1: 記帳 ===
with tab1:
    st.markdown("### 😈 小壞蛋，錢要花的值得！")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("📅 日期", taiwan_date)
        with col2:
            cat_val = st.selectbox("📂 分類", [
                "🍔 飲食 (三餐/飲料)",
                "🛒 日用 (超市/藥妝)",
                "🚗 交通 (車票/加油)",
                "🏠 居家 (房貸/水電)",
                "👗 服飾 (衣物/鞋包)",
                "💆‍♂️ 醫療 (看診/藥品)",
                "🎮 娛樂 (電影/旅遊/遊戲)",
                "📚 教育 (書籍/課程)",
                "💼 保險稅務",
                "👶 子女 (尿布/學費)", 
                "💸 其他"
            ])
            
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input("📝 備註 (詳細記錄謝謝❗ )")
        
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 確認儲存")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted:
            if amount_val > 0:
                try:
                    current_time_str = taiwan_now.strftime("%H:%M:%S")
                    full_timestamp = f"{date_val} {current_time_str}"

                    new_data = pd.DataFrame([{
                        "Date": full_timestamp, 
                        "Category": cat_val, 
                        "Amount": amount_val, 
                        "Note": note_val
                    }])
                    
                    raw_df = conn.read(worksheet="Expenses", ttl=0)
                    updated_df = pd.concat([raw_
