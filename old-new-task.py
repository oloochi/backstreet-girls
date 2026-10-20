import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# 1. STIMULUS POOL CONFIGURATION
# ==========================================
# Insert your list of 75 unique words for this specific version/treatment below:
# WORD_LIST = "ball boss buck dirt door drop east flat gold hair hole lake mess mild nest park post rain ring yard anger beach bench brain bread brush chain chair clock crash dress flame flesh hotel knife mouth paint shirt snake train bottle bridge bucket butter canyon carpet closet danger drawer engine finger guitar jungle market pencil pocket silver spider ticket window blanket channel feather kitchen station village hospital mountain railroad sandwich stranger apartment machinery instrument television".split()
# WORD_LIST = ["boat, card, coal, dust, fish, frog, iron, lion, meat, moon, path, pipe, roof, rope, sand, seat, ship, song, suit, wind, apple, blade, brick, cabin, chalk, chest, cliff, cloud, crown, fruit, grass, heart, horse, metal, money, motor, penny, river, stone, wheel, barrel, basket, camera, castle, circle, cotton, cradle, donkey, forest, garage, hammer, island, kettle, monkey, pillow, rabbit, rocket, stream, throat, turkey, bulletin, curtain, factory, highway, luggage, surface, calendar, elevator, platform, sidewalk, umbrella, orchestra, passenger, locomotive, restaurant"]
# WORD_LIST = ["bell, bone, boot, bowl, cake, clay, coat, coin, corn, crow, deer, desk, drum, duck, fork, gate, hill, lamp, leaf, rock, block, board, camel, fence, flute, glass, globe, grape, honey, house, lemon, mouse, onion, paper, pilot, plate, radio, salad, sugar, table, bullet, cheese, cherry, coffee, cookie, cousin, dinner, flight, freeze, garlic, jacket, ladder, lizard, meadow, noodle, palace, parrot, powder, saddle, tunnel, airport, bedroom, compass, mailbox, morning, uniform, basement, corridor, monument, notebook, shoulder, companion, gentleman, motorcycle, helicopter"]
# WORD_LIST = ["band, bath, belt, camp, date, farm, flag, game, hand, moon, page, pool, road, shoe, skin, star, tail, tent, tree, wall, badge, broom, clerk, flock, flour, ghost, jeans, liver, lunch, pearl, piano, queen, scarf, shark, sheep, skirt, smoke, spoon, stick, towel, anchor, beetle, border, button, carrot, cattle, church, doctor, drawer, kitten, magnet, muffin, napkin, packet, pigeon, ribbon, salmon, statue, string, weapon, cottage, package, parade, receipt, stomach, theater, daughter, envelope, neighbor, property, suitcase, newspaper, performer, blacksmith, calculator"]
WORD_LIST = ["ball, park, drum, gate, hill, leaf, bone, bell, flag, instrument, cousin, cottage"]

# Set to True for testing with dummy words if WORD_LIST is empty
DEBUG_MODE = False
if not WORD_LIST and DEBUG_MODE:
    WORD_LIST = [f"sample_{i}" for i in range(75)]

# ==========================================
# 2. TRIAL SCHEDULE GENERATOR
# ==========================================
def generate_trial_schedule(words, min_lag=2, max_attempts=1000):
    for _ in range(max_attempts):
        pool_new = list(words)
        np.random.shuffle(pool_new)
        
        schedule = []
        pending_repeats = []
        
        while pool_new or pending_repeats:
            valid_repeats = [
                w for w in pending_repeats 
                if (len(schedule) - schedule.index((w, "New")) - 1) >= min_lag
            ]
            
            can_draw_new = len(pool_new) > 0
            can_draw_old = len(valid_repeats) > 0
            
            if can_draw_new and can_draw_old:
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
            
    # Deterministic fallback
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
            
            # Metrics derivations
            rts = [r["reaction_time_sec"] for r in records]
            avg_rt = np.mean(rts) if rts else 0.0
            
            total_hits = sum(1 for r in records if r["signal_type"] == "Hit")
            total_misses = sum(1 for r in records if r["signal_type"] == "Miss")
            total_familiar_clicks = sum(1 for r in records if r["user_response"] == "Familiar")
            
            correct_lengths = [r["word_length"] for r in records if r["is_correct"] == 1]
            avg_correct_length = np.mean(correct_lengths) if correct_lengths else 0.0

            st.markdown("### Participant Summary Metrics")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Time", f"{total_time:.2f} s")
            m_col2.metric("Avg Reaction Time", f"{avg_rt:.2f} s")
            m_col3.metric("Total Trials", total_trials)

            m_col4, m_col5, m_col6 = st.columns(3)
            m_col4.metric("Total Hits", total_hits)
            m_col5.metric("Total Misses", total_misses)
            m_col6.metric("Times 'Familiar' Pressed", total_familiar_clicks)

            st.metric("Avg Length of Correct Words", f"{avg_correct_length:.2f} letters")

            st.divider()
            if st.button("Reset Session for Next Participant"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        elif password_input != "":
            st.error("Incorrect password. Please try again.")
