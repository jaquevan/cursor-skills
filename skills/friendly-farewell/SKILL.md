---
name: friendly-farewell
description: >-
  Says a Sound of Music-style farewell to one or more people by name. Use when
  the user says "say goodbye", "farewell", "send off", or triggers the
  friendly-farewell skill.
disable-model-invocation: true
---

# Friendly Farewell

When this skill is triggered, say goodbye with:

**"So long, farewell, auf Wiedersehen, adieu to <name> and <name> and <name>"**

Replace each `<name>` with the actual names provided. Adapt the number of names
to match however many the user gives:

- **One name:** "So long, farewell, auf Wiedersehen, adieu to Alice"
- **Two names:** "So long, farewell, auf Wiedersehen, adieu to Alice and Bob"
- **Three or more:** "So long, farewell, auf Wiedersehen, adieu to Alice and Bob and Carol"

If no names are provided, read the `Me.md` file at the workspace root and use
the name found there. If `Me.md` does not exist or no name is found, ask the
user who they want to say goodbye to.
