import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 頁面基本設定
st.set_page_config(page_title="家庭記帳本", layout="centered")
st.title("💰 家庭記帳本")

# --- 1. 記帳輸入區 (直接嵌在 App 裡) ---
st.subheader("📝 新增一筆")

# 這是您提供的正確 Google 表單網址
google_form_url = "https://forms.gle/fsfaQKjYiLthphfCA"

# 使用 iframe 顯示表單
components.iframe(google_form_url, height=600, scrolling=True)

# --- 2. 顯示結果區 (讀取 Google 試算表) ---
st.write("---")
st.subheader("📊 最新記帳紀錄")

# 重新整理按鈕
if st.button("🔄 重新整理查看最新紀錄"):
    st.rerun()

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 讀取資料
    # 請注意：如果您的試算表分頁名稱不是 "表單回應 1"，請修改這裡
    df = conn.read(worksheet="表單回應 1", ttl=0)
    
    # 檢查資料是否為空 (這裡就是原本報錯的地方，我已經修好了)
    if not df.empty:
        # 顯示最新的 5 筆資料 (反轉順序)
        st.dataframe(df.tail(5).iloc[::-1], use_container_width=True)
    else:
        st.info("目前還沒有資料，試著填寫上面的表單看看！")
        
except Exception as e:
    st.warning("⚠️ 讀取資料時發生錯誤")
    st.markdown(f"""
    **請檢查試算表的分頁名稱：**
    1. 打開您的 Google 試算表
    2. 看下方新出現的分頁是不是叫 **`表單回應 1`**？
    3. 如果是英文介面可能叫 `Form Responses 1`，請修改程式碼第 33 行。
    
    錯誤訊息: {e}
    """)
