# Eval people-detection Grading — without-skill

**Result:** 4/5 PASS

| Assertion | Result | Evidence |
|---|---|---|
| The tags must include #andy | **PASS** | Tags include "#andy" |
| The tags must include #steven | **PASS** | Tags include "#steven" |
| The tags must NOT include #zack (he was not mentioned) | **PASS** | No "#zack" in tags |
| The tags must include #team (3+ people referenced) | **PASS** | Tags include "#team" |
| The tags must include #debugging for Session B | **FAIL** | Tags include "#ci" but not "#debugging" specifically |
