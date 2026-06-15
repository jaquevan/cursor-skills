---
name: source-reader
description: >-
  Extracts text content from external sources — Google Docs, Google Slides,
  Slack channels/DMs, Jira issues via Dataverse, and Google Drive files. Use
  as the first step when the user references a URL, file ID, Slack channel,
  or Jira project key and wants to process the content (e.g., make notes,
  summarize, create slides). Also use when another skill needs to pull content
  from an external source before processing it.
disable-model-invocation: true
---

# Source Reader

Detects what kind of source the user referenced and extracts its text content
using the appropriate tool. This skill is a building block — other skills
(like notetaking or notes-to-slides) use it as step 0.

## Source detection

Match the user's input against these patterns to determine the source type:

| Pattern | Source type |
|---|---|
| `docs.google.com/document/d/<id>` | Google Doc |
| `docs.google.com/presentation/d/<id>` | Google Slides |
| `docs.google.com/spreadsheets/d/<id>` | Google Sheet |
| `drive.google.com/file/d/<id>` | Google Drive file |
| `#channel-name` or `in:channel-name` | Slack channel |
| `@person` or `from:person` in Slack context | Slack DMs |
| `PROJ-1234` (uppercase letters + dash + numbers) | Jira issue key |
| Project key alone (e.g., `<YOUR_STRATEGY_PROJECT>`) | Jira project |

If the input doesn't match any pattern, it's likely pasted text — pass it
through to the downstream skill directly.

## Extraction instructions

### Google Docs

Extract the document ID from the URL (the segment after `/d/` and before `/`).

```bash
gws docs documents get --params '{"documentId":"<id>"}' --format json 2>/dev/null
```

The response contains the document's structured content in `body.content`.
Walk through the `paragraph` elements and concatenate each `textRun.content`
value to build the full text. Preserve paragraph breaks.

### Google Slides

Extract the presentation ID from the URL.

```bash
gws slides presentations get --params '{"presentationId":"<id>"}' --format json 2>/dev/null
```

Walk through each slide in `slides[]`. For each slide, extract text from
`pageElements[].shape.text.textElements[].textRun.content`. Prefix each
slide's content with `--- Slide N ---` to preserve structure.

### Slack

Use the Slack MCP tools or call the slack-mcp server directly:

- **Channel history:** `get_channel_history` with the channel name and a
  message limit appropriate to the time range
- **Search:** `search_messages` with `from:<person>` or `in:<channel>`
- **DMs:** `search_messages` with `from:<person> to:<user>` and the reverse

Capture both sides of a conversation. Include timestamps and sender names.

### Jira via Dataverse

Use the Dataverse MCP 4-step pipeline:

1. `identify_dataproducts` — confirms `jira` data product
2. `shortlist_tables` with `data_product: "jira"`
3. `get_sql` with the shortlisted tables and a query for the issues
4. `execute_sql` with the generated SQL

For a single issue key, query for that issue's summary, description, status,
assignee, and comments. For a project key, query for recent or in-progress
issues with key, summary, status, and assignee.

### Google Drive (unknown type)

When the user provides a Drive link without a clear type:

```bash
gws drive files get --params '{"fileId":"<id>","fields":"id,name,mimeType"}' --format json 2>/dev/null
```

Check the `mimeType` field and delegate:
- `application/vnd.google-apps.document` -> Google Docs extraction
- `application/vnd.google-apps.presentation` -> Google Slides extraction
- `application/vnd.google-apps.spreadsheet` -> Google Sheets (use
  `gws sheets spreadsheets values get` to pull cell data)

## Output format

Return the extracted text to the calling context. Include a source metadata
block at the top:

```
Source: <type> — <name or URL>
Extracted: <timestamp>

<content>
```

The downstream skill decides how to structure and format the content.

## Accuracy rules

- Extract only what the source contains. Do not summarize, interpret, or
  add context during extraction.
- Preserve the original structure (paragraphs, slide boundaries, message
  order) so the downstream skill can make informed formatting decisions.
- If extraction fails (auth error, file not found, API error), report the
  error clearly and suggest what the user can try (check the URL, verify
  access, re-authenticate).
