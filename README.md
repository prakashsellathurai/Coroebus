# Coroebus 🏃‍♂️🚴‍♀️🏊‍♂️

Coroebus is a performance tracking dashboard designed to help athletes monitor their Training Load, Fitness (CTL), Fatigue (ATL), and Readiness (TSB).

Built with **Shiny for Python**, **Plotly**, and **Pandas**, it provides an interactive way to visualize training trends and identify optimal training zones.

## Features

- **Automated Load Calculation**: Processes Strava-style activity JSON files and calculates a Training Stress Score (TSS) equivalent.
- **Dynamic Metrics**:
  - **Fitness (CTL)**: Chronic Training Load (Long-term trend).
  - **Fatigue (ATL)**: Acute Training Load (Short-term stress).
  - **Form (TSB)**: Fitness minus Fatigue, indicating recovery and readiness.
  - **Ramp Rate**: 7-day change in Fitness (CTL) to monitor training progression.
  - **Estimated Race Pace**: Tracks best efforts (>5km) over time.
- **Pace Predictions**:
  - Automatically calculates **Zone 2 (Endurance)** and **Easy Run** paces based on recent best performances.
- **Interactive Visualization**:
  - **Synchronized Subplots**: Coordinated views for Load, Metrics, Ramp, and Pace.
  - **Spikelines**: Cross-chart markers for precise date comparison.
  - Zoom, pan, and hover over data points.
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
- [uv](https://github.com/astral-sh/uv)

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```

### Usage

1. **Process Activity Data**:
   Ensure the `activities/` directory is populated with Strava activity JSON files. 
   See [Strava Backup Setup](https://github.com/prakashsellathurai/strava-backup) for instructions on how to configure and sync your activities.
   
   Then, run:
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
