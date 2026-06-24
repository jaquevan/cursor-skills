---
name: budget-tracker
description: >
  Manages a personal budget via a Google Sheets tracker. Logs spending, records
  income and fixed expenses, shows a budget dashboard, processes paychecks,
  handles month rollover, tracks investments, imports bank statements (PDF,
  CSV, or pasted text) with auto-categorization and deduplication, and can
  modify the spreadsheet itself (fix formulas, add annual totals, conditional
  formatting, sparklines, subscriptions, expand tracker). Use when the user
  says "log spending", "budget check", "paycheck came in", "how much have I
  spent", "record expense", "budget dashboard", "month rollover", "investment
  update", "import statement", "process my bank statement", "how's my budget",
  "paid rent", "spent money on", "add expense", "budget status", "fix my
  spreadsheet", "improve the tracker", "set up annual totals", "add
  subscriptions", "set planned budget", "add progress bars", "apply theme",
  "style the spreadsheet", or "make it look good".
---

# Budget Tracker

Conversational budget assistant backed by a Google Sheet. Reads via the
`sheets_read` MCP tool, writes via `scripts/budget_tracker.py`.

## Prerequisites

- Google Workspace MCP (`<YOUR_GOOGLE_MCP_SERVER>`) connected
- On first write, the script triggers an OAuth flow for the `spreadsheets` scope
  using the existing `client_secret.json` at `~/.config/g-workspace-mcp/`

## Spreadsheet Reference

**Sheet ID:** `1bov7q2pvyg2l-T4IMtBZB3qRlFFzjUj7YoheI0tmmb0`

**Tab naming:** `<Month> <Year>` (e.g., "June 2026"). Always use the current
month's tab unless the user specifies otherwise.

### Cell map

| Section | Range | Details |
|---|---|---|
| Income headers | A1:D2 | Row 1 = section title, Row 2 = column headers |
| Income data | A3:D6 | Paycheck (row 3), Grandma (row 4), empty rows 5-6 |
| Fixed expense headers | A7:C8 | Row 7 = section title, Row 8 = column headers |
| Fixed expense data | A9:C12 | Rent=9, Utilities=10, Student Debt=11, 401k=12 |
| Variable expense headers | E1:J2 | Row 1 = section title, Row 2 = column headers |
| Variable expense data | E3:J7 | Gas=3, Eating Out=4, Buying Stuff=5, Groceries=6, TOTAL=7 |
| Spending tracker label | F9 | "Spending Tracking (Update when you spend money)" |
| Spending tracker headers | F10:I10 | Gas / Eating out / Buying Stuff / Groceries |
| Spending tracker grid | F11:I37 | Daily entries (rows 11-37) |
| Big Picture label | B13 | "BIG PICTURE STATUS" |
| Big Picture headers | B14:D14 | Income / Expense / SAVINGS |
| Big Picture Planned | B15:D15 | Planned row |
| Big Picture Actual | B16:D16 | Actual row |
| Notes | A21:A48 | Free-text notes area |

### Column mapping for spending tracker

| Category | Column |
|---|---|
| Gas | F |
| Eating Out | G |
| Buying Stuff | H |
| Groceries | I |

### Income rows (Actual = column C)

| Source | Row |
|---|---|
| Paycheck | 3 |
| Grandma | 4 |
| (spare) | 5, 6 |

### Fixed expense rows (Actual = column C)

| Expense | Row |
|---|---|
| Rent | 9 |
| Utilities | 10 |
| Student Debt | 11 |
| 401k | 12 |

### Key financial constants

- Bi-weekly paycheck: **$1,889** (2 per month, $3,778 total)
- 401k contribution: **7%** of gross ($264.46 planned per month)
- Rent: **$950**/month
- Student Debt: **$100**/month

---

## Capabilities

### 1. Log Spending

**Trigger:** "spent $X on Y", "log spending", "add expense", "$15 at Chipotle"

