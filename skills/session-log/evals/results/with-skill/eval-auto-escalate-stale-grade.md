# Eval auto-escalate-stale Grading — with-skill

**Result:** 5/5 PASS

| Assertion | Result | Evidence |
|---|---|---|
| The item must show [DAY 3] marker (incremented from DAY 2) | **PASS** | "### [DAY 3] API integration blocked on backend team" |
| The importance must be 5/5 (auto-escalated at DAY 3+) | **PASS** | "**Importance:** 5/5 (auto-escalated — carried 3+ days)" |
| The output must include a #stale tag | **PASS** | Tags include "#stale" |
| The item must appear at the top of the Carried Forward section | **PASS** | It's the only item and appears first under "## Carried Forward" |
| The Signal line must mention the stale carry-forward by name or topic | **PASS** | "**Signal:** 0 important items, 1 stale carry-forward (API integration blocked on backend team)" |
