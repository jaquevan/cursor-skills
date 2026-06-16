# Eval importance-scoring Grading — with-skill

**Result:** 10/11 PASS

| Assertion | Result | Evidence |
|---|---|---|
| Session A must be scored 4 or 5 out of 5 | **PASS** | "Importance: 4/5 (involves manager + sprint ticket)" |
| Session B must be scored 1 out of 5 | **PASS** | "Importance: 1/5 (networking, no deliverables)" |
| Session C must be scored 1 or 2 out of 5 | **PASS** | "Importance: 1/5 (exploratory research, no deliverables)" |
| Session A must appear first in the sorted output | **PASS** | Session A is "### 1." in the list |
| Session B must appear last in the sorted output | **PASS** | Session B is "### 3." — last in the list |
| Session A must have the [IMPORTANT] prefix in its heading | **PASS** | "### 1. [IMPORTANT] 1:1 with Zack — prototype-creator eval integration" |
| Session B must NOT have the [IMPORTANT] prefix | **PASS** | "### 3. Intro coffee chat with fellow intern" — no prefix |
| The output must include a #zack tag | **PASS** | Tags line includes "#zack" |
| The output must include a #sprint-work tag | **PASS** | Tags line includes "#sprint-work" |
| The output must include a #networking tag for Session B | **FAIL** | Tags line does not include "#networking" — only present implicitly in the session description |
| Session B must NOT include Changed or Why fields | **PASS** | Session B only has What and Outcome fields |
