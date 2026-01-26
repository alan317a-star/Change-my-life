import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="個人小助手", layout="centered")

# 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 側邊欄導覽 ---
page = st.sidebar.selectbox("切換功能", ["📅 每日計畫", "💰 隨手記帳"])

# --- 每日計畫功能 ---
if page == "📅 每日計畫":
    st.header("今日目標達成")
    
    # 讀取現有任務
    df_tasks = conn.read(worksheet="Tasks")
    
    with st.form("task_form"):
        new_task = st.text_input("新增代辦事項")
        submit = st.form_submit_button("加入計畫")
        if submit and new_task:
            new_data = pd.DataFrame([{"Task": new_task, "Status": "未完成"}])
            updated_df = pd.concat([df_tasks, new_data], ignore_index=True)
            conn.update(worksheet="Tasks", data=updated_df)
            st.success("已加入！")
            st.rerun()

    st.write("---")
    st.dataframe(df_tasks) # 顯示清單

# --- 記帳功能 ---
elif page == "💰 隨手記帳":
    st.header("支出紀錄")
    
    with st.form("expense_form"):
        day = st.date_input("日期", date.today())
        cat = st.selectbox("分類", ["食", "衣", "住", "行", "育兒", "轉職準備"])
        amt = st.number_input("金額", min_value=0, step=1)
        submit_ex = st.form_submit_button("儲存這筆支出")
        
        if submit_ex:
            df_ex = conn.read(worksheet="Expenses")
            new_ex = pd.DataFrame([{"Date": str(day), "Category": cat, "Amount": amt}])
            updated_ex = pd.concat([df_ex, new_ex], ignore_index=True)
            conn.update(worksheet="Expenses", data=updated_ex)
            st.success(f"已記錄：{cat} ${amt}")