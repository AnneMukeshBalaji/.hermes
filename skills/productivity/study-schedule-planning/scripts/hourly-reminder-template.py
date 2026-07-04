#!/usr/bin/env python3
"""
Template script for hourly study reminder Telegram cron job.
Usage:
1. Copy to ~/.hermes/scripts/
2. Define topics per day in the topics{} dict
3. Define schedule messages with the hour -> message mapping
4. Create cron job: cronjob(action='create', script='your-script.py', no_agent=True,
       schedule='0 5-23 <day1>,<day2> <month> *', deliver='origin')
"""
from datetime import datetime

now = datetime.now()
hour = now.hour
day = now.day

topics = {
    # Example: day 4 (Saturday)
    4: {
        "aptitude": "Topic A - resources here",
        "dsa": "Topic B",
        "sb": "Topic C"
    },
    # Example: day 5 (Sunday)
    5: {
        "aptitude": "Topic D - resources here",
        "dsa": "Topic E",
        "sb": "Topic F"
    }
}

t = topics.get(day, topics[4])

schedule = {
    5:  f"Start Day - Aptitude: {t['aptitude']}",
    6:  f"Continue Aptitude: {t['aptitude']}",
    7:  "Break",
    8:  f"Back to Aptitude: {t['aptitude']}",
    9:  f"Start DSA: {t['dsa']}",
    10: f"Continue DSA: {t['dsa']}",
    11: f"Continue DSA: {t['dsa']}",
    12: "DSA until 12:20, then Lunch",
    13: "Back from Lunch - Continue DSA",
    14: f"Continue DSA: {t['dsa']}",
    15: f"Continue DSA - last hour: {t['dsa']}",
    16: f"Start Spring Boot: {t['sb']}",
    17: f"Continue Spring Boot: {t['sb']}",
    18: "Dinner Break",
    19: f"Back to Spring Boot: {t['sb']}",
    20: f"Continue Spring Boot: {t['sb']}",
    21: f"Continue Spring Boot: {t['sb']}",
    22: f"Continue Spring Boot: {t['sb']}",
    23: "Wrap-up - Review day"
}

if hour in schedule:
    msg = schedule[hour]
elif hour < 5:
    msg = "Sleep time."
else:
    msg = "Off-schedule."

day_name = "Saturday" if day == 4 else "Sunday"
print(f"[{day_name} - {hour}:00] {msg}")
