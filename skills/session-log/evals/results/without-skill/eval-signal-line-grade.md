# Eval signal-line Grading — without-skill

**Result:** 3/5 PASS

| Assertion | Result | Evidence |
|---|---|---|
| The output must start with '# Session Log —' followed by today's date | **PASS** | "# Session Log — 2026-06-16" |
| The second line must be a '**Signal:**' line | **PASS** | "**Signal:** 2 important items today. 1 stale carry-forward at DAY 4 needs attention." |
| The Signal line must mention '2 important items' | **PASS** | "2 important items" present |
| The Signal line must mention the stale carry-forward | **PASS** | "1 stale carry-forward at DAY 4" |
| A **Tags:** line must appear after the Signal line | **FAIL** | Tags line exists but uses different formatting — no "#daily-log" or "#YYYY-MM-DD" format as required. Contains "#sprint-work #carried-forward #stale" but missing mandatory tags. |
