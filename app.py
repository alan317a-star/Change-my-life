# --- CSS 優化：徹底解決 iPhone 黑底與選單顏色問題 ---
st.markdown("""
    <style>
    /* 統一輸入框樣式 */
    .stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] > div {
        font-size: 18px !important;
        background-color: #fff9c4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    /* 針對 iPhone 下拉選單彈出層的文字顏色優化 */
    div[data-baseweb="popover"] li {
        color: #000000 !important;
    }
    /* 儲存按鈕美化 */
    div.stButton > button {
        width: 100%; height: 3.5em; font-size: 20px !important; font-weight: bold;
        border-radius: 12px; background-color: #FF4B4B; color: white;
        border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-amount { font-size: 20px; font-weight: bold; color: #FF4B4B; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# === 分頁 1: 記帳 (修正變數 Bug) ===
with tab1:
    st.markdown("### 😈 每一筆錢都要花得值得！")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("📅 日期", taiwan_date)
        with col2:
            cat_val = st.selectbox("📂 分類", ["🍔 飲食", "🛒 日用", "🚗 交通", "🇯🇵 旅遊", "👶 寶寶", "💸 其他"])
        
        amount_val = st.number_input("💲 金額", min_value=0, step=1, format="%d")
        note_val = st.text_input("📝 備註 (例如：福岡一蘭拉麵)")
        
        if st.form_submit_button("💾 儲存紀錄"):
            if amount_val > 0:
                # 使用正確的變數名稱
                ts = f"{date_val} {taiwan_now.strftime('%H:%M:%S')}"
                new_row = pd.DataFrame([{"Date": ts, "Category": cat_val, "Amount": amount_val, "Note": note_val}])
                
                # 這裡建議使用緩存清理，確保數據即時更新
                raw_data = conn.read(worksheet="Expenses", ttl=0)
                updated_df = pd.concat([raw_data, new_row], ignore_index=True)
                conn.update(worksheet="Expenses", data=updated_df)
                
                st.toast("✅ 紀錄成功！")
                time.sleep(1)
                st.rerun()
            else:
                st.error("請輸入正確金額")
