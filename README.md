# Early Fault Detection in Wind Turbines: Normal Behavior Modeling with Calibrated CUSUM Detection on Multi-Farm SCADA Data

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6-ee4c2c.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Project-IV Capstone Research**  
*Department of Computer Science Engineering, School of Engineering and Technology*  
*BML Munjal University, Gurugram, India*

**Authors:**
- Karanveer Singh (Roll No. 230535)
- Kartik Kotnala (Roll No. 230526)
- Vaishnavi Singh (Roll No. 230508)
- Ketan Choudary (Roll No. 230840)

**Faculty Mentor:**  
**Dr. Devanjali Relan**, Associate Professor, Department of Computer Science Engineering

---

## 📌 Executive Summary

Modern wind turbine maintenance costs account for **25%–30% of the Levelized Cost of Energy (LCOE)**. Among drivetrain subsystems, **Generator Drive-End (DE) bearing failures** are the most economically devastating, with direct crane mobilization and replacement costs between **$150,000 and $300,000**, compounded by downtime revenue losses of **~$10,000/day**.

Commercial SCADA monitoring systems rely predominantly on static scalar trip thresholds (e.g., alarming when temperature breaches 60°C or 70°C). By the time these thresholds trigger, destructive thermal runaway and mechanical seizure are actively underway—yielding **zero actionable prognostic lead time**. Furthermore, conventional supervised binary classification models suffer catastrophically from real-world class imbalance (>98% healthy data).

This repository presents an industrial-grade early fault detection framework combining:
1. **Semi-Supervised Normal Behavior Modeling (NBM)** trained exclusively on operational healthy telemetry (`status_type_id == 0`) under robust **Huber Loss ($\delta=1.0$)**.
2. **Sequential Upper One-Sided Cumulative Sum (CUSUM) Change-Point Detection** with persistence filtering ($p=6$) and frozen statistical drift allowances ($k, \tau$).
3. **Cross-Farm Schema Harmonization** across 95 full-year operational runs (~5.1M SCADA records) from the Fraunhofer IEE *Care_To_Compare* benchmark.
4. An interactive, zero-dependency **Digital Twin SCADA Dashboard (`AeroPulse Enterprise™`)** for real-time turbine health surveillance.

---

## 🏆 Key Achievements & Benchmark Highlights

- **24.0 to 26.0 Hours Advance Lead Time** before failure event onset (**37.0 hours** before catastrophic 60°C thermal runaway).
- **0.00% False Alarm Rate (FAR)** across continuous unseen healthy test streams (54,986 continuous 10-minute intervals).
- **100% Precision ($1.000$)** and **$0.8934$ F1-Score** on continuous degradation streams.
- **Top Composite CARE Score of 0.7857** (Coverage, Accuracy, Reliability, Earliness).
- **GRU Emerged as the Superior Architecture**, outperforming LSTM, TCN, Temporal Transformers, and XGBoost by balancing multi-day thermal memory with high-frequency turbulence filtering.

---

## 📊 Comprehensive Benchmark Leaderboard

### Table 1: 24-Hour Prognostic Horizon ($W = 144$ steps)
| Model | Test FAR | Advance Lead Time | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | CARE Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GRU (Best)** | **0.00%** | **24.0 h early** | **1.0000** | **0.7143** | **0.8333** | **0.9304** | **0.8775** | **0.7857** |
| **LSTM** | 0.00% | 0.0 h (at event) | 1.0000 | 0.4067 | 0.5783 | 0.8707 | 0.7774 | 0.7500 |
| **TCN** | 0.00% | 0.0 h (at event) | 1.0000 | 0.4067 | 0.5783 | 0.8487 | 0.7007 | 0.7500 |
| **Transformer**| 0.00% | 0.0 h (at event) | 1.0000 | 0.3829 | 0.5538 | 0.7764 | 0.5830 | 0.7500 |
| **XGBoost** | 25.11% | 56.0 h early | 0.8208 | 0.5179 | 0.6350 | 0.8655 | 0.7358 | 0.7257 |

### Table 2: Continuous Multi-Farm Horizon ($W = 288$ steps)
| Model | Frozen $k$ | Frozen $\tau$ | Persist ($p$) | Test FAR | Lead Time (Event) | Lead Time (60°C Trip) | Precision | Recall | F1-Score | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GRU (Best)** | **4.88°C** | **27.67** | **6** | **0.00%** | **26.0 h** | **37.0 h** | **1.0000** | **0.8073** | **0.8934** | **0.9853** |
| **XGBoost** | 7.11°C | 25.47 | 6 | 0.00% | 0.0 h | 0.0 h | 1.0000 | 0.6172 | 0.7633 | 0.9010 |
| **Transformer**| 5.63°C | 11.76 | 6 | 0.00% | 0.0 h | 0.0 h | 1.0000 | 0.5469 | 0.7071 | 0.8627 |
| **LSTM** | 5.27°C | 21.18 | 6 | 0.00% | 0.0 h | 0.0 h | 1.0000 | 0.4688 | 0.6383 | 0.8436 |
| **TCN** | 13.37°C | 360.78 | 6 | 0.00% | 0.0 h | 0.0 h | 1.0000 | 0.3359 | 0.5029 | 0.8218 |

---

## 🛠️ Unified 7-Channel Physical SCADA Schema

To resolve extreme column heterogeneity across diverse OEM manufacturers (Farm A: 86 channels; Farm B: 257 channels; Farm C: 957 channels), all telemetry was harmonized into a standardized thermodynamic feature schema:

