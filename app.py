import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import random

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    /* 輸入框與文字設定 */
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
    
    /* 按鈕設定 */
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; border: none; margin-top: 10px;
    }
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .save-btn > button:hover { background-color: #E03A3A; color: white; }
    .del-btn > button { background-color: #6c757d; color: white; }
    .del-btn > button:hover { background-color: #5a6268; color: white; }
    
    /* 列表垃圾桶小按鈕 */
    .stButton > button[kind="secondary"] {
        height: 100% !important;
        margin-top: 0px !important;
        font-size: 16px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #ddd !important;
        color: #666 !important;
    }

    .game-status { font-size: 20px; font-weight: bold; margin-bottom: 5px; }

    /* Toast 樣式 */
    div[data-testid="stToast"] {
        position: fixed !important; top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important; width: 90vw !important;
        max-width: 500px !important; border-radius: 50px !important;
        background-color: #ffffff !important; box-shadow: 0 4px 30px rgba(0,0,0,0.3) !important;
        text-align: center !important; z-index: 999999 !important; border: 2px solid #FF4B4B !important;
    }
    div[data-testid="stToast"] * { color: #000000 !important; font-size: 20px !important; font-weight: bold !important; }
    
    .card-title { font-size: 18px; font-weight: bold; color: #333; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
    
    /* 金句樣式 */
    .quote-box {
        background-color: #f0f2f6;
        border-left: 5px solid #FF4B4B;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 5px;
        font-style: italic;
        color: #555;
        text-align: center;
        font-size: 16px;
    }
    
    /* 底部作者署名樣式 */
    .footer {
        text-align: center;
        font-size: 14px;
        color: #aaaaaa;
        margin-top: 50px;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Everyday Moments")

# --- 隨機勉勵短語 (30句) ---
quotes = [
    "🌱 每一筆省下的錢，都是未來的自由。", "💪 記帳不是為了省錢，而是為了更聰明地花錢。",
    "✨ 今天的自律，是為了明天的選擇權。", "🧱 財富是像堆積木一樣，一點一點累積起來的。",
    "🌟 你不理財，財不理你；用心生活，歲月靜好。", "🎯 透過記帳，看見真實的自己。",
    "🌈 能夠控制慾望的人，才能掌控人生。", "🌻 每一塊錢都有它的使命，別讓它白白流失。",
    "🚀 投資自己，是報酬率最高的投資。", "❤️ 簡單生活，富足心靈。",
    "💧 涓涓細流，終成大海；小錢不省，大錢難留。", "🛑 想要不等於需要，下單前多想三秒鐘。",
    "📅 記帳是給未來的自己一封情書。", "⚖️ 理財就是理生活，平衡才是王道。",
    "🗝️ 財富不是人生的目的，而是實現夢想的工具。", "🦁 省錢不需要像苦行僧，只需要像獵人一樣精準。",
    "⏳ 時間就是金錢，善用每一分資源。", "🛡️ 建立緊急預備金，是給生活穿上防彈衣。",
    "👣 千里之行，始於足下；百萬資產，始於記帳。", "🚫 遠離精緻窮，擁抱踏實富。",
    "💎 真正的富有，是擁有支配時間的權利。", "🧘‍♀️ 心若富足，生活處處是寶藏。",
    "📈 每天進步 1%，一年後你會感謝現在的自己。", "🌤️ 存錢不是為了過苦日子，而是為了迎接好日子。",
    "🔍 記帳不只是紀錄數字，更是檢視生活軌跡。", "🎁 最好的禮物，是一個無後顧之憂的未來。",
    "🚦 克制一時的衝動，換來長久的安穩。", "🧠 投資大腦，永遠不會虧損。",
    "🕊️ 財務自由的第一步，從了解你的現金流開始。", "🏡 家的溫暖，建立在安穩的經濟基礎之上。"
]
selected_quote = random.choice(quotes)
st.markdown(f'<div class="quote-box">{selected_quote}</div>', unsafe_allow_html=True)

# --- 2. 建立連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 讀取資料 ---
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

taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

# --- 計算花費邏輯 (本月 & 上月比較) ---
current_spent = 0
last_month_spent = 0
total_all_time = 0

if not df.empty:
    # 本月花費
    current_spent = df[df["Month"] == current_month_str]["Amount"].sum()
    
    # 歷史總花費
    total_all_time = df["Amount"].sum()
    
    # 計算上個月的月份字串
    first_day_current = taiwan_date.replace(day=1)
    last_month_end = first_day_current - timedelta(days=1)
    last_month_str = last_month_end.strftime("%Y-%m")
    
    # 上月花費
    last_month_spent = df[df["Month"] == last_month_str]["Amount"].sum()

# --- 側邊欄 ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    love_days = (taiwan_date - date(2019, 6, 15)).days
    if love_days > 0: st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    if baby_days > 0: st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    elif baby_days == 0: st.success("🎂 就是今天！寶寶誕生啦！")
    else: st.warning(f"👶 距離寶寶出生還有 **{-baby_days}** 天")

    st.write("---")
    
    # === 錢包狀態 (含上月比較) ===
    st.header("💰 錢包狀態")
    monthly_budget = st.number_input("本月預算 (血量)", value=30000, step=1000)
    
    # 計算與上個月的差額
    diff = current_spent - last_month_spent
    delta_label = f"比上月{'多' if diff > 0 else '少'}花 ${abs(diff):,.0f}"
    
    # 顯示指標
    st.metric(
        label="💸 本月已花費", 
        value=f"${current_spent:,.0f}", 
        delta=delta_label,
        delta_color="inverse" 
    )
    st.caption(f"📅 上月同期花費：${last_month_spent:,.0f}")
    
# --- 🛡️ 錢包防禦戰 ---
percent = current_spent / monthly_budget if monthly_budget > 0 else 0
remaining = monthly_budget - current_spent
_, last_day = calendar.monthrange(taiwan_date.year, taiwan_date.month)
days_left = last_day - taiwan_date.day + 1
daily_budget = remaining / days_left if days_left > 0 else 0

st.subheader("🛡️ 錢包防禦戰")
c_b1, c_b2, c_b3 = st.columns([2, 1, 1])

with c_b1:
    if percent < 0.3: status_text = "🏆 黃金理財大師 (狀態絕佳)"
    elif percent < 0.6: status_text = "🛡️ 白銀防禦騎士 (穩健前行)"
    elif percent < 0.9: status_text = "⚔️ 青銅奮戰勇者 (遭遇苦戰)"
    elif percent < 1.0: status_text = "🔴 紅色警戒兵 (瀕臨極限)"
    else: status_text = "☠️ 骷髏錢包 (任務失敗)"
        
    st.markdown(f'<div class="game-status">{status_text}</div>', unsafe_allow_html=True)
    st.progress(min(percent, 1.0))

with c_b2: st.metric("剩餘血量", f"${remaining:,.0f}")
with c_b3: st.metric("📅 今日可用", f"${daily_budget:,.0f}")

st.write("---")

tab1, tab2, tab3 = st.tabs(["📝 記帳", "📊 分析", "📋 列表"])

# === Tab 1: 記帳 ===
with tab1:
    st.markdown("### 😈 每一筆錢都要花得值得！")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1: date_val = st.date_input("📅 日期", taiwan_date)
        with col2: cat_val = st.selectbox("📂 分類", ["🍔 飲食 (三餐/飲料)", "🛒 日用 (超市/藥妝)", "🚗 交通 (車票/加油)", "🏠 居家 (房貸/水電)", "👗 服飾 (衣物/鞋包)", "💆‍♂️ 醫療 (看診/藥品)", "🎮 娛樂 (旅遊/遊戲)", "📚 教育 (書籍/課程)", "💼 保險稅務", "👶 子女 (尿布/學費)", "💸 其他"])
        amount_val = st.number_input("💲 金額", min_value=0, step=10, format="%d")
        note_val = st.text_input("📝 備註")
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 確認儲存")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted:
            if amount_val > 0:
                try:
                    new_row = pd.DataFrame([{"Date": f"{date_val} {taiwan_now.strftime('%H:%M:%S')}", "Category": cat_val, "Amount": amount_val, "Note": note_val}])
                    raw_df = conn.read(worksheet="Expenses", ttl=0)
                    conn.update(worksheet="Expenses", data=pd.concat([raw_df, new_row], ignore_index=True))
                    st.toast("✨ 記帳完成！成功的開始")
                    time.sleep(1); st.rerun()
                except Exception as e: st.error(f"錯誤：{e}")

    with st.expander("記錯帳按這邊 (快速復原)", expanded=False):
        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
        if st.button("↩️ 刪除最後一筆紀錄 (Undo)"):
            try:
                raw_df = conn.read(worksheet="Expenses", ttl=0)
                if not raw_df.empty:
                    conn.update(worksheet="Expenses", data=raw_df.iloc[:-1])
                    st.toast("已刪除最後一筆紀錄")
                    time.sleep(1); st.rerun()
            except Exception as e: st.error(f"刪除失敗: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# === Tab 2: 分析 ===
with tab2:
    if not df.empty:
        selected_month = st.selectbox("🗓️ 選擇月份", ["全部"] + sorted(df["Month"].dropna().unique(), reverse=True))
        plot_df = df if selected_month == "全部" else df[df["Month"] == selected_month]
        st.metric(f"總支出", f"${plot_df['Amount'].sum():,.0f}")
        if not plot_df.empty:
            fig = px.pie(plot_df.groupby("Category")["Amount"].sum().reset_index(), values="Amount", names="Category", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    else: st.info("尚無資料")

# === Tab 3: 列表 ===
with tab3:
    st.subheader("📋 最近紀錄 (點擊 🗑️ 刪除)")
    if not df.empty:
        df_display = df.copy()
        df_display['orig_idx'] = df_display.index
        df_display = df_display.sort_values("Date", ascending=False).head(20)
        for _, row in df_display.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.5, 0.8])
                with c1:
                    st.markdown(f'<div class="card-title">{row["Category"]}</div>', unsafe_allow_html=True)
                    st.caption(f"{row['Date']} | {row['Note']}")
                with c2: st.markdown(f'<div class="card-amount">${row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"del_{row['orig_idx']}"):
                        try:
                            fresh_df = conn.read(worksheet="Expenses", ttl=0)
                            conn.update(worksheet="Expenses", data=fresh_df.drop(row['orig_idx']))
                            st.toast("🗑️ 已成功刪除紀錄")
                            time.sleep(1); st.rerun()
                        except Exception as e: st.error(f"失敗：{e}")
    else: st.info("尚無資料")

# --- 底部署名 ---
st.write("---")
st.markdown('<div class="footer">作者 LunGo</div>', unsafe_allow_html=True)
