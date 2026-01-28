import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- 頁面設定 ---
st.set_page_config(page_title="我們的家庭花費", layout="centered")

# --- CSS 美化 (大按鈕、優化排版) ---
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

# --- 建立連線 (使用 Secrets 裡的機器人金鑰) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 記帳輸入區 ---
st.markdown("### 📝 新增一筆支出")

with st.container():
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("📅 日期", date.today())
        with col2:
            cat_val = st.selectbox("📂 分類", [
                "👶 育兒 ", "✈️ 旅遊 (機票/住宿)",  
                "🚗 交通/加油", "🏠 家用雜支", "👔 治裝", "💰 其他"
            ])
            
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input("📝 備註 (選填)")
        
        submitted = st.form_submit_button("💾 確認儲存")
        
        if submitted:
            if amount_val > 0:
                try:
                    # 讀取現有資料
                    df = conn.read(worksheet="Expenses", ttl=0)
                    if df.empty: df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
                    
                    # 建立新資料並寫入
                    new_data = pd.DataFrame([{"Date": str(date_val), "Category": cat_val, "Amount": amount_val, "Note": note_val}])
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.success(f"✅ 已記錄：${amount_val} ({cat_val})")
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")
            else:
                st.warning("⚠️ 金額不能為 0")

# --- 顯示紀錄區 ---
st.write("---")
st.markdown("### 📊 最近 5 筆紀錄")

try:
    df = conn.read(worksheet="Expenses", ttl=0)
    if not df.empty:
        st.dataframe(df.tail(5).iloc[::-1], use_container_width=True, hide_index=True)
        # 計算總金額
        total = pd.to_numeric(df["Amount"], errors='coerce').sum()
        st.metric("累積總支出", f"${total:,.0f}")
    else:
        st.info("目前沒有資料，快記下第一筆吧！")
except:
    st.info("連線中...如果這是第一次使用，請先新增一筆資料。")