**Workflow:**
1. Determine category from context (Gas, Eating Out, Buying Stuff, Groceries)
2. If ambiguous, ask: "Which category: Gas, Eating Out, Buying Stuff, or Groceries?"
3. Run the script to find the next empty row in the spending tracker and write:
   ```bash
   python3 <SKILL_DIR>/scripts/budget_tracker.py log \
     --category "Eating Out" --amount 15.50
   ```
4. Read back the updated variable expense summary via MCP `sheets_read` and
   confirm: "Logged $15.50 under Eating Out. You've spent $27.50 of $300 (91% remaining)."

### 2. Record Income

**Trigger:** "paycheck came in", "got paid", "grandma sent money", "received $X"

**Workflow:**
1. Identify the income source (Paycheck, Grandma, or a new source)
2. Run:
   ```bash
   python3 <SKILL_DIR>/scripts/budget_tracker.py income \
     --source Paycheck --amount 1889
   ```
3. The script adds the amount to the existing Actual value (column C) for that
   income row, so two paychecks accumulate correctly.
4. Confirm: "Recorded $1,889 paycheck. Total income this month: $1,889 of $3,778 planned."

### 3. Record Fixed Expenses

**Trigger:** "paid rent", "paid student loans", "utilities paid"

**Workflow:**
1. Map to the correct row (Rent=9, Utilities=10, Student Debt=11, 401k=12)
2. Run:
   ```bash
   python3 <SKILL_DIR>/scripts/budget_tracker.py fixed \
     --expense Rent --amount 950
   ```
3. Confirm with the updated Big Picture status.

### 4. Budget Dashboard

**Trigger:** "budget check", "how's my budget", "budget status", "budget dashboard"

**Workflow:**
1. Read the current month's tab via MCP:
   ```
   sheets_read(spreadsheet_id="1bov7q2pvyg2l-T4IMtBZB3qRlFFzjUj7YoheI0tmmb0",
               range_notation="'June 2026'!A1:J16")
   ```
2. Present a summary:
   - Income: Planned vs Actual
   - Fixed expenses: what's paid, what's outstanding
   - Variable spending: per-category burn rate vs month progress
   - Big Picture: total savings on track or off track
3. **Spending alerts:** If any category's Budget Left % < Month Left %, flag it:
   "Eating Out is at 60% budget with 70% of the month left. You're ahead of pace."

### 5. Paycheck Processing

**Trigger:** "paycheck came in, help me allocate", "got paid, what should I do"

**Workflow:**
1. Record the paycheck income (capability 2)
2. Read current fixed expense actuals
3. Suggest allocation based on what's unpaid:
   - "Rent ($950) is unpaid this month. Set aside?"
   - "Student debt ($100) is due. Pay now?"
   - "401k contribution ($132.23) will be deducted automatically."
4. Show remaining disposable income after fixed expenses

### 6. Month Rollover

**Trigger:** "new month", "month rollover", "start July budget"

**Workflow:**
1. Run:
   ```bash
   python3 <SKILL_DIR>/scripts/budget_tracker.py new-month \
     --month July --year 2026
   ```
2. The script duplicates the current tab, renames it to the new month, and
   clears all Actual values while preserving Planned amounts and formulas.
3. Confirm: "Created 'July 2026' tab. All planned amounts carried over, actuals reset to zero."

### 7. Investment Tracking

**Trigger:** "401k update", "investment update", "contributed to 401k"

**Workflow:**
1. Record the 401k contribution as a fixed expense (row 12)
2. If the user mentions other investments, add a note to the Notes section
3. Show the running total of 401k contributions for the month

### 8. Savings Goal Tracking

**Trigger:** "am I saving enough", "savings check", "will I hit my savings goal"

**Workflow:**
1. Read Big Picture Planned vs Actual savings
2. Calculate projected end-of-month savings based on current pace
3. Report: "Planned savings: $2,064. Current actual: $1,760. At this pace,
   you'll end the month at approximately $X."

### 9. Bank Statement Import

**Trigger:** "import statement", "process my bank statement", "here's my statement",
user drops a PDF/CSV file, user pastes transaction text

**Workflow:**

**Step 1: Parse.** Determine the input format:
- **PDF:** Claude reads the document natively and extracts the transaction table
  into `{date, description, amount, type}` entries
