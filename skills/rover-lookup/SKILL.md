---
name: rover-lookup
description: >-
  Looks up a Red Hat employee's title, location, and manager using the Dataverse
  MCP and the roverpeople data product. Use when the user says "who is",
  "look up", "what is their title", "who manages", "where is <person> located",
  "rover lookup", "find <person> in rover", or asks about someone's role,
  manager, or office location at Red Hat. Also use when the user asks
  "what team is <person> on" or "who does <person> report to".
disable-model-invocation: true
---

# Rover Lookup

Looks up a person's title, location, and manager at Red Hat using the Dataverse
MCP against the `roverpeople` data product.

## Instructions

1. **Extract the person identifier.** Pull the person's name, email, or kerberos
   ID from the user's prompt. If the user doesn't provide enough to identify
   someone, ask them for a name or email.

2. **Call `shortlist_tables`** on the Dataverse MCP with:
   - `data_product`: `"roverpeople"`
   - `user_query`: a query about looking up the person's info
   
   Expect the table `ROVER_PEOPLE_CURR` in schema `RHAI_MARTS`.

3. **Call `get_sql`** on the Dataverse MCP with:
   - `data_product`: `"roverpeople"`
   - `tables_list`: the shortlisted tables from step 2
   - `user_query`: a query requesting the person's name, display name, email,
     title, location, country, geo, hire date, cost center, work profile, and
     manager details. The manager fields come from a self-join on
     `MANAGER_UUID` — request manager name, email, and title.

4. **Call `execute_sql`** on the Dataverse MCP with:
   - `sql`: the SQL returned from step 3

5. **Present the results** using the output format below.

## Output format

For a single match, present a clean summary:

```
**Name:** Jane Doe
**Email:** jdoe@redhat.com
**Title:** Senior Software Engineer
**Location:** RH - Raleigh, USA
**Hire Date:** January 15, 2023
**Work Profile:** Office-Flex
**Manager:** John Smith (jsmith@redhat.com) — Manager, Engineering
```

For multiple matches, present each person in the same format separated by a
horizontal rule, and ask the user if they meant a specific one.

## Edge cases

- **Multiple results:** Present all matches and ask the user to clarify which
  person they meant.
- **No results:** Tell the user no match was found. Suggest checking the
  spelling, trying the full legal name, or using an email address instead.
- **Person has no manager listed:** Show "Manager: (none listed)" rather than
  omitting the field.

## Example triggers

1. "Who is Jane Doe?"
2. "Look up jdoe@redhat.com in Rover"
3. "What is John Smith's title and who does he report to?"
