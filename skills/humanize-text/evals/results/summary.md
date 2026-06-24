# Eval Summary — humanize-text

**Date:** 2026-06-16
**Evals run:** 3
**Total assertions:** 17

| Eval | With Skill | Without Skill |
|------|-----------|---------------|
| 1 (Humanize AI text) | **7/7** | 5/7 |
| 2 (Reply to manager) | **5/5** | 4/5 |
| 3 (Rewrite formal interest) | **5/5** | 3/5 |
| **Total** | **17/17 (100%)** | **12/17 (71%)** |

---

## Passed in both (skill not adding value)

| Eval | Assertion |
|---|---|
| 1 | No buzzwords (delve, leverage, robust, etc.) |
| 1 | No "I wanted to reach out" or "It's important to note" |
| 1 | Preserves core meaning (eval framework, Playwright, Jira ACs, HTML report) |
| 1 | Ends with Changed: summary |
| 1 | Shorter than input |
| 2 | Addresses both questions (evaluator progress AND consistency checker) |
| 2 | Sounds like a casual Slack reply |
| 2 | No formal opener |
| 2 | Appropriately short |
| 3 | Zero em dashes or en dashes |
| 3 | No buzzwords (would like to express, extensive experience, etc.) |
| 3 | Preserves intent of wanting to join working group |

## Passed only with skill (skill adding value)

| Eval | Assertion |
|---|---|
| 1 | Zero em dashes or en dashes — baseline used "Hey —" with an em dash |
| 1 | Casual voice (im/bc/rn/lmk) — baseline was conversational but not Evan-casual, no abbreviations |
| 2 | Zero em dashes or en dashes — baseline used "—" twice |
| 3 | Humble and curious tone — baseline was confident/self-promotional ("solid technical side", "bring a lot to the table") |
| 3 | Intern tone — baseline sounded like a mid-career professional, not an enthusiastic intern asking questions |

## Failed in both (gap or bad assertion)

| Eval | Assertion | Recommendation |
|---|---|---|
| — | — | No assertions failed in both configurations |

---

## Analysis

The skill scored **100% (17/17)** vs the baseline's **71% (12/17)**. The skill adds clear value in three areas:

1. **Dash elimination** — The model's default writing style naturally reaches for em dashes. Without the skill's explicit "NEVER use dashes" rule, the baseline used em dashes in 2 of 3 evals. The skill caught all of them.

2. **Evan-specific casual register** — The baseline can write "casually" but it lands on generic professional-casual (proper grammar, full words). The skill hits Evan's actual register: "lmk", "rn", "im", "atm", "havent", dropped capitalization. This is the hardest thing to replicate without the voice profile.

3. **Intern persona vs professional persona** — The baseline writes like a competent mid-career professional. The skill writes like a curious intern who asks questions and expresses genuine uncertainty ("not sure how the wg works but am I able to just express interest?"). The voice profile examples make this possible.

No assertions failed in both configurations, which means the eval suite is well-calibrated — every assertion is achievable, and the skill makes the difference on the ones that matter.
