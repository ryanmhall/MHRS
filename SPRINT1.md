# Sprint 1

## 1. Mission

For health-conscious individuals who require accurate heart-rate monitoring during exercise, the Multispectral Heart Rate Sensor (MHRS) is a wearable fitness device that provides high-confidence heart-rate data. Unlike mainstream fitness devices, MHRS investigates multiple sensing techniques to reduce corruption caused by external sources of error.

> This mission is our current hypothesis and may change based on experimental results.

## 2. Target User

Our primary target user is a **runner** who relies on heart-rate measurements to monitor exercise intensity and training.

## 3. User Stories

### User Story 1 — Cardio Zones

As a runner, I want accurate heart-rate measurements during exercise so that I can maintain my desired cardio zone.

**Acceptance Criteria:**
- The prototype produces a heart-rate measurement during a controlled exercise test.
- The measured heart rate can be compared against a reference measurement.
- Measurement error can be quantified.

### User Story 2 — Movement Robustness

As a runner, I want my heart-rate measurements to remain reliable while I am moving so that normal running motion does not make my heart-rate data unusable.

**Acceptance Criteria:**
- Raw PPG data can be recorded during both stationary and movement conditions.
- Motion-corrupted portions of the signal can be identified.
- At least one sensing or processing configuration can be compared against the baseline configuration.

### User Story 3 — Training Data

As a runner, I want reliable heart-rate data from my workouts so that I can use it to track training progress and performance.

**Acceptance Criteria:**
- Heart-rate measurements can be recorded and saved over the duration of a test.
- Recorded measurements include timestamps.
- Saved data can be loaded and visualized after the experiment.

### User Story 4 — Low-Profile Wearable

As a runner, I want a low-profile heart-rate sensor so that the device does not significantly interfere with my workout.

**Acceptance Criteria:**
- The sensing hardware can be mounted on a wearable strap or test fixture.
- The prototype remains attached during the selected movement test.
- The device can collect data without requiring the user to hold the sensor in place.

### User Story 5 — Battery Usage

As a runner, I want a heart-rate sensor that does not need to be charged frequently so that I can use it for extended periods without interruption.

**Acceptance Criteria:**
- The prototype's electrical power consumption can be measured or calculated.
- Power requirements of tested sensing configurations can be compared.
- The team can estimate runtime for a defined battery capacity.

## 4. Feasibility

### Dataset

We will use a publicly available UC Irvine dataset containing physiological and activity measurements relevant to heart-rate monitoring.

For Sprint 1, feasibility will be demonstrated by:
- Downloading the dataset.
- Loading the data using a script in the repository.
- Documenting the dataset source and relevant signals.
- Producing at least one visualization from the loaded data.

### Hardware

We will demonstrate hardware feasibility by obtaining and testing the initial PPG sensing hardware and microcontroller.

For Sprint 1:
- The microcontroller will be connected and programmed.
- The PPG sensor will communicate with the microcontroller.
- Raw PPG measurements will be collected.
- A sample recording will be saved and visualized.

## 5. Tooling

- **Python** — Data loading, signal processing, visualization, and experimental analysis.
- **Git/GitHub** — Version control, issue tracking, pull requests, and team collaboration.
- **GitHub Projects** — Tracking user stories and Sprint 1 progress.
- **Microcontroller** — Controlling sensors and transferring measurements to a computer.
- **PPG sensor** — Collecting raw optical pulse measurements from the user.
- **Motion sensor** — Recording movement for comparison with PPG signal corruption.
- **LLM collaboration** — Assisting with prototype design, debugging, documentation, and exploration of implementation approaches.

## 6. Sprint 1 Demo

At the end of two weeks, we will show an end-to-end system that loads and visualizes heart-rate data from the selected dataset and collects, saves, and visualizes raw PPG measurements from our initial hardware prototype.