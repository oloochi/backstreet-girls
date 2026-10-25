import streamlit as st
import time
import random

# --- Page Configuration & Styling ---
st.set_page_config(page_title="Pattern Recognition Task", layout="centered")

st.markdown("""
    <style>
    /* Force consistent 3x3 button dimensions across all states */
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
    /* Active highlight style for sequence playback */
    div.stButton > button.tile-active {
        background-color: #FFFFFF !important;
        border-color: #FFFFFF !important;
        box-shadow: 0 0 16px rgba(255, 255, 255, 0.9) !important;
    }
    </style>
""", unsafe_allow_html=True)

MAX_LEVEL = 10

# Display timing calibration
DISPLAY_FLASH_TIME = 0.65  # Seconds each tile illuminates white
DISPLAY_GAP_TIME = 0.20    # Seconds between consecutive flashes

# --- State Initialization ---
if "stage" not in st.session_state:
    st.session_state.stage = "intro"            # intro, showing, input, completed
if "master_pattern" not in st.session_state:
    st.session_state.master_pattern = [random.randint(0, 8) for _ in range(MAX_LEVEL)]
if "current_level" not in st.session_state:
    st.session_state.current_level = 1
if "user_input" not in st.session_state:
    st.session_state.user_input = []
if "trial_results" not in st.session_state:
    st.session_state.trial_results = []
if "task_start_time" not in st.session_state:
    st.session_state.task_start_time = None
if "task_end_time" not in st.session_state:
    st.session_state.task_end_time = None
if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = None
if "current_level_click_times" not in st.session_state:
    st.session_state.current_level_click_times = []


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
# 1. INTRO / "ARE YOU READY" SCREEN
# ==========================================
if st.session_state.stage == "intro":
    st.title("Pattern Recognition Task")
    st.write(
        "A sequence of tiles will illuminate in white across the 3x3 grid one by one. "
        "Watch closely, then reproduce the exact sequence in order by clicking the tiles."
    )
    st.write(
        "After each sequence, one additional tile is added to the pattern. "
        "The test will continue until all sequences are complete."
    )
    st.markdown("---")
    st.subheader("Are you ready?")
    
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

    def draw_playback_grid(active_idx=-1):
        with grid_slot.container():
            # Inject dynamic CSS to illuminate the specific target tile white
            if active_idx >= 0:
                st.markdown(f"""
                    <style>
                    div.stButton > button[key="play_{active_idx}"] {{
                        background-color: #FFFFFF !important;
                        border-color: #FFFFFF !important;
                        box-shadow: 0 0 18px rgba(255, 255, 255, 0.95) !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

            for r in range(3):
                cols = st.columns(3)
                for c in range(3):
                    idx = r * 3 + c
                    with cols[c]:
                        st.button(" ", key=f"play_{idx}", disabled=True)

    # Initial rest pause before sequence initiates
    draw_playback_grid(-1)
    time.sleep(0.4)

    # Flash sequence
    for tile in active_sequence:
        draw_playback_grid(tile)
        time.sleep(DISPLAY_FLASH_TIME)
        draw_playback_grid(-1)
        time.sleep(DISPLAY_GAP_TIME)

    # Clear playback container to prevent duplicate elements
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
                if st.button(" ", key=f"input_{idx}", use_container_width=True):
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
# 4. TASK COMPLETION & STATS
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
    elif admin_pw:
        st.error("Incorrect password.")
