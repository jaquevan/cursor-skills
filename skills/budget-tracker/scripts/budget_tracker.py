#!/usr/bin/env python3
"""Budget tracker for Google Sheets integration.

Usage:
    python3 budget_tracker.py log --category "Eating Out" --amount 15.50
    python3 budget_tracker.py income --source Paycheck --amount 1889
    python3 budget_tracker.py fixed --expense Rent --amount 950
    python3 budget_tracker.py dashboard
    python3 budget_tracker.py note --text "Car repair $200"
    python3 budget_tracker.py new-month --month July --year 2026
    python3 budget_tracker.py parse-csv --file statement.csv
    python3 budget_tracker.py import --transactions-file /tmp/txns.json
    python3 budget_tracker.py fix-formulas
    python3 budget_tracker.py create-annual --year 2026
    python3 budget_tracker.py apply-formatting
    python3 budget_tracker.py add-sparklines
    python3 budget_tracker.py add-subscriptions --items '{"Spotify":10.99,"Netflix":15.49}'
    python3 budget_tracker.py expand-tracker
    python3 budget_tracker.py set-planned --category Gas --amount 150
    python3 budget_tracker.py apply-theme
    python3 budget_tracker.py apply-theme-annual --year 2026
    python3 budget_tracker.py apply-theme-all
    python3 budget_tracker.py --setup
"""

import argparse
import csv
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = Path.home() / ".config" / "g-workspace-mcp" / "sheets_write_token.json"
CLIENT_SECRET = Path.home() / ".config" / "g-workspace-mcp" / "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1bov7q2pvyg2l-T4IMtBZB3qRlFFzjUj7YoheI0tmmb0"

CATEGORY_COLUMNS = {
    "Gas": "F",
    "Eating Out": "G",
    "Buying Stuff": "H",
    "Groceries": "I",
}

SPENDING_TRACKER_START_ROW = 11
SPENDING_TRACKER_END_ROW = 37

INCOME_ROWS = {
    "Paycheck": 3,
    "Grandma": 4,
}
INCOME_ACTUAL_COL = "C"

FIXED_EXPENSE_ROWS = {
    "Rent": 9,
    "Utilities": 10,
    "Student Debt": 11,
    "401k": 12,
}
FIXED_EXPENSE_ACTUAL_COL = "C"

NOTES_START_ROW = 21
NOTES_END_ROW = 48

CATEGORIZATION_RULES = {
    "Gas": [
        "shell", "exxon", "bp", "wawa", "chevron", "sunoco", "gas",
        "fuel", "petrol", "marathon", "speedway", "circle k", "racetrac",
        "quiktrip", "sheetz", "pilot", "murphy",
    ],
    "Eating Out": [
        "restaurant", "cafe", "coffee", "chipotle", "mcdonald", "starbucks",
        "doordash", "ubereats", "grubhub", "pizza", "burger", "diner",
        "wendy", "taco bell", "chick-fil-a", "panera", "subway", "dunkin",
        "panda express", "popeye", "sonic", "applebee", "chili",
        "ihop", "waffle house", "domino", "papa john",
    ],
    "Groceries": [
        "walmart grocery", "kroger", "aldi", "trader joe", "publix",
        "grocery", "whole foods", "food lion", "harris teeter", "safeway",
        "wegmans", "costco", "sam's club", "piggly wiggly", "h-e-b",
        "sprouts", "market basket", "stop & shop", "giant",
    ],
    "Buying Stuff": [
        "amazon", "target", "best buy", "retail", "shop", "ebay",
        "etsy", "walmart", "home depot", "lowe", "ikea", "apple.com",
        "gamestop", "barnes", "nike", "adidas",
    ],
    "Rent": ["rent", "property management", "apartment", "lease"],
    "Utilities": [
        "electric", "water", "internet", "phone", "comcast", "verizon",
        "at&t", "duke energy", "utility", "spectrum", "t-mobile", "xfinity",
    ],
    "Student Debt": [
        "nelnet", "fedloan", "great lakes", "navient", "student loan", "mohela",
    ],
    "Income": [
        "payroll", "direct deposit", "salary", "wage",
    ],
    "Skip": [
        "fee", "interest charge", "atm withdrawal", "overdraft",
        "transfer from", "transfer to",
    ],
}


# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_str):
    """Convert '#RRGGBB' to Google Sheets API RGB dict (0-1 floats)."""
    h = hex_str.lstrip("#")
    return {
        "red": int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue": int(h[4:6], 16) / 255,
    }


THEME = {
    "colors": {
        "header_bg":      _hex_to_rgb("#1B2A4A"),
        "header_fg":      _hex_to_rgb("#FFFFFF"),
        "col_header_bg":  _hex_to_rgb("#E8EDF3"),
        "col_header_fg":  _hex_to_rgb("#1B2A4A"),
        "row_alt":        _hex_to_rgb("#F7F9FC"),
        "row_default":    _hex_to_rgb("#FFFFFF"),
        "total_bg":       _hex_to_rgb("#D6E4F0"),
        "positive":       _hex_to_rgb("#27AE60"),
        "negative":       _hex_to_rgb("#E74C3C"),
        "warning":        _hex_to_rgb("#F39C12"),
        "notes_bg":       _hex_to_rgb("#FFFDE7"),
    },
    "fonts": {
        "section_header": {"fontFamily": "Arial", "fontSize": 12, "bold": True},
        "col_header":     {"fontFamily": "Arial", "fontSize": 10, "bold": True},
        "data":           {"fontFamily": "Arial", "fontSize": 10, "bold": False},
        "total":          {"fontFamily": "Arial", "fontSize": 10, "bold": True},
        "notes":          {"fontFamily": "Arial", "fontSize": 9,  "bold": False},
    },
    "formats": {
        "currency":         "$#,##0.00",
        "currency_no_cents": "$#,##0",
        "percent":          "0%",
        "percent_decimal":  "0.0%",
    },
    "col_widths_monthly": {
        0: 140,   # A - labels
        1: 90,    # B - planned
        2: 90,    # C - actual
        3: 90,    # D - difference
        4: 120,   # E - variable labels
        5: 85,    # F - planned / gas
        6: 85,    # G - actual / eating out
        7: 85,    # H - remaining / buying stuff
        8: 85,    # I - budget left / groceries
        9: 70,    # J - month left
        10: 100,  # K - sparkline
    },
    "col_widths_annual": {
        0: 160,   # A - row labels
    },
}


def get_credentials(force_setup=False):
    creds = None
    if TOKEN_FILE.exists() and not force_setup:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())
        return creds
    if creds and creds.valid:
        return creds
    if not CLIENT_SECRET.exists():
        print(f"ERROR: No client_secret.json at {CLIENT_SECRET}")
        print("Copy your Google Cloud OAuth client secret there first.")
        sys.exit(1)
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())
    print("Authentication successful.")
    return creds


