---
name: obsidian-workflow
description: Workflow for managing Obsidian vaults as an autonomous content creator.
---

# Obsidian Workflow

This skill extends the core `obsidian` skill with specific workflows for acting as an autonomous content creator and note manager.

## Workflow Preferences
- **Agent as Content Creator:** The user directs, and the agent performs all creation, updating, and organization of notes.
- **Vault Location:** The agent assumes responsibility for managing notes in `/home/luffy/Documents/ObsidianVault`.
- **Standardized Content:** Notes are created with clear headings and organized sections.
- **No Manual Writing:** The user does not write notes; the agent is responsible for writing/patching them based on user input.

## Vault Organization Strategy

### Folder Structure
Organize notes into topic-based folders rather than keeping everything flat in the root:

```
ObsidianVault/
├── Dashboard.md                 ← Minimal landing page (points to HTML dashboard if one exists)
├── Dashboard.html               ← Self-contained HTML dashboard (if user wants website-like UI)
├── Spring Boot/                 ← Topic folder (15+ notes)
│   ├── 01_Introduction.md
│   └── ...
├── DSA/
│   ├── DSA-30-Day-Plan.md
│   └── Aptitude-30-Day-Plan.md
└── ...
```

Rules:
- **One topic per folder.** If a folder would hold only one file, keep it flat until it grows.
- **Use subdirectories** when a topic has 2+ files (e.g. `DSA/`, `Spring Boot/`).
- **Dashboard vs Index.md:** When the user asks for a home page / dashboard / overview, prefer a self-contained HTML file (`Dashboard.html`) with inline CSS over markdown with emoji symbols. Users who say "like a website" or "like a dashboard" want HTML + CSS, not markdown. If they just want navigation links, a plain `Dashboard.md` with `[[wikilinks]]` is sufficient.

### Cleanup Workflow
When the user asks to clean up or organize:
1. List all notes with `search_files(target="files", pattern="*.md")`
2. Read each note to understand its topic
3. Propose a folder structure
4. Get approval before moving/deleting
5. Use `terminal` for `mv`/`rm` operations on notes, not file tools (bulk operations)

### Deleting Notes
- Confirm with the user before deleting any note
- Use `terminal` `rm` for removal
- Inform the user of what was removed

### Renaming Notes
- Use `terminal` `mv` for rename operations
- Update any `[[wikilinks]]` that pointed to the old name in other notes

## Creating a New Note
1. Determine correct folder based on topic
2. Write with proper Markdown hierarchy (`# title`, `## section`, etc.)
3. Add `[[wikilinks]]` to related existing notes where relevant
4. Inform the user of where it was created

## Creating Structured Tracker / Plan Documents

When the user asks to create a multi-day plan, schedule tracker, or study plan:

### Iterative Refinement Pattern
The user often builds these documents piece by piece — they give one instruction, you create the skeleton, then they refine the details over multiple turns. **Do not try to anticipate all future requirements upfront.**

1. **Create a minimal skeleton first** — just the date table or basic structure. Let the user tell you what to fill in next.
2. **Update in-place** — edit the same file via `patch` or `write_file` as the user refines. Prefer `patch` for small targeted changes (updating a single cell, changing a header).
3. **Use `write_file` for major restructures** — if the table layout changes completely (e.g. adding/removing columns, reordering), rewrite the whole file.
4. **Confirm each update** — after each edit, briefly summarize what changed to keep the user oriented.

### Document Structure for Trackers
- **Header block:** Start/end dates, total days, any recurring schedule notes
- **Schedule summary table:** If there are variable day types (holidays vs normal days), show a quick-reference table of the day types and time slots
- **Progress log table:** The core tracking table with Day #, Date, Day of week, Day type, Topics/Tasks, Done?, Notes
- Holiday rows should be visually distinct (🎉 emoji, different label) so the user can see which days have more time

### Handling Schedule Constraints
When the user specifies variable study hours per day type:
1. Calculate and show the total hours available per day type
2. List which specific dates fall into each type
3. Mark each row in the progress table with its type so it's visible at a glance
4. Let the user decide how to allocate content across day types

### Multi-Subject Allocation Within a Plan
When the user wants to study multiple subjects in the same plan:

