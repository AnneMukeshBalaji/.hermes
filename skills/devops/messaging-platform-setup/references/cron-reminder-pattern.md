# Cron + Telegram Reminder Pattern

Use cron jobs with `no_agent=True` + a Python script to send timed reminders to the user via Telegram.

## When to Use

- Hourly study reminders
- Break notifications
- Scheduled check-ins ("review what you learned")
- Any recurring time-based message that doesn't need LLM reasoning

## Pattern

### 1. Write a Python script in `~/.hermes/scripts/`

The script checks `datetime.now()` to determine what message to send based on the time and day.

```python
#!/usr/bin/env python3
from datetime import datetime

now = datetime.now()
hour = now.hour
day = now.day

# Map hour -> message
schedule = {
    5:  "Start Aptitude",
    6:  "Continue Aptitude",
    7:  "Break time",
    8:  "Back to Aptitude",
    9:  "Start DSA",
    10: "Continue DSA",
    # ...
}

# Map day -> topic overrides
topics = {
    4: {"aptitude": "Number System", "dsa": "Arrays"},
    5: {"aptitude": "Train Problems", "dsa": "Linked List"},
}

msg = schedule.get(hour, "Off-schedule")
print(f"[{day} - {hour}:00] {msg}")
```

**Key rules:**
- Print the message to stdout — cron delivers it verbatim when `no_agent=True`
- The script runs in a fresh process, no conversation context
- Must be fully self-contained (no user interaction)

### 2. Create the cron job

```bash
# Schedule: run at minute 0 of hours 5-23 on specific dates
# Cron: 0 5-23 4,5 7 *
# no_agent=True: skips LLM, delivers script stdout directly
# deliver=origin: sends to the same chat (Telegram) this session is in
```

Use the `cronjob` tool:
```
cronjob(
    action='create',
    name='Hourly Study Guide',
    schedule='0 5-23 4,5 7 *',
    script='hourly-study-guide.py',
    no_agent=True,
    deliver='origin'
)
```

### 3. Cron Schedule Patterns

| Goal | Cron Expression |
| :--- | :--- |
| Every hour, 5 AM - 11 PM, specific dates | `0 5-23 4,5 7 *` (minutes 0, hours 5-23, days 4-5, month 7) |
| Every hour, specific hours, every day | `0 9-18 * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Every 2 hours | Use `repeat` field: `schedule='0 5-23 * * *'` is wrong for every 2h; use `'every 2h'` |

### 4. Delivery Behavior with `no_agent=True`

- **Non-empty stdout** → message is sent to the user (Telegram)
- **Empty stdout** → silent (nothing is sent)
- **Non-zero exit / timeout** → error alert is sent

This makes it easy to have the script stay quiet during times when no message is needed (e.g., sleep hours that are outside the cron range anyway).

## Pitfalls

- **Script must be standalone** — it cannot access conversation memory, skills, or tools. All logic must be in the Python code.
- **Time zone** — Python's `datetime.now()` uses the system timezone. Verify with `date` command before scheduling.
- **Day detection** — Use `now.day` for date-specific messages, `now.weekday()` for day-of-week (Monday=0, Sunday=6).
- **No LLM involved** — `no_agent=True` means the prompt and skills fields are ignored. The script output IS the message.
