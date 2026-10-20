Python 3.11.7 (tags/v3.11.7:fa7a6f2, Dec  4 2023, 19:24:49) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import streamlit as st
... import pandas as pd
... import numpy as np
... import time
... 
... # ==========================================
... # 1. STIMULUS POOL CONFIGURATION
... # ==========================================
... # Insert your list of 75 unique words for this specific version/treatment below:
... WORD_LIST = [
...     # "word1", "word2", "word3", ...
... ]
... 
... # Set to True to allow the app to run with sample stimuli if WORD_LIST is empty
... DEBUG_MODE = False
... if not WORD_LIST and DEBUG_MODE:
...     WORD_LIST = [f"sample_{i}" for i in range(75)]
... 
... # ==========================================
... # 2. TRIAL SCHEDULE GENERATOR
... # ==========================================
... def generate_trial_schedule(words, min_lag=2, max_attempts=1000):
...     """
...     Generates a 150-trial continuous recognition schedule:
...     - 75 'New' presentations (first exposure)
...     - 75 'Old' presentations (second exposure)
...     - Enforces a minimum repetition lag (intervening items >= min_lag)
...     """
...     for _ in range(max_attempts):
...         pool_new = list(words)
...         np.random.shuffle(pool_new)
...         
...         schedule = []
...         seen_words = []
...         pending_repeats = []
...         
...         while pool_new or pending_repeats:
            valid_repeats = [
                w for w in pending_repeats 
                if (len(schedule) - schedule.index((w, "New")) - 1) >= min_lag
            ]
            
            # Decide whether to draw a New word or an Old word
            can_draw_new = len(pool_new) > 0
            can_draw_old = len(valid_repeats) > 0
            
            if can_draw_new and can_draw_old:
                # Balance probability dynamically based on remaining backlog
                p_old = len(valid_repeats) / (len(pool_new) + len(valid_repeats))
                draw_old = np.random.rand() < p_old
            elif can_draw_old:
                draw_old = True
            elif can_draw_new:
                draw_old = False
            else:
                break
                
            if draw_old:
                chosen_word = np.random.choice(valid_repeats)
                schedule.append((chosen_word, "Old"))
                pending_repeats.remove(chosen_word)
            else:
                chosen_word = pool_new.pop()
                schedule.append((chosen_word, "New"))
                pending_repeats.append(chosen_word)
                
        if len(schedule) == len(words) * 2:
            return [{"word": w, "ground_truth": gt} for w, gt in schedule]
            
    # Fallback deterministic schedule with staggered lag
    schedule = []
    half_1 = words[:len(words)//2]
    half_2 = words[len(words)//2:]
    for w in half_1:
        schedule.append({"word": w, "ground_truth": "New"})
    for w in half_1:
        schedule.append({"word": w, "ground_truth": "Old"})
    for w in half_2:
        schedule.append({"word": w, "ground_truth": "New"})
    for w in half_2:
        schedule.append({"word": w, "ground_truth": "Old"})
    return schedule

# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
st.set_page_config(page_title="Recognition Memory Task", layout="centered")

if "trials" not in st.session_state:
    st.session_state.trials = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "is_started" not in st.session_state:
    st.session_state.is_started = False
if "is_completed" not in st.session_state:
    st.session_state.is_completed = False
if "experiment_start_time" not in st.session_state:
    st.session_state.experiment_start_time = None
if "total_session_time" not in st.session_state:
    st.session_state.total_session_time = None
if "last_trial_time" not in st.session_state:
    st.session_state.last_trial_time = None
if "results" not in st.session_state:
    st.session_state.results = []

def process_response(user_choice):
    now = time.time()
    idx = st.session_state.current_index
    current_trial = st.session_state.trials[idx]
    
    # Timing logic: Start clock only when "Unfamiliar" is hit for the first time
    if not st.session_state.is_started:
        if user_choice == "Unfamiliar":
            st.session_state.is_started = True
            st.session_state.experiment_start_time = now
            st.session_state.last_trial_time = now
            reaction_time = 0.0
        else:
            # First item must be new; "Familiar" is an error before the clock starts
            reaction_time = 0.0
    else:
        reaction_time = round(now - st.session_state.last_trial_time, 4)
        st.session_state.last_trial_time = now

    ground_truth = current_trial["ground_truth"]
    
    # Familiar -> Old, Unfamiliar -> New
    if user_choice == "Familiar":
        is_correct = (ground_truth == "Old")
        signal_type = "Hit" if is_correct else "False Alarm"
    else:
        is_correct = (ground_truth == "New")
        signal_type = "Correct Rejection" if is_correct else "Miss"

    st.session_state.results.append({
        "trial_number": idx + 1,
        "word": current_trial["word"],
        "ground_truth": ground_truth,
        "user_response": user_choice,
        "is_correct": int(is_correct),
        "signal_type": signal_type,
        "reaction_time_sec": reaction_time
    })

    # Progress or Complete
    if idx + 1 >= len(st.session_state.trials):
        st.session_state.is_completed = True
        st.session_state.total_session_time = round(now - st.session_state.experiment_start_time, 2)
    else:
        st.session_state.current_index += 1

# ==========================================
# 4. EXPERIMENT INTERFACE
# ==========================================
st.markdown("## Continuous Recognition Memory Task")

if not WORD_LIST:
    st.warning("Word list is currently empty. Populate `WORD_LIST` at the top of the script to run this version.")
    st.stop()

# Build schedule once
if not st.session_state.trials and not st.session_state.is_completed:
    st.session_state.trials = generate_trial_schedule(WORD_LIST)

if not st.session_state.is_completed:
    idx = st.session_state.current_index
    total_trials = len(st.session_state.trials)
    current_trial = st.session_state.trials[idx]

    # Metrics Tracker
    res_df = pd.DataFrame(st.session_state.results) if st.session_state.results else pd.DataFrame()
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.metric("Progress", f"{idx + 1} / {total_trials}")
    with col_m2:
        last_rt = res_df["reaction_time_sec"].iloc[-1] if not res_df.empty else 0.0
        st.metric("Reaction Time", f"{last_rt:.2f} s")
    with col_m3:
        corr_new = len(res_df[res_df["signal_type"] == "Correct Rejection"]) if not res_df.empty else 0
        st.metric("Correct 'New'", corr_new)
    with col_m4:
        corr_old = len(res_df[res_df["signal_type"] == "Hit"]) if not res_df.empty else 0
        st.metric("Correct 'Old'", corr_old)

    st.divider()

    # Stimulus Display Card
    st.markdown(
        f"""
        <div style="text-align: center; margin: 40px 0;">
            <p style="font-size: 16px; color: #888;">Is this word Familiar or Unfamiliar?</p>
            <h1 style="font-size: 64px; letter-spacing: 2px;">{current_trial['word']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Response Buttons
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.button("Unfamiliar", use_container_width=True, on_click=process_response, args=("Unfamiliar",))
    with c_btn2:
        st.button("Familiar", use_container_width=True, on_click=process_response, args=("Familiar",))

    if not st.session_state.is_started:
        st.caption("Note: The session timer will officially start once 'Unfamiliar' is clicked for the first word.")

# ==========================================
# 5. POST-EXPERIMENT REPORTING
# ==========================================
else:
    st.success("Simulation Complete! All stimuli have been cycled through.")
    df_results = pd.DataFrame(st.session_state.results)
    
    total_time = st.session_state.total_session_time
    hits = len(df_results[df_results["signal_type"] == "Hit"])
    misses = len(df_results[df_results["signal_type"] == "Miss"])
    cr = len(df_results[df_results["signal_type"] == "Correct Rejection"])
    fa = len(df_results[df_results["signal_type"] == "False Alarm"])
    
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
    fa_rate = fa / (fa + cr) if (fa + cr) > 0 else 0
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Elapsed Time", f"{total_time:.2f} s")
    m_col2.metric("Overall Accuracy", f"{(df_results['is_correct'].mean() * 100):.1f}%")
    m_col3.metric("Mean Reaction Time", f"{df_results['reaction_time_sec'].mean():.2f} s")

    st.markdown("### Performance Breakdown")
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        st.write(f"- **Correct 'Old' (Hits):** {hits} / {hits + misses} ({hit_rate:.1%})")
        st.write(f"- **Missed 'Old' (Misses):** {misses} / {hits + misses}")
    with c_sub2:
        st.write(f"- **Correct 'New' (Correct Rejections):** {cr} / {cr + fa} ({(1 - fa_rate):.1%})")
        st.write(f"- **False Alarms ('New' marked Familiar):** {fa} / {cr + fa}")

    st.divider()
    st.markdown("### Raw Trial Data")
    st.dataframe(df_results, use_container_width=True)

    csv_data = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Task Data as CSV",
        data=csv_data,
        file_name="recognition_memory_results.csv",
        mime="text/csv"
