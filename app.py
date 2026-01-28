import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import time # 引入時間套件，為了讓鼓勵訊息停留一下

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stSelectbox, .stDateInput { font-size: 18px !important; }
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; border: none; margin-top: 10px;
    }
    /* 綠色確認按鈕 */
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .save-btn > button:hover { background-color: #E03A3A; color: white; }
    
    /* 灰色刪除按鈕 */
    .del-btn > button { background-color: #6c757d; color: white; }
    .del-btn > button:hover { background-color: #5a6268; color: white; }
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

# --- 時間校正 (台灣時區 UTC+8) ---
taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()

# --- 4. 記帳輸入區 ---
with st.expander("😈 紅字小壞蛋，錢要花的值得！", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("📅 日期", taiwan_date)
        with col2:
            cat_val = st.selectbox("📂 分類", [
                "🍔 飲食 (三餐/飲料)",
                "🛒 日用 (超市/藥妝)",
                "🚗 交通 (車票/加油)",
                "🏠 居家 (房租/水電/網路)",
                "👗 服飾 (衣物/鞋包)",
                "💆‍♂️ 醫療 (看診/藥品)",
                "🎮 娛樂 (電影/旅遊/遊戲)",
                "📚 教育 (書籍/課程)",
                "💼 保險稅務",
                "👶 子女 (尿布/學費)", 
                "💸 其他"
            ])
            
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input("📝 備註 (選填)")
        
        # 按鈕樣式
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
                    updated_df = pd.concat([raw_df, new_data], ignore_index=True)
                    conn.update(worksheet="Expenses", data=updated_df)
                    
                    # --- 修改點：這裡加入了激勵人心的跳窗通知 ---
                    st.toast("🌈 一切會更好，請繼續努力！", icon="💪")
                    st.success(f"✅ 已記錄：${amount_val}\n\n✨ 一切會更好，請繼續努力！")
                    
                    # 暫停 1.5 秒，讓您有時間看到這句話
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")
            else:
                st.warning("⚠️ 金額不能為 0")

# --- 5. 🗑️ 管理與刪除紀錄 ---
if not df.empty:
    with st.expander("🗑️ 管理與刪除紀錄", expanded=False):
        st.warning("⚠️ 刪除後無法復原，請小心操作")
        
        # 1. 快速刪除最後一筆
        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
        if st.button("↩️ 刪除「最後一筆」紀錄 (Undo)"):
            try:
                raw_df = conn.read(worksheet="Expenses", ttl=0)
                if not raw_df.empty:
                    updated_df = raw_df.iloc[:-1]
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.toast("✅ 已復原 (刪除最後一筆)", icon="↩️")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("已經沒有資料可以刪除了")
            except Exception as e:
                st.error(f"刪除失敗: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 2. 指定刪除
        delete_options = [
            f"{i}: {row['Date']} | {row['Category']} | ${row['Amount']} | {row['Note']}" 
            for i, row in df.iterrows()
        ]
        
        selected_item = st.selectbox("🔍 選擇要刪除的特定紀錄：", ["(請選擇)"] + list(reversed(delete_options)))
        
        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
        if st.button("❌ 確認刪除此筆紀錄"):
            if selected_item != "(請選擇)":
                try:
                    index_to_drop = int(selected_item.split(":")[0])
                    raw_df = conn.read(worksheet="Expenses", ttl=0)
                    updated_df = raw_df.drop(index_to_drop)
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.success(f"✅ 已刪除紀錄：{selected_item}")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"刪除失敗: {e}")
            else:
                st.warning("請先選擇一筆資料")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 圓餅圖分析區 ---
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
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("查無此月份資料")
else:
    st.info("尚無資料")

# --- 7. 詳細列表 ---
st.write("---")
with st.expander("📋 查看詳細紀錄列表", expanded=True):
    if not df.empty:
        display_df = df[["Date", "Category", "Amount", "Note"]].sort_values("Date", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
