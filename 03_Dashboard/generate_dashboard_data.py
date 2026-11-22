import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import xgboost as xgb

SAVE_DIR = Path(r'c:\Users\veerk\Downloads\PRJ4\02_ML\saved_model_nbm')
FARM_A_DIR = Path(r'c:\Users\veerk\Downloads\PRJ4\Care_To_Compare\Wind Farm A')
DASHBOARD_DIR = Path(r'c:\Users\veerk\Downloads\PRJ4\03_Dashboard')
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

# Scalers
scaler_X = joblib.load(SAVE_DIR / 'scaler_X.joblib')
scaler_y = joblib.load(SAVE_DIR / 'scaler_y.joblib')

EXOGENOUS_FEATURES = ['power_30_avg', 'wind_speed_3_avg', 'sensor_0_avg', 'sensor_18_avg', 'sensor_52_avg', 'sensor_5_avg']
TARGET_COL = 'sensor_13_avg'

# Load PyTorch architectures
class LSTMRegressor(nn.Module):
    def __init__(self, input_dim=6, hidden_dim=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Sequential(nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Dropout(dropout), nn.Linear(32, 1))
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

class GRURegressor(nn.Module):
    def __init__(self, input_dim=6, hidden_dim=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Sequential(nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Dropout(dropout), nn.Linear(32, 1))
    def forward(self, x):
        out, _ = self.gru(x)
        return self.fc(out[:, -1, :])

class Chomp1d(nn.Module):
    def __init__(self, chomp_size): super().__init__(); self.chomp_size = chomp_size
    def forward(self, x): return x[:, :, :-self.chomp_size].contiguous()

class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, dropout=0.2):
        super().__init__()
        self.conv1 = nn.Conv1d(n_inputs, n_outputs, kernel_size, stride=stride, padding=padding, dilation=dilation)
        self.chomp1 = Chomp1d(padding)
        self.relu1 = nn.ReLU(); self.dropout1 = nn.Dropout(dropout)
        self.conv2 = nn.Conv1d(n_outputs, n_outputs, kernel_size, stride=stride, padding=padding, dilation=dilation)
        self.chomp2 = Chomp1d(padding); self.relu2 = nn.ReLU(); self.dropout2 = nn.Dropout(dropout)
        self.net = nn.Sequential(self.conv1, self.chomp1, self.relu1, self.dropout1, self.conv2, self.chomp2, self.relu2, self.dropout2)
        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        self.relu = nn.ReLU()
    def forward(self, x):
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)

class TCNRegressor(nn.Module):
    def __init__(self, input_dim=6, num_channels=[32, 64, 64], kernel_size=3, dropout=0.2):
        super().__init__()
        layers = []
        for i in range(len(num_channels)):
            dilation = 2 ** i
            in_ch = input_dim if i == 0 else num_channels[i-1]
            out_ch = num_channels[i]
            layers.append(TemporalBlock(in_ch, out_ch, kernel_size, stride=1, dilation=dilation, padding=(kernel_size-1)*dilation, dropout=dropout))
        self.network = nn.Sequential(*layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(num_channels[-1], 1)
    def forward(self, x):
        x = x.transpose(1, 2)
        out = self.network(x)
        out = self.pool(out).squeeze(2)
        return self.fc(out)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model=64, max_len=400):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))
    def forward(self, x): return x + self.pe[:, :x.size(1), :]

class TransformerRegressor(nn.Module):
    def __init__(self, input_dim=6, d_model=64, nhead=4, num_layers=2, dim_feedforward=128, dropout=0.2):
        super().__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward, dropout=dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Sequential(nn.Linear(d_model, 32), nn.ReLU(), nn.Dropout(dropout), nn.Linear(32, 1))
    def forward(self, x):
        out = self.embedding(x)
        out = self.pos_encoder(out)
        out = self.transformer_encoder(out)
        out = out.mean(dim=1)
        return self.fc(out)

class SeqDataset(Dataset):
    def __init__(self, x): self.x = torch.from_numpy(x)
    def __len__(self): return len(self.x)
    def __getitem__(self, idx): return self.x[idx]

def predict_dl(model, x_seq):
    model.eval()
    loader = DataLoader(SeqDataset(x_seq), batch_size=64, shuffle=False)
    preds = []
    with torch.no_grad():
        for bx in loader:
            preds.extend(model(bx).cpu().numpy().flatten())
    return scaler_y.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()

# Load models
models = {}
xgb_m = xgb.XGBRegressor()
xgb_m.load_model(SAVE_DIR / 'xgboost_nbm.json')
models['XGBoost'] = ('xgb', xgb_m)

lstm_m = LSTMRegressor()
lstm_m.load_state_dict(torch.load(SAVE_DIR / 'lstm_best.pt', map_location='cpu'))
models['LSTM'] = ('dl', lstm_m)

gru_m = GRURegressor()
gru_m.load_state_dict(torch.load(SAVE_DIR / 'gru_best.pt', map_location='cpu'))
models['GRU'] = ('dl', gru_m)

