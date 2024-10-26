import streamlit as st
import pandas as pd
import time
from streamlit_option_menu import option_menu
from DashBoard import DashBoard
from Chatbot import chatBot

st.set_page_config(
    page_title="Wingzxel",
    page_icon=":airplane:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=[
            "DashBoard",
            "Chatbot",
        ],
        icons=["bar-chart-line-fill", "robot"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "DashBoard":
    DashBoard()
elif selected == "Chatbot":
    chatBot()
