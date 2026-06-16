# Eval carry-forward Grading — with-skill

**Result:** 6/6 PASS

| Assertion | Result | Evidence |
|---|---|---|
| The output must contain a '## Carried Forward' section | **PASS** | "## Carried Forward" section present |
| The carried item must show [DAY 2] marker | **PASS** | "### [DAY 2] Prototype-evaluate PR" |
| The carried item must reference the original date 2026-06-15 | **PASS** | "**Originally:** 2026-06-15" |
| The carried item must show 'Last status: in progress' or similar | **PASS** | "**Last status:** in progress — PR #42 open, awaiting Andy's review" |
| The output must include a #carried-forward tag | **PASS** | Tags line includes "#carried-forward" |
| The carried item must NOT be tagged #stale (only 2 days, not 3+) | **PASS** | No #stale in tags |
