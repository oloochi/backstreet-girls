import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# 1. STIMULUS POOL CONFIGURATION
# ==========================================
# Insert your list of 75 unique words for this specific version/treatment below:
# WORD_LIST = "ball boss buck dirt door drop east flat gold hair hole lake mess mild nest park post rain ring yard anger beach bench brain bread brush chain chair clock crash dress flame flesh hotel knife mouth paint shirt snake train bottle bridge bucket butter canyon carpet closet danger drawer engine finger guitar jungle market pencil pocket silver spider ticket window blanket channel feather kitchen station village hospital mountain railroad sandwich stranger apartment machinery instrument television".split()
# WORD_LIST = "boat card coal dust fish frog iron lion meat moon path pipe roof rope sand seat ship song suit wind apple blade brick cabin chalk chest cliff cloud crown fruit grass heart horse metal money motor penny river stone wheel barrel basket camera castle circle cotton cradle donkey forest garage hammer island kettle monkey pillow rabbit rocket stream throat turkey bulletin curtain factory highway luggage surface calendar elevator platform sidewalk umbrella orchestra passenger locomotive restaurant".split()
# WORD_LIST = "bell bone boot bowl cake clay coat coin corn crow deer desk drum duck fork gate hill lamp leaf rock block board camel fence flute glass globe grape honey house lemon mouse onion paper pilot plate radio salad sugar table bullet cheese cherry coffee cookie cousin dinner flight freeze garlic jacket ladder lizard meadow noodle palace parrot powder saddle tunnel airport bedroom compass mailbox morning uniform basement corridor monument notebook shoulder companion gentleman motorcycle helicopter".split()
# WORD_LIST = "band bath belt camp date farm flag game hand moon page pool road shoe skin star tail tent tree wall badge broom clerk flock flour ghost jeans liver lunch pearl piano queen scarf shark sheep skirt smoke spoon stick towel anchor beetle border button carrot cattle church doctor drawer kitten magnet muffin napkin packet pigeon ribbon salmon statue string weapon cottage package parade receipt stomach theater daughter envelope neighbor property suitcase newspaper performer blacksmith calculator".split()
WORD_LIST = "ball park drum gate hill leaf bone bell flag instrument cousin cottage".split()

# Set to True for testing with dummy words if WORD_LIST is empty
DEBUG_MODE = False
if not WORD_LIST and DEBUG_MODE:
    WORD_LIST = [f"sample_{i}" for i in range(75)]

