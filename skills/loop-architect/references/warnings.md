# Warnings, Cost Control, and Anti-Patterns

Things that go wrong with loops and how to prevent them.

---

## Cost Control

Loops burn tokens autonomously. Every unsupervised cycle is a model
call you didn't manually approve. Goal loops are the worst offenders
because they iterate until a condition is met, and a vague condition
means infinite iteration.

### Cost hierarchy (cheapest to most expensive)

1. **Schedule loop, read-only** (daily summary): predictable, low cost
2. **Event loop, narrow trigger** (on PR open): cost scales with events
3. **Schedule loop with subagents** (daily + helpers): multiplied cost
4. **Goal loop, tight condition** (all tests pass): bounded but variable
5. **Goal loop, loose condition** (make it better): unbounded, dangerous
6. **Compound loop** (schedule + subagents + goals): multiply everything

### How to control cost

1. **Set iteration limits.** Even if using /goal, tell the agent to
   stop after N attempts and escalate to a human.
2. **Scope narrowly.** "Fix failing tests in test/auth/" not "fix all
   tests everywhere."
3. **Use cheap models for exploration.** Not every subagent needs the
   strongest model. Explorers and reporters can use fast models.
4. **Skip no-op cycles.** If nothing changed since last run, exit
   early. Check git log, issue timestamps, or state files.
5. **Log token usage.** Track what each loop costs per run so you can
   spot runaway loops early.

### Red flags

- A goal loop that hasn't converged after 10 iterations
- A schedule loop that takes longer to run than its interval
- A subagent that spawns its own subagents without limits
- A loop with no escalation path (it just keeps trying forever)

---

## Prompt Quality for Loops

Loop prompts need more precision than conversational prompts. You are
not there to course-correct. Every ambiguity becomes a confident guess.

### The intent debt problem

The agent starts every session cold. It will fill any hole in your
intent with a confident guess (Osmani calls this "intent debt"). A
skill reduces this by codifying project knowledge. But the loop prompt
itself still needs to be precise.

### Common prompt failures

**Too vague:**
```
Check our code and fix any issues.
```
Problem: "issues" is undefined. The agent will find things to fix that
you didn't want changed and miss things you care about.

**Too broad:**
```
Review all files in the repo and ensure they follow best practices.
```
Problem: "all files" and "best practices" are both unbounded. This
loop will never finish.

**No success criteria:**
```
Make the documentation better.
```
Problem: "better" is subjective. The agent can't validate its own
work. It will either stop too early or never stop.

**No escalation:**
```
Fix all the failing tests.
```
Problem: What if a test fails because of a real bug that needs a
design decision? The agent will attempt a fix, break something else,
attempt another fix, and spiral.

### Good prompt checklist

Before enabling any loop prompt, verify:

- [ ] **Scope is bounded**: specific files, directories, or issues
- [ ] **Actions are verbs**: "run tests", "post to Slack", "create PR"
- [ ] **Success criteria are measurable**: "all tests pass", "zero lint errors"
- [ ] **Escalation path exists**: "if blocked after 3 attempts, stop and post to #team"
- [ ] **Anti-patterns are named**: "do NOT modify files outside src/"
- [ ] **Subagent goals are specific**: each helper has its own clear exit condition

---

## Structural Anti-Patterns

### The Monolith Loop

**Problem:** One giant loop that does discovery, implementation,
testing, deployment, and reporting all in one prompt.

**Fix:** Break into stages. Use a parent loop for orchestration and
subagents for each stage. The parent tracks state and routes work.

### The Echo Chamber

**Problem:** The same agent writes code and validates it. It will
always think its own code is correct.

**Fix:** Maker/checker split. The implementer writes code. A separate
verifier with different instructions (and potentially a different
model) checks it. This is what /goal does internally: a separate
small model validates the goal condition.

### The Context Bomb

**Problem:** Loading every skill, every reference file, and every
piece of project context on every loop cycle. The agent runs out of
context window or wastes tokens processing irrelevant information.

**Fix:** Load only what's needed for THIS cycle. Use progressive
disclosure: the loop prompt loads core skills, and subagents load
specialized skills only when they need them.

### The Groundhog Day Loop

**Problem:** No state tracking between runs. The loop rediscovers
the same issues, attempts the same fixes, and produces the same
reports every cycle.

**Fix:** Add a memory layer. Write results to a markdown file, update
a Jira ticket, or use git branch state. Check memory at the start of
each cycle and skip already-handled items.

### The Token Bonfire

**Problem:** A goal loop with vague success criteria that iterates
indefinitely, burning tokens without converging.

**Fix:** Write measurable goal conditions. Set iteration limits.
Monitor cost per run. If a loop costs more than a human would, it's
not saving you anything.

### The Yolo Deploy

**Problem:** A loop that pushes changes without review. Automations
are powerful, but unsupervised code changes to production branches
are dangerous.

**Fix:** Always target a feature branch. Require human approval for
merges to main. Use the loop to prepare work, not to ship it.

---

## When NOT to Use a Loop

Not everything needs to be a loop. Sometimes a prompt is fine.

- **One-time tasks**: refactoring a module, writing a feature. Just
  prompt it directly.
- **Subjective work**: design decisions, architecture choices, naming.
  These need human judgment, not autonomous iteration.
- **Low-frequency tasks**: something you do once a quarter. A loop is
  overhead for rare work.
- **Tasks requiring deep context**: if the agent needs to understand
  your entire system to do the work, a conversational session where
  you provide context is more effective than an unsupervised loop.

The goal is not to eliminate prompting. The goal is to automate the
prompts that are repetitive, predictable, and verifiable. Everything
else still benefits from a human in the loop.

---

## Sources

- Addy Osmani, "Loop Engineering" (June 2026):
  https://addyosmani.com/blog/loop-engineering/
- How I AI podcast, "Prompts are out and loops are in" (June 2026)
- OpenAI, "Using Goals in Codex":
  https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex
- Internal Slack discussions:
  - forum-cursor: /loop as Cursor's first version of /goal
  - team-openshift-ai-dashboard-experiments: /preflight skill for
    PR merge readiness loops
  - acs-ai: Agent memory and experience feedback loops
  - wg-ge-agentic-sdlc: Agent loops for cloud-native verification
