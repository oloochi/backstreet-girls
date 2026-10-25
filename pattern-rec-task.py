import streamlit as st
import time
import random

# --- Page Configuration & Styling ---
st.set_page_config(page_title="Pattern Recognition Task", layout="centered")

st.markdown("""
    <style>
    .tile-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div.stButton > button {
        width: 100%;
        height: 100px;
        font-size: 26px;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.15s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

# Target: 10 levels (sequence lengths 1 through 10)
# Demonstration: ~40s cumulative display time
# User input: ~100s cumulative response time
# Total duration: ~2.3 - 2.5 minutes
MAX_LEVEL = 10

# --- State Initialization ---
if "stage" not in st.session_state:
    st.session_state.stage = "intro"            # Stages: intro, showing, input, completed
if "master_pattern" not in st.session_state:
    st.session_state.master_pattern = [random.randint(0, 8) for _ in range(MAX_LEVEL)]
if "current_level" not in st.session_state:
    st.session_state.current_level = 1          # 1 to MAX_LEVEL
if "user_input" not in st.session_state:
    st.session_state.user_input = []
if "trial_results" not in st.session_state:
    st.session_state.trial_results = []         # Dicts per level: {level, correct, click_times}
if "task_start_time" not in st.session_state:
    st.session_state.task_start_time = None
if "task_end_time" not in st.session_state:
    st.session_state.task_end_time = None
if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = None
if "current_level_click_times" not in st.session_state:
    st.session_state.current_level_click_times = []


def record_level_submission():
    """Evaluates the submitted sequence against the target pattern."""
    target_seq = st.session_state.master_pattern[:st.session_state.current_level]
    is_correct = (st.session_state.user_input == target_seq)
    
    st.session_state.trial_results.append({
        "level": st.session_state.current_level,
        "correct": is_correct,
        "click_times": list(st.session_state.current_level_click_times)
    })
    
    # Reset input buffers
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
        "A sequence of squares will highlight across the 3x3 grid one by one. "
        "Watch closely, then reproduce the exact sequence in order by clicking the tiles."
    )
    st.write(
        "Each successful or unsuccessful round adds one additional square to the pattern, "
        "continuing until all sequences are complete."
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

    grid_placeholder = st.empty()
    active_sequence = st.session_state.master_pattern[:st.session_state.current_level]

    def render_display_grid(highlighted_tile=-1):
        with grid_placeholder.container():
            for row in range(3):
                cols = st.columns(3)
                for col in range(3):
                    tile_idx = row * 3 + col
                    with cols[col]:
                        if tile_idx == highlighted_tile:
                            st.markdown(
                                """<div style="background-color: #2E7D32; height: 100px; border-radius: 8px; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-size: 28px; font-weight: bold;">■</div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                """<div style="background-color: #E0E0E0; height: 100px; border-radius: 8px; 
                                border: 1px solid #BDBDBD;"></div>""",
                                unsafe_allow_html=True
                            )

    # Initial brief pause before sequence playback
    render_display_grid(-1)
    time.sleep(0.4)

    # Flash each tile in the sequence
    for tile in active_sequence:
        render_display_grid(tile)
        time.sleep(0.65)  # Flash duration
        render_display_grid(-1)
        time.sleep(0.20)  # Inter-stimulus interval

    # Move to participant response phase
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

    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            tile_idx = row * 3 + col
            with cols[col]:
                if st.button(" ", key=f"tile_{tile_idx}", use_container_width=True):
                    now = time.time()
                    interval = now - st.session_state.last_click_time
                    st.session_state.current_level_click_times.append(interval)
                    st.session_state.last_click_time = now

                    st.session_state.user_input.append(tile_idx)

                    # Trigger next stage immediately once length matches
                    if len(st.session_state.user_input) == target_len:
                        record_level_submission()
                    else:
                        st.rerun()

# ==========================================
# 4. TASK COMPLETION & PASSWORD-LOCKED STATS
# ==========================================
elif st.session_state.stage == "completed":
    st.title("Task Complete")
    st.success("Thank you! You have finished the pattern recognition evaluation.")
    st.markdown("---")

    st.subheader("Administrative Results")
    admin_pw = st.text_input("Enter password to unlock participant performance metrics:", type="password")

    if admin_pw == "backstreet":
        st.markdown("### Performance Summary")

        # Metric 1: Total completion time
        total_time = st.session_state.task_end_time - st.session_state.task_start_time
        mins = int(total_time // 60)
        secs = total_time % 60

        # Metric 2: Trials correct out of total
        total_trials = len(st.session_state.trial_results)
        correct_trials = sum(1 for res in st.session_state.trial_results if res["correct"])

        # Metric 3: First trial failed (sequence length)
        first_error_length = None
        for res in st.session_state.trial_results:
            if not res["correct"]:
                first_error_length = res["level"]
                break

        # Metric 4: Average response latency per tile
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
