import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

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
        note_val = st.text_input("📝 備註 (選填)")
        
        # [修復重點] 確保這一行是完整的，沒有斷掉
        submitted = st.form_submit_button("💾 確認儲存")
        
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
                    updated_df = pd.concat([raw_df, new_data], ignore_index=True)
                    conn.update(worksheet="Expenses", data=updated_df)
                    
                    st.success(f"✅ 已記錄：${amount_val} ({full_timestamp})")
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")
            else:
                st.warning("⚠️ 金額不能為 0")

# --- 5. 圓餅圖分析區 ---
st.write("---")
st.subheader("📊 月份支出分析")

if not df.empty and len(df) > 0:
    available_months = sorted(df["Month"].dropna().unique(), reverse=True)
    if len(available_months) > 0:
        col_filter1, col_filter2 = st.columns([1, 2])
        with col_filter1:
            selected_month = st.selectbox("🗓️ 選擇月份", ["全部"] + list(available_months))
        
        if selected_month == "全部":
            plot_df = df
            chart_title = "📅 所有時間的支出比例"
        else:
            plot_df = df[df["Month"] == selected_month]
            chart_title = f"📅 {selected_month} 支出比例"

        total_spent = plot_df["Amount"].sum()
        with col_filter2:
            st.metric("總支出", f"${total_spent:,.0f}")

        if total_spent > 0:
            pie_data = plot_df.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(pie_data, values="Amount", names="Category", title=chart_title, hole=0.4)
            # [修復重點] 這裡的括號已經補上，圓餅圖不會再報錯了
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("查無此月份資料")
else:
    st.info("尚無資料")

# --- 6. 詳細列表 ---
st.write("---")
with st.expander("📋 查看詳細紀錄列表", expanded=True):
    if not df.empty:
        display_df = df[["Date", "Category", "Amount", "Note"]].sort_values("Date", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
