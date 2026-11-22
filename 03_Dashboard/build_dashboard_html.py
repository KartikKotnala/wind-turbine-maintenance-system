import os
from pathlib import Path

dashboard_dir = Path(r"c:\Users\veerk\Downloads\PRJ4\03_Dashboard")
html_file = dashboard_dir / "index.html"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wind Turbine Predictive Maintenance | NBM Digital Twin Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .chart-container { position: relative; width: 100%; height: 260px; }
    canvas { display: block; width: 100%; height: 100%; }
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased flex flex-col selection:bg-cyan-500 selection:text-black">

  <!-- TOP HEADER -->
  <header class="bg-slate-900/90 border-b border-slate-800 backdrop-blur sticky top-0 z-50 px-6 py-3.5">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <svg class="w-6 h-6 text-white animate-spin-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4m15.364-5.364l-11.314 11.314m11.314 0L7.686 6.686" />
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            Wind Turbine Predictive Maintenance
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">NBM Digital Twin</span>
          </h1>
          <p class="text-xs text-slate-400">Wind Farm A &bull; Asset #0 &bull; Generator Drive-End Bearing (<span class="font-mono text-cyan-400">sensor_13_avg</span>)</p>
        </div>
      </div>

      <!-- STATUS PILL -->
      <div class="flex items-center gap-3">
        <div id="system-status-badge" class="px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-2 border bg-emerald-950/80 text-emerald-300 border-emerald-700/60 shadow-sm transition-all duration-300">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span id="system-status-text">SYSTEM NORMAL &bull; RESIDUALS IN PHYSICAL BOUNDS</span>
        </div>
      </div>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto w-full px-6 py-5 flex-1 space-y-5">

    <!-- CONTROLS ROW -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80 shadow-md">
      
      <!-- STREAM SWITCHER -->
      <div class="lg:col-span-4 flex flex-col gap-1.5">
        <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Test Operational Stream</label>
        <div class="inline-flex rounded-xl p-1 bg-slate-950 border border-slate-800">
          <button id="btn-stream-fail" onclick="switchStream('event_0_failure')" class="flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all duration-200 bg-red-950/70 text-red-300 border border-red-800/80 shadow-sm flex items-center justify-center gap-1.5">
            <span>🚨</span> Event 0: Bearing Failure
          </button>
          <button id="btn-stream-norm" onclick="switchStream('event_24_normal')" class="flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all duration-200 text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5">
            <span>🛡️</span> Event 24: Healthy Test
          </button>
        </div>
      </div>

      <!-- MODEL SWITCHER -->
      <div class="lg:col-span-8 flex flex-col gap-1.5">
        <label class="text-xs font-medium text-slate-400 uppercase tracking-wider flex justify-between">
          <span>Active NBM Architecture</span>
          <span id="model-score-pill" class="text-cyan-400 font-mono text-xs">F1: 0.85 | FAR: 0.00%</span>
        </label>
        <div class="grid grid-cols-5 gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button onclick="switchModel('GRU')" id="btn-model-GRU" class="model-btn py-1.5 px-2 rounded-lg text-xs font-semibold bg-cyan-600 text-white shadow transition-all flex flex-col items-center">
            <span>GRU</span><span class="text-[10px] opacity-80 font-mono">F1 0.85</span>
          </button>
          <button onclick="switchModel('LSTM')" id="btn-model-LSTM" class="model-btn py-1.5 px-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex flex-col items-center">
            <span>LSTM</span><span class="text-[10px] opacity-80 font-mono">F1 0.84</span>
          </button>
          <button onclick="switchModel('Transformer')" id="btn-model-Transformer" class="model-btn py-1.5 px-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex flex-col items-center">
            <span>Transformer</span><span class="text-[10px] opacity-80 font-mono">F1 0.78</span>
          </button>
          <button onclick="switchModel('XGBoost')" id="btn-model-XGBoost" class="model-btn py-1.5 px-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex flex-col items-center">
            <span>XGBoost</span><span class="text-[10px] opacity-80 font-mono">F1 0.68</span>
          </button>
          <button onclick="switchModel('TCN')" id="btn-model-TCN" class="model-btn py-1.5 px-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex flex-col items-center">
            <span>TCN</span><span class="text-[10px] opacity-80 font-mono">F1 0.41</span>
          </button>
        </div>
      </div>
    </div>

    <!-- KPI CARDS -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <!-- KPI 1 -->
      <div class="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl shadow-sm">
        <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Actual Bearing Temp</div>
        <div class="mt-1 flex items-baseline gap-1.5">
          <span id="kpi-actual-temp" class="text-2xl font-bold font-mono text-white">--</span>
          <span class="text-xs text-slate-400">°C</span>
        </div>
        <div id="kpi-temp-sub" class="text-[11px] text-slate-500 mt-1 flex items-center gap-1">Physical sensor</div>
      </div>

      <!-- KPI 2 -->
      <div class="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl shadow-sm">
        <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">NBM Expected Temp</div>
        <div class="mt-1 flex items-baseline gap-1.5">
          <span id="kpi-expected-temp" class="text-2xl font-bold font-mono text-cyan-400">--</span>
          <span class="text-xs text-slate-400">°C</span>
        </div>
        <div class="text-[11px] text-slate-500 mt-1">Physics baseline</div>
      </div>

      <!-- KPI 3 -->
      <div class="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl shadow-sm">
        <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Thermal Residual (rt)</div>
        <div class="mt-1 flex items-baseline gap-1.5">
          <span id="kpi-residual" class="text-2xl font-bold font-mono text-white">--</span>
          <span class="text-xs text-slate-400">°C</span>
        </div>
        <div id="kpi-residual-sub" class="text-[11px] text-slate-500 mt-1">Dev: T - T̂</div>
      </div>

      <!-- KPI 4 -->
      <div class="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl shadow-sm">
        <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">CUSUM Score (St)</div>
        <div class="mt-1 flex items-baseline gap-1.5">
          <span id="kpi-cusum" class="text-2xl font-bold font-mono text-purple-400">--</span>
          <span class="text-xs text-slate-400" id="kpi-thresh-target">/ --</span>
        </div>
        <div class="text-[11px] text-slate-500 mt-1">Accumulated drift</div>
      </div>

      <!-- KPI 5 -->
      <div class="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl shadow-sm">
        <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Alarm Counter</div>
        <div class="mt-1 flex items-baseline gap-1.5">
          <span id="kpi-alarm-counter" class="text-2xl font-bold font-mono text-white">--</span>
          <span class="text-xs text-slate-400" id="kpi-persist-target">/ -- steps</span>
        </div>
        <div id="kpi-counter-sub" class="text-[11px] text-slate-500 mt-1">Persistence gate</div>
      </div>

      <!-- KPI 6 -->
      <div class="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl shadow-sm">
        <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Detection Earliness</div>
        <div class="mt-1 flex items-baseline gap-1.5">
          <span id="kpi-lead-time" class="text-2xl font-bold font-mono text-amber-400">34.7h</span>
        </div>
        <div class="text-[11px] text-slate-500 mt-1">Prior to 60°C trip</div>
      </div>
    </div>

    <!-- TIMELINE & PLAYBACK CONTROLLER -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <button id="btn-play" onclick="togglePlay()" class="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-1.5 px-4 rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-md shadow-cyan-600/20">
            <span id="play-icon">▶</span> <span id="play-text">Play Simulation</span>
          </button>
          <button onclick="resetPlayback()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-1.5 px-3 rounded-xl text-xs transition-all">
            ⏮ Start
          </button>
          <button onclick="stepForward(1)" class="bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-1.5 px-3 rounded-xl text-xs transition-all">
            Step +1h
          </button>
          <button onclick="stepForward(6)" class="bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-1.5 px-3 rounded-xl text-xs transition-all">
            Step +6h
          </button>
          <select id="play-speed" class="bg-slate-800 border border-slate-700 text-slate-300 rounded-xl px-2 py-1 text-xs outline-none">
            <option value="200">Speed: 1x</option>
            <option value="80" selected>Speed: 3x</option>
            <option value="30">Speed: 10x</option>
          </select>
        </div>

        <div class="flex items-center gap-4 text-xs font-mono">
          <div class="text-slate-400">Timestamp: <span id="current-timestamp" class="text-cyan-300 font-semibold">2023-08-04 06:10:00</span></div>
          <div class="text-slate-400">SCADA ID: <span id="current-id" class="text-white">52148</span></div>
          <div class="text-slate-400">Power: <span id="current-power" class="text-emerald-400">-- kW</span></div>
          <div class="text-slate-400">Wind: <span id="current-wind" class="text-blue-400">-- m/s</span></div>
        </div>
      </div>

      <!-- RANGE SLIDER -->
      <div class="relative pt-1">
        <input type="range" id="time-slider" min="0" max="383" value="0" oninput="onSliderChange(this.value)"
               class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500">
        <div class="flex justify-between text-[11px] text-slate-500 mt-1">
          <span>Simulation Start</span>
          <span id="slider-event-marker" class="text-amber-400 font-medium font-mono">▲ Pre-Fault 48h Window</span>
          <span>Simulation End</span>
        </div>
      </div>
    </div>

    <!-- CHARTS SECTION -->
    <div class="space-y-4">

      <!-- CHART 1: ACTUAL VS EXPECTED -->
      <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between mb-2">
          <div>
            <h3 class="text-sm font-semibold text-white flex items-center gap-2">
              <span>1. Physical Thermal Physics Trajectory</span>
              <span class="text-xs font-normal text-slate-400">Actual ($T_{actual}$) vs Normal Behavior Model ($T̂_{expected}$)</span>
            </h3>
          </div>
          <div class="flex items-center gap-4 text-xs">
            <span class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-red-500 rounded"></span> Actual Bearing Temp</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-cyan-400 rounded"></span> NBM Expected Temp</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 bg-amber-500/20 border border-amber-500/60 rounded"></span> Pre-fault 48h</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="chart-temp"></canvas>
        </div>
      </div>

      <!-- CHART 2 & 3: GRID -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        
        <!-- CHART 2: THERMAL RESIDUAL -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-semibold text-white flex items-center gap-2">
              <span>2. Thermal Residual Anomaly ($r_t = T - T̂$)</span>
            </h3>
            <span class="text-xs text-slate-400 font-mono">Zero Mean Baseline</span>
          </div>
          <div class="chart-container">
            <canvas id="chart-residual"></canvas>
          </div>
        </div>

        <!-- CHART 3: CUSUM ACCUMULATION -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-semibold text-white flex items-center gap-2">
              <span>3. CUSUM Accumulation ($S_t$) & Alarm Layer</span>
            </h3>
            <span class="text-xs text-purple-400 font-mono" id="chart-thresh-label">Threshold: --</span>
          </div>
          <div class="chart-container">
            <canvas id="chart-cusum"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- CALIBRATION TUNER & BENCHMARK MATRIX -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

      <!-- TUNER (4 COLS) -->
      <div class="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 class="text-sm font-semibold text-white flex items-center gap-2">
            <svg class="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Interactive CUSUM Parameter Tuner
          </h3>
          <button onclick="resetTuningToFrozen()" class="text-xs text-cyan-400 hover:text-cyan-300 font-medium">Reset to Frozen</button>
        </div>

        <p class="text-xs text-slate-400">
          Adjust detector parameters live to observe how drift filtering ($k$) and persistence ($p$) prevent false alarms without missing true degradation.
        </p>

        <!-- K SLIDER -->
        <div class="space-y-1.5">
          <div class="flex justify-between text-xs font-medium">
            <span class="text-slate-300">Reference Drift ($k$)</span>
            <span id="tune-k-val" class="font-mono text-cyan-400">3.61 °C</span>
          </div>
          <input type="range" id="tune-k" min="0.5" max="8.0" step="0.1" value="3.6" oninput="onTuningChange()"
                 class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500">
          <div class="flex justify-between text-[10px] text-slate-500">
            <span>0.5°C (High sensitivity)</span>
            <span>8.0°C (High tolerance)</span>
          </div>
        </div>

        <!-- THRESHOLD SLIDER -->
        <div class="space-y-1.5">
          <div class="flex justify-between text-xs font-medium">
            <span class="text-slate-300">CUSUM Threshold ($\tau$)</span>
            <span id="tune-thresh-val" class="font-mono text-purple-400">36.03</span>
          </div>
          <input type="range" id="tune-thresh" min="0.0" max="80.0" step="0.5" value="36.0" oninput="onTuningChange()"
                 class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
          <div class="flex justify-between text-[10px] text-slate-500">
            <span>0.0 (Immediate)</span>
            <span>80.0 (Strict accumulation)</span>
          </div>
        </div>

        <!-- PERSISTENCE SLIDER -->
        <div class="space-y-1.5">
          <div class="flex justify-between text-xs font-medium">
            <span class="text-slate-300">Persistence Steps ($p$)</span>
            <span id="tune-persist-val" class="font-mono text-amber-400">4 steps (40 min)</span>
          </div>
          <input type="range" id="tune-persist" min="1" max="8" step="1" value="4" oninput="onTuningChange()"
                 class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500">
          <div class="flex justify-between text-[10px] text-slate-500">
            <span>1 step (Single spike)</span>
            <span>8 steps (Sustained trend)</span>
          </div>
        </div>

        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
          <div class="font-semibold text-slate-300">Methodology Note:</div>
          <div>In the final evaluation notebook, all parameters were tuned strictly on healthy validation data and frozen before test evaluation.</div>
        </div>
      </div>

      <!-- BENCHMARK TABLE (7 COLS) -->
      <div class="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
            <h3 class="text-sm font-semibold text-white">Frozen Benchmark Evaluation Leaderboard</h3>
            <span class="text-xs text-slate-400 font-mono">Wind Farm A Evaluated</span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="text-[11px] text-slate-400 uppercase bg-slate-950/60 border-b border-slate-800">
                <tr>
                  <th class="py-2.5 px-3 font-semibold">Model</th>
                  <th class="py-2.5 px-2 font-semibold">F1-Score</th>
                  <th class="py-2.5 px-2 font-semibold">Precision</th>
                  <th class="py-2.5 px-2 font-semibold">Recall</th>
                  <th class="py-2.5 px-2 font-semibold">Test FAR</th>
                  <th class="py-2.5 px-2 font-semibold">PR-AUC</th>
                </tr>
              </thead>
              <tbody id="benchmark-tbody" class="divide-y divide-slate-800/60 font-mono">
                <!-- Dynamically populated from NBM_DATA -->
              </tbody>
            </table>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>🏆 Top Architecture: <strong class="text-cyan-400 font-semibold font-mono">GRU Regressor</strong></span>
          <span>Zero False Alarms: <strong class="text-emerald-400 font-mono">0.00% FAR</strong> on Healthy Test</span>
        </div>
      </div>
    </div>
  </main>

  <!-- DATA EMBED -->
  <script src="data.js"></script>

  <!-- DASHBOARD ENGINE SCRIPT -->
  <script>
    // State
    let currentStreamKey = 'event_0_failure';
    let currentModelName = 'GRU';
    let currentIndex = 0;
    let isPlaying = false;
    let playInterval = null;

    // Custom Live Parameters
    let customParams = {
      k: 3.61,
      threshold: 36.03,
      persistence: 4
    };

    // DOM Elements
    const slider = document.getElementById('time-slider');
    const playBtn = document.getElementById('btn-play');
    const playText = document.getElementById('play-text');
    const playIcon = document.getElementById('play-icon');

    // Canvas references
    const canvasTemp = document.getElementById('chart-temp');
    const canvasRes = document.getElementById('chart-residual');
    const canvasCusum = document.getElementById('chart-cusum');

    // Init
    window.addEventListener('DOMContentLoaded', () => {
      initBenchmarkTable();
      resetTuningToFrozen();
      renderDashboard();
      window.addEventListener('resize', renderCharts);
    });

    function initBenchmarkTable() {
      const tbody = document.getElementById('benchmark-tbody');
      tbody.innerHTML = '';
      if (!window.NBM_DATA || !NBM_DATA.benchmark) return;

      NBM_DATA.benchmark.forEach(row => {
        const model = (row['Model'] || row['Model      '] || '').trim();
        const f1 = parseFloat(row['F1-Score']).toFixed(4);
        const prec = parseFloat(row['Precision']).toFixed(4);
        const rec = parseFloat(row['Recall (Detection Rate)']).toFixed(4);
        const far = (parseFloat(row['Test FAR']) * 100).toFixed(2) + '%';
        const prAuc = parseFloat(row['PR-AUC']).toFixed(4);

        const isBest = model === 'GRU';
        const tr = document.createElement('tr');
        tr.className = isBest ? 'bg-cyan-950/30 text-white font-medium' : 'text-slate-300 hover:bg-slate-800/30';
        tr.innerHTML = `
          <td class="py-2.5 px-3 flex items-center gap-1.5 font-sans font-semibold text-white">
            ${isBest ? '⭐' : ''} ${model}
          </td>
          <td class="py-2.5 px-2 text-cyan-400">${f1}</td>
          <td class="py-2.5 px-2">${prec}</td>
          <td class="py-2.5 px-2">${rec}</td>
          <td class="py-2.5 px-2 ${row['Test FAR'] == 0 ? 'text-emerald-400' : 'text-amber-400'}">${far}</td>
          <td class="py-2.5 px-2 text-purple-400">${prAuc}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function switchStream(streamKey) {
      currentStreamKey = streamKey;
      currentIndex = 0;
      slider.value = 0;
      stopPlayback();

      const btnFail = document.getElementById('btn-stream-fail');
      const btnNorm = document.getElementById('btn-stream-norm');

      if (streamKey === 'event_0_failure') {
        btnFail.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all bg-red-950/70 text-red-300 border border-red-800/80 shadow-sm flex items-center justify-center gap-1.5';
        btnNorm.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5';
        document.getElementById('slider-event-marker').innerText = '▲ Pre-Fault 48h Window';
      } else {
        btnNorm.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all bg-emerald-950/70 text-emerald-300 border border-emerald-800/80 shadow-sm flex items-center justify-center gap-1.5';
        btnFail.className = 'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5';
        document.getElementById('slider-event-marker').innerText = '▲ Fully Healthy Stream';
      }

      const stream = NBM_DATA.streams[currentStreamKey];
      slider.max = stream.telemetry.times.length - 1;
      resetTuningToFrozen();
      renderDashboard();
    }

    function switchModel(modelName) {
      currentModelName = modelName;
      document.querySelectorAll('.model-btn').forEach(b => {
        b.className = 'model-btn py-1.5 px-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex flex-col items-center';
      });
      const activeBtn = document.getElementById(`btn-model-${modelName}`);
      if (activeBtn) {
        activeBtn.className = 'model-btn py-1.5 px-2 rounded-lg text-xs font-semibold bg-cyan-600 text-white shadow transition-all flex flex-col items-center';
      }
      resetTuningToFrozen();
      renderDashboard();
    }

    function resetTuningToFrozen() {
      const stream = NBM_DATA.streams[currentStreamKey];
      const modelData = stream.models[currentModelName];
      if (modelData && modelData.config) {
        customParams.k = modelData.config.k;
        customParams.threshold = modelData.config.threshold;
        customParams.persistence = modelData.config.persistence;

        document.getElementById('tune-k').value = customParams.k;
        document.getElementById('tune-k-val').innerText = customParams.k.toFixed(2) + ' °C';

        document.getElementById('tune-thresh').value = customParams.threshold;
        document.getElementById('tune-thresh-val').innerText = customParams.threshold.toFixed(2);

        document.getElementById('tune-persist').value = customParams.persistence;
        document.getElementById('tune-persist-val').innerText = customParams.persistence + ' steps (' + (customParams.persistence*10) + ' min)';
      }
      renderDashboard();
    }

    function onTuningChange() {
      customParams.k = parseFloat(document.getElementById('tune-k').value);
      customParams.threshold = parseFloat(document.getElementById('tune-thresh').value);
      customParams.persistence = parseInt(document.getElementById('tune-persist').value);

      document.getElementById('tune-k-val').innerText = customParams.k.toFixed(2) + ' °C';
      document.getElementById('tune-thresh-val').innerText = customParams.threshold.toFixed(2);
      document.getElementById('tune-persist-val').innerText = customParams.persistence + ' steps (' + (customParams.persistence*10) + ' min)';

      recomputeLiveCUSUM();
      renderDashboard();
    }

    // Dynamic live CUSUM recomputation on slider changes
    function recomputeLiveCUSUM() {
      const stream = NBM_DATA.streams[currentStreamKey];
      const modelData = stream.models[currentModelName];
      const residuals = modelData.residuals;

      let s = 0.0;
      let scores = [];
      let alarms = [];
      let counter = 0;

      for (let i = 0; i < residuals.length; i++) {
        let r = residuals[i];
        s = Math.max(0.0, s + (r - customParams.k));
        scores.push(parseFloat(s.toFixed(2)));

        let c_trig = (s > customParams.threshold);
        let e_trig = (r > 12.5); // extreme spike
        if (c_trig || e_trig) counter++;
        else counter = Math.max(0, counter - 1);

        alarms.push(counter >= customParams.persistence ? 1 : 0);
      }

      modelData.liveScores = scores;
      modelData.liveAlarms = alarms;
    }

    function onSliderChange(val) {
      currentIndex = parseInt(val);
      renderDashboard();
    }

    function togglePlay() {
      if (isPlaying) stopPlayback();
      else startPlayback();
    }

    function startPlayback() {
      isPlaying = true;
      playText.innerText = 'Pause';
      playIcon.innerText = '⏸';
      playBtn.className = 'bg-amber-600 hover:bg-amber-500 text-white font-semibold py-1.5 px-4 rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-md';

      const speed = parseInt(document.getElementById('play-speed').value);
      const stream = NBM_DATA.streams[currentStreamKey];
      const maxLen = stream.telemetry.times.length;

      playInterval = setInterval(() => {
        if (currentIndex >= maxLen - 1) {
          currentIndex = 0;
        } else {
          currentIndex++;
        }
        slider.value = currentIndex;
        renderDashboard();
      }, speed);
    }

    function stopPlayback() {
      isPlaying = false;
      playText.innerText = 'Play Simulation';
      playIcon.innerText = '▶';
      playBtn.className = 'bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-1.5 px-4 rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-md shadow-cyan-600/20';
      if (playInterval) clearInterval(playInterval);
    }

    function resetPlayback() {
      stopPlayback();
      currentIndex = 0;
      slider.value = 0;
      renderDashboard();
    }

    function stepForward(hours) {
      stopPlayback();
      const stream = NBM_DATA.streams[currentStreamKey];
      currentIndex = Math.min(stream.telemetry.times.length - 1, currentIndex + hours);
      slider.value = currentIndex;
      renderDashboard();
    }

    // MAIN RENDER FUNCTION
    function renderDashboard() {
      const stream = NBM_DATA.streams[currentStreamKey];
      const modelData = stream.models[currentModelName];
      const telem = stream.telemetry;

      const idx = Math.min(currentIndex, telem.times.length - 1);

      // KPI extraction
      const actualT = telem.actual_temp[idx];
      const expT = modelData.expected_temp[idx];
      const res = modelData.residuals[idx];
      const scores = modelData.liveScores || modelData.cusum_scores;
      const alarms = modelData.liveAlarms || modelData.alarms;
      const cusum = scores[idx];
      const isAlarm = alarms[idx] === 1;

      // Update KPIs
      document.getElementById('kpi-actual-temp').innerText = actualT.toFixed(1);
      document.getElementById('kpi-expected-temp').innerText = expT.toFixed(1);
      
      const resElem = document.getElementById('kpi-residual');
      resElem.innerText = (res >= 0 ? '+' : '') + res.toFixed(2);
      resElem.className = res > 5.0 ? 'text-2xl font-bold font-mono text-red-400' :
                          res > 2.5 ? 'text-2xl font-bold font-mono text-amber-400' : 'text-2xl font-bold font-mono text-white';

      document.getElementById('kpi-cusum').innerText = cusum.toFixed(1);
      document.getElementById('kpi-thresh-target').innerText = '/ ' + customParams.threshold.toFixed(1);

      document.getElementById('kpi-alarm-counter').innerText = isAlarm ? customParams.persistence : '0';
      document.getElementById('kpi-persist-target').innerText = `/ ${customParams.persistence} steps`;

      // Status Badge
      const statusBadge = document.getElementById('system-status-badge');
      const statusText = document.getElementById('system-status-text');

      if (isAlarm) {
        statusBadge.className = 'px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-2 border bg-red-950/90 text-red-300 border-red-700/80 shadow-lg shadow-red-950 animate-pulse';
        statusText.innerText = '🚨 CRITICAL PERSISTENT FAULT ALARM: THERMAL RUNAWAY DEGRADATION';
      } else if (res > 3.0 || cusum > (customParams.threshold * 0.5)) {
        statusBadge.className = 'px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-2 border bg-amber-950/80 text-amber-300 border-amber-700/60 shadow-sm';
        statusText.innerText = '⚠️ PRE-FAULT THERMAL ANOMALY: RESIDUAL DEVIATION ELEVATED';
      } else {
        statusBadge.className = 'px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-2 border bg-emerald-950/80 text-emerald-300 border-emerald-700/60 shadow-sm';
        statusText.innerText = 'SYSTEM NORMAL &bull; SCADA WITHIN EXPECTED NBM PHYSICS';
      }

      // Telemetry row
      document.getElementById('current-timestamp').innerText = telem.times[idx];
      document.getElementById('current-id').innerText = telem.ids[idx];
      document.getElementById('current-power').innerText = (telem.power_kw[idx] * 2000).toFixed(0) + ' kW';
      document.getElementById('current-wind').innerText = telem.wind_speed[idx].toFixed(1) + ' m/s';

      document.getElementById('chart-thresh-label').innerText = `Threshold: ${customParams.threshold.toFixed(1)}`;

      // Render Charts
      renderCharts();
    }

    // NATIVE CANVAS CHART RENDERER (Fast, Responsive, 100% Offline)
    function renderCharts() {
      const stream = NBM_DATA.streams[currentStreamKey];
      const modelData = stream.models[currentModelName];
      const telem = stream.telemetry;
      const scores = modelData.liveScores || modelData.cusum_scores;
      const alarms = modelData.liveAlarms || modelData.alarms;

      // 1. Chart Temp
      drawTimeSeriesChart(canvasTemp, {
        actual: telem.actual_temp,
        expected: modelData.expected_temp,
        alarms: alarms,
        currentIndex: currentIndex,
        titleActual: 'Actual Temp',
        titleExpected: 'Expected Temp',
        colorActual: '#ef4444',
        colorExpected: '#38bdf8',
        yUnit: '°C',
        showPreFaultZone: (currentStreamKey === 'event_0_failure')
      });

      // 2. Chart Residual
      drawSingleSeriesChart(canvasRes, {
        data: modelData.residuals,
        currentIndex: currentIndex,
        color: '#22c55e',
        yUnit: '°C',
        baselineZero: true,
        alertBands: true
      });

      // 3. Chart CUSUM
      drawCusumChart(canvasCusum, {
        scores: scores,
        alarms: alarms,
        threshold: customParams.threshold,
        currentIndex: currentIndex,
        color: '#c084fc',
        yUnit: ''
      });
    }

    // HELPER: DRAW TIME SERIES (ACTUAL VS EXPECTED)
    function drawTimeSeriesChart(canvas, opts) {
      const ctx = setupCanvas(canvas);
      const w = canvas.width;
      const h = canvas.height;
      const padL = 45, padR = 15, padT = 20, padB = 25;
      const plotW = w - padL - padR;
      const plotH = h - padT - padB;

      ctx.clearRect(0, 0, w, h);

      const n = opts.actual.length;
      let minVal = Math.min(...opts.actual, ...opts.expected);
      let maxVal = Math.max(...opts.actual, ...opts.expected);
      minVal = Math.floor(minVal - 2);
      maxVal = Math.ceil(maxVal + 4);

      // Grid
      drawGrid(ctx, padL, padT, plotW, plotH, minVal, maxVal, opts.yUnit);

      // Pre-fault zone (First 48 windows in Event 0)
      if (opts.showPreFaultZone && n >= 48) {
        const xPre = padL + (48 / n) * plotW;
        ctx.fillStyle = 'rgba(245, 158, 11, 0.08)';
        ctx.fillRect(padL, padT, xPre - padL, plotH);
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.4)';
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(xPre, padT);
        ctx.lineTo(xPre, padT + plotH);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = '#f59e0b';
        ctx.font = '10px Inter';
        ctx.fillText('Event Start (48h)', xPre + 4, padT + 12);
      }

      // Expected line
      ctx.strokeStyle = opts.colorExpected;
      ctx.lineWidth = 1.8;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const x = padL + (i / (n - 1)) * plotW;
        const y = padT + plotH - ((opts.expected[i] - minVal) / (maxVal - minVal)) * plotH;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Actual line
      ctx.strokeStyle = opts.colorActual;
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const x = padL + (i / (n - 1)) * plotW;
        const y = padT + plotH - ((opts.actual[i] - minVal) / (maxVal - minVal)) * plotH;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Current position cursor
      drawCursor(ctx, padL, padT, plotW, plotH, opts.currentIndex, n);
    }

    // HELPER: DRAW SINGLE SERIES (RESIDUAL)
    function drawSingleSeriesChart(canvas, opts) {
      const ctx = setupCanvas(canvas);
      const w = canvas.width;
      const h = canvas.height;
      const padL = 40, padR = 15, padT = 20, padB = 25;
      const plotW = w - padL - padR;
      const plotH = h - padT - padB;

      ctx.clearRect(0, 0, w, h);

      const n = opts.data.length;
      let minVal = Math.min(-5, ...opts.data);
      let maxVal = Math.max(15, ...opts.data);

      drawGrid(ctx, padL, padT, plotW, plotH, minVal, maxVal, opts.yUnit);

      // Zero baseline
      const zeroY = padT + plotH - ((0 - minVal) / (maxVal - minVal)) * plotH;
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(padL, zeroY);
      ctx.lineTo(padL + plotW, zeroY);
      ctx.stroke();
      ctx.setLineDash([]);

      // Residual Line
      ctx.strokeStyle = opts.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const x = padL + (i / (n - 1)) * plotW;
        const y = padT + plotH - ((opts.data[i] - minVal) / (maxVal - minVal)) * plotH;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      drawCursor(ctx, padL, padT, plotW, plotH, opts.currentIndex, n);
    }

    // HELPER: DRAW CUSUM ACCUMULATION CHART
    function drawCusumChart(canvas, opts) {
      const ctx = setupCanvas(canvas);
      const w = canvas.width;
      const h = canvas.height;
      const padL = 40, padR = 15, padT = 20, padB = 25;
      const plotW = w - padL - padR;
      const plotH = h - padT - padB;

      ctx.clearRect(0, 0, w, h);

      const n = opts.scores.length;
      let maxVal = Math.max(opts.threshold * 1.3, ...opts.scores, 40);
      let minVal = 0;

      drawGrid(ctx, padL, padT, plotW, plotH, minVal, maxVal, '');

      // Threshold line
      const threshY = padT + plotH - ((opts.threshold - minVal) / (maxVal - minVal)) * plotH;
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 1.8;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.moveTo(padL, threshY);
      ctx.lineTo(padL + plotW, threshY);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = '#f43f5e';
      ctx.font = '10px Inter';
      ctx.fillText(`Threshold: ${opts.threshold.toFixed(1)}`, padL + plotW - 90, threshY - 5);

      // Shaded active alarm areas
      for (let i = 0; i < n; i++) {
        if (opts.alarms[i] === 1) {
          const x = padL + (i / (n - 1)) * plotW;
          const nextX = padL + (Math.min(n - 1, i + 1) / (n - 1)) * plotW;
          ctx.fillStyle = 'rgba(244, 63, 94, 0.2)';
          ctx.fillRect(x, padT, Math.max(2, nextX - x), plotH);
        }
      }

      // CUSUM score curve
      ctx.strokeStyle = opts.color;
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const x = padL + (i / (n - 1)) * plotW;
        const y = padT + plotH - ((opts.scores[i] - minVal) / (maxVal - minVal)) * plotH;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      drawCursor(ctx, padL, padT, plotW, plotH, opts.currentIndex, n);
    }

    function setupCanvas(canvas) {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      const ctx = canvas.getContext('2d');
      ctx.scale(dpr, dpr);
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      return ctx;
    }

    function drawGrid(ctx, padL, padT, plotW, plotH, minVal, maxVal, unit) {
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Inter';

      const steps = 4;
      for (let s = 0; s <= steps; s++) {
        const val = minVal + (s / steps) * (maxVal - minVal);
        const y = padT + plotH - (s / steps) * plotH;

        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + plotW, y);
        ctx.stroke();

        ctx.textAlign = 'right';
        ctx.fillText(Math.round(val) + unit, padL - 6, y + 3);
      }
    }

    function drawCursor(ctx, padL, padT, plotW, plotH, currIdx, totalLen) {
      const x = padL + (currIdx / (totalLen - 1)) * plotW;

      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(x, padT);
      ctx.lineTo(x, padT + plotH);
      ctx.stroke();

      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.arc(x, padT + 3, 3.5, 0, Math.PI * 2);
      ctx.fill();
    }
  </script>
</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated dashboard HTML: {html_file.resolve()} ({len(html_content)} bytes)")
