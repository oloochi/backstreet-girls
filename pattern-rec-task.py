import streamlit as st
import time
import random

# --- Page Configuration & Styling ---
st.set_page_config(page_title="Pattern Recognition Task", layout="centered")

st.markdown("""
    <style>
    /* Center text alignment for instructions and start screens */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    .start-title {
        text-align: center;
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }
    .start-instructions {
        text-align: center;
        font-size: 1.15rem;
        line-height: 1.6;
        color: #D1D5DB;
        margin-bottom: 2rem;
    }
    .ready-prompt {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    /* Fixed square dimensions for 3x3 grid tiles */
    div.stButton > button {
        width: 100% !important;
        height: 110px !important;
        border-radius: 8px !important;
        border: 2px solid #333333 !important;
        background-color: #262730 !important;
        color: transparent !important;
        transition: none !important;
    }
    div.stButton > button:hover {
        border-color: #555555 !important;
        background-color: #262730 !important;
    }
    /* Override for standard primary action buttons (start & reset) */
    div[data-testid="stButton"] > button[kind="primary"] {
        height: 52px !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

MAX_LEVEL = 10
DISPLAY_FLASH_TIME = 0.65  # Seconds tile stays white
DISPLAY_GAP_TIME = 0.20    # Seconds between flashes

# --- State Management ---
def initialize_state(force_reset=False):
    if force_reset or "stage" not in st.session_state:
        st.session_state.stage = "intro"
        st.session_state.master_pattern = [random.randint(0, 8) for _ in range(MAX_LEVEL)]
        st.session_state.current_level = 1
        st.session_state.user_input = []
        st.session_state.trial_results = []
        st.session_state.task_start_time = None
        st.session_state.task_end_time = None
        st.session_state.last_click_time = None
        st.session_
