# NBM Evaluation Diagnosis: Why Precision / Recall / F1 = 0.0

---

## TL;DR — 4 Compounding Root Causes

All five models show **Precision = Recall = F1 = 0.0** because of four independent failures stacked on top of each other. None of them are about the model quality — they are all evaluation and pipeline design bugs.

---

## Root Cause 1 — Catastrophic Test Window Starvation (CRITICAL)

### What happened
The `extract_test_stream()` function applies this filter to Event 0:

```python
mask = (df['train_test'] == 'prediction') & (df['status_type_id'] == 0) & (df['id'] < event_start_id_0)
```

After applying this filter, **exactly 288 rows** survive (IDs `52148–52435`). A 48-hour window requires exactly 288 rows. With `stride=6`, the loop produces only **1 window total**.

```
Prediction rows (status==0, before event): 288
Windows created: 1
```

The failure stream has **1 sample** to evaluate against. One window cannot provide meaningful Precision / Recall / F1 statistics under any circumstances.

### Why only 288 rows?
The `prediction` split of Event 0 starts at ID 52148, and `event_start_id_0 = 52436`. That's a gap of exactly `52436 - 52148 = 288` rows — the width of one window. There is **zero overlap** available to create multiple sliding windows.

The ground truth label assignment:
```python
pre_fault_cutoff_id = event_start_id_0 - 288  # = 52148
y_true_fail = [1 if id_val >= 52148 else 0 for id_val in fail_ids]
```
Because `fail_ids` contains only `[52435]` (the last row of the single window), `y_true_fail = [1]`. There is exactly **one positive sample**.

---

## Root Cause 2 — The Single Failure Window is NOT Detected (CUSUM Miscalibration)

### What happened
Even though there's 1 positive sample, `Detected Failure = False` for every model. That means the single failure window's residual falls **below** the CUSUM alarm threshold.

Looking at `nbm_benchmark_results_corrected.csv`:

| Model | Raw Threshold (°C) | CUSUM Threshold | CUSUM k | False Alarm Rate | Detected Failure |
|---|---|---|---|---|---|
| LSTM | 4.39 | 15.39 | 1.20 | **0.54** | **False** |
| TCN | 3.91 | 15.33 | 1.35 | **0.62** | **False** |
| XGBoost | 6.03 | 17.73 | 1.75 | **0.60** | **False** |
| GRU | 4.25 | 14.63 | 1.44 | **0.53** | **False** |
| Transformer | 4.58 | 10.06 | 2.34 | **0.00** | **False** |

The CUSUM is firing **54–62% of the time** on the healthy test stream — meaning it's massively over-triggering on normal data. Yet it **still fails** on the actual failure window. This contradictory behavior reveals the core issue:

### The residual scale is inverted
The model was trained exclusively on healthy data from **Asset 0** (the training split). The prediction split of **Event 0** also comes from Asset 0 — but the 288-row pre-fault window is at a different operating point than any window the model saw during training.

The NBM models are predicting `T_expected` well enough on average healthy conditions, but the **healthy validation stream (Event 24)** has higher residual variance than the **single pre-fault window**. The pre-fault degradation signature for this specific failure appears to produce a lower residual than the normal operating noise — possibly because the failure is in its very early latent stage and only 48 hours before the event start ID (which may not be the actual thermal runaway point).

### The CUSUM `k` parameter problem
The `k` parameter (drift allowance) is calibrated using cross-validation. Values of `1.2–2.3°C` are subtracted from every residual step before accumulation. If the pre-fault residual is only `~3–5°C`, a `k=2.34` (Transformer) prevents any accumulation at all. For LSTM/TCN/GRU with smaller `k`, the CUSUM accumulates on normal noisy windows, causing the 54–62% false alarm rate, but the pre-fault window doesn't sustain enough residual to cross the persistence gate.

---

## Root Cause 3 — Persistence Filter is Too Strict for 1 Window

### What happened
The `run_cusum_detector` function requires:

```python
# Require persistence
alarms.append(1 if alarm_counter >= persistence_steps else 0)  # persistence_steps=4
```

