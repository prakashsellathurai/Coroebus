from performance import get_race_pace_history

print("Testing get_race_pace_history()...")
history = get_race_pace_history()

print(f"Found {len(history)} records.")
if history:
    print("First 3 records:")
    for rec in history[:3]:
        print(rec)
    print("Last 3 records:")
    for rec in history[-3:]:
        print(rec)
else:
    print("No history found.")
