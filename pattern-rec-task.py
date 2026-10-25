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
        max-width: 500px;
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
        font-size: 1.4rem;
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

    /* Buttons */
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

    /* Admin Password & Results */
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
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        width: 100%;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 16px;
        text-align: left;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9CA3AF;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-val {
        font-size: 1.4rem;
        font-weight: 700;
        color: #F9FAFB;
    }

    /* Collapsible Breakdown Section */
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
        font-size: 1rem;
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
        font-size: 0.8rem;
        color: #9CA3AF;
        transition: transform 0.2s ease;
    }
    details[open] summary::after {
        transform: rotate(180deg);
    }
    .table-wrapper {
        padding: 0 16px 16px 16px;
        overflow-x: auto;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
        text-align: left;
    }
    th, td {
        padding: 10px 12px;
        border-bottom: 1px solid #374151;
    }
    th {
        color: #9CA3AF;
        font-weight: 600;
        font-size: 0.85rem;
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
        Each round displays the previous pattern plus one new addition.<br>
        The test will continue until all sequences are complete.
    </p>
    <h2 style="margin-bottom: 1.5rem;">Are you ready?</h2>
    <button class="btn-primary" onclick="startTask()">Click Here to Begin</button>
</div>

<!-- 2. Interactive Testing Screen -->
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

<!-- 3. Completion & Password-Protected Results Screen -->
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
                <div class="metric-label">Avg Press Latency</div>
                <div class="metric-val" id="metric-avg-latency">-</div>
            </div>
        </div>

        <!-- Detailed Breakdown -->
        <details open>
            <summary>Trial Breakdown</summary>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Sequence Length</th>
                            <th>Result</th>
                            <th>Avg Press Latency (s)</th>
                        </tr>
                    </thead>
                    <tbody id="trial-rows">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </details>

        <button class="btn-primary" onclick="resetTask()">Reset for Next Participant</button>
    </div>
</div>

<script>
    const MAX_LEVEL = 10;
    const FLASH_DURATION = 550; // ms
    const GAP_DURATION = 150;   // ms

    let masterPattern = [];
    let currentLevel = 1;
    let userInput = [];
    let trialResults = [];
    let taskStartTime = 0;
    let taskEndTime = 0;
    let lastClickTime = 0;
    let currentTrialLatencies = [];
    let isAcceptingInput = false;

    const tiles = document.querySelectorAll('.tile');

    function showScreen(id) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    function generateMasterPattern() {
        const pattern = [];
        for (let i = 0; i < MAX_LEVEL; i++) {
            let nextTile;
            do {
                nextTile = Math.floor(Math.random() * 9);
            // Re-roll if the candidate matches the preceding two selections
            } while (i >= 2 && nextTile === pattern[i - 1] && nextTile === pattern[i - 2]);
            
            pattern.push(nextTile);
        }
        return pattern;
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
        }, 400);
    }

    function enableInputPhase() {
        isAcceptingInput = true;
        tiles.forEach(t => t.classList.add('interactive'));
        lastClickTime = performance.now();
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
            currentTrialLatencies.push((now - lastClickTime) / 1000);
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

        trialResults.push({
            level: currentLevel,
            correct: isCorrect,
            latencies: [...currentTrialLatencies]
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

            // 1. Total Time
            const totalSecs = (taskEndTime - taskStartTime) / 1000;
            const m = Math.floor(totalSecs / 60);
            const s = (totalSecs % 60).toFixed(1);
            document.getElementById('metric-total-time').innerText = `${m}m ${s}s`;

            // 2. Correct Trials
            const correctCount = trialResults.filter(r => r.correct).length;
            document.getElementById('metric-correct').innerText = `${correctCount} / ${MAX_LEVEL}`;

            // 3. First Error Sequence Length
            const firstFail = trialResults.find(r => !r.correct);
            document.getElementById('metric-first-error').innerText = firstFail ? `${firstFail.level} squares` : 'None (100%)';

            // 4. Avg Time per Tile
            const allLatencies = trialResults.flatMap(r => r.latencies);
            const avgLatency = allLatencies.reduce((a, b) => a + b, 0) / (allLatencies.length || 1);
            document.getElementById('metric-avg-latency').innerText = `${avgLatency.toFixed(2)} s`;

            // 5. Populate Detailed Table Rows
            const tbody = document.getElementById('trial-rows');
            tbody.innerHTML = '';
            trialResults.forEach(res => {
                const tr = document.createElement('tr');
                const avgTrialLat = res.latencies.length > 0
                    ? (res.latencies.reduce((a, b) => a + b, 0) / res.latencies.length).toFixed(3)
                    : '0.000';
                const tagClass = res.correct ? 'tag-correct' : 'tag-incorrect';
                const tagText = res.correct ? 'Correct' : 'Incorrect';

                tr.innerHTML = `
                    <td>${res.level}</td>
                    <td><span class="${tagClass}">${tagText}</span></td>
                    <td>${avgTrialLat}</td>
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

components.html(TASK_HTML, height=750, scrolling=True)
