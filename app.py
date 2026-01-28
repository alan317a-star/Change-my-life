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

# --- CSS 美化 (重點：強制縮減頂部留白 & 左右並排優化) ---
st.markdown("""
    <style>
    /* 1. 暴力縮減網頁頂部留白，讓內容往上衝 */
    .block-container {
        padding-top: 1rem !important; /* 原本是 5rem，改成 1rem */
        padding-bottom: 1rem !important;
    }
    
    /* 2. 輸入框與文字設定 */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }
    div[data-baseweb="select"] > div { background-color: #fff9c4 !important; color: #000000 !important; }
    div[data-baseweb="select"] span { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
    div[data-baseweb="select"] svg { fill: #000000 !important; }
    
    /* 3. 按鈕設定 */
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; border: none; margin-top: 0px; /* 移除上方間距 */
    }
    .save-btn > button { background-color: #FF4B4B; color: white; }
    
    /* 4. 通知視窗優化 */
    div[data-testid="stToast"] {
        width: 95vw !important; max-width: 600px !important;
        background-color: #ffffff !important;
        border-left: 10px solid #FF4B4B !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        border-radius: 8px !important;
        opacity: 1 !important; padding: 15px 20px !important; margin: 10px auto !important;
    }
    div[data-testid="stToast"] p {
        color: #333333 !important; font-size: 18px !important; font-weight: bold !important; margin: 0 !important;
    }
    
    /* 5. 分頁籤與卡片 */
    button[data-baseweb="tab"] div p { font-size: 18px !important; font-weight: bold !important; }
    .card-title { font-size: 16px; font-weight: bold; color: #333; }
    .card-note { font-size: 12px; color: #666; }
    .card-amount { font-size: 18px; font-weight: bold; color: #FF4B4B; text-align: right; }
    
    /* 6. 強制 Metric 指標文字縮小一點，避免在小螢幕換行 */
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 移除大標題 st.title，節省空間
# st.title("Everyday Moments") 

# --- 2. 建立連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 讀取與處理資料 ---
try:
    df = conn.read(worksheet="Expenses", ttl=0)
    if df.empty: df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
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
    if love_days > 0: st.info(f"👩‍❤️‍👨 在一起 **{love_days}** 天")
    
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    if baby_days > 0: st.success(f"👶 承淅 **{baby_days}** 天大了")
    elif baby_days == 0: st.success("🎂 寶寶誕生！")
    else: st.warning(f"👶 還有 **{-baby_days}** 天出生")

    st.write("---")
    st.header("⚙️ 設定")
    monthly_budget = st.number_input("本月預算", value=30000, step=1000)

# --- 🛡️ 錢包防禦戰 (極簡化版) ---
if not df.empty:
    current_month_df = df[df["Month"] == current_month_str]
    current_spent = current_month_df["Amount"].sum()
else:
    current_spent = 0

percent = current_spent / monthly_budget if monthly_budget > 0 else 0
_, last_day_of_month = calendar.monthrange(taiwan_date.year, taiwan_date.month)
days_remaining_in_month = last_day_of_month - taiwan_date.day + 1
remaining_budget = monthly_budget - current_spent
daily_budget = remaining_budget / days_remaining_in_month if days_remaining_in_month > 0 else 0

# 狀態判定
if percent < 0.5: status_text = "🟢 狀態良好"
elif percent < 0.8: status_text = "🟡 遭遇小怪"
elif percent < 1.0: status_text = "🔴 BOSS 戰"
else: status_text = "☠️ 已陣亡"

# === 介面佈局優化 ===
# 1. 第一行：狀態 + 進度條 (緊湊排列)
st.caption(f"🛡️ {status_text} (已花費 {percent:.0%})")
st.progress(min(percent, 1.0))

# 2. 第二行：左右兩欄顯示金額 (強制分開)
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric("剩餘血量", f"${remaining_budget:,.0f}", delta=None)
with col_m2:
    st.metric("今日可用", f"${daily_budget:,.0f}", help="剩餘 ÷ 天數")

# 移除分隔線，讓 Tab 直接貼上來
# st.write("---") 

# --- 📂 分頁切換 (直接緊接在數據下方) ---
tab1, tab2, tab3 = st.tabs(["📝 記帳", "📊 分析", "📋 列表"])

# === 分頁 1: 記帳 ===
with tab1:
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1: date_val = st.date_input("📅 日期", taiwan_date)
        with col2: cat_val = st.selectbox("📂 分類", ["🍔 飲食", "🛒 日用", "🚗 交通", "🏠 居家", "👗 服飾", "💆‍♂️ 醫療", "🎮 娛樂", "📚 教育", "💼 保險", "👶 子女", "💸 其他"])
            
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input("📝 備註")
        
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 儲存") # 按鈕文字簡化
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted:
            if amount_val > 0:
                try:
                    full_timestamp = f"{date_val} {taiwan_now.strftime('%H:%M:%S')}"
                    new_data = pd.DataFrame([{
                        "Date": full_timestamp, "Category": cat_val, "Amount": amount_val, "Note": note_val
                    }])
                    raw_df = conn.read(worksheet="Expenses", ttl=0)
                    updated_df = pd.concat([raw_df, new_data], ignore_index=True)
                    conn.update(worksheet="Expenses", data=updated_df)
                    
                    components.html("<script>window.navigator.vibrate([100,50,100]);</script>", height=0, width=0)
                    
                    st.toast("✅ 記帳成功！\n開始記帳，就是成功的開始！")
                    st.success(f"已存：${amount_val}")
                    
                    time.sleep(1.2)
                    st.rerun()
                except Exception as e:
                    st.error(f"失敗：{e}")
            else:
                st.warning("金額不能為 0")

    with st.expander("↺ 復原上一筆", expanded=False):
        if st.button("確認刪除最後一筆"):
            try:
                raw_df = conn.read(worksheet="Expenses", ttl=0)
                if not raw_df.empty:
                    conn.update(worksheet="Expenses", data=raw_df.iloc[:-1])
                    st.toast("✅ 已刪除")
                    time.sleep(1.2)
                    st.rerun()
            except Exception as e:
                st.error(f"錯誤: {e}")

# === 分頁 2: 分析 ===
with tab2:
    if not df.empty and len(df) > 0:
        available_months = sorted(df["Month"].dropna().unique(), reverse=True)
        selected_month = st.selectbox("月份", ["全部"] + list(available_months))
        plot_df = df if selected_month == "全部" else df[df["Month"] == selected_month]
        total_spent = plot_df["Amount"].sum()
        
        st.metric(f"總支出", f"${total_spent:,.0f}")
        if total_spent > 0:
            pie_data = plot_df.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(pie_data, values="Amount", names="Category", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300) # 圖表縮小邊距
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("無資料")

# === 分頁 3: 列表 ===
with tab3:
    if not df.empty:
        display_df = df[["Date", "Category", "Amount", "Note"]].sort_values("Date", ascending=False)
        for index, row in display_df.head(15).iterrows(): # 為了效能，只顯示前 15 筆
            with st.container(border=True): 
                c1, c2 = st.columns([3, 1]) 
                with c1:
                    st.markdown(f'<div class="card-title">{row["Category"]}</div>', unsafe_allow_html=True)
                    st.caption(f"{row['Date'][5:16]} | {row['Note']}") # 日期只顯示 月-日 時:分
                with c2:
                    st.markdown(f'<div class="card-amount">${row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
