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

# --- 初始化刪除確認狀態 ---
if "delete_verify_idx" not in st.session_state:
    st.session_state["delete_verify_idx"] = None

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
    .stButton > button[kind="secondary"] { height: 100% !important; margin-top: 0px !important; font-size: 16px !important; background-color: #f8f9fa !important; border: 1px solid #ddd !important; color: #666 !important; }
    
    .game-status { font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    div[data-testid="stToast"] { position: fixed !important; top: 50% !important; left: 50% !important; transform: translate(-50%, -50%) !important; width: 90vw !important; max-width: 500px !important; border-radius: 50px !important; background-color: #ffffff !important; box-shadow: 0 4px 30px rgba(0,0,0,0.3) !important; text-align: center !important; z-index: 999999 !important; border: 2px solid #FF4B4B !important; }
    div[data-testid="stToast"] * { color: #000000 !important; font-size: 20px !important; font-weight: bold !important; }
    
    /* 卡片樣式 */
    .card-title { font-size: 20px; font-weight: bold; color: #2196F3 !important; margin-bottom: 3px; }
    .card-note { font-size: 15px; color: inherit; opacity: 0.9; }
    .card-amount { font-size: 22px; font-weight: bold; color: #FF4B4B; text-align: right; }
    
    /* 金句樣式 */
    .quote-box { background-color: #f0f2f6; border-left: 5px solid #FF4B4B; padding: 15px; margin-bottom: 20px; border-radius: 5px; font-style: italic; color: #555; text-align: center; font-size: 16px; }
    .footer { text-align: center; font-size: 14px; color: #aaaaaa; margin-top: 50px; margin-bottom: 20px; font-family: sans-serif; }
    </style>
