# Eval signal-line Grading — with-skill

**Result:** 5/5 PASS

| Assertion | Result | Evidence |
|---|---|---|
| The output must start with '# Session Log —' followed by today's date | **PASS** | "# Session Log — 2026-06-16" |
| The second line must be a '**Signal:**' line | **PASS** | "**Signal:** 2 important items, 1 stale carry-forward (DAY 4)" |
| The Signal line must mention '2 important items' | **PASS** | "2 important items" in Signal line |
| The Signal line must mention the stale carry-forward | **PASS** | "1 stale carry-forward (DAY 4)" |
| A **Tags:** line must appear after the Signal line | **PASS** | "**Tags:** #daily-log #2026-06-16 #stale #carried-forward" appears after Signal |
