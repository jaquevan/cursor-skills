---
name: tomorrow-calendar-accepted
description: >-
  Shows accepted calendar events for tomorrow using the Google Workspace CLI
  (gws). Queries all selected calendars, filters to accepted events only, and
  displays a clean schedule with time, title, location, and calendar source.
  Use when the user says "what's on my calendar tomorrow", "show tomorrow's
  schedule", "what meetings do I have tomorrow", "tomorrow's accepted events",
  or asks about their schedule for the next day.
disable-model-invocation: true
---

# Tomorrow's Calendar — Accepted Events Only

Shows a filtered view of tomorrow's calendar using the GWS CLI, including only
events the user has accepted.

## Instructions

1. **Determine tomorrow's date** in the user's timezone. Read `Me.md` for
   timezone if available (look for the timezone field), otherwise default to
   `America/New_York`.

2. **Get the list of calendars** by running:

   ```
   gws calendar calendarList list --params '{}' --format json
   ```

   Include calendars where `selected: true` or `accessRole: "owner"`. At
   minimum, always include the primary calendar.

3. **Query each calendar** for tomorrow's events. For each calendar, run:

   ```
   gws calendar events list --params '{
     "calendarId": "<calendar-id>",
     "timeMin": "<tomorrow-midnight-local-ISO>",
     "timeMax": "<day-after-midnight-local-ISO>",
     "singleEvents": true,
     "orderBy": "startTime",
     "timeZone": "<user-timezone>"
   }' --format json
   ```

   Redirect stderr to `/dev/null` to avoid the keyring backend line breaking
   JSON parsing.

4. **Filter to accepted events only.** For each event:
   - If there is an attendee entry with `"self": true`, include the event only
     if `"responseStatus": "accepted"`. Exclude declined, tentative, and
     needsAction.
   - If there is no `attendees` array (personal blocks, owned events), include
     it only if the user is the organizer (`organizer.self: true`) or the
     event is on the primary calendar with no explicit decline.

5. **Present the results** as a simple schedule sorted by start time:

   ```
   Tomorrow — <Day of Week>, <Month Day, Year> (<timezone>)

   TIME                  EVENT                              LOCATION              CALENDAR
   ─────────────────────────────────────────────────────────────────────────────────────────
   9:00 AM – 9:25 AM     Evan / Zack 1:1                    Google Meet           Primary
   11:00 AM – 12:00 PM   Agentic AI Demos                   RH - Raleigh 310      Primary
   ```

   If no accepted events exist for tomorrow, say:
   "No accepted events tomorrow (<day>, <date>). Your schedule is clear."

## Notes

- Always use `singleEvents: true` so recurring events expand into individual
  instances. Without this, recurring events return as a single entry with
  recurrence rules instead of concrete dates.
- Always redirect stderr when piping GWS output to a JSON parser — GWS prints
  `"Using keyring backend: keyring"` to stderr which corrupts the JSON stream.
- The `gws calendar +agenda` shortcut omits RSVP status, which is why this
  skill uses `events list` with manual filtering instead.
