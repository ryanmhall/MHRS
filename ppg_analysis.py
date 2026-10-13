import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# =====================================================================
# 1. LOAD DATA
# =====================================================================
# Path is relative to this script, so it works wherever the repo is cloned:
#   <repo>/data/S1/S1.pkl   (download instructions in README.md)
SUBJECT = 'S1'
file_path = Path(__file__).resolve().parent / 'PPG_FieldStudy' / SUBJECT / f'{SUBJECT}.pkl'
if not file_path.exists():
    raise SystemExit(f'Data file not found: {file_path}\n'
                     f'Download PPG-DaLiA (see README.md) and put {SUBJECT}.pkl there.')

with open(file_path, 'rb') as f:
    data = pickle.load(f, encoding='latin1')

ppg = data['signal']['wrist']['BVP'].flatten()
hr_true = data['label']        # mean chest-ECG HR over 8 s windows, one every 2 s
fs = 64                        # wrist BVP sample rate (Hz)
WIN, STEP = 8, 2               # label window length and shift (s)

# Label i covers seconds [2i, 2i+8): one value every 2 s (0.5 Hz, not 2 Hz).
# Plot each label at its window centre.
t_hr = (np.arange(len(hr_true)) * STEP + WIN / 2) / 60     # minutes
t_ppg = np.arange(len(ppg)) / fs / 60

# =====================================================================
# 2. PPG HEART RATE: dominant frequency in each 8 s window
# =====================================================================
b, a = butter(2, [0.5, 4.0], btype='band', fs=fs)          # 30-240 BPM passband
ppg_f = filtfilt(b, a, ppg)

NFFT = 8192                                                # zero-pad -> 0.47 BPM bins
f_bpm = np.fft.rfftfreq(NFFT, 1 / fs) * 60
band = (f_bpm >= 40) & (f_bpm <= 200)

hr_raw = np.empty(len(hr_true))
for i in range(len(hr_true)):                              # same windows as the labels
    seg = ppg_f[i * STEP * fs:(i * STEP + WIN) * fs]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), NFFT))
    hr_raw[i] = f_bpm[band][np.argmax(spec[band])]

# =====================================================================
# 3. CLEANING (uses the PPG estimate only, never the ground truth)
# =====================================================================
SPAN = 15        # windows in the running median/mean (15 x 2 s = 30 s)
GATE = 15        # BPM: drop points further than this from the running median

hr = pd.Series(hr_raw).mask((hr_raw <= 41) | (hr_raw >= 199))   # band-edge picks aren't pulses
median = hr.rolling(SPAN, center=True, min_periods=1).median()
hr_clean = (hr.where((hr - median).abs() <= GATE)
              .rolling(SPAN, center=True, min_periods=1).mean()
              .interpolate(limit_direction='both')
              .to_numpy())
# For a real-time (wearable-style) filter, use center=False in both rolling() calls.

def score(est):
    err = est - hr_true
    return f'bias {np.mean(err):+.1f} BPM, MAE {np.mean(np.abs(err)):.1f} BPM'

print('Before:', score(hr_raw))
print('After: ', score(hr_clean))

# =====================================================================
# 4. PLOT: before, after, raw PPG
# =====================================================================
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 11), sharex=True,
                                    gridspec_kw={'height_ratios': [2, 2, 1]})

for ax, est, color, name in [(ax1, hr_raw, '#eb6834', 'Before: raw 8 s FFT estimate'),
                             (ax2, hr_clean, '#008300', 'After: 30 s median-gated average')]:
    ax.plot(t_hr, hr_true, color='#2a78d6', lw=1.6, label='Chest ECG (ground truth)')
    ax.plot(t_hr, est, color=color, lw=1.0, label='Wrist PPG estimate')
    ax.set_title(f'{name}   ({score(est)})', loc='left')
    ax.set_ylabel('Heart rate (BPM)')
    ax.set_ylim(35, 200)
    ax.legend(loc='upper left')

ax3.plot(t_ppg, ppg, color='#52514e', lw=0.3, rasterized=True)
lo, hi = np.percentile(ppg, [0.1, 99.9])                   # hide the largest motion spikes
ax3.set_ylim(lo - 0.1 * (hi - lo), hi + 0.1 * (hi - lo))
ax3.set_title('Raw wrist PPG (BVP)', loc='left')
ax3.set_ylabel('Amplitude (a.u.)')
ax3.set_xlabel('Time (min)')

for ax in (ax1, ax2, ax3):
    ax.grid(alpha=0.3)
# ax1.set_xlim(5, 8)   # zoom: adjust to inspect a few minutes at a time

plt.tight_layout()
plt.show()