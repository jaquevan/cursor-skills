# Critique: AI-Powered Usability Test Reports from Jira ACs

Here's my read on this:

**The idea in two sentences:** You want to build an internal Red Hat tool where AI agents read STRAT ticket acceptance criteria, run Playwright walkthroughs against a live prototype, score 7 usability dimensions, and produce an HTML report — automating what currently takes researchers 2-3 hours of manual usability evaluation per prototype.

**What I researched:** I looked into academic research on AI-powered heuristic evaluation vs. human experts (INTERACT 2025, arXiv synthetic evaluation studies), the current landscape of Jira-to-test-case automation tools (AI Test Studio, VibeTester, QMetry, ContextQA), and Playwright's MCP capabilities for agent-driven browser automation. Key finding: LLMs can identify the *presence* of usability issues at 73-84% agreement, but severity scoring has near-zero inter-rater reliability (Krippendorff's Alpha ≈ 0), and only 21% of expert-identified issues were caught by GPT-4o in a controlled comparison.

**The critiques:**

## 1. Your scoring system is built on quicksand

The most dangerous part of this proposal is "score 7 usability dimensions." Recent research (Nizamani et al., 2024, applying GPT-4o's heuristic evaluation to 30 websites) found that while LLMs achieve 84% agreement on *whether* a usability issue exists, their severity judgments have exact agreement of just 56% and a Krippendorff's Alpha near zero — meaning the scores are essentially random when it comes to *how bad* something is. A separate INTERACT 2025 study found GPT-4o only identified 21.2% of issues that human experts found, and generated false positives from hallucinations. Scoring dimensions gives the appearance of rigor while the underlying signal may be noise.

**What if:** A report scores a prototype 4/5 on "learnability" and the team ships it. A real user study later reveals the onboarding flow is deeply confusing — but nobody ran one because the AI report said it was fine. The tool becomes a rubber stamp that erodes the quality bar.

**De-risk it:** Before building the full pipeline, run a blind validation study. Have researchers evaluate 5-10 prototypes manually, then run your AI scoring on the same prototypes. Measure correlation. If severity scores don't correlate at r > 0.7, the scoring feature isn't ready and you need a different output format (issue identification without scores, perhaps).

## 2. Acceptance criteria are the wrong input for usability evaluation

Acceptance criteria define *what the system should do* — they're functional specifications written for developers. Usability evaluation assesses *how users experience doing it*. ACs say "User can filter results by date range." A usability evaluation asks "Can a first-time user figure out that the date filter exists, understand its interaction model, and recover from errors?" These are fundamentally different questions. The tools that already exist in this space (VibeTester, QMetry, AI Test Studio) generate *functional test cases* from ACs, not usability evaluations — and that's not a coincidence.

**What if:** The agent faithfully walks through every AC and confirms each feature works, producing a clean report. But the real usability problems — confusing navigation hierarchy, inconsistent mental models between sections, cognitive overload from too many simultaneous options — are invisible because they live *between* the acceptance criteria, in the connective tissue of the experience.

**De-risk it:** Supplement ACs with explicit usability task scenarios written by a researcher (e.g., "As a new user seeing this screen for the first time, find and apply the date filter without any guidance"). These could be a lightweight addition to STRAT tickets — 3-5 task scenarios per prototype. The AI evaluates against tasks, not ACs.

## 3. Playwright walkthroughs can't simulate user confusion

Playwright (even via MCP with accessibility tree snapshots) navigates deterministically. It reads element roles, names, and refs — then clicks the right thing. But usability problems emerge precisely when users *don't* click the right thing. They look at a button and don't recognize it as a button. They scan past the filter because its visual weight doesn't match their expectation. They try a wrong path first. A Playwright agent operating on the accessibility tree will always find the correct interaction path because it has perfect structural knowledge of the page. It cannot simulate the bounded rationality, scanning patterns, or prior-experience biases that make usability testing valuable.

**What if:** The agent reports "all flows completable, average task completion: 100%" because it always finds elements by their accessible name. Meanwhile, real users completing the same tasks have a 40% failure rate because the visual hierarchy doesn't match the information architecture. The tool can't distinguish between "technically navigable" and "intuitively navigable."

**De-risk it:** Reframe what the Playwright agent does. Instead of simulating a user, use it as an *audit tool*: check for accessibility violations, measure interaction depth (how many clicks to complete a task), identify inconsistencies between similar patterns across screens, verify error states exist. These are things automation genuinely excels at. Pair this with a separate LLM-based visual evaluation pass using screenshots (which the arXiv synthetic evaluation research shows is more effective for layout and visual hierarchy issues).

## 4. You'll face a trust gap that technical quality can't close

Even if the tool produces technically competent reports, you're replacing the judgment of UX researchers — people whose professional identity is built on qualitative evaluation skill. Research from Wiley (Sagar & Saha, 2019) on automated vs. manual usability assessment found that "most usability problems were uncovered by end-users that were not detected by tool" and concluded tools fail to evaluate key features. If your researchers already know this literature, they'll be skeptical. If stakeholders start treating AI reports as equivalent to researcher reports, you've created a political problem: researchers feel devalued, and the organization loses the muscle memory of doing real user research.

**What if:** The tool works well enough that a PM says "we already have the usability report, we don't need to schedule a user study this sprint." One sprint becomes two. Real usability research atrophies. Six months later, a major redesign ships with fundamental UX problems because nobody talked to actual users — the AI said it was fine.

**De-risk it:** Position the tool explicitly as a *pre-screening layer*, not a replacement. The framing matters: "This catches the obvious stuff so researchers can focus their 2-3 hours on the hard, judgment-intensive problems" is very different from "This replaces the 2-3 hour evaluation." Get researcher buy-in on the framing before building. Let them define what the tool should and shouldn't claim.

## 5. The "running prototype" dependency is heavier than it looks

The pipeline assumes a prototype is deployed, stable, accessible via URL, and in a state worth evaluating. In practice, early prototypes are often: behind VPN or auth walls that need manual setup, partially broken (404s on secondary flows), using mock data that doesn't exercise real states, or changing daily. Every time the prototype breaks or updates, your Playwright agent hits errors that aren't usability findings — they're infrastructure noise. You'll spend significant effort on environment management, test stability, and distinguishing "prototype is broken" from "prototype has a usability problem."

**What if:** The team spends 3 weeks building the agent pipeline, then discovers that 60% of runs fail because prototypes aren't stable enough for automated traversal. The tool becomes a maintenance burden — someone has to triage every failed run to determine if it's a real finding or a flaky prototype.

**De-risk it:** Start with a constraint: only run against prototypes deployed to a stable staging environment with a health-check endpoint. Build a "readiness gate" that verifies the prototype is navigable before running the evaluation. Accept that this limits the tool to later-stage prototypes (which is fine — that's where the 2-3 hour evaluations happen anyway).

---

**Verdict: Rethink this part**

The core assumption — that AI agents can *score usability dimensions* reliably — isn't supported by the current research. The numbers are damning: near-zero reliability on severity, only 21% overlap with expert findings in controlled studies. But there's a strong tool hiding inside this idea. If you reframe it as an *automated accessibility and interaction audit* (not a usability evaluation), use researcher-written task scenarios (not ACs) as input, and position it as a pre-screening layer that surfaces obvious issues before researchers spend their time — you'd have something genuinely useful that researchers would actually adopt. The 2-3 hours doesn't go to zero, but the first 45 minutes of "checking the obvious stuff" could.

Want me to dig deeper on any of these, or stress-test a specific angle?
