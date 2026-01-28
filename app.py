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
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
    }
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; margin-top: 10px;
    }
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
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
    love_days = (taiwan_date - date(2019, 6, 15)).days
    if love_days > 0: st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    if baby_days > 0: st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    elif baby_days == 0: st.success("🎂 就是今天！寶寶誕生啦！")
    else: st.warning(f"👶 距離寶寶出生還有 **{-baby_days}** 天")

    st.write("---")
    st.header("⚙️ 遊戲設定")
    monthly_budget = st.number_input("本月總預算", value=30000, step=1000)

# --- 🛡️ 錢包防禦戰 ---
current_spent = df[df["Month"] == current_month_str]["Amount"].sum() if not df.empty else 0
percent = (current_spent / monthly_budget) if monthly_budget > 0 else 0

st.subheader(f"🛡️ 錢包防禦戰")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    status = "🟢 狀態良好" if percent < 0.5 else "🟡 注意赤字" if percent < 0.8 else "🔴 警告"
    st.markdown(f"**{status}**")
    st.progress(min(percent, 1.0))
with col2: st.metric("剩餘預算", f"${(monthly_budget - current_spent):,.0f}")
with col3: 
    _, last_day = calendar.monthrange(taiwan_date.year, taiwan_date.month)
    days_left = last_day - taiwan_date.day + 1
    st.metric("今日可用", f"${((monthly_budget - current_spent) / days_left):,.0f}" if days_left > 0 else "$0")

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
        if st.form_submit_button("💾 儲存紀錄"):
            if a_val > 0:
                ts = f"{d_val} {taiwan_now.strftime('%H:%M:%S')}"
                new_row = pd.DataFrame([{"Date": ts, "Category": c_val, "Amount": a_val, "Note": n_val}])
                updated = pd.concat([conn.read(worksheet="Expenses", ttl=0), new_row], ignore_index=True)
                conn.update(worksheet="Expenses", data=updated)
                st.toast("記好囉！辛苦了 ✨")
                time.sleep(1)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# === 分頁 2: 分析 ===
with tab2:
    if not df.empty:
        mon = st.selectbox("🗓️ 選擇月份", ["全部"] + sorted(df["Month"].unique().tolist(), reverse=True))
        pdf = df if mon == "全部" else df[df["Month"] == mon]
        st.metric("總累計支出", f"${pdf['Amount'].sum():,.0f}")
        fig = px.pie(pdf, values="Amount", names="Category", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

# === 分頁 3: 列表 ===
with tab3:
    if not df.empty:
        for _, row in df.sort_values("Date", ascending=False).head(20).iterrows():
            with st.container(border=True):
                cl1, cl2 = st.columns([3, 1])
                cl1.markdown(f"**{row['Category']}** \n<small>{row['Date']} | {row['Note']}</small>", unsafe_allow_html=True)
                cl2.markdown(f"<div class='card-amount'>${row['Amount']:,.0f}</div>", unsafe_allow_html=True)

# 刪除功能 (放在側邊欄下方)
with st.sidebar.expander("🗑️ 刪除最後一筆紀錄"):
    if st.button("確認撤銷最後一筆"):
        raw = conn.read(worksheet="Expenses", ttl=0)
        if not raw.empty:
            conn.update(worksheet="Expenses", data=raw.iloc[:-1])
            st.rerun()
