import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
import time
import requests

# --- 關鍵修改：引入 GPS 套件 ---
# 如果您看到錯誤，請在終端機輸入：pip install streamlit-js-eval
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    st.error("⚠️ 請先安裝 GPS 套件：在終端機輸入 `pip install streamlit-js-eval`")

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Everyday Moments", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    /* 輸入框與文字設定 (iPhone 黑字優化) */
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
    div[data-baseweb="select"] svg {
        fill: #000000 !important;
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
    
    /* 進度條文字 */
    .game-status {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    /* 跳窗設定 (單行文字) */
    div[data-testid="stToast"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 90vw !important;
        max-width: 500px !important;
        padding: 15px 25px !important;
        border-radius: 50px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 30px rgba(0,0,0,0.3) !important;
        text-align: center !important;
        z-index: 999999 !important;
        border: 2px solid #FF4B4B !important;
    }
    
    div[data-testid="stToast"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        font-family: sans-serif !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
    }
    
    /* 分頁籤 (Tabs) 字體放大 */
    button[data-baseweb="tab"] div p {
        font-size: 20px !important;
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

# --- 🌤️ 天氣功能 ---
@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia%2FTaipei"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['current_weather']['temperature']
            code = data['current_weather']['weathercode']
            if code <= 3: icon = "🌤️"
            elif code <= 48: icon = "☁️"
            elif code <= 67: icon = "🌧️"
            elif code <= 99: icon = "⛈️"
            else: icon = "🌡️"
            return f"{icon} {temp}°C"
        else:
            return None
    except:
        return None

# --- ⏳ 側邊欄：GPS + 重要時刻 ---
with st.sidebar:
    st.header("📍 目前位置")
    
    # === 關鍵修改：GPS 定位 ===
    # 第一次執行時，瀏覽器會跳出「是否允許存取位置」，請點選「允許」
    try:
        loc = get_geolocation()
    except:
        loc = None

    weather_text = "☁️ 定位中..."
    location_name = "偵測中"
    
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        location_name = "📍 您的位置"
        
        # 取得天氣
        w_data = get_weather(lat, lon)
        if w_data:
            weather_text = w_data
    else:
        # 如果還沒按允許，或定位失敗，預設顯示台中
        weather_text = "⏳ 等待 GPS..."
        # 預設台中北區座標，避免空白
        default_weather = get_weather(24.16, 120.68)
        if default_weather:
             # 如果真的抓不到，就先顯示台中，但標註是預設
             pass

    st.metric(location_name, weather_text)
    if not loc:
        st.caption("請在瀏覽器左上角點選「允許」位置存取，即可顯示當地氣溫。")
    
    st.write("---")
    
    # 2. 重要時刻
    st.header("⏳ 重要時刻")
    
    # 在一起 (2019/06/15)
    love_start = date(2019, 6, 15)
    love_days = (taiwan_date - love_start).days
    if love_days > 0:
        st.info(f"👩‍❤️‍👨 我們在一起 **{love_days}** 天囉！")
    
    # 寶寶出生 (114/09/12 -> 2025/09/12)
    baby_born = date(2025, 9, 12)
    baby_days = (taiwan_date - baby_born).days
    if baby_days > 0:
        st.success(f"👶 承淅來到地球 **{baby_days}** 天囉！")
    elif baby_days == 0:
        st.success("🎂 就是今天！寶寶誕生啦！")
    else:
        st.warning(f"👶 距離寶寶出生還有 **{-baby_days}** 天")

    st.write("---")
    st.header("⚙️ 遊戲設定 (預算)")
    monthly_budget = st.number_input("本月錢包總血量 (預算)", value=30000, step=1000)

# --- 🛡️ 錢包血量條 (3欄) ---
if not df.empty:
    current_month_df = df[df["Month"] == current_month_str]
    current_spent = current_month_df["Amount"].sum()
else:
    current_spent = 0

if monthly_budget > 0:
    percent = current_spent / monthly_budget
else:
    percent = 0

st.subheader(f"🛡️ 本月錢包防禦戰")

_, last_day_of_month = calendar.monthrange(taiwan_date.year, taiwan_date.month)
days_remaining_in_month = last_day_of_month - taiwan_date.day + 1
remaining_budget = monthly_budget - current_spent
daily_budget = remaining_budget / days_remaining_in_month if days_remaining_in_month > 0 else 0

col_bar1, col_bar2, col_bar3 = st.columns([2, 1, 1])

with col_bar1:
    if percent < 0.5:
        status_text = "🟢 勇者狀態良好！"
    elif percent < 0.8:
        status_text = "🟡 遭遇小怪，受傷中..."
    elif percent < 1.0:
        status_text = "🔴 BOSS 戰預警！告急！"
    else:
        status_text = "☠️ 錢包已陣亡"
    st.markdown(f'<div class="game-status">{status_text}</div>', unsafe_allow_html=True)
    display_percent = min(percent, 1.0)
    st.progress(display_percent)

with col_bar2:
    st.metric("剩餘血量", f"${remaining_budget:,.0f}", delta=f"-${current_spent:,.0f}", delta_color="inverse")

with col_bar3:
    st.metric("📅 今日可用", f"${daily_budget:,.0f}", help="剩餘預算 ÷ 本月剩餘天數")

st.write("---")

# --- 📂 分頁切換 ---
tab1, tab2, tab3 = st.tabs(["📝 記帳", "📊 分析", "📋 列表"])

# === 分頁 1: 記帳輸入 + 摺疊刪除區 ===
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
        note_val = st.text_input("📝 備註 (~詳細記錄謝謝~)")
        
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
                    
                    vibration_script = """<script>try{window.navigator.vibrate([100,50,100]);}catch(e){}</script>"""
                    components.html(vibration_script, height=0, width=0)
                    
                    st.toast("記帳的開始，就是成功的開始！")
                    st.success(f"✅ 已記錄：${amount_val}\n\n記帳的開始，就是成功的開始！")
                    
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")
            else:
                st.warning("⚠️ 金額不能為 0")
    
    st.write("---")
    
    # --- 記錯帳管理區 ---
    with st.expander("記錯帳按這邊", expanded=False):
        # 1. 快速復原 (Undo)
        st.caption("👇 剛剛記錯了嗎？這裡可以快速復原上一筆")
        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
        if st.button("↩️ 刪除剛記的那一筆 (Undo)"):
            try:
                raw_df = conn.read(worksheet="Expenses", ttl=0)
                if not raw_df.empty:
                    updated_df = raw_df.iloc[:-1]
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.toast("已復原 (刪除成功)")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.info("已經沒有資料")
            except Exception as e:
                st.error(f"刪除失敗: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. 指定刪除 (下拉選單)
        if not df.empty:
            st.markdown("---")
            st.caption("或是選擇刪除特定的一筆：")
            delete_options = [f"{i}: {row['Date']} | {row['Category']} | ${row['Amount']} | {row['Note']}" for i, row in df.iterrows()]
            selected_item = st.selectbox("🔍 選擇要刪除的紀錄：", ["(請選擇)"] + list(reversed(delete_options)))
            
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("❌ 確認刪除此筆紀錄"):
                if selected_item != "(請選擇)":
                    try:
                        index_to_drop = int(selected_item.split(":")[0])
                        raw_df = conn.read(worksheet="Expenses", ttl=0)
                        updated_df = raw_df.drop(index_to_drop)
                        conn.update(worksheet="Expenses", data=updated_df)
                        st.success(f"✅ 刪除成功：{selected_item}")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")


# === 分頁 2: 圓餅圖分析 ===
with tab2:
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

# === 分頁 3: 詳細列表 (純檢視) ===
with tab3:
    st.subheader("📋 詳細紀錄列表")
    
    if not df.empty:
        # 1. 顯示資料 (原生表格)
        display_df = df[["Date", "Category", "Amount", "Note"]].sort_values("Date", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)


