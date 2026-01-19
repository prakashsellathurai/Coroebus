import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Path to activities
ACTIVITIES_DIR = Path(__file__).parent / "activities" / "activities"

def get_pace_string(speed_mps):
    """Convert speed in m/s to min/km string (e.g. '5:00')."""
    if speed_mps <= 0:
        return "-"
    
    seconds_per_km = 1000 / speed_mps
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    return f"{minutes}:{seconds:02d}"

def calculate_predictions():
    """
    Calculate race pace, zone 2 pace, and easy pace based on recent run history.
    
    Returns:
        dict: containing formatted strings for different paces.
    """
    
    cutoff_date = datetime.now().date() - timedelta(days=90)
    best_speed_mps = 0.0
    
    if not ACTIVITIES_DIR.exists():
        return {
            "race_pace": "-",
            "zone2_pace": "-",
            "easy_pace": "-"
        }

    # Find best speed in runs > 5km in last 90 days
    try:
        if not ACTIVITIES_DIR.exists():
             print(f"Directory not found: {ACTIVITIES_DIR}")
             return { "race_pace": "-", "zone2_pace": "-", "easy_pace": "-" }
             
        # Use os.listdir to be safe
        files = os.listdir(ACTIVITIES_DIR)
        activity_files = [ACTIVITIES_DIR / f for f in files if f.endswith(".json")]
        
        # print(f"Scanning directory: {ACTIVITIES_DIR}")
        # print(f"Found {len(activity_files)} files.")
        
        for file_path in activity_files:
            # Skip stream files
            if "_streams" in file_path.name:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    activity = json.load(f)
                    
                    # Check if it's a Run
                    if activity.get("type") != "Run":
                        continue
                        
                    # Check date
                    date_str = activity.get("start_date")
                    if not date_str:
                        continue
                        
                    # Parse date (handle Z if present)
                    date_dt = datetime.strptime(date_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").date()
                    
                    if date_dt < cutoff_date:
                        # print(f"Skipping {file_path.name}: Date {date_dt} < {cutoff_date}")
                        # Keep it commented to avoid spam, but useful if we enable it.
                        pass
                        
                    # Check distance (meters) - strictly > 5000m
                    distance = activity.get("distance", 0)
                    if distance <= 5000:
                        # print(f"Skipping {file_path.name}: Distance {distance} <= 5000")
                        continue
                        
                    # Check speed
                    avg_speed = activity.get("average_speed", 0)
                    # print(f"Candidate: {file_path.name}, Date: {date_dt}, Dist: {distance}, Speed: {avg_speed}")
                    if avg_speed > best_speed_mps:
                        best_speed_mps = avg_speed
                        
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error scanning activities: {e}")
        return {
            "race_pace": "-",
            "zone2_pace": "-",
            "easy_pace": "-"
        }

    if best_speed_mps == 0:
         return {
            "race_pace": "-",
            "zone2_pace": "-",
            "easy_pace": "-"
        }
        
    # Calculate Prediction Ranges
    # Race Pace Reference = 10k/Threshold roughly
    race_pace_str = get_pace_string(best_speed_mps)
    
    # Zone 2: 0.80 - 0.88 of Threshold Speed
    z2_low_speed = best_speed_mps * 0.80
    z2_high_speed = best_speed_mps * 0.88
    z2_str = f"{get_pace_string(z2_high_speed)} - {get_pace_string(z2_low_speed)} /km" # faster - slower
    
    # Easy: 0.70 - 0.78 of Threshold Speed
    easy_low_speed = best_speed_mps * 0.70
    easy_high_speed = best_speed_mps * 0.78
    easy_str = f"{get_pace_string(easy_high_speed)} - {get_pace_string(easy_low_speed)} /km"

    return {
        "race_pace": f"{race_pace_str} /km",
        "zone2_pace": z2_str,
        "easy_pace": easy_str
    }

def get_race_pace_history():
    """
    Extract historical race pace data from activities.
    Returns:
        list of dicts: [{"date": date_obj, "speed_mps": float}, ...]
    """
    history = []
    
    if not ACTIVITIES_DIR.exists():
        return history

    try:
        files = os.listdir(ACTIVITIES_DIR)
        activity_files = [ACTIVITIES_DIR / f for f in files if f.endswith(".json")]
        
        for file_path in activity_files:
            if "_streams" in file_path.name:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    activity = json.load(f)
                    
                    if activity.get("type") != "Run":
                        continue
                        
                    date_str = activity.get("start_date")
                    if not date_str:
                        continue
                        
                    date_dt = datetime.strptime(date_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").date()
                    
                    distance = activity.get("distance", 0)
                    if distance <= 5000:
                        continue
                        
                    avg_speed = activity.get("average_speed", 0)
                    if avg_speed > 0:
                        history.append({
                            "date": date_dt,
                            "speed_mps": avg_speed
                        })
                        
            except Exception:
                continue
                
        # Sort by date
        history.sort(key=lambda x: x["date"])
        
    except Exception as e:
        print(f"Error getting history: {e}")
    history = [{"date": rec["date"].isoformat(), "speed_mps": rec["speed_mps"]} for rec in history]
    return history
