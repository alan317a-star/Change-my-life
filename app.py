import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px  # 引入繪圖套件
from datetime import date

# --- 1. 頁面設定 ---
st.set_page_config(page_title="家庭與旅遊帳本", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stSelectbox, .stDateInput { font-size: 18px !important; }
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        background-color: #FF4B4B; color: white; border-radius: 10px; border: none; margin-top: 20px;
    }
    div.stButton > button:hover { background-color: #E03A3A; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 家庭與旅遊帳本")

# --- 2. 建立連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 讀取與處理資料 (關鍵步驟) ---
try:
    df = conn.read(worksheet="Expenses", ttl=0)
    if df.empty:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    else:
        # 【重要】把資料轉成正確格式，才能畫圖
        # 1. 金額轉為數字 (遇到無法轉換的變成 0)
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        # 2. 日期轉為時間格式
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        # 3. 建立一個「月份」欄位 (例如 2024-02) 用來篩選
        df["Month"] = df["Date"].dt.strftime("%Y-%m")
        # 4. 處理空值
        df["Note"] = df["Note"].fillna("")
except Exception:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# --- 4. 記帳輸入區 ---
with st.expander("📝 新增一筆支出", expanded=False): # 用摺疊區塊讓畫面乾淨點
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("📅 日期", date.today())
        with col2:
            cat_val = st.selectbox("📂 分類", [
                "👶 育兒 (尿布/奶粉)", "✈️ 日本行 (機票/住宿)", "🍣 日本行 (吃喝玩樂)", 
                "🚗 交通/加油", "🏠 家用雜支", "👔 個人/治裝", "💰 其他"
            ])
            
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input("📝 備註 (選填)")
        
        submitted = st.form_submit_button("💾 確認儲存")
        
        if submitted:
            if amount_val > 0:
                try:
                    # 寫入時轉回字串處理，避免格式跑掉
                    new_data = pd.DataFrame([{
                        "Date": str(date_val), 
                        "Category": cat_val, 
                        "Amount": amount_val, 
                        "Note": note_val
                    }])
                    
                    # 重新讀取原始資料(避免格式衝突)並合併
                    raw_df = conn.read(worksheet="Expenses", ttl=0)
                    updated_df = pd.concat([raw_df, new_data], ignore_index=True)
                    
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.success(f"✅ 已記錄：${amount_val}")
                    st.rerun()
                except Exception as e:
                    st.error(
