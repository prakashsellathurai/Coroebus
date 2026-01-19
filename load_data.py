import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

# Path to activities
ACTIVITIES_DIR = Path(__file__).parent / "activities" / "activities"

def calculate_load(activity):
    """
    Simulate a Training Stress Score (TSS) like metric.
    In a real app, we'd use FTP or MaxHR. 
    Here we use heuristic scaling.
    """
    moving_time = activity.get("moving_time", 0)
    avg_watts = activity.get("average_watts")
    avg_hr = activity.get("average_heartrate")
    
    # Base load: 50 points per hour of moving time
    base_load = (moving_time / 3600) * 50
    
    if avg_watts:
        # Scale by power if available (assume 200W is a solid effort)
        load = base_load * (avg_watts / 200)
    elif avg_hr:
        # Scale by HR if available (assume 140bpm is a solid effort)
        load = base_load * (avg_hr / 140)
    else:
        load = base_load
        
    return load

def get_daily_load():
    data = []
    
    if not os.path.exists(ACTIVITIES_DIR):
        print(f"Directory not found: {ACTIVITIES_DIR}")
        return

    files = [f for f in os.listdir(ACTIVITIES_DIR) if f.endswith(".json") and "_streams" not in f]
    print(f"Processing {len(files)} activity files...")
    
    for filename in files:
        filepath = os.path.join(ACTIVITIES_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                activity = json.load(f)
                
                # We only want basic activity info (resource_state 2 or 3)
                if not isinstance(activity, dict) or "start_date" not in activity:
                    continue
                    
                date_str = activity["start_date"]
                # Convert "2024-09-10T02:15:29Z" to date
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").date()
                
                load = calculate_load(activity)
                
                data.append({
                    "date": date,
                    "load": load,
                    "type": activity.get("type", "Other")
                })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if not data:
        print("No valid activity data found.")
        return

    df = pd.DataFrame(data)
    
    # Aggregate by date
    daily_load = df.groupby("date")["load"].sum().reset_index()
    
    # Fill missing dates with 0 load
    all_dates = pd.date_range(start=daily_load["date"].min(), end=daily_load["date"].max())
    daily_load["date"] = pd.to_datetime(daily_load["date"])
    daily_load = daily_load.set_index("date").reindex(all_dates, fill_value=0).reset_index()
    daily_load.columns = ["date", "load"]
    
    return daily_load

if __name__ == "__main__":
    main()