def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def current_tab_name():
    now = datetime.now()
    return f"{now.strftime('%B')} {now.year}"


def _read_range(service, range_notation):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_notation,
        valueRenderOption="FORMATTED_VALUE",
    ).execute()
    return result.get("values", [])


def _write_range(service, range_notation, values):
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_notation,
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()


def _append_to_range(service, range_notation, values):
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=range_notation,
        valueInputOption="USER_ENTERED",
        insertDataOption="OVERWRITE",
        body={"values": values},
    ).execute()


# ---------------------------------------------------------------------------
# Capability 1: Log spending
# ---------------------------------------------------------------------------

def log_expense(category, amount, tab=None):
    if category not in CATEGORY_COLUMNS:
        print(f"ERROR: Unknown category '{category}'. "
              f"Valid: {', '.join(CATEGORY_COLUMNS.keys())}")
        return False

    tab = tab or current_tab_name()
    col = CATEGORY_COLUMNS[category]
    service = get_sheets_service()

    col_range = f"'{tab}'!{col}{SPENDING_TRACKER_START_ROW}:{col}{SPENDING_TRACKER_END_ROW}"
    existing = _read_range(service, col_range)

    next_row = SPENDING_TRACKER_START_ROW + len(existing)
    if next_row > SPENDING_TRACKER_END_ROW:
        print(f"ERROR: Spending tracker column {col} ({category}) is full "
              f"(max row {SPENDING_TRACKER_END_ROW}).")
        return False

    cell = f"'{tab}'!{col}{next_row}"
    _write_range(service, cell, [[amount]])

    summary_cell = f"'{tab}'!G{CATEGORY_COLUMNS_TO_SUMMARY_ROW(category)}"
    print(f"OK: Logged ${amount:.2f} under {category} at {col}{next_row}")
    return True


def CATEGORY_COLUMNS_TO_SUMMARY_ROW(category):
    mapping = {"Gas": 3, "Eating Out": 4, "Buying Stuff": 5, "Groceries": 6}
    return mapping.get(category, 3)


# ---------------------------------------------------------------------------
# Capability 2: Record income
# ---------------------------------------------------------------------------

def record_income(source, amount, tab=None):
    tab = tab or current_tab_name()
    service = get_sheets_service()

    if source in INCOME_ROWS:
        row = INCOME_ROWS[source]
    else:
        empty_rows = [r for r in [5, 6] if r not in INCOME_ROWS.values()]
        if not empty_rows:
            print(f"ERROR: No empty income rows. Cannot add source '{source}'.")
            return False
        row = empty_rows[0]
        label_cell = f"'{tab}'!A{row}"
        _write_range(service, label_cell, [[source]])
        print(f"Added new income source '{source}' at row {row}")

    actual_cell = f"'{tab}'!{INCOME_ACTUAL_COL}{row}"
    existing = _read_range(service, actual_cell)

    current = 0.0
    if existing and existing[0] and existing[0][0]:
        try:
            current = float(str(existing[0][0]).replace("$", "").replace(",", ""))
        except ValueError:
            current = 0.0

    new_total = current + amount
    _write_range(service, actual_cell, [[new_total]])
    print(f"OK: Recorded ${amount:.2f} for {source}. "
          f"Total actual: ${new_total:.2f}")
    return True


# ---------------------------------------------------------------------------
# Capability 3: Record fixed expenses
# ---------------------------------------------------------------------------

def record_fixed_expense(expense, amount, tab=None):
    tab = tab or current_tab_name()
    service = get_sheets_service()

    if expense not in FIXED_EXPENSE_ROWS:
        print(f"ERROR: Unknown fixed expense '{expense}'. "
              f"Valid: {', '.join(FIXED_EXPENSE_ROWS.keys())}")
        return False

    row = FIXED_EXPENSE_ROWS[expense]
    actual_cell = f"'{tab}'!{FIXED_EXPENSE_ACTUAL_COL}{row}"
    _write_range(service, actual_cell, [[amount]])
    print(f"OK: Recorded ${amount:.2f} for {expense} at C{row}")
    return True


# ---------------------------------------------------------------------------
# Capability 4: Dashboard
# ---------------------------------------------------------------------------

def read_dashboard(tab=None):
    tab = tab or current_tab_name()
    service = get_sheets_service()

    income_data = _read_range(service, f"'{tab}'!A2:D6")
    fixed_data = _read_range(service, f"'{tab}'!A8:C12")
    variable_data = _read_range(service, f"'{tab}'!E2:J7")
    big_picture = _read_range(service, f"'{tab}'!B13:D16")

    report = {"tab": tab, "income": [], "fixed_expenses": [], "variable_expenses": [], "big_picture": {}}

    for row in income_data[1:]:
        if len(row) >= 3 and row[0]:
            report["income"].append({
                "source": row[0],
                "planned": row[1] if len(row) > 1 else "",
                "actual": row[2] if len(row) > 2 else "",
                "difference": row[3] if len(row) > 3 else "",
            })

    for row in fixed_data[1:]:
        if len(row) >= 1 and row[0]:
            report["fixed_expenses"].append({
                "expense": row[0],
                "planned": row[1] if len(row) > 1 else "",
                "actual": row[2] if len(row) > 2 else "",
            })

    for row in variable_data[1:]:
        if len(row) >= 1 and row[0] and row[0] != "TOTAL":
            entry = {"category": row[0], "planned": row[1] if len(row) > 1 else ""}
            entry["actual"] = row[2] if len(row) > 2 else ""
            entry["remaining"] = row[3] if len(row) > 3 else ""
            entry["budget_left"] = row[4] if len(row) > 4 else ""
            entry["month_left"] = row[5] if len(row) > 5 else ""
            report["variable_expenses"].append(entry)

    if len(big_picture) >= 4:
        report["big_picture"] = {
            "planned_income": big_picture[2][0] if len(big_picture[2]) > 0 else "",
            "planned_expense": big_picture[2][1] if len(big_picture[2]) > 1 else "",
            "planned_savings": big_picture[2][2] if len(big_picture[2]) > 2 else "",
            "actual_income": big_picture[3][0] if len(big_picture[3]) > 0 else "",
            "actual_expense": big_picture[3][1] if len(big_picture[3]) > 1 else "",
            "actual_savings": big_picture[3][2] if len(big_picture[3]) > 2 else "",
        }

    print(json.dumps(report, indent=2))
    return report


# ---------------------------------------------------------------------------
# Capability 6: Month rollover
# ---------------------------------------------------------------------------

