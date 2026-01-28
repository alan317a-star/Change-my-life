with st.sidebar:
    st.header("📍 目前位置")
    
    # 加入一個緩衝開關，預設關閉以防止網頁崩潰
    use_gps = st.toggle("使用手機 GPS 偵測天氣", value=False)
    
    if use_gps:
        loc = get_geolocation()
        if loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.metric("當前氣溫", get_weather(lat, lon))
        else:
            st.info("⌛ 偵測中，請點選瀏覽器「允許」位置存取...")
    else:
        # 預設直接顯示台中西屯天氣，確保畫面穩定
        st.metric("🏠 台中西屯 (預設)", get_weather(24.16, 120.68))
