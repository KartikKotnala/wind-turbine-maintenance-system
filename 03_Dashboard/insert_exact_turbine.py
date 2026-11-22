with open('03_Dashboard/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for turbine spin if not present
if '/* SVG Turbine Spin */' not in html or '@keyframes turbine-rotate' not in html:
    css_to_add = '''    /* SVG Turbine Spin */
    @keyframes turbine-rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .spin-blade {
      transform-origin: 100px 90px;
      animation: turbine-rotate 3.5s linear infinite;
    }
    .spin-fast {
      animation-duration: 1.2s;
    }
    .spin-slow {
      animation-duration: 6s;
    }
    .spin-stop {
      animation-play-state: paused;
    }
'''
    insert_marker = '</style>'
    idx = html.find(insert_marker)
    html = html[:idx] + css_to_add + html[idx:]
    print("Added SVG Turbine Spin CSS")

# 2. Replace the turbine panel
panel_start = html.find('<!-- Live Interactive 2D Vector Wind Turbine (5 Cols) -->')
panel_end = html.find('<!-- 6 KPI Metric Cards & Scrubber (7 Cols) -->')

assert panel_start != -1 and panel_end != -1, "Panel markers not found"

exact_panel = '''<!-- Live Interactive 2D Vector Wind Turbine (5 Cols) -->
        <div class="lg:col-span-4 panel p-5 flex flex-col justify-between space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wider">Live Twin Subsystem</h3>
              <p class="text-[11px] text-slate-500" id="current-scenario-badge-label">1.5 MW WTG-04 Drive Train</p>
            </div>
            <span id="turbine-spin-badge" class="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">Rotor Spinning</span>
          </div>

          <!-- SVG Graphic matching user code exactly -->
          <div class="flex items-center justify-center p-4 bg-slate-50 rounded-xl border border-slate-200/80">
            <svg class="w-48 h-48 drop-shadow-sm" viewBox="0 0 200 220">
              <!-- Tower -->
              <polygon points="90,105 110,105 118,215 82,215" fill="#cbd5e1" stroke="#94a3b8" stroke-width="2"/>
              <!-- Nacelle Box -->
              <rect x="75" y="80" width="55" height="25" rx="4" fill="#334155" stroke="#1e293b" stroke-width="2"/>
              <!-- Hot Bearing Heat Highlight Area -->
              <circle id="svg-bearing-spot" cx="112" cy="92" r="7" fill="#10b981" stroke="#ffffff" stroke-width="1.5" class="transition-all duration-300"/>
              <!-- Nacelle Hub -->
              <circle cx="100" cy="90" r="9" fill="#0f172a"/>
              <!-- Spinning Blades -->
              <g id="svg-blades" class="spin-blade">
                <!-- Blade 1 -->
                <path d="M100,90 Q92,30 98,10 Q106,30 100,90" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
                <!-- Blade 2 (rotated 120) -->
                <path d="M100,90 Q150,120 170,140 Q135,145 100,90" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
                <!-- Blade 3 (rotated 240) -->
                <path d="M100,90 Q50,120 30,140 Q65,145 100,90" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
                <circle cx="100" cy="90" r="5" fill="#3b82f6"/>
              </g>
            </svg>
          </div>

          <!-- Dynamic Inspection Tooltip -->
          <div class="p-3 bg-white rounded-lg border border-slate-200 text-xs space-y-1.5 shadow-sm">
            <div class="flex justify-between items-center">
              <span class="text-slate-500 font-medium">Drive-End Bearing State:</span>
              <span id="turbine-bearing-state" class="font-bold text-emerald-600">NORMAL THERMAL</span>
            </div>
            <div class="flex justify-between items-center text-[11px] font-mono">
              <span class="text-slate-400">Rotor Speed:</span>
              <span id="turbine-blade-speed" class="text-slate-700 font-semibold">14.2 RPM</span>
            </div>
            <div class="flex justify-between items-center text-[11px] font-mono">
              <span class="text-slate-400">Thermomechanical Slip:</span>
              <span id="turbine-slip-val" class="text-slate-700 font-semibold">+0.12 °C</span>
            </div>
          </div>

          <div class="flex justify-end pt-0.5">
            <button onclick="setTab('xray')" class="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1 text-[11px]">
              <span>Internal Cross-Section</span>
              <i data-lucide="arrow-right" class="w-3 h-3"></i>
            </button>
          </div>
        </div>

        '''

html = html[:panel_start] + exact_panel + html[panel_end:]

# Adjust grid cols to lg:col-span-8 for the right-hand KPI cards (4 + 8 = 12 grid)
html = html.replace('<div class="lg:col-span-7 flex flex-col justify-between space-y-3.5">', '<div class="lg:col-span-8 flex flex-col justify-between space-y-3.5">')

with open('03_Dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied exact SVG turbine HTML and layout!")