def create_new_month(month, year, tab=None):
    """Duplicate the current month tab for a new month, resetting actuals."""
    tab = tab or current_tab_name()
    service = get_sheets_service()

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID
    ).execute()

    source_sheet_id = None
    for sheet in spreadsheet.get("sheets", []):
        if sheet["properties"]["title"] == tab:
            source_sheet_id = sheet["properties"]["sheetId"]
            break

    if source_sheet_id is None:
        print(f"ERROR: Source tab '{tab}' not found.")
        return False

    new_tab_name = f"{month} {year}"

    for sheet in spreadsheet.get("sheets", []):
        if sheet["properties"]["title"] == new_tab_name:
            print(f"ERROR: Tab '{new_tab_name}' already exists.")
            return False

    dup_request = {
        "requests": [{
            "duplicateSheet": {
                "sourceSheetId": source_sheet_id,
                "newSheetName": new_tab_name,
            }
        }]
    }
    dup_result = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=dup_request,
    ).execute()

    new_sheet_id = dup_result["replies"][0]["duplicateSheet"]["properties"]["sheetId"]

    clear_ranges = [
        f"'{new_tab_name}'!C3:C6",
        f"'{new_tab_name}'!C9:C12",
        f"'{new_tab_name}'!F11:I37",
        f"'{new_tab_name}'!A21:A48",
    ]
    service.spreadsheets().values().batchClear(
        spreadsheetId=SPREADSHEET_ID,
        body={"ranges": clear_ranges},
    ).execute()

    print(f"OK: Created '{new_tab_name}' tab. "
          f"Planned amounts preserved, actuals cleared.")
    return True


# ---------------------------------------------------------------------------
# Capability 9: Bank statement import
# ---------------------------------------------------------------------------

def categorize_transaction(description):
    desc_lower = description.lower()
    for category, keywords in CATEGORIZATION_RULES.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    return "Unknown"


