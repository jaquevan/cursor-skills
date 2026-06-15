---
name: note-to-email
description: >-
  Reads a note and drafts a professional email based on its content. Adapts the
  email format to the note type — meeting follow-up, status update, research
  summary, request, or general share. Use whenever the user says "draft an email
  from this note", "write a follow-up email", "turn this note into an email",
  "email this to...", "send this to...", or references a note and asks for an
  email. Also use when the user pastes raw notes and asks to email them to
  someone, even if they don't explicitly mention this skill.
disable-model-invocation: true
---

# Note-to-Email

Reads a note and generates a professional, ready-to-send email draft. The email
format adapts to the content — a meeting note becomes a follow-up, a research
note becomes a findings summary, a status note becomes a progress update.

## Instructions

1. **Read the note.** The input may be a file path, an `@` reference, or pasted
   text. Read all of it before drafting.

2. **Identify the note type.** This determines the email's structure and tone:

   | Note type | Email format |
   |---|---|
   | Meeting notes | Follow-up: thank the recipient, recap key points, confirm next steps |
   | Research / analysis | Summary: lead with findings, highlight what matters to the recipient |
   | Status update | Progress report: what's done, what's blocked, what's next |
   | Request or ask | Request: state the ask clearly, provide context, include deadline |
   | General / other | Share: brief summary with the most relevant highlights |

3. **Extract key content.** Pull from the note:
   - Recipient name and email (if mentioned)
   - Key points or findings relevant to the recipient
   - Decisions that were made
   - Action items — especially ones owned by the sender or recipient
   - Open questions that need the recipient's input
   - Deadlines or time-sensitive details

4. **Read `Me.md`** at the workspace root to get the sender's name and role for
   the signature.

5. **Draft the email** using the output format below.

6. **Save the draft** to `notes/YYYY-MM-DD-email-draft-<slug>.md` using today's
   date and a short slug based on the recipient or topic.

## Tone and style

The email should sound like a competent professional who respects the
recipient's time. Think: the kind of email you'd actually want to receive.

- Professional but warm — not stiff, not overly casual
- Short paragraphs, ideally 2–3 sentences each
- Lead with the most important thing — don't bury the point
- Use bullet points for lists of items, action steps, or questions
- Only include facts present in the note — never fabricate details
- When something in the note is uncertain (a name, a number), use a bracketed
  placeholder like `[confirm exact headcount]` so the sender knows to verify
- Keep the body under 200 words when possible — brevity is respect
- No filler phrases ("I hope this email finds you well", "per our conversation")

## Output format

```markdown
# Email Draft — <subject line>

**To:** <recipient name and email if known, otherwise [recipient]>
**Subject:** <concise, specific subject line>

---

<greeting — "Hi <name>," or "Hi team,">

<opening — 1-2 sentences stating the purpose>

<body — key points, decisions, or findings as short paragraphs or bullets>

<action items or questions for the recipient, if any>

<closing — brief, forward-looking sentence>

---

Best,
<sender name from Me.md>
<sender role from Me.md>
```

### Formatting rules

- Title as H1 with the subject line
- `**To:**` and `**Subject:**` as bold metadata
- Horizontal rules to separate metadata, body, and signature
- Bullet points for lists of 3+ items
- Bracketed placeholders for anything uncertain: `[confirm date]`, `[TBD]`
- Omit sections that don't apply — not every email needs action items

## Example triggers

These prompts should activate this skill:

1. "Draft a follow-up email from my AlphaAlpha meeting notes"
2. "Turn this note into an email I can send to the team"
3. "Write an email based on these notes"