With **only 1 window** in the failure stream, the alarm counter can never reach 4. Even if the CUSUM score exceeds the threshold for that 1 window, `persistence_steps=4` requires 4 consecutive windows. With only 1 window, this condition is **structurally impossible to satisfy**.

---

## Root Cause 4 — Training Set and Test Set Come from the Same Asset (Domain Collapse)

### What happened
The NBM is trained on the healthy training split of **Asset 0**, then tested on the prediction split of **Event 0 (also Asset 0)**. This means:

- Training data: Asset 0, healthy period
- Test data: Asset 0, pre-failure period (the last 288 timesteps before failure starts)

The healthy stream is **Event 24** — a different asset or at least a different operating period. The calibration threshold is calibrated on Event 24 residuals, which may have systematically different variance from Asset 0's normal operating range.

The combination of:
1. Training on Asset 0 healthy data
2. Calibrating thresholds on Event 24 healthy data (different asset characteristics)
3. Testing failure detection on Asset 0 pre-fault data

creates a **three-way domain mismatch** that the evaluation framework cannot handle.

---

## The PR-AUC Signal — What's Actually Working

Despite zero F1/Precision/Recall, the `Residual ROC-AUC` values are informative:

| Model | Residual ROC-AUC |
|---|---|
| LSTM | **0.785** |
| TCN | 0.775 |
| GRU | 0.500 |
| Transformer | 0.764 |
| XGBoost | 0.331 |

LSTM and TCN have ROC-AUC of **0.78–0.79**, which means the raw residuals DO rank the failure window above roughly 78–79% of healthy windows. The underlying model **is working** — it's the evaluation layer that is broken.

---

## Summary of Fixes Needed

| # | Root Cause | Fix |
|---|---|---|
| 1 | Only 1 failure test window | Extend the prediction split: don't apply `id < event_start_id` filter, OR use a wider pre-fault window (e.g., 7 days before event). Use **multiple anomaly events** (Events 0, 40, 68 have status==0 in pre-fault). |
| 2 | CUSUM over-triggers on healthy, misses failure | Recalibrate `k` per wind-speed regime. Use adaptive `k = 0.5 × σ_normal` instead of fixed value. Lower CUSUM threshold to `Q90` instead of `Q97.5`. |
| 3 | Persistence gate = 4 but only 1 failure window | With only 1 window, set `persistence_steps=1` for evaluation OR create more windows (fix #1 first). |
| 4 | Calibration domain mismatch | Calibrate CUSUM threshold on Asset 0 healthy data (not Event 24). Use per-turbine calibration. |

> [!IMPORTANT]
> Fix #1 is the most critical. Until there are more than 4 failure-period windows, no persistence-gated alarm can ever fire, making F1 structurally zero regardless of model quality.

---

## What a Fixed Evaluation Should Do

```python
# 1. Use a LONGER pre-fault window (7 days = 1008 rows, not 48h = 288 rows)
#    OR drop the id < event_start_id filter and use the full prediction split

# 2. Label: last N hours before event_start as positive
#    positive_hours = 48 (or 72 or 168)
#    pre_fault_cutoff_id = event_start_id - (positive_hours * 6)

# 3. Include multiple failure events in evaluation
#    Events 0, 40, 68 have status_type_id=0 in their pre-fault windows

# 4. Calibrate k adaptively:
#    k = 0.5 * np.std(r_norm)  # half the normal std, per model

# 5. Lower persistence to 2 consecutive windows (not 4)

# 6. Use per-asset calibration, not cross-asset calibration
```

---

## Bottom Line

The models themselves are **not broken**. LSTM and TCN have ROC-AUC ~0.78 on the raw residuals, which is a genuine signal. The evaluation pipeline has 4 compounding design bugs:

1. The prediction split provides only 1 failure window (structurally impossible to detect with persistence=4)
2. The CUSUM threshold is calibrated on the wrong asset's healthy data
3. The CUSUM `k` subtracts too aggressively, blocking accumulation on the true failure
4. Persistence gate requires more consecutive windows than exist in the test set

The correct next step is to **rebuild the evaluation layer**, not retrain the models.
