---
name: study-schedule-planning
description: "Build intensive study schedules for multi-day preparation blocks. Manages hourly/daily time allocation, subject splits, break placement, sleep, and delivery (Telegram cron reminders)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [study-plan, schedule, time-management, preparation]
    related_skills: [plan, obsidian-workflow]
---

# Study Schedule Planning

Use this when the user asks for a study plan spanning one or more full days.

## Process

### 1. Clarify the constraints first

Before laying out any schedule, ask:

- What subjects/topics are being studied?
- What are the start and end times each day? (e.g., 5 AM - 12 AM = 19h window)
- What are the fixed break times? (breakfast, lunch, dinner, etc.)
- How should the remaining time be split between subjects?
- Is this a holiday or college day? (affects available hours)

### 2. Do NOT create files prematurely

Plan flow:

1. Ask clarifying questions.
2. Present the schedule **inline in chat**.
3. Iterate on timings and subject splits based on user feedback.
4. Only save to a file when the user explicitly says "save it", "prepare the plan", or "write it down".

**Pitfall:** Users may correct you if you write a file before they approve the plan. If this happens, delete the file immediately and continue in-chat.

### 3. Calculate total available time

| Input | Calculation |
| :--- | :--- |
| End - Start = Total window | e.g., 12 AM - 5 AM = 19h |
| Minus all breaks | Breakfast, lunch, dinner, short breaks |
| = Net study time | e.g., 19h - 2h 50m = 16h 10m |

### 4. Subject split

When the user says "split remaining time equally" or gives a specific split:

- Calculate per-day allocation: `net_study_hours / number_of_subjects` or per the ratio given
- Multiply by number of days for total

### 5. Build the hourly table

Use a clean table format:

| Time Slot | Activity | Duration |
| :--- | :--- | :--- |

Keep break rows clearly marked. Show subject totals at the bottom.

### 6. Topic assignment

Ask what specific topics to cover within each subject before finalizing. Be specific with sub-topics (e.g., "Arrays: two-pointer, prefix sum, sliding window" — not just "Arrays").

### 7. Automation setup (when requested)

If the user wants hourly Telegram reminders:

- Write a Python script to `~/.hermes/scripts/` that determines the current hour/day and prints a study instruction
- Create a cron job with `cronjob(action='create', script='script-name.py', no_agent=True, schedule='...', deliver='origin')`
- The cron schedule should only fire during waking hours (e.g., 5 AM - 11 PM) on the specified dates
- If the user asks about the laptop being off, explain that local cron stops when the machine sleeps and offer alternatives (GitHub Actions, taking a screenshot, saving to Obsidian)

**Pitfall:** Do not use emojis in files, notes, or saved plans — the user explicitly dislikes them.

## Common Topics Reference

### Aptitude resources (this user)
- Learn: Aptitude Academy (YouTube), Fresh Careers (TCS NQT)
- Practice: GeeksforGeeks, IndiaBix, PrepInsta

### Sample topic lists
- **Aptitude:** Number System, Percentages, Profit & Loss, Time & Work, Train Problems, Time Speed Distance
- **DSA:** Arrays (two-pointer, prefix sum, sliding window), Linked Lists (reversal, cycle detection, merge), Trees, Graphs, DP
- **Spring Boot:** REST CRUD API (Entity/Repository/Service/Controller/PostgreSQL/DTOs), Exception Handling (@ControllerAdvice, Bean Validation), JWT Security

## Pitfalls

- Never save a plan file until the user explicitly approves. "Prepare a plan" means show it, not write it.
- Present separate tables for multi-day plans, not one merged table.
- Always calculate total study time across all days when asked.
