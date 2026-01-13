# Coroebus 🏃‍♂️🚴‍♀️🏊‍♂️

Coroebus is a performance tracking dashboard designed to help athletes monitor their Training Load, Fitness (CTL), Fatigue (ATL), and Readiness (TSB).

Built with **Shiny for Python**, **Plotly**, and **Pandas**, it provides an interactive way to visualize training trends and identify optimal training zones.

## Features

- **Automated Load Calculation**: Processes Strava-style activity JSON files and calculates a Training Stress Score (TSS) equivalent.
- **Dynamic Metrics**:
  - **Fitness (CTL)**: Chronic Training Load (Long-term trend).
  - **Fatigue (ATL)**: Acute Training Load (Short-term stress).
  - **Form (TSB)**: Fitness minus Fatigue, indicating recovery and readiness.
- **Interactive Visualization**:
  - Zoom, pan, and hover over data points.
  - Adjust CTL and ATL time constants via sliders to see real-time changes.
- **Training Zones**:
  - 🔴 **High Risk**: TSB < -30 (High injury risk/overreaching).
  - 🟢 **Optimal**: TSB between -10 and -30 (Sweet spot for fitness gains).
  - ⚪ **Other**: TSB > -10 (Freshness or recovery).

## Project Structure

```text
Coroebus/
├── activities/       # Raw activity JSON files
├── app.py           # Main Shiny application
├── load_data.py     # Script to process activities into daily_load.csv
├── daily_load.csv   # Aggregated training load data
├── pyproject.toml   # Project dependencies and metadata
└── README.md        # This file
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended for package management)

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```

### Usage

1. **Process Activity Data**:
   Place your Strava activity JSON files in the `activities/` directory, then run:
   ```bash
   uv run python load_data.py
   ```
   This will generate `daily_load.csv`.

2. **Run the Dashboard**:
   ```bash
   uv run python -m shiny run app.py --reload
   ```
   Open the provided URL (usually `http://127.0.0.1:8000`) in your browser.

## Customization

The dashboard allows you to tune the Banister model parameters:
- **Fitness (CTL) Days**: Default is 42 days (standard for chronic load).
- **Fatigue (ATL) Days**: Default is 7 days (standard for acute load).

---
*Created by Prakash Sellathurai*
