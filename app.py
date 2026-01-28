import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components # 引入元件庫，為了做震動效果
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import time

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 (含 iPhone 黑字 + 跳窗置中放大) ---
st.markdown("""
    <style>
    /* 1. 輸入框本體設定：淡黃色背景 + 強制黑字 */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }
    
    /* 2. 下拉選單設定 */
    div[data-baseweb="select"] > div {
        background-color: #fff9c4 !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    div[data-baseweb="select"] svg {
        fill: #000000 !important;
    }
    
    /* 3. 按鈕設定 */
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 22px !important; font-weight: bold;
        border-radius: 10px; border: none; margin-top: 10px;
    }
    .save-btn > button { background-color: #FF4B4B; color: white; }
    .save-btn > button:hover { background-color: #E03A3A; color: white; }
    .del-btn > button { background-color: #6c757d; color: white; }
    .del-btn > button:hover { background-color: #5a6268; color: white; }
    
    /* 4. 進度條文字美化 */
    .game-status {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    /* 5. 【關鍵修改】Toast 跳窗置中放大術 */
    div[data-testid="stToast"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 80vw !important; /* 寬度佔螢幕 80% */
        max-width: 400px !important;
        padding: 30px !important;
        border-radius: 20px !important;
        background-color: #ffffff !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
        text-align: center !important;
        font-size: 24px !important; /* 字體放大 */
        z-index: 999999 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    /* 調整 Toast 裡面的圖示和文字 */
    div[data-testid="stToast"] > div {
        font-size: 22px !important;
        font-weight: bold !important;
    }
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

# --- 🎮 遊戲化預算設定 ---
with st.sidebar:
    st.header("⚙️ 遊戲設定 (預算)")
    monthly_budget = st.number_input("本月錢包總血量 (預算)", value=30000, step=1000)
    st.info("💡 設定好預算，右邊會顯示您的「闖關進度」喔！")

# --- 🎮 顯示錢包血量條 ---
if not df.empty:
    current_month_df = df[df["Month"] == current_month_str]
    current_spent = current_month_df["Amount"].sum()
else:
    current_spent = 0

if monthly_budget > 0:
    percent = current_spent / monthly_budget
else:
    percent = 0

st.write("---")
st.subheader(f"🛡️ 本月錢包防禦戰 ({current_month_str})")

col_bar1, col_bar2 = st.columns([3, 1])

with col_bar1:
    if percent < 0.5:
        status_text = "🟢 勇者狀態良好，繼續冒險！"
    elif percent < 0.8:
        status_text = "🟡 遭遇小怪，錢包受傷中..."
    elif percent < 1.0:
        status_text = "🔴 BOSS 戰預警！血量告急！"
    else:
        status_text = "☠️ GAME OVER... 錢包已陣亡 (超支)"

    st.markdown(f'<div class="game-status">{status_text}</div>', unsafe_allow_html=True)
    display_percent = min(percent, 1.0)
    st.progress(display_percent)

with col_bar2:
    remaining = monthly_budget - current_spent
    st.metric("剩餘血量", f"${remaining:,.0f}", delta=f"-${current_spent:,.0f} 已損血", delta_color="inverse")

st.write("---")

# --- 4. 記帳輸入區 ---
with st.expander("😈 紅字小壞蛋，要花的值得！", expanded=True):
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
        note_val = st.text_input("📝 備註 (詳細記錄謝謝)")
        
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
                    
                    # 1. 觸發震動 (使用 JS)
                    # 嘗試震動 200毫秒 (注意：iPhone 需要在 Safari 設定開啟相關權限，Android 較容易支援)
                    vibration_script = """
                    <script>
                    try {
                        window.navigator.vibrate(200);
                    } catch(e) {
                        console.log("Vibration not supported");
                    }
                    </script>
                    """
                    components.html(vibration_script, height=0, width=0)
                    
                    # 2. 顯示置中放大的跳窗
                    st.toast("🌟 記帳的開始，就是成功的開始！", icon="✨")
                    
                    st.success(f"✅ 已記錄：${amount_val}\n\n✨ 記帳的開始，就是成功的開始！")
                    
                    # 3. 延長停留時間 (3.5 秒)
                    time.sleep(3.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")
            else:
                st.warning("⚠️ 金額不能為 0")

# --- 5. 🗑️ 管理與刪除紀錄 ---
if not df.empty:
    with st.expander("🗑️ 管理與刪除紀錄", expanded=False):
        st.warning("⚠️ 刪除後無法復原，請小心操作")
        
        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
        if st.button("↩️ 刪除「最後一筆」紀錄 (Undo)"):
            try:
                raw_df = conn.read(worksheet="Expenses", ttl=0)
                if not raw_df.empty:
                    updated_df = raw_df.iloc[:-1]
                    conn.update(worksheet="Expenses", data=updated_df)
                    
                    # 震動 + 跳窗
                    components.html("<script>window.navigator.vibrate(100);</script>", height=0, width=0)
                    st.toast("↩️ 已復原 (刪除成功)", icon="✅")
                    
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.info("已經沒有資料可以刪除了")
            except Exception as e:
                st.error(f"刪除失敗: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
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
                    
                    components.html("<script>window.navigator.vibrate(100);</script>", height=0, width=0)
                    st.success(f"✅ 已刪除紀錄：{selected_item}")
                    time.sleep(1.5)
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
            st.metric("該月總支出", f"${total_spent:,.0f}")

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