def parse_csv_statement(file_path):
    """Parse a bank statement CSV into structured transactions.

    Handles common column layouts: Date, Description, Amount (or Debit/Credit).
    Returns a list of {date, description, amount, type, category}.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}")
        return []

    content = path.read_text(encoding="utf-8", errors="replace")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    if not rows:
        return []

    header = [h.strip().lower() for h in rows[0]]

    date_col = _find_col(header, ["date", "posting date", "transaction date", "trans date"])
    desc_col = _find_col(header, ["description", "memo", "merchant", "name", "payee", "details"])
    amount_col = _find_col(header, ["amount", "transaction amount"])
    debit_col = _find_col(header, ["debit", "withdrawals", "withdrawal"])
    credit_col = _find_col(header, ["credit", "deposits", "deposit"])

    if date_col is None or desc_col is None:
        print("ERROR: Could not identify date and description columns in CSV.")
        print(f"Headers found: {header}")
        return []

    transactions = []
    for row in rows[1:]:
        if len(row) <= max(filter(None, [date_col, desc_col, amount_col, debit_col, credit_col]), default=0):
            continue

        date_str = row[date_col].strip() if date_col is not None else ""
        desc = row[desc_col].strip() if desc_col is not None else ""

        if not desc:
            continue

        amount = 0.0
        txn_type = "debit"

        if amount_col is not None:
            raw = row[amount_col].strip().replace("$", "").replace(",", "")
            if raw:
                try:
                    val = float(raw)
                    amount = abs(val)
                    txn_type = "credit" if val > 0 else "debit"
                except ValueError:
                    continue
        elif debit_col is not None or credit_col is not None:
            if debit_col is not None and row[debit_col].strip():
                raw = row[debit_col].strip().replace("$", "").replace(",", "").replace("(", "").replace(")", "")
                try:
                    amount = abs(float(raw))
                    txn_type = "debit"
                except ValueError:
                    pass
            if credit_col is not None and row[credit_col].strip():
                raw = row[credit_col].strip().replace("$", "").replace(",", "")
                try:
                    amount = abs(float(raw))
                    txn_type = "credit"
                except ValueError:
                    pass
        else:
            continue

        if amount == 0:
            continue

        category = categorize_transaction(desc)

        if txn_type == "credit" and category not in ("Income",):
            category = "Income"

        transactions.append({
            "date": date_str,
            "description": desc,
            "amount": round(amount, 2),
            "type": txn_type,
            "category": category,
        })

    print(f"Parsed {len(transactions)} transactions from CSV.")
    return transactions


def _find_col(header, candidates):
    for i, h in enumerate(header):
        for c in candidates:
            if c in h:
                return i
    return None


def deduplicate_transactions(transactions, tab=None):
    """Compare transactions against existing tracker entries.

    Returns (new_transactions, duplicates).
    """
    tab = tab or current_tab_name()
    service = get_sheets_service()

    existing_amounts = {}
    for category, col in CATEGORY_COLUMNS.items():
        col_range = f"'{tab}'!{col}{SPENDING_TRACKER_START_ROW}:{col}{SPENDING_TRACKER_END_ROW}"
        values = _read_range(service, col_range)
        amounts = []
        for row in values:
            if row and row[0]:
                try:
                    amounts.append(float(str(row[0]).replace("$", "").replace(",", "")))
                except ValueError:
                    pass
        existing_amounts[category] = amounts

    income_range = f"'{tab}'!C3:C6"
    income_values = _read_range(service, income_range)
    existing_income = []
    for row in income_values:
        if row and row[0]:
            try:
                existing_income.append(float(str(row[0]).replace("$", "").replace(",", "")))
            except ValueError:
                pass

    new_txns = []
    dupes = []

    for txn in transactions:
        cat = txn["category"]
        amt = txn["amount"]

        if cat in existing_amounts and amt in existing_amounts[cat]:
            dupes.append(txn)
            existing_amounts[cat].remove(amt)
        elif cat == "Income" and amt in existing_income:
            dupes.append(txn)
            existing_income.remove(amt)
        else:
            new_txns.append(txn)

    return new_txns, dupes


def import_transactions(transactions_file, tab=None):
    """Write a batch of approved transactions to the sheet."""
    tab = tab or current_tab_name()
    service = get_sheets_service()

    path = Path(transactions_file)
    if not path.exists():
        print(f"ERROR: File not found: {transactions_file}")
        return False

    transactions = json.loads(path.read_text())

    spending = {}
    income_entries = []
    fixed_entries = []

    for txn in transactions:
        cat = txn.get("category", "")
        amount = txn.get("amount", 0)

        if cat in CATEGORY_COLUMNS:
            spending.setdefault(cat, []).append(amount)
        elif cat.lower() == "income":
            source = txn.get("source", "Paycheck")
            income_entries.append({"source": source, "amount": amount})
        elif cat.lower() == "fixed":
            expense = txn.get("expense", "")
            fixed_entries.append({"expense": expense, "amount": amount})

    written = 0

    for category, amounts in spending.items():
        col = CATEGORY_COLUMNS[category]
        col_range = f"'{tab}'!{col}{SPENDING_TRACKER_START_ROW}:{col}{SPENDING_TRACKER_END_ROW}"
        existing = _read_range(service, col_range)
        start_row = SPENDING_TRACKER_START_ROW + len(existing)

        for i, amt in enumerate(amounts):
            row_num = start_row + i
            if row_num > SPENDING_TRACKER_END_ROW:
                print(f"WARNING: {category} column full, skipping ${amt:.2f}")
                continue
            cell = f"'{tab}'!{col}{row_num}"
            _write_range(service, cell, [[amt]])
            written += 1

    for entry in income_entries:
        record_income(entry["source"], entry["amount"], tab)
        written += 1

    for entry in fixed_entries:
        record_fixed_expense(entry["expense"], entry["amount"], tab)
        written += 1

    now = datetime.now().strftime("%Y-%m-%d")
    note = f"Imported {written} transactions on {now}"
    add_note(note, tab)

    print(f"OK: Imported {written} transactions.")
    return True


# ---------------------------------------------------------------------------
# Phase 1: Fix formulas
# ---------------------------------------------------------------------------

FORMULA_FIXES = {
    "G3": "=SUM(F11:F)",
    "G6": "=SUM(I11:I)",
    "C15": "=B9+B10+B11+B12+F7",
}


def fix_formulas(tab=None):
    """Correct known formula bugs in the monthly tab."""
    tab = tab or current_tab_name()
    service = get_sheets_service()

    fixed = 0
    for cell, formula in FORMULA_FIXES.items():
        cell_ref = f"'{tab}'!{cell}"
        _write_range(service, cell_ref, [[formula]])
        fixed += 1
        print(f"  Fixed {cell}: {formula}")

    _write_range(service, f"'{tab}'!G4", [["=SUM(G11:G)"]])
    _write_range(service, f"'{tab}'!G5", [["=SUM(H11:H)"]])
    fixed += 2
    print(f"  Fixed G4: =SUM(G11:G)")
    print(f"  Fixed G5: =SUM(H11:H)")

    print(f"OK: Fixed {fixed} formulas in '{tab}'.")
    return True


# ---------------------------------------------------------------------------
# Phase 2: Annual Totals tab
# ---------------------------------------------------------------------------

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

ANNUAL_ROW_LABELS = [
    "Income (Actual)",
    "Rent",
    "Utilities",
    "Student Debt",
    "401k",
    "Gas",
    "Eating Out",
    "Buying Stuff",
    "Groceries",
    "Total Expenses",
    "Savings",
]

ANNUAL_SOURCE_CELLS = {
    "Income (Actual)":  "B16",
    "Rent":             "C9",
    "Utilities":        "C10",
    "Student Debt":     "C11",
    "401k":             "C12",
    "Gas":              "G3",
    "Eating Out":       "G4",
    "Buying Stuff":     "G5",
    "Groceries":        "G6",
    "Total Expenses":   "C16",
    "Savings":          "D16",
}


def create_annual_tab(year):
    """Create an Annual Totals tab with INDIRECT cross-tab formulas."""
    service = get_sheets_service()
    tab_name = f"Annual Totals {year}"

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID
    ).execute()

    for sheet in spreadsheet.get("sheets", []):
        if sheet["properties"]["title"] == tab_name:
            print(f"ERROR: Tab '{tab_name}' already exists.")
            return False

    add_sheet = {
        "requests": [{
            "addSheet": {
                "properties": {"title": tab_name}
            }
        }]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=add_sheet,
    ).execute()

    header_row = [""] + MONTHS + ["YEAR TOTAL", "MONTHLY AVG"]
    rows = [header_row]

    for label in ANNUAL_ROW_LABELS:
        src_cell = ANNUAL_SOURCE_CELLS[label]
        row = [label]
        month_refs = []
        for i, month in enumerate(MONTHS):
            month_tab = f"{month} {year}"
            col_letter = chr(ord("B") + i)
            formula = f'=IFERROR(INDIRECT("\'{month_tab}\'!{src_cell}"),0)'
            row.append(formula)
            month_refs.append(col_letter)

        first_col = month_refs[0]
        last_col = month_refs[-1]
        row_idx = len(rows) + 1
        row.append(f"=SUM({first_col}{row_idx}:{last_col}{row_idx})")
        row.append(f'=IFERROR(AVERAGEIF({first_col}{row_idx}:{last_col}{row_idx},"<>0"),0)')
        rows.append(row)

    rows.append([])
    rows.append(["YEAR-TO-DATE INSIGHTS"])
    insight_start = len(rows) + 1

    rows.append(["Total Earned YTD", f"=N2"])
    rows.append(["Total Spent YTD", f"=N10"])
    rows.append(["Total Saved YTD", f"=N11"])
    rows.append(["Savings Rate", f'=IFERROR(N11/N2, 0)'])
    rows.append(["401k Contributions YTD", f"=N5"])
    rows.append(["Highest Spending Month",
                  f'=IFERROR(INDEX(B1:M1, MATCH(MAX(B10:M10), B10:M10, 0)), "N/A")'])
    rows.append(["Lowest Spending Month",
                  f'=IFERROR(INDEX(B1:M1, MATCH(MINIFS(B10:M10, B10:M10, ">0"), B10:M10, 0)), "N/A")'])

    rows.append([])
    rows.append(["CATEGORY BREAKDOWN (% of Variable Spending)"])

    variable_cats = ["Gas", "Eating Out", "Buying Stuff", "Groceries"]
    for cat in variable_cats:
        cat_row = ANNUAL_ROW_LABELS.index(cat) + 2
        total_var = f"=SUM(N6:N9)"
        rows.append([cat, f'=IFERROR(N{cat_row}/SUM(N6:N9), 0)'])

    _write_range(service,
                 f"'{tab_name}'!A1",
                 rows)

    print(f"OK: Created '{tab_name}' with {len(ANNUAL_ROW_LABELS)} tracked rows, "
          f"YTD insights, and category breakdown.")
    return True


# ---------------------------------------------------------------------------
# Phase 3a: Conditional formatting
# ---------------------------------------------------------------------------

def _get_sheet_id(service, tab_name):
    """Get the numeric sheetId for a tab name."""
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID
    ).execute()
    for sheet in spreadsheet.get("sheets", []):
        if sheet["properties"]["title"] == tab_name:
            return sheet["properties"]["sheetId"]
    return None


def _make_bool_rule(sheet_id, start_row, end_row, start_col, end_col,
                    formula, red, green, blue):
    """Build a conditional formatting booleanRule request."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": start_row - 1,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_col - 1,
                    "endColumnIndex": end_col,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": formula}],
                    },
                    "format": {
                        "backgroundColor": {
                            "red": red, "green": green, "blue": blue,
                        }
                    },
                },
            },
            "index": 0,
        }
    }