- **CSV:** Pass to the script's parser:
  ```bash
  python3 <SKILL_DIR>/scripts/budget_tracker.py parse-csv \
    --file /path/to/statement.csv
  ```
- **Pasted text:** Claude parses the transactions directly from the message

**Step 2: Auto-categorize.** Map each transaction by merchant description:

| Category | Keyword patterns |
|---|---|
| Gas | Shell, Exxon, BP, Wawa, Chevron, Sunoco, gas, fuel, petrol |
| Eating Out | restaurant, cafe, coffee, Chipotle, McDonald, Starbucks, DoorDash, UberEats, Grubhub, pizza, burger, diner |
| Groceries | Walmart Grocery, Kroger, Aldi, Trader Joe, Publix, grocery, Whole Foods, Food Lion, Harris Teeter |
| Buying Stuff | Amazon, Target, Walmart (non-grocery), Best Buy, retail, shop |
| Rent | rent, property management, apartment, lease |
| Utilities | electric, water, internet, phone, Comcast, Verizon, AT&T, Duke Energy, utility |
| Student Debt | Nelnet, FedLoan, Great Lakes, Navient, student loan, MOHELA |
| Income | payroll, direct deposit, salary, Zelle (incoming), Venmo (incoming) |
| Skip | fee, transfer, ATM withdrawal, interest charge |
| Unknown | anything that doesn't match (flagged for user review) |

**Step 3: Deduplicate.** Read the current spending tracker via MCP. A transaction
is a duplicate if the same amount exists in the same category column in the
current month. Present duplicates separately for confirmation.

**Step 4: User review.** Present a table of categorized transactions. The user
can approve all, re-categorize items, skip items, or adjust amounts.

**Step 5: Batch write.** Run:
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py import \
  --transactions-file /tmp/budget_transactions.json
```

The JSON file contains the approved transactions:
```json
[
  {"category": "Eating Out", "amount": 12.30, "description": "CHIPOTLE"},
  {"category": "Gas", "amount": 42.50, "description": "SHELL"},
  {"category": "income", "source": "Paycheck", "amount": 1889},
  {"category": "fixed", "expense": "Rent", "amount": 950}
]
```

**Step 6: Reconcile.** Read the sheet back and show updated Big Picture Status.
Flag any discrepancies between expected and actual totals.

**Safety rules for statement import:**
- Always present transactions for user approval before writing
- When unsure if something is a duplicate, ask rather than skip
- Only append to empty rows; never overwrite existing data
- Add an audit note: "Imported N transactions from [filename] on [date]"

### 10. Notes Logger

**Trigger:** "add a budget note", "note that...", context within other operations

**Workflow:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py note \
  --text "Unexpected car repair $200 - paid from savings"
```

### 11. Spreadsheet Setup / Improve

**Trigger:** "fix my spreadsheet", "improve the tracker", "set up annual totals",
"add subscriptions", "fix formulas", "expand tracker", "set planned budget",
"add progress bars", "apply formatting", "apply theme", "style the spreadsheet",
"make it look good", "fix the styling", "theme all tabs"

This capability modifies the spreadsheet structure itself. Always confirm with
the user before running structural changes.

**11a. Fix formula bugs:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py fix-formulas
```
Fixes known issues: Gas/Groceries SUM ranges, Planned expense calculation.
Also updates all variable expense SUM formulas to use open-ended ranges.

**11b. Create annual totals tab:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py create-annual --year 2026
```
Creates an "Annual Totals 2026" tab with:
- Monthly summary table pulling from each month via INDIRECT formulas
- 11 tracked rows: Income, Rent, Utilities, Student Debt, 401k, Gas, Eating Out,
  Buying Stuff, Groceries, Total Expenses, Savings
- Year Total and Monthly Average columns
- YTD insights: total earned/spent/saved, savings rate, 401k YTD,
  highest/lowest spending month
- Category breakdown: each variable category as % of total variable spending

