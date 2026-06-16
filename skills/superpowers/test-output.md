# Deep Dive: Improving the Agent Eval Harness Feedback Loop

**Mode:** Deep Dive (4-5 ideas with full depth)
**Topic:** Improving the agent eval harness at Red Hat — the feedback loop between skill creation and evaluation is slow and manual.

---

**1. Watch-and-Reeval on Save**

Right now, editing a SKILL.md and seeing the impact means manually running `/eval-run`, waiting minutes to hours, then reading the report. What if saving a SKILL.md automatically triggered a targeted re-run against only the cases that failed last time? A filesystem watcher (inotify/fswatch) monitors the skill file, diffs the change against the last edit, identifies which judges are likely affected, and fires off a fast eval pass using `--cases` (the subset that failed) and `--no-llm-judges` (deterministic judges only). Results stream into a terminal or status bar in real time. Full LLM judge runs happen on explicit request or git push.

**Why it works:** The eval harness already supports `--cases` for targeted runs and `--no-llm-judges` for fast deterministic-only scoring. The infrastructure for a 10-second feedback loop is already there — it just isn't wired to a trigger. Most skill edits fix structural issues (missing fields, wrong format) that deterministic `check` judges catch instantly. You don't need to wait for an Opus LLM judge to tell you a YAML field is missing.

**Risk:** False confidence. Deterministic judges catch format and structure, but the hardest bugs are semantic — and those require LLM judges. Teams might over-index on the fast loop and ship skills that pass `check` judges but fail `prompt` judges. You'd need a clear visual distinction between "fast check passed" and "full eval passed."

**First step:** Write a shell script that watches a SKILL.md with `fswatch`, reads the last `summary.yaml` to extract failing case IDs, and calls `eval-run --cases <failing-ids> --no-llm-judges`. Time it against the current manual workflow and see if sub-30-second feedback is achievable.

---

**2. Eval-in-the-Loop Skill Editor**

Instead of the current flow where you edit a skill, then separately run eval, then separately read results — collapse all three into a single agent session. An "edit mode" agent that has both the SKILL.md and the eval results loaded in context. When you describe a change ("make the skill always include acceptance criteria"), the agent: (1) proposes the SKILL.md edit, (2) predicts which judges will be affected based on the judge definitions in eval.yaml, (3) runs a targeted eval, (4) shows you a before/after score comparison, and (5) asks if you want to keep, revise, or revert — all without leaving the conversation. Basically `/eval-optimize` but interactive and human-in-the-loop at every edit, not just at the end.

**Why it works:** The current `/eval-optimize` skill already does steps 1-4 autonomously, but it's a black box. You set it loose and hope it doesn't overfit. The problem isn't automation — it's that humans lose control of the edit-verify cycle. An interactive version lets you steer each edit while the agent handles the mechanical work of running evals and comparing scores. It also captures your intent ("I want this to be more concise") as structured context that judges can use, rather than hoping the agent infers it from failure patterns.

**Risk:** Context window pressure. A SKILL.md + eval.yaml + summary.yaml + transcript snippets + conversation history could easily hit 100K+ tokens. The agent would need aggressive context management: summarize old iterations, drop transcript chunks after extracting the relevant insight, keep only the diff of the last edit rather than the full file.

**First step:** Build a proof-of-concept Claude Code slash command that loads the SKILL.md and latest summary.yaml into context, accepts a natural-language edit request, applies the edit, runs `/eval-run --cases <relevant> --no-llm-judges`, and shows a score delta table. Test with one skill that has at least 5 test cases.

---

**3. Adversarial Dataset Flywheel**

After every eval run, automatically mine the results for failure patterns and generate new test cases that stress those exact failure modes. If the `output_quality` judge fails because the skill produces vague acceptance criteria, generate 3 new test cases with inputs specifically designed to trigger vague outputs (ambiguous requirements, overly broad scope, conflicting constraints). Add them to the dataset, re-run, and repeat. The dataset grows organically based on what actually breaks, not what a human guesses might break. Over time, each skill develops a battle-hardened test suite that covers its real weaknesses.

**Why it works:** The current `/eval-dataset` generates test cases from skill analysis, which means it guesses at edge cases based on the SKILL.md text. But the real edge cases emerge from running the skill against real inputs and seeing where it stumbles. Failure-driven test generation is how fuzzing works in security — and it's wildly more effective than hand-written test suites. The eval harness already has the failure data (judge rationale, transcript evidence); it just doesn't feed that data back into test generation.