def apply_conditional_formatting(tab=None):
    """Apply color rules to budget status cells."""
    tab = tab or current_tab_name()
    service = get_sheets_service()
    sheet_id = _get_sheet_id(service, tab)

    if sheet_id is None:
        print(f"ERROR: Tab '{tab}' not found.")
        return False

    requests = []

    # Budget Left % (col I = 9, rows 3-7): green >= month left, red < month left
    # Green: Budget Left >= Month Left
    requests.append(_make_bool_rule(
        sheet_id, 3, 7, 9, 10,
        '=AND(I3<>"", J3<>"", I3>=J3)',
        0.72, 0.88, 0.72,  # light green
    ))
    # Yellow: Budget Left within 10% of Month Left
    requests.append(_make_bool_rule(
        sheet_id, 3, 7, 9, 10,
        '=AND(I3<>"", J3<>"", I3<J3, I3>=J3-0.1)',
        1.0, 0.95, 0.6,  # light yellow
    ))
    # Red: Budget Left well below Month Left
    requests.append(_make_bool_rule(
        sheet_id, 3, 7, 9, 10,
        '=AND(I3<>"", J3<>"", I3<J3-0.1)',
        0.96, 0.7, 0.7,  # light red
    ))

    # Difference column (col D = 4, rows 3-6): green if positive, red if negative
    requests.append(_make_bool_rule(
        sheet_id, 3, 6, 4, 5,
        '=D3>0',
        0.72, 0.88, 0.72,
    ))
    requests.append(_make_bool_rule(
        sheet_id, 3, 6, 4, 5,
        '=D3<0',
        0.96, 0.7, 0.7,
    ))

    # Savings cell (D16): green if actual >= planned, red if below
    requests.append(_make_bool_rule(
        sheet_id, 16, 16, 4, 5,
        '=D16>=D15',
        0.72, 0.88, 0.72,
    ))
    requests.append(_make_bool_rule(
        sheet_id, 16, 16, 4, 5,
        '=D16<D15',
        0.96, 0.7, 0.7,
    ))

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": requests},
    ).execute()

    print(f"OK: Applied {len(requests)} conditional formatting rules to '{tab}'.")
    return True


# ---------------------------------------------------------------------------
# Phase 3b: Sparklines
# ---------------------------------------------------------------------------

def add_sparklines(tab=None):
    """Add SPARKLINE progress bars next to variable expense categories."""
    tab = tab or current_tab_name()
    service = get_sheets_service()

    sparkline_col = "K"
    sparklines = {
        3: '=IF(F3="","",SPARKLINE({IFERROR(G3/F3,0), IFERROR(1-G3/F3,1)}, {"charttype","bar"; "color1","#cc0000"; "color2","#e8e8e8"}))',
        4: '=IF(F4="","",SPARKLINE({IFERROR(G4/F4,0), IFERROR(1-G4/F4,1)}, {"charttype","bar"; "color1","#cc0000"; "color2","#e8e8e8"}))',
        5: '=IF(F5="","",SPARKLINE({IFERROR(G5/F5,0), IFERROR(1-G5/F5,1)}, {"charttype","bar"; "color1","#cc0000"; "color2","#e8e8e8"}))',
        6: '=IF(F6="","",SPARKLINE({IFERROR(G6/F6,0), IFERROR(1-G6/F6,1)}, {"charttype","bar"; "color1","#cc0000"; "color2","#e8e8e8"}))',
    }

    _write_range(service, f"'{tab}'!{sparkline_col}2", [["Burn Rate"]])

    for row, formula in sparklines.items():
        cell = f"'{tab}'!{sparkline_col}{row}"
        _write_range(service, cell, [[formula]])

    print(f"OK: Added sparkline progress bars in column {sparkline_col} for '{tab}'.")
    return True


# ---------------------------------------------------------------------------
# Phase 3c: Subscriptions
# ---------------------------------------------------------------------------

SUBSCRIPTIONS_HEADER_ROW = 14
SUBSCRIPTIONS_START_ROW = 15


def add_subscriptions_section(tab=None, subscriptions=None):
    """Add a subscriptions tracker section to the monthly tab.

    subscriptions: dict of {"Name": monthly_cost, ...}
    """
    tab = tab or current_tab_name()
    service = get_sheets_service()

    if not subscriptions:
        subscriptions = {}

    rows = [["Subscriptions", "Monthly", "Annual"]]
    data_start = SUBSCRIPTIONS_START_ROW
    for i, (name, cost) in enumerate(subscriptions.items()):
        row_num = data_start + i
        rows.append([name, cost, f"=F{row_num}*12"])

    total_row = data_start + len(subscriptions)
    first_data = data_start
    last_data = total_row - 1
    rows.append([
        "TOTAL",
        f"=SUM(F{first_data}:F{last_data})",
        f"=SUM(G{first_data}:G{last_data})",
    ])

    _write_range(service,
                 f"'{tab}'!E{SUBSCRIPTIONS_HEADER_ROW}",
                 rows)

    print(f"OK: Added subscriptions section with {len(subscriptions)} items "
          f"starting at E{SUBSCRIPTIONS_HEADER_ROW} in '{tab}'.")
    return True


# ---------------------------------------------------------------------------
# Phase 3d: Expand tracker grid
# ---------------------------------------------------------------------------

def expand_tracker_grid(tab=None):
    """Update SUM formulas to use open-ended ranges (F11:F, G11:G, etc.)."""
    tab = tab or current_tab_name()
    service = get_sheets_service()

    open_range_formulas = {
        "G3": "=SUM(F11:F)",
        "G4": "=SUM(G11:G)",
        "G5": "=SUM(H11:H)",
        "G6": "=SUM(I11:I)",
    }

    for cell, formula in open_range_formulas.items():
        _write_range(service, f"'{tab}'!{cell}", [[formula]])

    global SPENDING_TRACKER_END_ROW
    SPENDING_TRACKER_END_ROW = 200

    print(f"OK: Updated SUM formulas to open-ended ranges in '{tab}'. "
          f"Spending tracker now supports unlimited rows.")
    return True


# ---------------------------------------------------------------------------
# Phase 3e: Set planned budget
# ---------------------------------------------------------------------------

PLANNED_BUDGET_CELLS = {
    "Gas": "F3",
    "Eating Out": "F4",
    "Buying Stuff": "F5",
    "Groceries": "F6",
}


def set_planned_budget(category, amount, tab=None):
    """Set the planned budget for a variable expense category."""
    tab = tab or current_tab_name()
    service = get_sheets_service()

    if category not in PLANNED_BUDGET_CELLS:
        print(f"ERROR: Unknown category '{category}'. "
              f"Valid: {', '.join(PLANNED_BUDGET_CELLS.keys())}")
        return False

    cell = f"'{tab}'!{PLANNED_BUDGET_CELLS[category]}"
    _write_range(service, cell, [[amount]])
    print(f"OK: Set planned budget for {category} to ${amount:.2f} in '{tab}'.")
    return True


# ---------------------------------------------------------------------------
# Capability 10: Notes
# ---------------------------------------------------------------------------