**11c. Apply conditional formatting:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py apply-formatting
```
Adds color rules:
- Budget Left % column: green (on track), yellow (close), red (over budget)
- Income Difference column: green (positive), red (negative)
- Savings cell: green (meeting goal), red (below goal)

**11d. Add sparkline progress bars:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py add-sparklines
```
Adds inline bar charts in column K showing burn rate for each variable category.

**11e. Add subscriptions section:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py add-subscriptions \
  --items '{"Spotify": 10.99, "Netflix": 15.49, "iCloud": 2.99}'
```
Creates a subscriptions tracker starting at E14 with monthly cost, annual cost,
and totals.

**11f. Expand spending tracker:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py expand-tracker
```
Updates SUM formulas to open-ended ranges (F11:F instead of F11:F37) so the
tracker supports unlimited entries.

**11g. Set planned budget:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py set-planned \
  --category Gas --amount 150
```
Sets the planned budget for a variable expense category. Use when Gas or Buying
Stuff show #DIV/0! because they have no planned amount.

**11h. Apply design theme (monthly tab):**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py apply-theme
```
Applies the full design system: dark navy section headers with white text,
light blue-gray column headers, alternating row stripes on the spending tracker,
currency/percentage number formatting, column widths, frozen header row, cream
notes section, and accounting-style borders on total rows.

**11i. Apply design theme (annual tab):**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py apply-theme-annual --year 2026
```
Styles the Annual Totals tab with matching dark header, alternating stripes,
currency formatting, percentage formatting on breakdown/savings rate, and frozen
row + column.

**11j. Apply theme to all tabs:**
```bash
python3 <SKILL_DIR>/scripts/budget_tracker.py apply-theme-all
```
Applies the theme to both the current monthly tab and the annual tab in one
command. Month rollover duplicates formatting, so new months inherit the theme
automatically.

**Recommended setup flow for new users:**
1. Fix formulas (11a)
2. Expand tracker (11f)
3. Set planned budgets for Gas and Buying Stuff (11g)
4. Apply conditional formatting (11c)
5. Add sparklines (11d)
6. Create annual totals (11b)
7. Add subscriptions if applicable (11e)
8. Apply theme to all tabs (11j)

---

## Reading the Sheet (MCP)

For all read operations, use the MCP tool:

```
Tool: sheets_read
Server: <YOUR_GOOGLE_MCP_SERVER>
Arguments:
  spreadsheet_id: "1bov7q2pvyg2l-T4IMtBZB3qRlFFzjUj7YoheI0tmmb0"
  range_notation: "'<Month> <Year>'!<range>"
```

Use the current month name. To determine the current month tab name, use
today's date to build `"<Month> <Year>"` format.

## Writing to the Sheet (Script)

All writes go through `scripts/budget_tracker.py`. The script handles auth,
cell targeting, and append-only safety. Never construct raw Sheets API calls
in the conversation; always use the script.

## Error Handling

| Error | Response |
|---|---|
| Sheet not found | "Can't find the '<Month> <Year>' tab. Want me to create it with month rollover?" |
| Auth token expired | "Auth expired. Run `python3 budget_tracker.py --setup` to re-authenticate." |
| Spending tracker full | "Run `expand-tracker` to switch to open-ended ranges, or run it now?" |
| Category not recognized | Ask the user to pick from: Gas, Eating Out, Buying Stuff, Groceries |
| Statement parse failure | "Couldn't parse that statement format. Can you export it as CSV from your bank's website?" |
| #DIV/0! in Budget Left | "Gas/Buying Stuff has no planned budget. Want me to set one?" Then use `set-planned`. |
| Annual tab exists | "Annual Totals tab for that year already exists. Want to view it instead?" |

## What NOT to Do

- Don't modify Planned values unless the user explicitly asks
- Don't overwrite existing Actual values; add to them (income accumulates)
- Don't write to the sheet without confirming the operation with the user first
  (except for simple single-entry logging where the user clearly stated what to log)
- Don't run structural changes (fix-formulas, expand-tracker, create-annual, etc.)
  without confirming with the user first
- Don't access any financial accounts or banking APIs; only work with data the user provides
- Don't store or log sensitive financial data outside the Google Sheet
