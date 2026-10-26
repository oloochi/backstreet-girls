import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pattern Recognition Task", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 650px !important;
    }
    </style>
""", unsafe_allow_html=True)

TASK_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        user-select: none;
        -webkit-user-select: none;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: transparent;
        color: #FFFFFF;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        min-height: 100vh;
        padding-top: 20px;
        padding-bottom: 30px;
    }

    .screen {
        display: none;
        width: 100%;
        max-width: 520px;
        text-align: center;
    }
    .screen.active {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Typography */
    h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }
    h2 {
        font-size: 1.35rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    p {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #D1D5DB;
        margin-bottom: 1.8rem;
    }
    .status-text {
        font-size: 1rem;
        font-weight: 500;
        color: #9CA3AF;
        margin-bottom: 1.2rem;
        height: 1.4rem;
    }

    /* Primary Action Buttons */
    .btn-primary {
        background-color: #FF4B4B;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 14px 28px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.15s ease;
        width: 100%;
        max-width: 300px;
    }
    .btn-primary:hover {
        background-color: #E03E3E;
    }

    /* 3x3 Tile Grid */
    .grid-board {
        display: grid;
        grid-template-columns: repeat(3, 110px);
        grid-template-rows: repeat(3, 110px);
        gap: 12px;
        margin: 0 auto;
    }
    .tile {
        width: 110px;
        height: 110px;
        border-radius: 8px;
        border: 2px solid #333333;
        background-color: #262730;
        cursor: default;
        transition: background-color 0.05s ease, box-shadow 0.05s ease;
    }
    .tile.interactive {
        cursor: pointer;
    }
    .tile.interactive:hover {
        border-color: #555555;
    }
    .tile.active-flash {
        background-color: #FFFFFF !important;
        border-color: #FFFFFF !important;
        box-shadow: 0 0 18px rgba(255, 255, 255, 0.95) !important;
    }
    .tile.user-press {
        background-color: #4B5563 !important;
    }

    /* Admin Password & Unlock Section */
    .admin-input-group {
        display: flex;
        gap: 10px;
        width: 100%;
        max-width: 360px;
        margin: 1.5rem 0;
    }
    .password-input {
        flex: 1;
        padding: 10px 14px;
        border-radius: 6px;
        border: 1px solid #4B5563;
        background-color: #1F2937;
        color: #FFFFFF;
        font-size: 1rem;
        outline: none;
    }
    .password-input:focus {
        border-color: #FF4B4B;
    }
    .error-msg {
        color: #EF4444;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        display: none;
    }

    /* Metrics Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        width: 100%;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 14px;
        text-align: left;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F9FAFB;
    }

    /* Breakdown Table Details */
    details {
        width: 100%;
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        margin-bottom: 1.8rem;
        text-align: left;
        overflow: hidden;
    }
    summary {
        padding: 14px 18px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        color: #E5E7EB;
        list-style: none;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    summary::-webkit-details-marker {
        display: none;
    }
    summary::after {
        content: "▼";
        font-size: 0.75rem;
        color: #9CA3AF;
        transition: transform 0.2s ease;
    }
    details[open] summary::after {
        transform: rotate(180deg);
    }
    .table-wrapper {
        padding: 0 14px 14px 14px;
        overflow-x: auto;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        text-align: left;
    }
    th, td {
        padding: 8px 10px;
        border-bottom: 1px solid #374151;
    }
    th {
        color: #9CA3AF;
        font-weight: 600;
        font-size: 0.78rem;
        text-transform: uppercase;
    }
    tr:last-child td {
        border-bottom: none;
    }
    .tag-correct {
        color: #34D399;
        font-weight: 600;
    }
    .tag-incorrect {
        color: #F87171;
        font-weight: 600;
    }
</style>
</head>
<body>

<!-- 1. Start Screen -->
<div id="screen-intro" class="screen active">
    <h1>Pattern Recognition Task</h1>
    <p>
        A sequence of tiles will illuminate in white across the 3x3 grid one by one.<br>
        Watch closely, then reproduce the exact sequence in order by clicking the tiles.<br><br>
        Each level will display the previous pattern plus one new addition.<br>
        The test will continue until all sequences are finished.
    </p>
    <h2 style="margin-bottom: 1.5rem;">Are you ready?</h2>
    <button class="btn-primary" onclick="startTask()">Click Here to Begin</button>
</div>

<!-- 2. Testing Screen -->
<div id="screen-task" class="screen">
    <h2 id="seq-header">Sequence 1 of 10</h2>
    <div id="status-text" class="status-text">Watch the pattern carefully...</div>
    <div class="grid-board" id="grid">
        <div class="tile" data-idx="0"></div>
        <div class="tile" data-idx="1"></div>
        <div class="tile" data-idx="2"></div>
        <div class="tile" data-idx="3"></div>
        <div class="tile" data-idx="4"></div>
        <div class="tile" data-idx="5"></div>
        <div class="tile" data-idx="6"></div>
        <div class="tile" data-idx="7"></div>
        <div class="tile" data-idx="8"></div>
    </div>
</div>

<!-- 3. Completion & Password Protected Results -->
<div id="screen-complete" class="screen">
    <h1>Task Complete</h1>
    <p>Thank you! You have finished the pattern recognition evaluation.</p>
    <hr style="border: 0; border-top: 1px solid #374151; width: 100%; margin-bottom: 1.5rem;">

    <h2 style="font-size: 1.2rem;">Administrative Results</h2>
    <div class="admin-input-group" id="pw-group">
        <input type="password" id="admin-pw" class="password-input" placeholder="Enter password">
        <button class="btn-primary" style="max-width: 100px; padding: 10px;" onclick="unlockStats()">Unlock</button>
    </div>
    <div id="pw-error" class="error-msg">Incorrect password.</div>

    <div id="stats-container" style="display: none; width: 100%;">
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Completion Time</div>
                <div class="metric-val" id="metric-total-time">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Trials Correct</div>
                <div class="metric-val" id="metric-correct">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">First Error Length</div>
                <div class="metric-val" id="metric-first-error">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Max Completed Span</div>
                <div class="metric-val" id="metric-max-span">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Units Recalled (Partial)</div>
                <div class="metric-val" id="metric-total-units">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Planning Latency (RT1)</div>
                <div class="metric-val" id="metric-rt1">-</div>
            </div>
            <div class="metric-card" style="grid-column: span 2;">
                <div class="metric-label">Avg Execution Interval (Subsequent ITI)</div>
                <div class="metric-val" id="metric-subsequent-iti">-</div>
            </div>
        </div>

        <!-- Detailed Breakdown -->
        <details open>
            <summary>Trial-by-Trial Breakdown</summary>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Level</th>
                            <th>Outcome</th>
                            <th>Units Recalled</th>
                            <th>Planning RT1 (s)</th>
                            <th>Subsequent ITI (s)</th>
                        </tr>
                    </thead>
                    <tbody id="trial-rows"></tbody>
                </table>
            </div>
        </details>

        <button class="btn-primary" onclick="resetTask()">Reset for Next Participant</button>
    </div>
</div>

<script>
    const MAX_LEVEL = 10;
    const FLASH_DURATION = 500; // ms
    const GAP_DURATION = 250;   // ms

    let masterPattern = [];
    let currentLevel = 1;
    let userInput = [];
    let trialResults = [];
    let taskStartTime = 0;
    let taskEndTime = 0;
    let inputStartTime = 0;
    let lastClickTime = 0;
    let currentTrialLatencies = [];
    let isAcceptingInput = false;

    const tiles = document.querySelectorAll('.tile');

    function showScreen(id) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    // Prevents tile repeats > 2 times in a row
   const FIXED_PATTERN = [7, 1, 6, 2, 0, 8, 4, 5, 3, 6];

    function generateMasterPattern() {
        return [...FIXED_PATTERN];
    }
    function startTask() {
        masterPattern = generateMasterPattern();
        currentLevel = 1;
        trialResults = [];
        taskStartTime = performance.now();
        showScreen('screen-task');
        runPlayback();
    }

    function runPlayback() {
        isAcceptingInput = false;
        userInput = [];
        currentTrialLatencies = [];
        tiles.forEach(t => t.classList.remove('interactive'));

        document.getElementById('seq-header').innerText = `Sequence ${currentLevel} of ${MAX_LEVEL}`;
        document.getElementById('status-text').innerText = "Watch the pattern carefully...";

        const seq = masterPattern.slice(0, currentLevel);
        let step = 0;

        setTimeout(() => {
            function flashNext() {
                if (step < seq.length) {
                    const tileIdx = seq[step];
                    tiles[tileIdx].classList.add('active-flash');

                    setTimeout(() => {
                        tiles[tileIdx].classList.remove('active-flash');
                        step++;
                        setTimeout(flashNext, GAP_DURATION);
                    }, FLASH_DURATION);
                } else {
                    enableInputPhase();
                }
            }
            flashNext();
        }, 500);
    }

    function enableInputPhase() {
        isAcceptingInput = true;
        tiles.forEach(t => t.classList.add('interactive'));
        inputStartTime = performance.now();
        lastClickTime = inputStartTime;
        updateInputStatus();
    }

    function updateInputStatus() {
        document.getElementById('status-text').innerText = 
            `Reproduce the pattern: ${userInput.length} / ${currentLevel} tiles selected`;
    }

    tiles.forEach(tile => {
        tile.addEventListener('click', () => {
            if (!isAcceptingInput) return;

            const now = performance.now();
            const latency = (now - lastClickTime) / 1000;
            currentTrialLatencies.push(latency);
            lastClickTime = now;

            const idx = parseInt(tile.dataset.idx);
            userInput.push(idx);

            tile.classList.add('user-press');
            setTimeout(() => tile.classList.remove('user-press'), 120);

            updateInputStatus();

            if (userInput.length === currentLevel) {
                isAcceptingInput = false;
                evaluateLevel();
            }
        });
    });

    function evaluateLevel() {
        const targetSeq = masterPattern.slice(0, currentLevel);
        const isCorrect = JSON.stringify(userInput) === JSON.stringify(targetSeq);

        // Continuous units recalled before the first misfire in this sequence
        let unitsRecalled = 0;
        for (let i = 0; i < currentLevel; i++) {
            if (userInput[i] === targetSeq[i]) {
                unitsRecalled++;
            } else {
                break;
            }
        }

        // Planning latency (RT1) vs. Subsequent tapping latencies (ITI)
        const planningRT = currentTrialLatencies.length > 0 ? currentTrialLatencies[0] : 0.0;
        const subsequentLatencies = currentTrialLatencies.slice(1);

        trialResults.push({
            level: currentLevel,
            correct: isCorrect,
            unitsRecalled: unitsRecalled,
            planningRT: planningRT,
            subsequentLatencies: subsequentLatencies
        });

        if (currentLevel < MAX_LEVEL) {
            currentLevel++;
            setTimeout(runPlayback, 600);
        } else {
            taskEndTime = performance.now();
            setTimeout(showCompletionScreen, 500);
        }
    }

    function showCompletionScreen() {
        showScreen('screen-complete');
    }

    function unlockStats() {
        const pw = document.getElementById('admin-pw').value;
        const err = document.getElementById('pw-error');
        if (pw === "backstreet") {
            err.style.display = 'none';
            document.getElementById('pw-group').style.display = 'none';
            document.getElementById('stats-container').style.display = 'block';

            // 1. Completion time
            const totalSecs = (taskEndTime - taskStartTime) / 1000;
            const m = Math.floor(totalSecs / 60);
            const s = (totalSecs % 60).toFixed(1);
            document.getElementById('metric-total-time').innerText = `${m}m ${s}s`;

            // 2. Correct trials
            const correctCount = trialResults.filter(r => r.correct).length;
            document.getElementById('metric-correct').innerText = `${correctCount} / ${MAX_LEVEL}`;

            // 3. First error sequence length
            const firstFail = trialResults.find(r => !r.correct);
            document.getElementById('metric-first-error').innerText = firstFail ? `${firstFail.level} squares` : 'None (100%)';

            // 4. Maximum span achieved prior to first error
            let maxSpan = 0;
            for (let r of trialResults) {
                if (r.correct) {
                    maxSpan = r.level;
                } else {
                    break;
                }
            }
            document.getElementById('metric-max-span').innerText = `${maxSpan} squares`;

            // 5. Total continuous units recalled across all trials
            const totalUnits = trialResults.reduce((acc, r) => acc + r.unitsRecalled, 0);
            const maxPossibleUnits = (MAX_LEVEL * (MAX_LEVEL + 1)) / 2; // 55 for level 10
            document.getElementById('metric-total-units').innerText = `${totalUnits} / ${maxPossibleUnits}`;

            // 6. Avg Planning Latency (RT1)
            const allRT1 = trialResults.map(r => r.planningRT);
            const avgRT1 = allRT1.reduce((a, b) => a + b, 0) / (allRT1.length || 1);
            document.getElementById('metric-rt1').innerText = `${avgRT1.toFixed(2)} s`;

            // 7. Avg Execution Latency (Subsequent ITI)
            const allSubsequent = trialResults.flatMap(r => r.subsequentLatencies);
            const avgSubsequent = allSubsequent.length > 0 
                ? (allSubsequent.reduce((a, b) => a + b, 0) / allSubsequent.length) 
                : 0.0;
            document.getElementById('metric-subsequent-iti').innerText = `${avgSubsequent.toFixed(2)} s`;

            // 8. Detailed Breakdown Table
            const tbody = document.getElementById('trial-rows');
            tbody.innerHTML = '';
            trialResults.forEach(res => {
                const tr = document.createElement('tr');
                const avgSubLat = res.subsequentLatencies.length > 0
                    ? (res.subsequentLatencies.reduce((a, b) => a + b, 0) / res.subsequentLatencies.length).toFixed(3)
                    : '-';
                const tagClass = res.correct ? 'tag-correct' : 'tag-incorrect';
                const tagText = res.correct ? 'Correct' : 'Incorrect';

                tr.innerHTML = `
                    <td>${res.level}</td>
                    <td><span class="${tagClass}">${tagText}</span></td>
                    <td>${res.unitsRecalled} / ${res.level}</td>
                    <td>${res.planningRT.toFixed(3)}</td>
                    <td>${avgSubLat}</td>
                `;
                tbody.appendChild(tr);
            });

        } else {
            err.style.display = 'block';
        }
    }

    function resetTask() {
        document.getElementById('admin-pw').value = '';
        document.getElementById('pw-group').style.display = 'flex';
        document.getElementById('stats-container').style.display = 'none';
        document.getElementById('pw-error').style.display = 'none';
        showScreen('screen-intro');
    }
</script>
</body>
</html>
"""

components.html(TASK_HTML, height=780, scrolling=True)
