# PPG-DaLiA heart-rate processing (single subject)

This README covers `ppg_analysis.py`. The script reads one subject from the PPG-DaLiA dataset and estimates heart rate from the wrist PPG. It then compares that estimate with the chest-ECG ground truth before and after a simple cleaning step.

**Requirements:** Python 3, `numpy`, `scipy`, `pandas`, `matplotlib`

**Run:** `ppg_analysis.py`. The file path is set at the top of the script.

## Pipeline at a glance

```
S1.pkl
 ├─ data['label'] ─────────────────────────────────────────► ground-truth HR (chest ECG)
 └─ data['signal']['wrist']['BVP']  (raw PPG, 64 Hz)
       │
       ├─ 1. band-pass 0.5–4 Hz (zero-phase Butterworth)
       ├─ 2. cut into 8 s windows, stepped every 2 s (same grid as the labels)
       ├─ 3. per window: Hann taper → zero-padded FFT → strongest peak in 40–200 BPM
       │                                                   ───► "Before" HR
       └─ 4. cleaning: band-edge rejection → running median → ±15 BPM gate
                       → running mean → gap interpolation   ───► "After" HR
```

## 1. Loading the data

- The `.pkl` file was written by Python 2, so it is opened with `pickle.load(f, encoding='latin1')`.
- **Raw PPG:** `data['signal']['wrist']['BVP']`. This is the blood volume pulse signal from the Empatica E4 wristband, sampled at **64 Hz** in arbitrary units. It is flattened to a 1-D array.
- **Ground truth:** `data['label']`. The dataset authors derived it from the chest ECG. Each value is the **average heart rate over an 8-second window**, and the windows advance **every 2 seconds**.
  - Label *i* covers seconds **[2i, 2i + 8)** of the recording.
  - That makes one label every 2 s, i.e. 0.5 Hz. This was the source of the original ~20 BPM offset: treating the labels as 2 Hz squeezed the ground-truth line into a quarter of the timeline.
  - Each label is plotted at the **centre of its window**, t = 2i + 4 s.

## 2. Band-pass filtering the raw PPG

- **Filter:** 2nd-order Butterworth band-pass, **0.5–4.0 Hz**, which corresponds to 30–240 BPM.
- **Applied with `filtfilt`:** the filter runs forward and then backward. This gives **zero phase shift**, so filtering doesn't move the signal in time, and the effective roll-off is 4th order.
- **Purpose:**
  - Remove slow baseline drift (DC level, respiration, sensor-contact changes) below 30 BPM.
  - Remove high-frequency noise above 240 BPM.
- Only the HR estimate uses the filtered signal. The bottom panel shows the **unfiltered** BVP.

## 3. Heart rate per window (the "Before" estimate)

Heart rate comes from the **dominant frequency** in each window, not from counting peaks.

1. **Windowing:** each estimate uses 8 s of filtered PPG, which is 512 samples. Window *i* spans samples 128·i to 128·i + 511, exactly matching label *i*, so there is one PPG estimate per ground-truth value.
2. **Hann taper:** the window is multiplied by a Hann function. Without it, the abrupt start and end of the segment would smear energy across frequencies (spectral leakage).
3. **Zero-padded FFT:** the 512 samples are padded to 8192 points before the FFT.
   - This puts spectrum points every 64 / 8192 Hz ≈ 0.0078 Hz ≈ **0.47 BPM**.
   - Zero-padding doesn't let the FFT separate two close frequencies; an 8 s window can only do that down to about 7.5 BPM. It does locate the single strongest peak far more precisely than unpadded bins would.
4. **Peak pick:** the magnitude spectrum is searched between **40 and 200 BPM**. The frequency of the largest value, × 60, is that window's heart rate.

This raw series appears in the **"Before"** panel. Its main error comes from wrist motion: arm swing, steps and hand movement add spectral peaks that are sometimes stronger than the pulse.

## 4. Cleaning (the "After" estimate)

The smoothing is a **median-gated moving average**. It is an outlier-rejection step (in the style of a Hampel filter) followed by a moving average of the values that survive.

