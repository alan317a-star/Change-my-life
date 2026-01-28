import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 頁面基本設定
st.set_page_config(page_title="家庭記帳本", layout="centered")
st.title("💰 家庭記帳本")

# --- 1. 記帳輸入區 (直接嵌在 App 裡) ---
st.subheader("📝 新增一筆")

# 這裡我已經幫您把剛剛給的網址填進去了，並加上 embedded=true 讓它完美嵌入
google_form_url = "https://forms.gle/fsfaQKjYiLthphfCA?embedded=true"

# 使用 iframe 顯示表單，高度設為 600 讓手機好滑動
components.iframe(google_form_url, height=600, scrolling=True)

# --- 2. 顯示結果區 (讀取 Google 試算表) ---
st.write("---")
st.subheader("📊 最新記帳紀錄")

# 重新整理按鈕 (記完帳後按一下這個，下面的表就會更新)
if st.button("🔄 重新整理查看最新紀錄"):
    st.rerun()

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 【關鍵注意】：
    # Google 表單連結到試算表後，通常會自動建立一個新分頁叫做 "表單回應 1"
    # 如果您的表格下方分頁名稱不同，請修改下面這行引號內的文字
    df = conn.read(worksheet="表單回應 1", ttl=0)
    
    if not df.empty:
        # 資料清理：通常表單的第一欄是「時間戳記」，我們把它改名或簡單處理
        #
