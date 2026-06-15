---
name: slack-summary
description: >-
  Summarizes Slack conversations and presents insights in a Cursor Canvas. Use
  when the user says "summarize slack", "review my slack messages", "slack
  summary", "what have I been discussing on slack", "prep for my meeting using
  slack", "review conversation with <person>", or asks for a summary or review
  of Slack activity. Also use when the user asks to prepare for a 1:1 or
  meeting and mentions Slack as a source.
disable-model-invocation: true
---

# Slack Summary

Searches Slack conversations and presents structured insights in a Canvas for
meeting prep, weekly reviews, or conversation summaries.

## When to use

Trigger this skill when the user mentions **summary** or **review** in the
context of Slack messages, DMs, or meeting prep that draws on Slack history.

## Source of truth

Every claim, talking point, and thread summary in the output must trace
directly to a specific Slack message or a file the user explicitly points to
(e.g., meeting notes). The Slack search results are the primary source. If the
user also provides a document or file reference, that is a secondary source.

**Nothing else is a valid source.** Do not pull in information from your
training data, from other files in the workspace, from Google Drive searches,
or from prior conversation context — unless the user explicitly asks you to.
If a detail cannot be attributed to a retrieved Slack message or a
user-provided file, leave it out.

## Instructions

### 1. Identify the scope

From the user's prompt, determine:
- **Who:** a specific person, a channel, or all conversations
- **Time range:** "past week", "past 3 weeks", "since Monday", etc.
- **Purpose:** meeting prep, weekly review, catch-up summary
- **Additional sources:** any files or documents the user points to

### 2. Search Slack

Use the Slack MCP `search_messages` tool (or call it directly via the
slack-mcp server) with queries like:

- `from:<person>` for messages from a specific person
- `from:<user> to:<person>` for DM conversations
- `in:<channel>` for channel activity

Run multiple searches to capture both sides of a conversation. Request enough
messages to cover the time range (use `limit` parameter).

### 3. Read any user-provided files

If the user pointed to specific meeting notes, documents, or files, read them
now. These are the only non-Slack sources you may use.

### 4. Group messages into threads

Organize the retrieved Slack messages into **conversation threads** by topic.
For each thread:
- Assign a short theme name
- Note the date range (from the message timestamps)
- List the key points as **direct paraphrases** of the actual messages

**Accuracy rules for this step:**
- Every bullet point must correspond to one or more specific messages from
  the search results. If you cannot point to the message it came from, do
  not include it.
- Use the names, terms, and details exactly as they appear in the messages.
  Do not substitute synonyms, round numbers, or fill in gaps with assumptions.
- If a message is ambiguous, preserve the ambiguity — do not interpret it
  into a definitive statement.
- Do not merge details from different messages into a single bullet unless
  they are clearly about the same thing. When in doubt, keep them separate.

### 5. Generate talking points (meeting prep only)

If the summary is for meeting prep, derive talking points from the threads.
Each talking point must reference which thread or messages it comes from.

Priority levels:
- **High:** items the other person explicitly asked about or is waiting on
- **Medium:** topics discussed but without clear resolution
- **Low:** context items worth mentioning but not urgent

**For each talking point, the "detail" text must describe what was actually
said in Slack — not what you think the user should say or do.** Framing like
"you should bring up X" is fine for the point title, but the supporting
detail must be factual and traceable.

### 6. Present as a Canvas

Build a `.canvas.tsx` file following the Canvas skill guidelines. The canvas
should include:

- **Header:** meeting/summary title, time, participants
- **Stats row:** message count, time period, thread count
- **Talking points:** prioritized cards with detail text (meeting prep only)
- **Conversation threads:** cards grouped by topic with bullet points
- **Supporting docs:** table of user-provided files only (not Drive searches)
- **Source callout:** attribution line stating "Source: Slack messages" and
  the date range. If user-provided files were used, list them by name.

Follow the Canvas skill's design guidance — use `useHostTheme()` tokens for
all colors, no hardcoded hex, no gradients, no emojis. Mix card styles with
open sections for visual variety.

Save the canvas to the workspace canvases directory.

### 7. Summarize in chat

Alongside the canvas, provide a brief text summary in chat with:
- Top 3 talking points
- A link to the canvas for the full breakdown

## What NOT to do

- Do not search Google Drive on your own. Only include documents the user
  explicitly tells you to use.
- Do not add context from your training data about people, projects, or
  teams — even if you "know" something is true.
- Do not infer what happened between messages. If there is a gap, note it
  as an open question rather than filling it in.
- Do not editorialize or add recommendations beyond what the messages
  themselves suggest. The talking points should surface what was discussed,
  not prescribe what the user should think about it.