1. **Collect allocation per subject** — Ask or calculate how many hours per subject per day type. Let the user propose the split, don't assume it.
2. **Build time-block tables** — For each day type (normal, holiday), create a time-slot schedule showing which subject fills which block. Use exact clock times (e.g., "6:00 PM → 6:50 PM: Aptitude") so the user knows when to switch.
3. **Show each day's row with per-subject breakdown** — Use separate columns in the progress table (College Apt | College DSA | Home Apt | Home DSA | Home SB) rather than lumping everything into one "Topics" column. This lets the user see at a glance if their day is balanced.
4. **Calculate and display grand totals** — After laying out all 30 days, add a totals row or section showing cumulative hours per subject. The user cares about the overall balance.

### Handling Day-of-Week Dependent Schedules
When the user has different activities on different days of the week (e.g., DSA in college only Mon/Tue/Thu/Fri):

1. **Create a day-type matrix** — Which days of the week get which activities. Show as a quick table:
   ```
   | Day       | College Apt | College DSA |
   |-----------|:-----------:|:-----------:|
   | Mon,Tue,Thu,Fri | ✅ 100m | ✅ 100m |
   | Wed, Sat  | ✅ 100m    | ❌ (other work) |
   ```
2. **Label each row with the day name** — Include the day of week column so the user can quickly see "Wed" = no college DSA, "Sat" = different schedule.
3. **Calculate totals per activity type** — Count how many days run each variant and multiply by the per-day hours. Show this as a separate subtotal.

### Splitting Study Time Across Locations
When the user studies both at college (daytime) and at home (evening):

1. **Treat them as separate time buckets** — College time and home time have different durations and constraints. Don't combine them into one "total per day" without showing the split.
2. **Show both in the schedule header** — Create separate sections: "College Time" with per-day details and "Home Time" with the clock schedule.
3. **Use separate columns in the progress table** — One column for each location-activity combination (e.g., "College Apt", "College DSA", "Home Apt", "Home DSA", "Home SB"). Empty cells for holidays or days without that slot.
4. **Sum location subtotals separately** — At the end, show "College total" vs "Home total" vs "Grand total" so the user sees the contribution of each.

### Finalize the Plan with Cumulative Totals
After the full schedule is laid out for all 30 days, always add a totals section:

1. **Calculate per-subject totals** — Sum hours across all day types for each subject.
2. **Show a clean totals table**:
   ```
   | Subject      | Normal Days | Holidays | Total |
   |--------------|:-----------:|:--------:|:-----:|
   | Aptitude     | 60h         | 18h      | 78h   |
   | DSA          | 95.3h       | 36h      | 131.3h|
   | Spring Boot  | 52h         | 36h      | 88h   |
   | **Total**    | **207.3h**  | **90h**  | **297.3h** |
   ```
3. **Confirm with the user** before filling in actual content — they may want to adjust the splits after seeing the totals.

### Handle Date Corrections Graciously
- When the user says "keep these dates only" or simplifies the range, **reset the table completely** — don't try to preserve previous calculations
- Always confirm the final date range with the user before filling in content

## Creating an HTML Dashboard

When the user asks for a dashboard, home page, index, or visual overview of the vault — especially if they say "like a website" or reject emoji-heavy markdown:

1. **Create a self-contained HTML file** (`Dashboard.html`) in the vault root
2. **Structure:**
   - Dark theme (common preference for dev tools)
   - Card-based layout with a grid for each topic section
   - Progress bars to show completion status
   - Header with quick stats (total notes, completion per section)
   - Today's focus / action items section
   - Quick-jump links to the most important or interview-critical notes
3. **Keep it self-contained:** All CSS inline in `<style>`, no external dependencies (system font stack, no JS frameworks)
4. **Use file:// links** to point to other notes in the vault (`<a href="Spring Boot/06_Authentication.md">`)
5. **Also update Dashboard.md** to be a minimal landing page that links to the HTML version, so Obsidian's file explorer still shows something useful

## Guidelines
- Always verify the directory structure before writing.
- Maintain consistent naming conventions and structure across notes.
- When creating content, ensure high-quality Markdown with proper hierarchy.
- Prefer topic-based folders over flat list when vault has 4+ notes.