tcn_m = TCNRegressor()
tcn_m.load_state_dict(torch.load(SAVE_DIR / 'tcn_best.pt', map_location='cpu'))
models['TCN'] = ('dl', tcn_m)

tf_m = TransformerRegressor()
tf_m.load_state_dict(torch.load(SAVE_DIR / 'transformer_best.pt', map_location='cpu'))
models['Transformer'] = ('dl', tf_m)

def extract_windows(df, x_cols, y_col, stride=6, window_size=288):
    X_vals = df[x_cols].to_numpy()
    y_raw = df[y_col].to_numpy()
    times = df['time_stamp'].to_numpy()
    ids = df['id'].to_numpy()
    statuses = df['status_type_id'].to_numpy()
    
    # Also grab raw power & wind speed for dashboard context
    power_raw = df['power_30_avg_raw'].to_numpy() if 'power_30_avg_raw' in df else df['power_30_avg'].to_numpy()
    wind_raw = df['wind_speed_3_avg_raw'].to_numpy() if 'wind_speed_3_avg_raw' in df else df['wind_speed_3_avg'].to_numpy()
    amb_raw = df['sensor_0_avg_raw'].to_numpy() if 'sensor_0_avg_raw' in df else df['sensor_0_avg'].to_numpy()
    rpm_raw = df['sensor_18_avg_raw'].to_numpy() if 'sensor_18_avg_raw' in df else df['sensor_18_avg'].to_numpy()

    x_seq, x_tab, y_actual = [], [], []
    win_times, win_ids, win_statuses = [], [], []
    win_power, win_wind, win_amb, win_rpm = [], [], [], []

    for s in range(0, len(df) - window_size + 1, stride):
        e = s + window_size
        w = X_vals[s:e]
        tab = np.concatenate([w.mean(0), w.std(0), w.min(0), w.max(0), w[-1] - w[0]])
        x_seq.append(w)
        x_tab.append(tab)
        y_actual.append(y_raw[e - 1])
        win_times.append(str(times[e - 1])[:19])
        win_ids.append(int(ids[e - 1]))
        win_statuses.append(int(statuses[e - 1]))
        win_power.append(float(power_raw[e - 1]))
        win_wind.append(float(wind_raw[e - 1]))
        win_amb.append(float(amb_raw[e - 1]))
        win_rpm.append(float(rpm_raw[e - 1]))

    return {
        'x_seq': np.array(x_seq, dtype=np.float32),
        'x_tab': np.array(x_tab, dtype=np.float32),
        'y_actual': np.array(y_actual, dtype=np.float32),
        'times': win_times,
        'ids': win_ids,
        'statuses': win_statuses,
        'power': win_power,
        'wind': win_wind,
        'ambient': win_amb,
        'rpm': win_rpm
    }

# 1. Failure Degradation Stream (Event 0)
df0 = pd.read_csv(FARM_A_DIR / 'datasets' / '0.csv', sep=';')
df0['time_stamp'] = pd.to_datetime(df0['time_stamp'])
for col in ['power_30_avg', 'wind_speed_3_avg', 'sensor_0_avg', 'sensor_18_avg']:
    df0[col + '_raw'] = df0[col]
df0[EXOGENOUS_FEATURES] = scaler_X.transform(df0[EXOGENOUS_FEATURES])

# Failure stream from buffer (52148 - 287) to event_end_id 54447
fail_df = df0.iloc[52148 - 287 : 54447 + 1].reset_index(drop=True)
fail_data = extract_windows(fail_df, EXOGENOUS_FEATURES, TARGET_COL, stride=6, window_size=288)

# 2. Healthy Operational Stream (Event 24)
df24 = pd.read_csv(FARM_A_DIR / 'datasets' / '24.csv', sep=';')
df24['time_stamp'] = pd.to_datetime(df24['time_stamp'])
for col in ['power_30_avg', 'wind_speed_3_avg', 'sensor_0_avg', 'sensor_18_avg']:
    df24[col + '_raw'] = df24[col]
df24[EXOGENOUS_FEATURES] = scaler_X.transform(df24[EXOGENOUS_FEATURES])

pred24 = df24[df24['train_test'] == 'prediction'].reset_index(drop=True)
norm_data = extract_windows(pred24, EXOGENOUS_FEATURES, TARGET_COL, stride=6, window_size=288)

