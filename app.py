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
    
    /* 按鈕 */
    div.stButton > button {
        width: 100%; height: 3.8em; font-size: 20px !important; font-weight: bold;
        border-radius: 15px; border: none; margin-top: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.1