# ==========================================
# 2. TRIAL SCHEDULE GENERATOR (DYNAMIC SIZE)
# ==========================================
def generate_trial_schedule(words, max_run=4, min_lag=2, max_attempts=2000):
    """
    Dynamically generates a 2*N continuous recognition schedule for any list size N.
    Automatically scales short, medium, and long lag tiers and prevents deadlocks.
    """
    n = len(words)
    total_trials = n * 2
    n_tier = max(1, n // 3)

    for _ in range(max_attempts):
        w_list = list(words)
        np.random.shuffle(w_list)

        short_words = w_list[:n_tier]
        med_words = w_list[n_tier:2 * n_tier]
        long_words = w_list[2 * n_tier:]

        # Stagger entrance: long-tier enters early, short-tier is distributed
        p1 = long_words + med_words[:len(med_words)//2] + short_words[:len(short_words)//3]
        p2 = med_words[len(med_words)//2:] + short_words[len(short_words)//3: 2*len(short_words)//3]
        p3 = short_words[2*len(short_words)//3:]
        np.random.shuffle(p1)
        np.random.shuffle(p2)
        np.random.shuffle(p3)
        new_queue = p1 + p2 + p3

        schedule = []
        tier_map = {w: 'short' for w in short_words}
        tier_map.update({w: 'med' for w in med_words})
        tier_map.update({w: 'long' for w in long_words})

        active_repeats = {}
        failed = False

        for t in range(total_trials):
            eligible = {
                w: t - first_i - 1 
                for w, first_i in active_repeats.items() 
                if (t - first_i - 1) >= min_lag
            }

            ready = []
            for w, lag in eligible.items():
                tier = tier_map[w]
                if tier == 'short' and lag >= min_lag:
                    ready.append((w, 1.0))
                elif tier == 'med' and lag >= max(3, n_tier):
                    ready.append((w, 1.0))
                elif tier == 'long' and (lag >= max(5, 2 * n_tier) or t >= int(0.70 * total_trials)):
                    ready.append((w, 2.0))
                elif t >= int(0.85 * total_trials):
                    ready.append((w, 1.0))

            can_new = len(new_queue) > 0
            can_old = len(ready) > 0

            # Streak constraint
            if len(schedule) >= max_run:
                recent = [x[1] for x in schedule[-max_run:]]
                if all(s == "New" for s in recent):
                    can_new = False
                elif all(s == "Old" for s in recent):
                    can_old = False

            if not can_new and not can_old:
                failed = True
                break

            if can_new and can_old:
                rem_new = len(new_queue)
                rem_old = len(active_repeats)
                p_old = rem_old / (rem_new + rem_old)
                draw_old = np.random.rand() < p_old
            elif can_old:
                draw_old = True
            else:
                draw_old = False

            if draw_old:
                words_r, weights = zip(*ready)
                weights = np.array(weights) / sum(weights)
                chosen = np.random.choice(words_r, p=weights)
                schedule.append((chosen, "Old"))
                del active_repeats[chosen]
            else:
                chosen = new_queue.pop(0)
                schedule.append((chosen, "New"))
                active_repeats[chosen] = t

        if not failed and len(schedule) == total_trials:
            return [{"word": w, "ground_truth": gt} for w, gt in schedule]

    # Robust deterministic fallback
    schedule = []
    for w in words:
        schedule.append({"word": w, "ground_truth": "New"})
    for w in words:
        schedule.append({"word": w, "ground_truth": "Old"})
    return schedule


# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
st.set_page_config(page_title="Recognition Task", layout="centered")

if "stage" not in st.session_state:
    st.session_state.stage = "ready"  # Stages: 'ready', 'testing', 'completed'
if "trials" not in st.session_state:
    st.session_state.trials = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "experiment_start_time" not in st.session_state:
    st.session_state.experiment_start_time = None
if "total_session_time" not in st.session_state:
    st.session_state.total_session_time = None
if "last_trial_time" not in st.session_state:
    st.session_state.last_trial_time = None
if "results" not in st.session_state:
    st.session_state.results = []
if "show_password_box" not in st.session_state:
    st.session_state.show_password_box = False

def start_experiment():
    now = time.time()
    st.session_state.stage = "testing"
    st.session_state.experiment_start_time = now
    st.session_state.last_trial_time = now

def process_response(user_choice):
    now = time.time()
    idx = st.session_state.current_index
    current_trial = st.session_state.trials[idx]
    
    # Calculate response latency for this word
    reaction_time = round(now - st.session_state.last_trial_time, 4)
    st.session_state.last_trial_time = now

    ground_truth = current_trial["ground_truth"]
    
    if user_choice == "Familiar":
        is_correct = (ground_truth == "Old")
        signal_type = "Hit" if is_correct else "False Alarm"
    else:
        is_correct = (ground_truth == "New")
        signal_type = "Correct Rejection" if is_correct else "Miss"

    st.session_state.results.append({
        "trial_number": idx + 1,
        "word": current_trial["word"],
        "word_length": len(current_trial["word"]),
        "ground_truth": ground_truth,
        "user_response": user_choice,
        "is_correct": int(is_correct),
        "signal_type": signal_type,
        "reaction_time_sec": reaction_time
    })

    if idx + 1 >= len(st.session_state.trials):
        st.session_state.stage = "completed"
        st.session_state.total_session_time = round(now - st.session_state.experiment_start_time, 2)
    else:
        st.session_state.current_index += 1

# ==========================================
# 4. VIEW ROUTING
# ==========================================

# --- SCREEN 1: PRE-TASK START SCREEN ---
if st.session_state.stage == "ready":
    if not WORD_LIST:
        st.warning("Word list is currently empty. Populate `WORD_LIST` at the top of the script.")
        st.stop()

    if not st.session_state.trials:
        st.session_state.trials = generate_trial_schedule(WORD_LIST)

    st.markdown(
        """
        <div style="text-align: center; margin-top: 100px; margin-bottom: 30px;">
            <h1 style="font-size: 54px; font-weight: 700;">Are You Ready?</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    _, col_btn, _ = st.columns([1, 1.2, 1])
    with col_btn:
        st.button(
            "Click Here to Begin", 
            use_container_width=True, 
            on_click=start_experiment
        )

# --- SCREEN 2: ACTIVE RECOGNITION TEST ---
elif st.session_state.stage == "testing":
    idx = st.session_state.current_index
    current_trial = st.session_state.trials[idx]

    # Stimulus Display Card (all counters and headers hidden)
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 80px; margin-bottom: 50px;">
            <p style="font-size: 18px; color: #888; margin-bottom: 24px;">Is this word Familiar or Unfamiliar?</p>
            <h1 style="font-size: 72px; letter-spacing: 2px; font-weight: 600;">{current_trial['word']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.button("Unfamiliar", use_container_width=True, on_click=process_response, args=("Unfamiliar",))
    with c_btn2:
        st.button("Familiar", use_container_width=True, on_click=process_response, args=("Familiar",))

# --- SCREEN 3: COMPLETION & PASSWORD VERIFICATION ---
elif st.session_state.stage == "completed":
    st.markdown(
        """
        <div style="text-align: center; margin-top: 60px; margin-bottom: 30px;">
            <h2>Task Complete</h2>
            <p style="color: #666;">Thank you for your participation.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.show_password_box:
        _, c_show, _ = st.columns([1, 1, 1])
        with c_show:
            if st.button("Show Results", use_container_width=True):
                st.session_state.show_password_box = True
                st.rerun()

    if st.session_state.show_password_box:
        password_input = st.text_input("Enter Administrator Password:", type="password")

        if password_input == "backstreet":
            st.success("Authorized Access")
            
            records = st.session_state.results
            total_trials = len(records)
            total_time = st.session_state.total_session_time

            # Reaction time
            rts = [r["reaction_time_sec"] for r in records]
            avg_rt = np.mean(rts) if rts else 0.0

            # Correct vs Incorrect tallies
            total_correct = sum(1 for r in records if r["is_correct"] == 1)
            total_incorrect = sum(1 for r in records if r["is_correct"] == 0)

            # Signal Detection 2x2 matrix
            total_hits = sum(1 for r in records if r["signal_type"] == "Hit")
            total_misses = sum(1 for r in records if r["signal_type"] == "Miss")
            total_fa = sum(1 for r in records if r["signal_type"] == "False Alarm")
            total_cr = sum(1 for r in records if r["signal_type"] == "Correct Rejection")

            total_familiar_clicks = sum(1 for r in records if r["user_response"] == "Familiar")
            total_unfamiliar_clicks = sum(1 for r in records if r["user_response"] == "Unfamiliar")

            # Word length diagnostic
            correct_lengths = [r["word_length"] for r in records if r["is_correct"] == 1]
            avg_correct_length = np.mean(correct_lengths) if correct_lengths else 0.0

            st.markdown("### Overall Performance")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Time", f"{total_time:.2f} s")
            m_col2.metric("Avg Reaction Time", f"{avg_rt:.2f} s")
            m_col3.metric("Total Trials", total_trials)

            acc_col1, acc_col2, acc_col3 = st.columns(3)
            acc_col1.metric("Total Correct", f"{total_correct} / {total_trials}")
            acc_col2.metric("Total Incorrect", f"{total_incorrect} / {total_trials}")
            acc_col3.metric("Accuracy", f"{(total_correct / total_trials * 100):.1f}%")

            st.divider()
            st.markdown("### Signal Detection Matrix (2×2)")
            c_sd1, c_sd2 = st.columns(2)
            with c_sd1:
                st.metric("Total Hits (Old marked Familiar)", total_hits)
                st.metric("Total Misses (Old marked Unfamiliar)", total_misses)
            with c_sd2:
                st.metric("Total False Alarms (New marked Familiar)", total_fa)
                st.metric("Total Correct Rejections (New marked Unfamiliar)", total_cr)

            st.divider()
            st.markdown("### Response & Stimulus Diagnostics")
            d_col1, d_col2, d_col3 = st.columns(3)
            d_col1.metric("Times 'Familiar' Pressed", total_familiar_clicks)
            d_col2.metric("Times 'Unfamiliar' Pressed", total_unfamiliar_clicks)
            d_col3.metric("Avg Length of Correct Words", f"{avg_correct_length:.2f} letters")

            st.divider()
            if st.button("Reset Session for Next Participant"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
