import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="簡易記帳測試")

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💰 簡易記帳測試")

# 嘗試讀取 Expenses 分頁
try:
    # ttl=0 確保不使用舊快取，直接向 Google 要資料
    df_ex = conn.read(worksheet="Expenses", ttl=0)
    st.success("✅ 成功連線至 Google 表格！")
except Exception as e:
    st.error(f"❌ 連線失敗，請檢查共用權限或分頁名稱。錯誤訊息: {e}")
    df_ex = pd.DataFrame(columns=["Date", "Category", "Amount"])

# 簡易記帳表單
with st.form("expense_form", clear_on_submit=True):
    amt = st.number_input("輸入測試金額", min_value=0, step=1)
    submit = st.form_submit_button("儲存測試")
    
    if submit:
        new_data = pd.DataFrame([{"Date": str(date.today()), "Category": "測試", "Amount": amt}])
        updated_df = pd.concat([df_ex, new_data], ignore_index=True)
        conn.update(worksheet="Expenses", data=updated_df)
        st.balloons()
        st.success("資料已成功寫入 Google 表格！")
        st.rerun()

st.write("目前表格內容：")
st.dataframe(df_ex)