**Risk:** Runaway dataset growth. If every failure spawns 3 new cases and the skill has persistent weaknesses, you end up with 200 test cases that all probe the same flaw from slightly different angles. You'd need deduplication (semantic similarity between test case inputs) and a cap on cases-per-failure-pattern. Also, adversarial cases might drift into unrealistic territory — testing the skill on inputs no real user would ever provide.

**First step:** After the next `/eval-run` that produces failures, manually write 3 test cases inspired by the failure patterns in `summary.yaml`. Run the eval with the expanded dataset and measure whether the new cases catch the same failures more reliably. If yes, script the pattern: parse `summary.yaml` failures, generate case YAML using an LLM call with the failure rationale as context, write to the dataset directory.

---

**4. Eval Cost Budgets with Speculative Fast-Path**

Full eval runs are expensive. An Opus run across 20 test cases with LLM judges can cost $5-15 and take 30+ minutes. This kills iteration speed because people batch their changes and run eval infrequently. Instead, implement a two-tier eval system: a fast path that runs in under 60 seconds using only deterministic judges and a cheaper model (Sonnet), and a full path that runs on commit/PR with Opus and all judges. The fast path gives you a "probably fine" or "definitely broken" signal instantly. The full path gives you the real score. A speculative execution layer could even pre-run the fast path in the background while you're still editing, using the last-saved version of the SKILL.md.

**Why it works:** In the current harness, `--no-llm-judges` already exists but nobody uses it as a first-pass filter because the workflow doesn't encourage it. Most skill regressions are caught by deterministic `check` judges anyway (file exists, field present, format valid). By making the fast path the default and the full path the "publish gate," you shift the cost curve. Teams iterate 10x per day on the fast path and run the full suite once before merging. The speculative pre-run is cheap enough (Sonnet + deterministic judges) that it can run on every save without anyone caring about the cost.

**Risk:** The two tiers could diverge. A skill might pass all deterministic judges but fail LLM judges badly, and the developer only discovers this at merge time after a day of iterating in the wrong direction. You'd need a "confidence gap" metric that estimates how much information the fast path is missing, and surfaces a warning when the gap is large (e.g., "4 of 6 judges are LLM-only and weren't run").

**First step:** Run the current eval suite twice on the same skill: once with `--no-llm-judges` and once with all judges. Compare which failures each catches. If the deterministic judges catch 60%+ of the failures the LLM judges catch, the fast-path tier is viable. Measure wall-clock time and cost for both runs.

---

**5. Cross-Skill Regression Radar**

Skills don't exist in isolation. Many skills invoke sub-skills (`/eval-run` calls `/eval-analyze`, the notetaking skill calls the tag scanner). When you edit one skill, you might break a downstream consumer. Right now, there's no way to know this without manually running eval on every skill in the chain. Build a dependency graph (parsed from `Skill` tool invocations in each SKILL.md) and a "blast radius" calculator. When a SKILL.md is edited, the system identifies all skills that depend on it, runs their eval suites, and reports cross-skill regressions. Think of it as `npm audit` but for skill chains.

**Why it works:** The eval harness's `/eval-analyze` already traces sub-skill chains recursively (up to 5 levels). The dependency data exists — it's just not persisted or used for cross-skill impact analysis. In a project with 15+ skills, a single edit to a low-level utility skill (like the notetaking formatter) could silently break 5 upstream skills. The blast radius calculator turns an invisible failure mode into a visible, testable one. It also lets you prioritize which skills to eval first: the ones with the most dependents.

**Risk:** Combinatorial explosion. If skill A depends on B, C, D and each of those has 20 test cases, one edit to A triggers 60+ test case runs across 3 skills. With Opus and LLM judges, that's a $20-40 eval run for a one-line change. You'd need smart filtering: only run the dependent skills' cases that exercise the dependency path, not their entire suite. The dependency graph also needs to handle dynamic invocations (skill names constructed from variables) which the static SKILL.md parser would miss.

**First step:** Write a script that parses all SKILL.md files in the project, extracts `/skill-name` references and `Skill` tool invocations, and outputs a dependency graph as JSON. Visualize it. See if the graph reveals dependency chains longer than 2 levels — because those are where silent regressions hide.

---

Which one grabs you? I can explore any of these further, combine elements from multiple ideas, or go in a completely different direction.