def add_note(text, tab=None):
    tab = tab or current_tab_name()
    service = get_sheets_service()

    notes_range = f"'{tab}'!A{NOTES_START_ROW}:A{NOTES_END_ROW}"
    existing = _read_range(service, notes_range)

    next_row = NOTES_START_ROW
    for i, row in enumerate(existing):
        if row and row[0] and str(row[0]).strip():
            next_row = NOTES_START_ROW + i + 1

    if next_row > NOTES_END_ROW:
        print("ERROR: Notes section is full.")
        return False

    cell = f"'{tab}'!A{next_row}"
    _write_range(service, cell, [[text]])
    print(f"OK: Added note at A{next_row}")
    return True


# ---------------------------------------------------------------------------
# Theme: helper builders
# ---------------------------------------------------------------------------

def _repeat_cell(sheet_id, r1, r2, c1, c2, bg=None, fg=None, font=None,
                 num_fmt=None, h_align=None, bold=None, borders=None):
    """Build a repeatCell request. Rows/cols are 0-indexed."""
    fmt = {}
    fields = []

    if bg:
        fmt["backgroundColor"] = bg
        fields.append("backgroundColor")
    if fg or font or bold is not None:
        tf = {}
        if fg:
            tf["foregroundColor"] = fg
        if font:
            tf["fontFamily"] = font["fontFamily"]
            tf["fontSize"] = font["fontSize"]
            if "bold" in font:
                tf["bold"] = font["bold"]
        if bold is not None:
            tf["bold"] = bold
        fmt["textFormat"] = tf
        fields.append("textFormat")
    if num_fmt:
        fmt["numberFormat"] = {"type": "NUMBER", "pattern": num_fmt}
        fields.append("numberFormat")
    if h_align:
        fmt["horizontalAlignment"] = h_align
        fields.append("horizontalAlignment")
    if borders:
        fmt["borders"] = borders
        fields.append("borders")

    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": r1,
                "endRowIndex": r2,
                "startColumnIndex": c1,
                "endColumnIndex": c2,
            },
            "cell": {"userEnteredFormat": fmt},
            "fields": "userEnteredFormat(" + ",".join(fields) + ")",
        }
    }


def _col_width(sheet_id, col_idx, px):
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": col_idx,
                "endIndex": col_idx + 1,
            },
            "properties": {"pixelSize": px},
            "fields": "pixelSize",
        }
    }


def _freeze(sheet_id, rows=0, cols=0):
    props = {}
    if rows:
        props["frozenRowCount"] = rows
    if cols:
        props["frozenColumnCount"] = cols
    return {
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": props},
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
        }
    }


THIN_BORDER = {"style": "SOLID", "width": 1, "color": _hex_to_rgb("#CCCCCC")}
THICK_BORDER = {"style": "SOLID_MEDIUM", "width": 2, "color": _hex_to_rgb("#1B2A4A")}


# ---------------------------------------------------------------------------
# Theme: apply to monthly tab
# ---------------------------------------------------------------------------

def apply_theme(tab=None):
    """Apply the full design system to a monthly budget tab."""
    tab = tab or current_tab_name()
    service = get_sheets_service()
    sheet_id = _get_sheet_id(service, tab)
    if sheet_id is None:
        print(f"ERROR: Tab '{tab}' not found.")
        return False

    c = THEME["colors"]
    f = THEME["fonts"]
    nf = THEME["formats"]
    reqs = []

    # --- Column widths ---
    for col_idx, px in THEME["col_widths_monthly"].items():
        reqs.append(_col_width(sheet_id, col_idx, px))

    # --- Freeze row 2 ---
    reqs.append(_freeze(sheet_id, rows=2))

    # --- Section headers (dark navy bg, white bold text) ---
    section_header_rows = [
        (0, 4),   # Row 1: "INCOME (Money Coming In)" (cols A-D)
        (6, 4),   # Row 7: "Fixed Monthly Expenses" (cols A-D)
        (12, 4),  # Row 13: "BIG PICTURE STATUS" label area (cols B-D)
    ]
    for row_0, ncols in section_header_rows:
        reqs.append(_repeat_cell(
            sheet_id, row_0, row_0 + 1, 0, ncols,
            bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
        ))

    # Row 1 right side: "Planned Spending on Variable Expenses" (E1)
    reqs.append(_repeat_cell(
        sheet_id, 0, 1, 4, 11,
        bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
    ))

    # Row 9 right side: "Spending Tracking" header
    reqs.append(_repeat_cell(
        sheet_id, 8, 9, 4, 11,
        bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
    ))

    # "NOTES:" header row 21
    reqs.append(_repeat_cell(
        sheet_id, 20, 21, 0, 4,
        bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
    ))

    # --- Column header rows (light bg, bold centered) ---
    col_header_rows = [
        (1, 0, 4),   # Row 2: Income/Planned/Actual/Difference
        (1, 4, 11),  # Row 2: Expenses/Planned/Actual/Remaining/BudgetLeft/MonthLeft/BurnRate
        (7, 0, 3),   # Row 8: Monthly Expenses/Planned/Actual
        (9, 5, 9),   # Row 10: Gas/Eating out/Buying Stuff/Groceries (tracker headers)
        (13, 1, 4),  # Row 14: Income/Expense/SAVINGS
    ]
    for row_0, c1, c2 in col_header_rows:
        reqs.append(_repeat_cell(
            sheet_id, row_0, row_0 + 1, c1, c2,
            bg=c["col_header_bg"], fg=c["col_header_fg"], font=f["col_header"],
            h_align="CENTER",
        ))

    # Section header thick bottom borders
    for row_0 in [0, 6, 8, 12, 20]:
        reqs.append(_repeat_cell(
            sheet_id, row_0, row_0 + 1, 0, 11,
            borders={"bottom": THICK_BORDER},
        ))

    # Column header thin bottom borders
    for row_0, c1, c2 in col_header_rows:
        reqs.append(_repeat_cell(
            sheet_id, row_0, row_0 + 1, c1, c2,
            borders={"bottom": THIN_BORDER},
        ))

    # --- Data cells: number formatting ---
    # Income planned/actual/difference (B3:D6) = currency
    reqs.append(_repeat_cell(sheet_id, 2, 6, 1, 4, num_fmt=nf["currency"]))
    # Fixed expense planned/actual (B9:C12) = currency
    reqs.append(_repeat_cell(sheet_id, 8, 12, 1, 3, num_fmt=nf["currency"]))
    # Variable planned/actual/remaining (F3:H7) = currency
    reqs.append(_repeat_cell(sheet_id, 2, 7, 5, 8, num_fmt=nf["currency"]))
    # Budget left % (I3:I7) = percent
    reqs.append(_repeat_cell(sheet_id, 2, 7, 8, 9, num_fmt=nf["percent"]))
    # Month left % (J3:J7) = percent
    reqs.append(_repeat_cell(sheet_id, 2, 7, 9, 10, num_fmt=nf["percent"]))
    # Big Picture (B15:D16) = currency
    reqs.append(_repeat_cell(sheet_id, 14, 16, 1, 4, num_fmt=nf["currency"]))
    # Spending tracker grid (F11:I37+) = currency
    reqs.append(_repeat_cell(sheet_id, 10, 60, 5, 9, num_fmt=nf["currency"]))
    # Subscriptions monthly (F15:F18) = currency
    reqs.append(_repeat_cell(sheet_id, 14, 18, 5, 6, num_fmt=nf["currency"]))
    # Subscriptions annual (G15:G18) = currency
    reqs.append(_repeat_cell(sheet_id, 14, 18, 6, 7, num_fmt=nf["currency"]))

    # --- Data label alignment (left) ---
    reqs.append(_repeat_cell(sheet_id, 2, 6, 0, 1, h_align="LEFT"))
    reqs.append(_repeat_cell(sheet_id, 8, 12, 0, 1, h_align="LEFT"))
    reqs.append(_repeat_cell(sheet_id, 2, 7, 4, 5, h_align="LEFT"))

    # --- Total row (variable expenses row 7) ---
    reqs.append(_repeat_cell(
        sheet_id, 6, 7, 4, 11,
        bg=c["total_bg"], font=f["total"],
        borders={"top": THIN_BORDER},
    ))

    # --- Big Picture section styling ---
    reqs.append(_repeat_cell(
        sheet_id, 12, 13, 1, 4,
        bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
    ))
    # Planned row label bold
    reqs.append(_repeat_cell(sheet_id, 14, 15, 0, 1, font=f["total"]))
    # Actual row label bold
    reqs.append(_repeat_cell(sheet_id, 15, 16, 0, 1, font=f["total"]))

    # --- Subscriptions header (row 14, cols E-G) ---
    reqs.append(_repeat_cell(
        sheet_id, 13, 14, 4, 7,
        bg=c["col_header_bg"], fg=c["col_header_fg"], font=f["col_header"],
        h_align="CENTER",
        borders={"bottom": THIN_BORDER},
    ))

    # Subscriptions total row
    reqs.append(_repeat_cell(
        sheet_id, 17, 18, 4, 7,
        bg=c["total_bg"], font=f["total"],
        borders={"top": THIN_BORDER},
    ))

    # --- Alternating row stripes on spending tracker ---
    for row_0 in range(10, 60):
        if row_0 % 2 == 0:
            reqs.append(_repeat_cell(
                sheet_id, row_0, row_0 + 1, 5, 9,
                bg=c["row_alt"],
            ))

    # --- Notes section cream background ---
    reqs.append(_repeat_cell(
        sheet_id, 21, 48, 0, 4,
        bg=c["notes_bg"], font=f["notes"],
    ))

    # --- Execute ---
    for i in range(0, len(reqs), 50):
        chunk = reqs[i:i + 50]
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": chunk},
        ).execute()

    print(f"OK: Applied theme to '{tab}' ({len(reqs)} formatting requests).")
    return True


