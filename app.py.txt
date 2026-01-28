import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="家庭財務儀表板", layout="centered")

st.title("📊 家庭財務儀表板")

# 1. 建立連線 (只讀取，不會報錯)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 這裡請注意：Google 表單連結進來的分頁通常叫 "表單回應 1" 或 "Form Responses 1"
    # ttl=0 確保每次打開都是最新的
    df = conn.read(worksheet="表單回應 1", ttl=0)
    
    # 資料清理 (確保欄位名稱對應)
    # Google 表單預設欄位通常是：'時間戳記', '日期', '分類', '金額'
    # 我們重新命名讓它好讀一點
    if not df.empty:
        # 自動偵測欄位並重新命名 (假設順序是：時間, 日期, 分類, 金額)
        df.columns = ["紀錄時間", "消費日期", "分類", "金額"]
        
        # 轉換日期格式
        df["消費日期"] = pd.to_datetime(df["消費日期"]).dt.date
        
        # --- 顯示區塊 1: 近期消費 ---
        st.subheader("📝 最近 5 筆紀錄")
        st.dataframe(df.tail(5).sort_index(ascending=False))

        # --- 顯示區塊 2: 統計分析 ---
        st.subheader("💰 支出統計")
        total_spent = df["金額"].sum()
        st.metric("總支出", f"${total_spent:,.0f}")

        # --- 顯示區塊 3: 分類圓餅圖 ---
        st.subheader("📊 消費分類")
        # 簡單的分類加總
        category_sum = df.groupby("分類")["金額"].sum().reset_index()
        st.bar_chart(category_sum, x="分類", y="金額")
        
    else:
        st.info("目前還沒有資料，請用 Google 表單記第一筆帳吧！")

except Exception as e:
    st.error(f"讀取資料時發生錯誤，請確認分頁名稱是否為 '表單回應 1'。錯誤訊息: {e}")

# 加入一個按鈕直接跳轉去記帳
st.markdown("---")
st.markdown("""
    <a href="您的_Google_表單_網址" target="_blank">
        <button style="width:100%; padding: 15px; background-color: #FF4B4B; color: white; border: none; border-radius: 10px; font-size: 18px;">
            ➕ 按這裡記帳 (開啟 Google 表單)
        </button>
    </a>
    """, unsafe_allow_html=True)