**It uses only the PPG estimate. The ground truth is never used**, so the improvement shown in the "After" panel is legitimate.

| Step | What it does | Setting |
|---|---|---|
| a. Band-edge rejection | Marks estimates at the edge of the search band as missing. A "peak" at 40 or 200 BPM means the spectrum was still rising at the limit, from drift or motion, so it isn't a pulse. | ≤ 41 or ≥ 199 BPM |
| b. Running median | Takes the median of each estimate and its 7 neighbours on each side. This is a robust centre line that ignores isolated spikes. | 15 estimates = 30 s, centred |
| c. Outlier gate | Discards estimates further than the gate from that median. | ±15 BPM |
| d. Running mean | Averages the surviving estimates over the same span to smooth the step-like median. | 15 estimates = 30 s, centred |
| e. Gap fill | Where no estimates survived in a window, fills by linear interpolation between neighbours. | — |

**Notes:**
- Steps b and d use `min_periods=1`. Near the start and end of the recording, or around gaps, each value is computed from whatever estimates are available.
- **Centred vs. real time:** the centred window looks 14 s into the future. That is fine for offline analysis, but a wearable can't do it. Setting `center=False` in both `rolling()` calls gives a trailing (causal) filter. Use that when comparing against a real-time device; it delays the output by roughly 15 s.
- **Settings were chosen beforehand, not tuned on S1.** Tuning the span or gate to minimise error on this subject would fit the filter to the answer.

## 5. Metrics shown in the panel titles

Both metrics are computed over every window:

- **Bias** = mean(PPG HR − ECG HR). A negative bias means the PPG reads low on average.
- **MAE** = mean(|PPG HR − ECG HR|), in BPM.

## 6. Figure

1. **Before:** ECG ground truth (blue) and the raw per-window PPG estimate (orange).
2. **After:** ECG ground truth and the cleaned estimate (green). This panel uses the same y-axis range as the first so the two compare directly.
3. **Raw wrist PPG:** the unfiltered BVP. The y-axis view is limited to the 0.1–99.9th percentile plus a 10% margin so the largest motion spikes don't flatten the trace. **This affects the display only; the data is unchanged.**

The x-axes are linked, so zooming one panel zooms all three. The commented line `ax1.set_xlim(5, 8)` sets a fixed zoom.

## Limitations

- **Sustained motion artifact can't be fixed by smoothing.** When the raw estimate locks onto the motion frequency for minutes, as during parts of stair climbing and walking, the running median follows the wrong value. Fixing those stretches needs motion information, such as the wrist accelerometer, which this script doesn't use.
- **Smoothing flattens fast heart-rate changes.** A 30 s span cuts the peaks of short efforts like a stair climb.
- **Single subject:** results are for S1 only.

## Changes from the original script

| Original | Now | Why |
|---|---|---|
| `fs_hr = 2` (labels assumed 2 Hz) | Labels at 0.5 Hz, plotted at window centres | The 2 Hz assumption misaligned the ground truth in time and caused the ~20 BPM offset. |
| Peak count per 8 s window × 7.5 | Dominant FFT frequency per window | Counting peaks can only give values in 7.5 BPM steps. |
| `np.clip(hr, 40, 180)` | Band-edge values rejected, then cleaned | Clipping turned "no beats found" into fake 40 BPM readings. |
| No smoothing | Median-gated moving average | Removes isolated spikes without using the ground truth. |

## Companion script

`dalia_hr_overview.py` runs the same pipeline with extra diagnostics:

- timing checks
- error by activity
- tests for sampling-rate, alignment, harmonic and motion-lock errors
- activity shading on the plot
- command-line options

It uses a 4th-order band-pass and subtracts each window's mean before the FFT, so its numbers differ slightly from this script's.

## Data source

PPG-DaLiA, UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/495/ppg+dalia
Reiss, A., Indlekofer, I., Schmidt, P., Van Laerhoven, K. (2019). *Deep PPG: Large-scale heart rate estimation with convolutional neural networks.* Sensors 19(14), 3079. https://doi.org/10.3390/s19143079