# ---------------------------------------------------------------------------
# Theme: apply to annual tab
# ---------------------------------------------------------------------------

def apply_theme_annual(year):
    """Apply the design system to the Annual Totals tab."""
    tab_name = f"Annual Totals {year}"
    service = get_sheets_service()
    sheet_id = _get_sheet_id(service, tab_name)
    if sheet_id is None:
        print(f"ERROR: Tab '{tab_name}' not found.")
        return False

    c = THEME["colors"]
    f = THEME["fonts"]
    nf = THEME["formats"]
    reqs = []

    # Column A width
    reqs.append(_col_width(sheet_id, 0, 160))
    # Month columns (B-M) width
    for col in range(1, 13):
        reqs.append(_col_width(sheet_id, col, 85))
    # YEAR TOTAL (N) and MONTHLY AVG (O) wider
    reqs.append(_col_width(sheet_id, 13, 100))
    reqs.append(_col_width(sheet_id, 14, 100))

    # Freeze row 1 and column A
    reqs.append(_freeze(sheet_id, rows=1, cols=1))

    # --- Header row (row 1): dark bg, white text ---
    reqs.append(_repeat_cell(
        sheet_id, 0, 1, 0, 15,
        bg=c["header_bg"], fg=c["header_fg"], font=f["col_header"],
        h_align="CENTER",
        borders={"bottom": THICK_BORDER},
    ))

    # --- Row labels column (A2:A12) bold ---
    reqs.append(_repeat_cell(
        sheet_id, 1, 12, 0, 1,
        font=f["total"], h_align="LEFT",
    ))

    # --- Data cells: currency format (B2:M12) ---
    reqs.append(_repeat_cell(sheet_id, 1, 12, 1, 13, num_fmt=nf["currency"]))

    # --- YEAR TOTAL and MONTHLY AVG columns (N-O) highlight bg ---
    reqs.append(_repeat_cell(
        sheet_id, 1, 12, 13, 15,
        bg=c["total_bg"], font=f["total"], num_fmt=nf["currency"],
    ))

    # --- Total Expenses row (row 11) ---
    reqs.append(_repeat_cell(
        sheet_id, 10, 11, 0, 15,
        bg=c["total_bg"], font=f["total"],
        borders={"top": THIN_BORDER},
    ))

    # --- Savings row (row 12) ---
    reqs.append(_repeat_cell(
        sheet_id, 11, 12, 0, 15,
        font=f["total"],
        borders={"top": THIN_BORDER},
    ))

    # --- Alternating row stripes (data rows 2-12) ---
    for row_0 in range(1, 12):
        if row_0 % 2 == 1:
            reqs.append(_repeat_cell(
                sheet_id, row_0, row_0 + 1, 0, 13,
                bg=c["row_alt"],
            ))

    # --- YTD Insights section header (row 14) ---
    reqs.append(_repeat_cell(
        sheet_id, 13, 14, 0, 5,
        bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
        borders={"bottom": THICK_BORDER},
    ))

    # YTD insight labels bold (A15:A21)
    reqs.append(_repeat_cell(
        sheet_id, 14, 21, 0, 1,
        font=f["total"], h_align="LEFT",
    ))

    # YTD insight values: currency for dollar amounts (B15:B17)
    reqs.append(_repeat_cell(sheet_id, 14, 17, 1, 2, num_fmt=nf["currency"]))
    # Savings rate as percentage (B18)
    reqs.append(_repeat_cell(sheet_id, 17, 18, 1, 2, num_fmt=nf["percent_decimal"]))
    # 401k YTD as currency (B19)
    reqs.append(_repeat_cell(sheet_id, 18, 19, 1, 2, num_fmt=nf["currency"]))

    # --- Category Breakdown section header (row 23) ---
    reqs.append(_repeat_cell(
        sheet_id, 22, 23, 0, 5,
        bg=c["header_bg"], fg=c["header_fg"], font=f["section_header"],
        borders={"bottom": THICK_BORDER},
    ))

    # Category breakdown labels bold (A24:A27)
    reqs.append(_repeat_cell(
        sheet_id, 23, 27, 0, 1,
        font=f["total"], h_align="LEFT",
    ))

    # Category breakdown percentages (B24:B27)
    reqs.append(_repeat_cell(sheet_id, 23, 27, 1, 2, num_fmt=nf["percent_decimal"]))

    # --- Execute ---
    for i in range(0, len(reqs), 50):
        chunk = reqs[i:i + 50]
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": chunk},
        ).execute()

    print(f"OK: Applied theme to '{tab_name}' ({len(reqs)} formatting requests).")
    return True


