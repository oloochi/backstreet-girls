import streamlit as st
import time
import random

# --- Page Configuration & Global Styling ---
st.set_page_config(page_title="Pattern Recognition Task", layout="centered")

st.markdown("""
    <style>
    .block-container {
        max-width: 650px;
        padding-top: 2.5rem;
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
    
    /* Playback HTML Grid */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        width: 100%;
        max-width: 480px;
        margin: 1.5rem auto;
    }
    .pb-tile {
        height: 110px;
        border-radius: 8px;
        border: 2px solid #333333;
        background-color: #262730;
        box-sizing: border-box;
    }
    .pb-tile-active {
        height: 110px;
        border-radius: 8px;
        border: 2px solid #FFFFFF;
        background-color: #FFFFFF;
        box-shadow: 0 0 18px rgba(255, 255, 255, 0.95);
        box-sizing: border-box;
    }

    /* Input Grid Native Buttons */
    div[data-testid="stColumn"] > div > div.stButton > button {
        width: 100% !important;
        height: 110px !important;
        border-radius: 8px !important;
        border: 2px solid #333333 !important;
        background-color: #262730 !important;
        color: transparent !important;
        transition: none !important;
    }
    div[data-testid="stColumn"] > div > div.stButton > button:hover {
        border-color: #555555 !important;
        background-color: #262730 !important;
    }

    /* Primary Action Buttons (Start & Reset) */
    div.stButton > button[kind="primary"] {
        height: 52px !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        background-color: #FF4B4B !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

MAX_LEVEL = 10
DISPLAY_FLASH_TIME = 0.65  # Seconds tile illuminates white
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
        st.session_state.current_level_click_times = []

initialize_state()

def record_level_submission():
    target_seq = st.session_state.master_pattern[:st.session_state.current_level]
    is_correct = (st.session_state.user_input == target_seq)
    
    st.session_state.trial_results.append({
        "level": st.session_state.current_level,
        "correct": is_correct,
        "click_times": list(st.session_state.current_level_click_times)
    })
    
    st.session_state.user_input = []
    st.session_state.current_level_click_times = []
    
    if st.session_state.current_level < MAX_LEVEL:
        st.session_state.current_level += 1
        st.session_state.stage = "showing"
    else:
        st.session_state.task_end_time = time.time()
        st.session_state.stage = "completed"
    st.rerun()


# ==========================================
# 1. INTRO / START SCREEN
# ==========================================
if st.session_state.stage == "intro":
    st.markdown('<div class="start-title">Pattern Recognition Task</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="start-instructions">
            A sequence of tiles will illuminate in white across the 3x3 grid one by one.<br>
            Watch closely, then reproduce the exact sequence in order by clicking the tiles.<br><br>
            Each round will display the previous pattern plus one new addition.<br>
            The test will continue until all sequences are finished.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="ready-prompt">Are you ready?</div>', unsafe_allow_html=True)
    
    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        if st.button("Click Here to Begin", type="primary", use_container_width=True):
            st.session_state.stage = "showing"
            st.session_state.task_start_time = time.time()
            st.session_state.current_level = 1
            st.session_state.user_input = []
            st.session_state.trial_results = []
            st.rerun()

# ==========================================
# 2. PATTERN DEMONSTRATION PHASE
# ==========================================
elif st.session_state.stage == "showing":
    st.subheader(f"Sequence {st.session_state.current_level} of {MAX_LEVEL}")
    st.info("Watch the pattern carefully...")

    active_sequence = st.session_state.master_pattern[:st.session_state.current_level]
    grid_slot = st.empty()

    def generate_grid_html(active_idx=-1):
        tiles_html = ""
        for i in range(9):
            cls = "pb-tile-active" if i == active_idx else "pb-tile"
            tiles_html += f'<div class="{cls}"></div>'
        return f'<div class="grid-container">{tiles_html}</div>'

    # Clear and render initial baseline state
    grid_slot.markdown(generate_grid_html(-1), unsafe_allow_html=True)
    time.sleep(0.4)

    # Flash each tile in the sequence cleanly
    for tile in active_sequence:
        grid_slot.markdown(generate_grid_html(tile), unsafe_allow_html=True)
        time.sleep(DISPLAY_FLASH_TIME)
        grid_slot.markdown(generate_grid_html(-1), unsafe_allow_html=True)
        time.sleep(DISPLAY_GAP_TIME)

    # Clear before moving to input stage
    grid_slot.empty()
    st.session_state.stage = "input"
    st.session_state.last_click_time = time.time()
    st.rerun()

# ==========================================
# 3. PARTICIPANT INPUT PHASE
# ==========================================
elif st.session_state.stage == "input":
    target_len = st.session_state.current_level
    current_clicks = len(st.session_state.user_input)

    st.subheader(f"Sequence {st.session_state.current_level} of {MAX_LEVEL}")
    st.caption(f"Reproduce the pattern: {current_clicks} / {target_len} tiles selected")

    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            idx = r * 3 + c
            with cols[c]:
                if st.button(" ", key=f"input_tile_{idx}", use_container_width=True):
                    now = time.time()
                    interval = now - st.session_state.last_click_time
                    st.session_state.current_level_click_times.append(interval)
                    st.session_state.last_click_time = now

                    st.session_state.user_input.append(idx)

                    if len(st.session_state.user_input) == target_len:
                        record_level_submission()
                    else:
                        st.rerun()

# ==========================================
# 4. TASK COMPLETION & ADMIN RESULTS
# ==========================================
elif st.session_state.stage == "completed":
    st.title("Task Complete")
    st.success("Thank you! You have finished the pattern recognition evaluation.")
    st.markdown("---")

    st.subheader("Administrative Results")
    admin_pw = st.text_input("Enter password to unlock participant performance metrics:", type="password")

    if admin_pw == "backstreet":
        st.markdown("### Performance Summary")

        total_time = st.session_state.task_end_time - st.session_state.task_start_time
        mins = int(total_time // 60)
        secs = total_time % 60

        total_trials = len(st.session_state.trial_results)
        correct_trials = sum(1 for res in st.session_state.trial_results if res["correct"])

        first_error_length = None
        for res in st.session_state.trial_results:
            if not res["correct"]:
                first_error_length = res["level"]
                break

        all_click_intervals = [
            interval
            for res in st.session_state.trial_results
            for interval in res["click_times"]
        ]
        avg_click_latency = (
            sum(all_click_intervals) / len(all_click_intervals)
            if all_click_intervals else 0.0
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Completion Time", f"{mins}m {secs:.2f}s")
            st.metric("Trials Correct", f"{correct_trials} / {total_trials}")
        with col2:
            st.metric(
                "First Error Sequence Length",
                f"{first_error_length} squares" if first_error_length is not None else "None (100% Correct)"
            )
            st.metric("Avg Time Per Square Selection", f"{avg_click_latency:.2f} s")

        st.markdown("---")
        with st.expander("Trial Breakdown"):
            st.dataframe(
                [
                    {
                        "Sequence Length": res["level"],
                        "Result": "Correct" if res["correct"] else "Incorrect",
                        "Avg Press Latency (s)": round(sum(res["click_times"]) / len(res["click_times"]), 3) if res["click_times"] else 0.0
                    }
                    for res in st.session_state.trial_results
                ],
                use_container_width=True
            )

        st.markdown("---")
        if st.button("Reset for Next Participant", type="primary", use_container_width=True):
            initialize_state(force_reset=True)
            st.rerun()

    elif admin_pw:
        st.error("Incorrect password.")
