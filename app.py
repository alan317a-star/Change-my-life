import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import random
import base64
import os

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Everyday Moments", 
    page_icon="icon.png", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- 🍎 專治 iPhone 主畫面圖示 ---
def add_apple_touch_icon(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            apple_touch_icon_html = f"""
            <link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,{encoded_string}">
            <link rel="icon" type="image/png" href="data:image/png;base64,{encoded_string}">
            """
            st.markdown(apple_touch_icon_html, unsafe_allow_html=True)
    except Exception as e:
        pass

add_apple_touch_icon("icon.png")

# --- CSS 優化 ---
st.markdown("""
    <style>
    /* 隱藏預設元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background-color: rgba(0,0,0,0); z-index: 999;}
    
    /* 手機版面調整 */
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 5rem !important;
    }
    
    /* 輸入框與文字 */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        height: 50px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #fff9c4 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        height: 50px !important; 
        align-items: center;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
        font-size: 18px !important; 
    }
    
    /* 按鈕通用 */
    div.stButton > button {
        width: 100%; height: 3.8em; font-size: 20px !important; font-weight: bold;
        border-radius: 15px; border: none; margin-top: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.98); }

    .save-btn > button { background: linear-gradient(135deg, #FF6B6B 0%, #FF4B4B 100%); color: white; }
    .del-btn > button { background-color: #6c757d; color: white; }
    .gift-btn > button { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: white; }
    
    /* 使用按鈕 (調整為適合卡片的高度) */
    .use-btn > button { 
        background-color: #4CAF50 !important; 
        color: white !important; 
        height: 100% !important; 
        min-height: 60px !important; /* 卡片模式下稍微矮一點 */
        font-size: 18px !important;
        margin-top: 0px !important;
        border-radius: 12px !important;
    }
    
    /* 信件內容樣式 */
    .letter-box {
        background-color: #fff;
        border: 1px dashed #FF4B4B;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        color: #555;
        margin-top: 10px;
        white-space: pre-wrap;
    }

    /* Toast 通知 */
    div[data-testid="stToast"] { 
        position: fixed !important; top: 50% !important; left: 50% !important;       
        transform: translate(-50%, -50%) !important; 
        width: auto !important; min-width: 300px !important; max-width: 80vw !important;  
        border-radius: 20px !important; background-color: rgba(255, 255, 255, 0.98) !important; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.2) !important; border: 2px solid #FF4B4B !important;
        text-align: center !important; padding: 10px !important; z-index: 999999 !important; 
    }
    div[data-testid="stToast"] * { font-size: 20px !important; color: #000000 !important; justify-content: center !important; }
    
    .game-status { font-size: 20px; font-weight: bold; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 19px; font-weight: bold; color: #2196F3 !important; margin-bottom: 2px; }
    .card-note { font-size: 14px; color: inherit; opacity: 0.8; }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; line-height: 1.5; }
    .quote-box { background-color: #f0f2f6; border-left: 5px solid #FF4B4B; padding: 12px; margin-bottom: 15px; border-radius: 8px; font-style: italic; color: #555; text-align: center; font-size: 15px; }
    .footer { text-align: center; font-size: 12px; color: #cccccc; margin-top: 30px; margin-bottom: 20px; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 初始化狀態 ---
if "delete_verify_idx" not in st.session_state: st.session_state["delete_verify_idx"] = None

st.title("Everyday Moments")

# --- 隨機勉勵短語 ---
if "current_quote" not in st.session_state:
    quotes = ["🌱 每一筆省下的錢，都是未來的自由。", "💪 記帳不是為了省錢，而是為了更聰明地花錢。", "✨ 今天的自律，是為了明天的選擇權。", "🧱 財富是像堆積木一樣，一點一點累積起來的。", "🌟 你不理財，財不理你；用心生活，歲月靜好。", "🎯 透過記帳，看見真實的自己。", "🌈 能夠控制慾望的人，才能掌控人生。", "🌻 每一塊錢都有它的使命。", "🚀 投資自己，是報酬率最高的投資。", "❤️ 簡單生活，富足心靈。", "🏡 家的溫暖，建立在安穩的經濟基礎之上。"]
    st.session_state["current_quote"] = random.choice(quotes)
st.markdown(f'<div class="quote-box">{st.session_state["current_quote"]}</div>', unsafe_allow_html=True)

# --- 連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 讀取記帳資料 ---
try:
    df = conn.read(worksheet="Expenses", ttl=600)
    if df.empty: df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    else:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date_dt"].dt.strftime("%Y-%m")
        df["Note"] = df["Note"].fillna("")
except:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    st.toast("⚠️ 連線忙碌中，請稍後再試")

taiwan_now = datetime.utcnow() + timedelta(hours=8)
taiwan_date = taiwan_now.date()
current_month_str = taiwan_now.strftime("%Y-%m")

current_spent = df[df["Month"] == current_month_str]["Amount"].sum() if not df.empty else 0
last_month_end = taiwan_date.replace(day=1) - timedelta(days=1)
last_month_spent = df[df["Month"] == last_month_end.strftime("%Y-%m")]["Amount"].sum() if not df.empty else 0

# --- 🔥 連勝計算邏輯 ---
def calculate_streak(df):
    if df.empty: return 0
    dates = df["Date_dt"].dt.date.dropna().unique()
    dates.sort()
    
    if len(dates) == 0: return 0
    
    if dates[-1] != taiwan_date and dates[-1] != (taiwan_date - timedelta(days=1)):
        return 0
        
    check_date = dates[-1]
    streak = 1
    
    for i in range(len(dates)-2, -1, -1):
        if dates[i] == check_date - timedelta(days=1):
            streak += 1
            check_date = dates[i]
        else:
            break
    return streak

current_streak = calculate_streak(df)

# --- 🏆 自動發獎系統 ---
TARGET_STREAK = 21 
ACHIEVEMENT_CODE = f"ACHIEVE_{TARGET_STREAK}DAYS" 

try:
    # 讀取 Coupons
    coupon_df = conn.read(worksheet="Coupons", ttl=0)
    if "Detail" not in coupon_df.columns: coupon_df["Detail"] = ""
except:
    coupon_df = pd.DataFrame(columns=["Code", "Prize", "Detail", "Status", "Date"])

# 檢查連勝發獎
if current_streak >= TARGET_STREAK:
    if not coupon_df.empty:
        coupon_df["Code"] = coupon_df["Code"].astype(str).str.strip()
        target_indices = coupon_df.index[coupon_df["Code"] == ACHIEVEMENT_CODE].tolist()
        
        if target_indices:
            idx = target_indices[0] 
            current_status = coupon_df.at[idx, "Status"]
            
            if current_status == "待發送":
                coupon_df.at[idx, "Status"] = "持有中" 
                coupon_df.at[idx, "Date"] = taiwan_now.strftime("%Y-%m-%d %H:%M:%S")
                conn.update(worksheet="Coupons", data=coupon_df)
                prize_name = coupon_df.at[idx, "Prize"]
                st.balloons()
                st.toast(f"🎉 恭喜達成 {TARGET_STREAK} 天連勝！\n獲得：{prize_name}")
                time.sleep(2)
                st.rerun()

# --- 側邊欄 (清爽版) ---
with st.sidebar:
    st.header("⏳ 重要時刻")
    love_days = (taiwan_date - date(2019, 6, 15)).days
    if love_days > 0: st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    
    baby_days = (taiwan_date - date(2025, 9, 12)).days
    if baby_days > 0: st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    elif baby_days == 0: st.success("🎂 就是今天！寶寶誕生啦！")
    else: st.warning(f"👶 距離寶寶出生還有 **{-baby_days}** 天")

    st.metric("🔥 記帳連勝", f"{current_streak} 天")
    if current_streak >= TARGET_STREAK: st.caption(f"✨ 已達成 {TARGET_STREAK} 天目標！")
    else: st.caption(f"目標: {TARGET_STREAK} 天，加油！")

    st.write("---")
    st.header("📊 帳務概況")
    st.metric(label="💸 本月已花費", value=f"${current_spent:,.0f}")
    
    st.write("") 
    st.markdown("##### 📜 歷史查詢")
    if not df.empty:
        month_options = ["🏆 歷史總花費"] + sorted(df["Month"].dropna().unique().tolist(), reverse=True)
        selected_query = st.selectbox("選擇月份", month_options, label_visibility="collapsed")
        if selected_query == "🏆 歷史總花費":
            query_amount = df["Amount"].sum()
            query_label = "累積總支出"
        else:
            query_amount = df[df["Month"] == selected_query]["Amount"].sum()
            query_label = f"{selected_query} 總支出"
        st.info(f"{query_label}: **${query_amount:,.0f}**")
    
    st.write("---")
    st.header("💰 錢包狀態")
    monthly_budget = st.number_input("本月預算 (血量)", value=30000, step=1000)

# --- 🛡️ 錢包防禦戰 ---
percent = current_spent / monthly_budget if monthly_budget > 0 else 0
remaining = monthly_budget - current_spent
_, last_day = calendar.monthrange(taiwan_date.year, taiwan_date.month)
days_left = last_day - taiwan_date.day + 1
daily_budget = remaining / days_left if days_left > 0 else 0

st.subheader("🛡️ 錢包防禦戰")
c_b1, c_b2, c_b3 = st.columns([2, 1, 1])
with c_b1:
    if percent < 0.3: status_text = "🏆 黃金理財大師"
    elif percent < 0.6: status_text = "🛡️ 白銀防禦騎士"
    elif percent < 0.9: status_text = "⚔️ 青銅奮戰勇者"
    elif percent < 1.0: status_text = "🔴 紅色警戒兵"
    else: status_text = "☠️ 骷髏錢包"
    st.markdown(f'<div class="game-status">{status_text}</div>', unsafe_allow_html=True)
    st.progress(min(percent, 1.0))
with c_b2: st.metric("剩餘血量", f"${remaining:,.0f}")
with c_b3: st.metric("📅 今日可用", f"${daily_budget:,.0f}")
st.write("---")

# === 主畫面分頁設定 (4個分頁) ===
tab1, tab2, tab3, tab4 = st.tabs(["📝 記帳", "📊 分析", "📋 列表", "🎒 背包"])

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
                    raw_df = conn.read(worksheet="Expenses", ttl=0)
                    if raw_df.empty: raw_df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
                    new_row = pd.DataFrame([{
                        "Date": f"{date_val} {taiwan_now.strftime('%H:%M:%S')}", 
                        "Category": cat_val, 
                        "Amount": amount_val, 
                        "Note": note_val
                    }])
                    final_df = pd.concat([raw_df, new_row], ignore_index=True)
                    if "User" in final_df.columns: final_df = final_df.drop(columns=["User"])
                    conn.update(worksheet="Expenses", data=final_df)
                    st.toast("✨ 記帳完成！")
                    conn.reset()
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
                    conn.reset()
                    time.sleep(1); st.rerun()
                else: st.warning("無紀錄可刪")
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
    st.subheader("📋 最近紀錄")
    if not df.empty:
        df_display = df.copy()
        df_display['orig_idx'] = df_display.index
        df_display = df_display.sort_values("Date", ascending=False).head(20)
        for _, row in df_display.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.5, 1.1])
                with c1:
                    st.markdown(f'<div class="card-title">{row["Category"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card-note">{row["Date"]} | {row["Note"]}</div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="card-amount">${row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
                with c3:
                    if st.session_state["delete_verify_idx"] == row['orig_idx']:
                        sub_c1, sub_c2 = st.columns(2)
                        with sub_c1:
                            if st.button("✅", key=f"conf_{row['orig_idx']}", type="primary"):
                                try:
                                    fresh_df = conn.read(worksheet="Expenses", ttl=0)
                                    conn.update(worksheet="Expenses", data=fresh_df.drop(row['orig_idx']))
                                    st.toast("🗑️ 已成功刪除")
                                    st.session_state["delete_verify_idx"] = None
                                    conn.reset()
                                    time.sleep(1); st.rerun()
                                except Exception as e: st.error(f"失敗：{e}")
                        with sub_c2:
                            if st.button("❌", key=f"cancel_{row['orig_idx']}"):
                                st.session_state["delete_verify_idx"] = None
                                st.rerun()
                    else:
                        if st.button("🗑️", key=f"del_{row['orig_idx']}"):
                            st.session_state["delete_verify_idx"] = row['orig_idx']
                            st.rerun()
    else: st.info("尚無資料")

# === Tab 4: 背包 (移到這裡！) ===
with tab4:
    st.subheader("🎒 我的背包")
    
    # 1. 兌換輸入區
    with st.expander("➕ 輸入代碼領取獎品", expanded=False):
        coupon_code = st.text_input("輸入代碼", key="coupon_input")
        st.markdown('<div class="gift-btn">', unsafe_allow_html=True)
        if st.button("🎁 領取"):
            if coupon_code:
                if not coupon_df.empty:
                    coupon_df["Code"] = coupon_df["Code"].astype(str).str.strip()
                    input_code = coupon_code.strip()
                    target_row = coupon_df[coupon_df["Code"] == input_code]
                    
                    if not target_row.empty:
                        idx = target_row.index[0]
                        current_status = target_row.at[idx, "Status"]
                        if current_status in ["未使用", "待發送"]:
                            prize = target_row.at[idx, "Prize"]
                            coupon_df.at[idx, "Status"] = "持有中"
                            coupon_df.at[idx, "Date"] = taiwan_now.strftime("%Y-%m-%d %H:%M:%S")
                            conn.update(worksheet="Coupons", data=coupon_df)
                            st.balloons()
                            st.toast(f"🎒 成功放入背包：{prize}")
                            conn.reset()
                            time.sleep(1); st.rerun()
                        elif current_status == "持有中":
                            st.warning("🎒 已經在背包裡囉！")
                        else:
                            st.error("❌ 已經使用過囉！")
                    else:
                        st.error("❓ 代碼錯誤")
                else:
                    st.error("請建立 Coupons 分頁")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.write("---")

    # 2. 背包物品展示 (卡片式)
    if not coupon_df.empty:
        inventory = coupon_df[coupon_df["Status"] == "持有中"]
        if not inventory.empty:
            for i, row in inventory.iterrows():
                # 使用 container 包裹每一個物品，看起來像一張票
                with st.container(border=True):
                    c1, c2 = st.columns([2.2, 1]) 
                    with c1:
                        st.markdown(f"**🎁 {row['Prize']}**")
                        st.caption(f"領取於: {row['Date']}")
                    with c2:
                        st.markdown('<div class="use-btn">', unsafe_allow_html=True)
                        if st.button("✨ 使用", key=f"use_btn_{i}"):
                            coupon_df.at[i, "Status"] = "已使用"
                            coupon_df.at[i, "Date"] = taiwan_now.strftime("%Y-%m-%d %H:%M:%S")
                            conn.update(worksheet="Coupons", data=coupon_df)
                            st.toast(f"✅ 已使用：{row['Prize']}")
                            st.balloons()
                            conn.reset()
                            time.sleep(1); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 展開內容 (如果有)
                    detail_content = str(row['Detail'])
                    if len(detail_content) > 1 and detail_content != "nan":
                        with st.expander("📩 展開閱讀信件/內容"):
                            st.markdown(f'<div class="letter-box">{detail_content}</div>', unsafe_allow_html=True)
        else:
            st.info("🎒 背包目前空空的，快去輸入代碼或達成連勝成就！")
    else:
        st.caption("尚無資料")

# --- Footer ---
st.write("---")
st.markdown("""
    <div class="footer">
        作者 <a href="https://line.me/ti/p/OSubE3tsH4" target="_blank" style="text-decoration:none; color:#cccccc;">LunGo.</a>
    </div>
""", unsafe_allow_html=True)