# ---------------------------------------------------------------------------
# Theme: apply all
# ---------------------------------------------------------------------------

def apply_theme_all():
    """Apply theme to current monthly tab and the annual tab."""
    now = datetime.now()
    apply_theme()
    apply_theme_annual(now.year)
    print("OK: Theme applied to all tabs.")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Budget tracker for Google Sheets")
    parser.add_argument("--setup", action="store_true", help="Run OAuth setup")

    subparsers = parser.add_subparsers(dest="command")

    log_p = subparsers.add_parser("log", help="Log a spending entry")
    log_p.add_argument("--category", required=True,
                       choices=list(CATEGORY_COLUMNS.keys()))
    log_p.add_argument("--amount", required=True, type=float)
    log_p.add_argument("--tab", default=None)

    inc_p = subparsers.add_parser("income", help="Record income")
    inc_p.add_argument("--source", required=True)
    inc_p.add_argument("--amount", required=True, type=float)
    inc_p.add_argument("--tab", default=None)

    fix_p = subparsers.add_parser("fixed", help="Record fixed expense")
    fix_p.add_argument("--expense", required=True,
                       choices=list(FIXED_EXPENSE_ROWS.keys()))
    fix_p.add_argument("--amount", required=True, type=float)
    fix_p.add_argument("--tab", default=None)

    subparsers.add_parser("dashboard", help="Show budget dashboard")

    note_p = subparsers.add_parser("note", help="Add a note")
    note_p.add_argument("--text", required=True)
    note_p.add_argument("--tab", default=None)

    month_p = subparsers.add_parser("new-month", help="Create new month tab")
    month_p.add_argument("--month", required=True)
    month_p.add_argument("--year", required=True, type=int)
    month_p.add_argument("--source-tab", default=None,
                         help="Tab to duplicate from (default: current month)")

    csv_p = subparsers.add_parser("parse-csv", help="Parse a bank statement CSV")
    csv_p.add_argument("--file", required=True)

    imp_p = subparsers.add_parser("import", help="Import approved transactions")
    imp_p.add_argument("--transactions-file", required=True)
    imp_p.add_argument("--tab", default=None)

    cat_p = subparsers.add_parser("categorize", help="Categorize a transaction description")
    cat_p.add_argument("--description", required=True)

    dedup_p = subparsers.add_parser("dedup", help="Check transactions for duplicates")
    dedup_p.add_argument("--transactions-file", required=True)
    dedup_p.add_argument("--tab", default=None)

    fix_p2 = subparsers.add_parser("fix-formulas", help="Fix known formula bugs")
    fix_p2.add_argument("--tab", default=None)

    annual_p = subparsers.add_parser("create-annual", help="Create annual totals tab")
    annual_p.add_argument("--year", required=True, type=int)

    fmt_p = subparsers.add_parser("apply-formatting", help="Apply conditional formatting")
    fmt_p.add_argument("--tab", default=None)

    spark_p = subparsers.add_parser("add-sparklines", help="Add sparkline progress bars")
    spark_p.add_argument("--tab", default=None)

    sub_p = subparsers.add_parser("add-subscriptions", help="Add subscriptions section")
    sub_p.add_argument("--items", required=True,
                       help='JSON object: {"Spotify": 10.99, "Netflix": 15.49}')
    sub_p.add_argument("--tab", default=None)

    expand_p = subparsers.add_parser("expand-tracker", help="Expand spending tracker to unlimited rows")
    expand_p.add_argument("--tab", default=None)

    plan_p = subparsers.add_parser("set-planned", help="Set planned budget for a category")
    plan_p.add_argument("--category", required=True,
                        choices=list(PLANNED_BUDGET_CELLS.keys()))
    plan_p.add_argument("--amount", required=True, type=float)
    plan_p.add_argument("--tab", default=None)

    theme_p = subparsers.add_parser("apply-theme", help="Apply design system to a tab")
    theme_p.add_argument("--tab", default=None)

    theme_a = subparsers.add_parser("apply-theme-annual", help="Apply design system to annual tab")
    theme_a.add_argument("--year", required=True, type=int)

    subparsers.add_parser("apply-theme-all", help="Apply design system to all tabs")

    args = parser.parse_args()

    if args.setup:
        get_credentials(force_setup=True)
        return

    if args.command == "log":
        log_expense(args.category, args.amount, args.tab)

    elif args.command == "income":
        record_income(args.source, args.amount, args.tab)

    elif args.command == "fixed":
        record_fixed_expense(args.expense, args.amount, args.tab)

    elif args.command == "dashboard":
        read_dashboard()

    elif args.command == "note":
        add_note(args.text, args.tab)

    elif args.command == "new-month":
        create_new_month(args.month, args.year, args.source_tab)

    elif args.command == "parse-csv":
        txns = parse_csv_statement(args.file)
        print(json.dumps(txns, indent=2))

    elif args.command == "import":
        import_transactions(args.transactions_file, args.tab)

    elif args.command == "categorize":
        cat = categorize_transaction(args.description)
        print(f"Category: {cat}")

    elif args.command == "dedup":
        path = Path(args.transactions_file)
        txns = json.loads(path.read_text())
        new_txns, dupes = deduplicate_transactions(txns, args.tab)
        print(json.dumps({"new": new_txns, "duplicates": dupes}, indent=2))

    elif args.command == "fix-formulas":
        fix_formulas(args.tab)

    elif args.command == "create-annual":
        create_annual_tab(args.year)

    elif args.command == "apply-formatting":
        apply_conditional_formatting(args.tab)

    elif args.command == "add-sparklines":
        add_sparklines(args.tab)

    elif args.command == "add-subscriptions":
        items = json.loads(args.items)
        add_subscriptions_section(args.tab, items)

    elif args.command == "expand-tracker":
        expand_tracker_grid(args.tab)

    elif args.command == "set-planned":
        set_planned_budget(args.category, args.amount, args.tab)

    elif args.command == "apply-theme":
        apply_theme(args.tab)

    elif args.command == "apply-theme-annual":
        apply_theme_annual(args.year)

    elif args.command == "apply-theme-all":
        apply_theme_all()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