| Harmonized Feature | Physical Meaning | Engineering Unit | Role in Pipeline | Thermodynamic Relationship |
| :--- | :--- | :---: | :---: | :--- |
| `power_kw` | Active Electrical Power Generated | kW | Input ($X_1$) | Electromagnetic loading & torque proxy |
| `wind_speed` | Atmospheric Wind Speed at Hub | m/s | Input ($X_2$) | Aerodynamic driving force; kinetic energy |
| `ambient_temp` | External Environmental Temperature| °C | Input ($X_3$) | Thermal boundary condition & cooling sink |
| `gen_rpm` | Generator High-Speed Shaft Speed | RPM | Input ($X_4$) | Bearing rotational friction cycle frequency |
| `rotor_rpm` | Low-Speed Main Rotor Velocity | RPM | Input ($X_5$) | Kinematic gearbox transmission coupling |
| `pitch_angle` | Aerodynamic Blade Pitch Angle | Degrees (°) | Input ($X_6$) | Controller regulation state indicator |
| `bearing_temp` | Generator Drive-End (DE) Bearing | °C | Target ($y$) | Passive thermal sink absorbing friction heat |

---

## 🔬 Mathematical Methodology

### Stage 1: Physics-Informed Normal Behavior Modeling (NBM)
The expected bearing temperature $\hat{y}_t$ under healthy thermodynamic equilibrium is modeled by deep sequential regression:
$$\hat{y}_t = f_\theta(X_{t-W+1 : t})$$

Trained using **Huber Loss ($\delta = 1.0$)** to guarantee robust convergence under non-Gaussian aerodynamic turbulence:
$$L_\delta(e) = \begin{cases} \frac{1}{2} e^2, & |e| \le \delta \\ \delta(|e| - \frac{1}{2}\delta), & |e| > \delta \end{cases} \quad \text{where } e = y_t - \hat{y}_t$$

### Stage 2: Sequential Change-Point Detection (One-Sided CUSUM)
Raw thermal residuals $r_t = y_t - \hat{y}_t$ isolate net frictional heat. Cumulative positive deviation is accumulated via:
$$S_0 = 0, \quad S_t = \max(0, S_{t-1} + (r_t - k))$$

- **Drift Allowance ($k$)**: $k = \mu_{\text{val}} + 0.5 \sigma_{\text{val}}$ frozen on healthy validation residuals.
- **Decision Threshold ($\tau$)**: 95th to 97.5th percentile of validation $S_t$ scores.
- **Persistence Gate ($p$)**: Requires $S_t > \tau$ for $p = 6$ consecutive timesteps (60 minutes) to suppress transient wind gust false alarms.

---

## 💻 Interactive Digital Twin SCADA Dashboard (`AeroPulse Enterprise™`)

An interactive, production-grade Digital Twin web application was developed and deployed in `03_Dashboard/`:
- **Dual Thermal Curve Tracking**: Live visual comparison between actual measured bearing temperature and the NBM physics baseline.
- **Real-Time Telemetry Simulation Player**: Play, pause, scrub, and step through 10-minute SCADA intervals.
- **Dynamic KPI Gauges**: Real-time thermal residual (°C), persistence counters, and CUSUM score meters.
- **Interactive Sensitivity Tuner**: Live slider adjustment of drift allowance ($k$) and threshold ($\tau$) to inspect operational trade-offs.

### Running the Dashboard Locally:
```bash
cd 03_Dashboard
python3 run_dashboard.py
```
Open your browser and navigate to `http://localhost:8080`.

---

## 📂 Repository Structure

```
├── 01_EDA/
│   ├── basic_eda.ipynb                     # Multi-farm telemetry distribution & physical checks
│   └── residual_analysis_eda.ipynb         # Weather decoupling & residual heteroscedasticity
│
├── 02_ML/
│   ├── 02_wind_farm_a_quick_prototype.ipynb# Baseline prototypes on Farm A
│   ├── 03_nbm_early_fault_detection.ipynb  # Sequence formulation & initial NBM modeling
│   ├── 04_nbm_model_evaluation.ipynb       # Diagnostic evaluation & root-cause analysis
│   ├── 05_final_model_train.ipynb          # Multi-farm NBM training under Huber loss
│   ├── 06_final_model_eval.ipynb           # Final leaderboard & zero-leakage evaluation
│   ├── saved_models_nbm/                   # Checkpoints & evaluation diagnostic records
│   └── saved_models_nbm_all/               # Serialized models (GRU, LSTM, TCN, Transformer, XGBoost)
│
├── 03_Dashboard/
│   ├── index.html                          # Complete AeroPulse Enterprise™ Dashboard UI
│   ├── data.js                             # Multi-farm pre-fault & healthy baseline telemetry data
│   ├── run_dashboard.py                    # Local HTTP server with automatic browser launch
│   ├── generate_dashboard_data.py          # Pipeline exporting NBM inference streams to JSON/JS
│   └── build_dashboard_html.py             # UI generator & template engine
│
├── .gitignore
└── README.md
```

---

## 📖 Citation & References
1. Fraunhofer Institute for Energy Economics and Energy System Technology (IEE), *“Care_To_Compare: Multi-Farm Wind Turbine Condition Monitoring Benchmark Dataset,”* 2024.
2. J. Schlechtingen, I. F. Santos, and S. Achiche, *“Using Data-Mining Approaches for Wind Turbine Condition Monitoring: A Comparative Study,”* IEEE Trans. Sustainable Energy, 2013.
3. E. S. Page, *“Continuous Inspection Schemes,”* Biometrika, 1954.
4. P. J. Huber, *“Robust Estimation of a Location Parameter,”* Ann. Math. Statist., 1964.
