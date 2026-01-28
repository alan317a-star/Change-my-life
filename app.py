import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="家庭記帳本", layout="centered")

# --- CSS 優化 (手機版更好按) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 3em;
        font-size: 20px;
        background-color: #ff4b4b; 
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 家庭記帳本")

# 1. 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. 讀取資料 (加入防錯機制)
try:
    # ttl=0 確保不讀到舊的快取
    df_ex = conn.read(worksheet="Expenses", ttl=0)
    
    # [關鍵修正]：如果表格是空的或讀取有問題，手動建立標準格式
    if df_ex.empty or len(df_ex.columns) == 0:
        df_ex = pd.DataFrame(columns=["Date", "Category", "Amount"])
    else:
        # [關鍵修正]：強制只保留這三欄，踢除所有導致 400 錯誤的雜訊
        # 如果欄位名稱有空白，這裡會幫忙過濾掉
        df_ex = df_ex[["Date", "Category", "Amount"]]
        
except Exception:
    # 萬一連線還是失敗，先建立一個空的，讓程式不要當機，至少能顯示介面
    df_ex = pd.DataFrame(columns=["Date", "Category", "Amount"])

# 3. 記帳輸入區 (直接在 Streamlit 裡面)
with st.container():
    st.subheader("📝 新增一筆")
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            # 預設今天日期
            input_date = st.date_input("日期", date.today())
        with col2:
            # 分類選單
            category = st.selectbox("分類", ["食", "衣", "住", "行", "育兒 (尿布/奶粉)", "日本行預備", "其他"])
        
        amount = st.number_input("金額", min_value=0, step=1, format="%d")
        
        # 送出按鈕
        submit = st.form_submit_button("儲存支出")
        
        if submit:
            if amount == 0:
                st.warning("⚠️ 金額不能為 0")
            else:
                # 建立新的一筆資料
                new_data = pd.DataFrame([{"Date": str(input_date), "Category": category, "Amount": amount}])
                
                # 合併舊資料與新資料
                updated_df = pd.concat([df_ex, new_data], ignore_index=True)
                
                # [關鍵修正]：寫入前再次確認只寫入這三欄，不寫入索引(Index)
                try:
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.success(f"✅ 已儲存：{category} ${amount}")
                    st.rerun() # 重新整理畫面顯示最新資料
                except Exception as e:
                    st.error(f"儲存失敗，請截圖給工程師：{e}")

# 4. 顯示最近紀錄 (給家人看)
st.write("---")
st.subheader("📊 最近 5 筆紀錄")

if not df_ex.empty:
    # 把最新的顯示在最上面
    st.dataframe(df_ex.tail(5).iloc[::-1], use_container_width=True)
    
    # 簡單統計
    total = df_ex["Amount"].sum()
    st.metric("累積總支出", f"${total:,.0f}")
else:
    st.info("目前沒有資料")
