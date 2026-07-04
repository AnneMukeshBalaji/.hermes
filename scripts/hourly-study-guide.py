#!/usr/bin/env python3
"""Hourly study guide for Saturday(Jul 4) and Sunday(Jul 5)."""
from datetime import datetime

now = datetime.now()
hour = now.hour
day = now.day       # 4 = Saturday, 5 = Sunday

# Resources
APTITUDE_PRACTICE = "GeeksforGeeks, IndiaBix, PrepInsta"
APTITUDE_LEARN = "Aptitude Academy (YouTube), Fresh Careers (TCS NQT)"

# Topics by day
topics = {
    4: {  # Saturday
        "aptitude": f"Number System (Divisibility, LCM/HCF, remainders, factors) - Learn: {APTITUDE_LEARN} | Practice: {APTITUDE_PRACTICE}",
        "dsa": "Arrays (Two-pointer, prefix sum, sliding window)",
        "sb": "REST CRUD API (Entity, Repository, Service, Controller, PostgreSQL, DTOs, validation)"
    },
    5: {  # Sunday
        "aptitude": f"Train Problems (Time, Speed, Distance - crossing platform/pole, relative speed) - Learn: {APTITUDE_LEARN} | Practice: {APTITUDE_PRACTICE}",
        "dsa": "Linked List (Insertion, deletion, reversal, cycle detection, merge)",
        "sb": "Exception Handling + Validation (@ControllerAdvice, Bean Validation)"
    }
}

t = topics.get(day, topics[4])

# Hour -> message mapping
schedule = {
    5:  f"Start Day - Aptitude: {t['aptitude']}",
    6:  f"Continue Aptitude: {t['aptitude']} - deep focus, solve problems",
    7:  "Break time. Rest until 8:00 AM. Get up, stretch, hydrate.",
    8:  f"Back to Aptitude - final hour: {t['aptitude']}",
    9:  f"Start DSA: {t['dsa']}",
    10: f"Continue DSA: {t['dsa']} - solve problems actively, don't just read",
    11: f"Continue DSA: {t['dsa']} - keep going",
    12: "DSA until 12:20, then Lunch Break (12:20 - 1:10 PM)",
    13: "Back from Lunch. Continue DSA.",
    14: f"Continue DSA: {t['dsa']} - push through",
    15: f"Continue DSA: {t['dsa']} - last hour of DSA for today",
    16: f"Start Spring Boot: {t['sb']}",
    17: f"Continue Spring Boot: {t['sb']}",
    18: "Dinner Break. Rest until 7:00 PM.",
    19: f"Back to Spring Boot: {t['sb']}",
    20: f"Continue Spring Boot: {t['sb']}",
    21: f"Continue Spring Boot: {t['sb']}",
    22: f"Continue Spring Boot: {t['sb']} - almost done",
    23: "Wrap-up. Review what you learned today. Plan for tomorrow."
}

if hour in schedule:
    msg = schedule[hour]
elif hour < 5:
    msg = "Sleep time (12 AM - 5 AM). Rest well."
else:
    msg = "Off-schedule time."

day_name = "Saturday" if day == 4 else "Sunday"
print(f"[{day_name} - {hour}:00] {msg}")