# Model inference & residuals
stream_results = {
    'event_0_failure': {
        'metadata': {
            'event_id': 0,
            'asset': 0,
            'description': 'Generator Bearing Failure',
            'event_start_id': 52436,
            'event_start_time': '2023-08-06 06:10:00',
            'breakdown_time': '2023-08-04 19:30:00',
            'event_end_id': 54447,
            'event_end_time': '2023-08-20 06:10:00'
        },
        'telemetry': {
            'times': fail_data['times'],
            'ids': fail_data['ids'],
            'statuses': fail_data['statuses'],
            'actual_temp': [round(float(v), 2) for v in fail_data['y_actual']],
            'power_kw': [round(float(v), 2) for v in fail_data['power']],
            'wind_speed': [round(float(v), 2) for v in fail_data['wind']],
            'ambient_temp': [round(float(v), 2) for v in fail_data['ambient']],
            'generator_rpm': [round(float(v), 1) for v in fail_data['rpm']],
        },
        'models': {}
    },
    'event_24_normal': {
        'metadata': {
            'event_id': 24,
            'asset': 0,
            'description': 'Normal Operational Baseline',
            'event_start_id': 52720,
            'event_start_time': '2023-05-01 00:00:00',
            'event_end_id': 54714,
            'event_end_time': '2023-05-13 11:20:00'
        },
        'telemetry': {
            'times': norm_data['times'],
            'ids': norm_data['ids'],
            'statuses': norm_data['statuses'],
            'actual_temp': [round(float(v), 2) for v in norm_data['y_actual']],
            'power_kw': [round(float(v), 2) for v in norm_data['power']],
            'wind_speed': [round(float(v), 2) for v in norm_data['wind']],
            'ambient_temp': [round(float(v), 2) for v in norm_data['ambient']],
            'generator_rpm': [round(float(v), 1) for v in norm_data['rpm']],
        },
        'models': {}
    }
}

# Frozen calibration parameters from the evaluation notebook
FROZEN_CONFIG = {
    'GRU': {'k': 3.61, 'threshold': 36.03, 'persistence': 4, 'extreme': 12.5},
    'LSTM': {'k': 3.43, 'threshold': 24.75, 'persistence': 6, 'extreme': 12.5},
    'Transformer': {'k': 3.62, 'threshold': 4.13, 'persistence': 6, 'extreme': 12.5},
    'XGBoost': {'k': 5.03, 'threshold': 0.00, 'persistence': 2, 'extreme': 12.5},
    'TCN': {'k': 4.62, 'threshold': 88.05, 'persistence': 6, 'extreme': 12.5}
}

def compute_cusum_arrays(residuals, k, thresh, persistence, extreme_thresh):
    s = 0.0
    scores = []
    alarms = []
    counter = 0
    for r in residuals:
        s = max(0.0, s + (r - k))
        scores.append(round(float(s), 2))
        c_trig = (s > thresh)
        e_trig = (r > extreme_thresh) if extreme_thresh else False
        if c_trig or e_trig: counter += 1
        else: counter = max(0, counter - 1)
        alarms.append(1 if counter >= persistence else 0)
    return scores, alarms

for name, (m_type, mdl) in models.items():
    cfg = FROZEN_CONFIG[name]
    
    # Event 0 predictions
    if m_type == 'xgb':
        p_fail = scaler_y.inverse_transform(mdl.predict(fail_data['x_tab']).reshape(-1, 1)).flatten()
        p_norm = scaler_y.inverse_transform(mdl.predict(norm_data['x_tab']).reshape(-1, 1)).flatten()
    else:
        p_fail = predict_dl(mdl, fail_data['x_seq'])
        p_norm = predict_dl(mdl, norm_data['x_seq'])
        
    r_fail = fail_data['y_actual'] - p_fail
    r_norm = norm_data['y_actual'] - p_norm
    
    s_fail, a_fail = compute_cusum_arrays(r_fail, cfg['k'], cfg['threshold'], cfg['persistence'], cfg['extreme'])
    s_norm, a_norm = compute_cusum_arrays(r_norm, cfg['k'], cfg['threshold'], cfg['persistence'], cfg['extreme'])
    
    stream_results['event_0_failure']['models'][name] = {
        'expected_temp': [round(float(v), 2) for v in p_fail],
        'residuals': [round(float(v), 2) for v in r_fail],
        'cusum_scores': s_fail,
        'alarms': a_fail,
        'config': cfg
    }
    
    stream_results['event_24_normal']['models'][name] = {
        'expected_temp': [round(float(v), 2) for v in p_norm],
        'residuals': [round(float(v), 2) for v in r_norm],
        'cusum_scores': s_norm,
        'alarms': a_norm,
        'config': cfg
    }

# Read benchmark results
bench_df = pd.read_csv(SAVE_DIR / 'nbm_evaluation_benchmark_fixed.csv')
bench_df.columns = [c.strip() for c in bench_df.columns]
benchmark_list = bench_df.to_dict(orient='records')

full_payload = {
    'benchmark': benchmark_list,
    'streams': stream_results
}

# Save to JS file
output_js = DASHBOARD_DIR / 'data.js'
with open(output_js, 'w', encoding='utf-8') as f:
    f.write('const NBM_DATA = ' + json.dumps(full_payload, indent=2) + ';\n')

print(f"Exported dashboard data to: {output_js.resolve()}")
print(f"Data file size: {output_js.stat().st_size / 1024:.1f} KB")
