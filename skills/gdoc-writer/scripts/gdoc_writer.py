#!/usr/bin/env python3
"""Google Docs writer with typography presets, tab navigation, and auto-bold.

Usage:
    python3 gdoc_writer.py create --title "My Doc" --preset redhat-formal --content-file /tmp/content.md
    python3 gdoc_writer.py format --doc-id <ID> --preset redhat-formal
    python3 gdoc_writer.py read --doc-id <ID>
    python3 gdoc_writer.py tabs --doc-id <ID>
    python3 gdoc_writer.py --setup
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_FILE = Path.home() / ".config" / "g-workspace-mcp" / "docs_write_token.json"
CLIENT_SECRET = Path.home() / ".config" / "g-workspace-mcp" / "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
]

COLORS = {
    "blue_link": {"red": 0.07, "green": 0.33, "blue": 0.80},
    "green_structure": {"red": 0.09, "green": 0.50, "blue": 0.22},
}

PRESETS = {
    "redhat-formal": {
        "h1": {"fontFamily": "Red Hat Display", "fontSize": 20, "bold": True},
        "h2": {"fontFamily": "Red Hat Display", "fontSize": 16, "bold": True},
        "h3": {"fontFamily": "Red Hat Display", "fontSize": 13, "bold": True},
        "body": {"fontFamily": "Red Hat Text", "fontSize": 11, "bold": False},
        "bold_patterns": [
            "Deliverable:", "Decision:", "Action:", "Key Learning:",
            "Author:", "Date:", "Status:", "Owner:",
        ],
    },
    "integration-proposal": {
        "h1": {"fontFamily": "Red Hat Display", "fontSize": 20, "bold": True},
        "h2": {"fontFamily": "Red Hat Display", "fontSize": 16, "bold": True},
        "h3": {"fontFamily": "Red Hat Display", "fontSize": 13, "bold": True},
        "body": {"fontFamily": "Red Hat Text", "fontSize": 11, "bold": False},
        "bold_patterns": [
            "Goal:", "Tasks:", "Success:", "Phase", "Timeline:",
            "Stakeholders:", "Background:", "Structure:", "Struggle:",
            "Context:", "Job (JTBD):", "Deliverable:", "Next steps:",
            "Author:", "Date:", "Status:", "Owner:",
        ],
        "color_rules": {
            "jira_keys": COLORS["blue_link"],
            "cross_tab_refs": COLORS["blue_link"],
            "urls": COLORS["blue_link"],
            "structure_diagrams": COLORS["green_structure"],
        },
    },
    "casual-notes": {
        "h1": {"fontFamily": "Arial", "fontSize": 18, "bold": True},
        "h2": {"fontFamily": "Arial", "fontSize": 14, "bold": True},
        "h3": {"fontFamily": "Arial", "fontSize": 12, "bold": True},
        "body": {"fontFamily": "Arial", "fontSize": 11, "bold": False},
        "bold_patterns": ["Owner:", "Date:", "Status:"],
    },
    "meeting-doc": {
        "h1": {"fontFamily": "Arial", "fontSize": 16, "bold": True},
        "h2": {"fontFamily": "Arial", "fontSize": 13, "bold": True},
        "h3": {"fontFamily": "Arial", "fontSize": 11, "bold": True},
        "body": {"fontFamily": "Arial", "fontSize": 11, "bold": False},
        "bold_patterns": [
            "Action:", "Decision:", "Blocker:", "Next Steps:",
            "Owner:", "Date:", "Status:",
        ],
    },
    "presentation-notes": {
        "h1": {"fontFamily": "Arial", "fontSize": 20, "bold": True},
        "h2": {"fontFamily": "Arial", "fontSize": 16, "bold": True},
        "h3": {"fontFamily": "Arial", "fontSize": 13, "bold": False},
        "body": {"fontFamily": "Arial", "fontSize": 12, "bold": False},
        "bold_patterns": ["Key Point:", "Transition:", "Demo:"],
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
        print(f"No client_secret.json at {CLIENT_SECRET}")
        sys.exit(1)
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())
    print("Authentication successful.")
    return creds


def get_services():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return docs, drive


def extract_doc_id(url_or_id: str) -> str:
    """Extract a document ID from a URL or return as-is if already an ID."""
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id


# --- Create Mode ---

def create_doc(title: str, content_md: str, preset: str = "casual-notes") -> str:
    """Create a new Google Doc from markdown content with the specified preset.

    Returns the document URL.
    """
    docs, drive = get_services()
    style = PRESETS.get(preset, PRESETS["casual-notes"])

    html = _markdown_to_html(content_md, style)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp_path = f.name

    try:
        file_metadata = {
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
        }
        media = MediaFileUpload(tmp_path, mimetype="text/html", resumable=True)
        file = drive.files().create(
            body=file_metadata, media_body=media, fields="id,webViewLink"
        ).execute()
    finally:
        os.unlink(tmp_path)

    doc_id = file["id"]
    doc_url = file["webViewLink"]

    _apply_preset_formatting(docs, doc_id, style)

    print(f"Created: {title}")
    print(f"URL: {doc_url}")
    print(f"Preset: {preset}")
    return doc_url


def _markdown_to_html(md: str, style: dict) -> str:
    """Convert markdown to HTML with semantic structure for Docs import."""
    lines = md.strip().split("\n")
    html_parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"]

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("### "):
            html_parts.append(f"<h3>{_escape(line[4:])}</h3>")
        elif line.startswith("## "):
            html_parts.append(f"<h2>{_escape(line[3:])}</h2>")
        elif line.startswith("# "):
            html_parts.append(f"<h1>{_escape(line[2:])}</h1>")
        elif line.startswith("- ") or line.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                items.append(f"<li>{_escape(lines[i][2:])}</li>")
                i += 1
            html_parts.append(f"<ul>{''.join(items)}</ul>")
            continue
        elif line.startswith("| "):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if re.match(r"^\|[\s\-:|]+\|$", lines[i].strip()):
                    i += 1
                    continue
                cells = [c.strip() for c in lines[i].split("|")[1:-1]]
                tag = "th" if not rows else "td"
                row_html = "".join(f"<{tag}>{_escape(c)}</{tag}>" for c in cells)
                rows.append(f"<tr>{row_html}</tr>")
                i += 1
            html_parts.append(f"<table border='1' cellpadding='4'>{''.join(rows)}</table>")
            continue
        elif line.strip() == "":
            pass
        else:
            html_parts.append(f"<p>{_escape(line)}</p>")

        i += 1

    html_parts.append("</body></html>")
    return "\n".join(html_parts)


def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _apply_preset_formatting(docs, doc_id: str, style: dict, tab_id: str | None = None):
    """Apply font families and sizes from a preset to the entire document."""
    doc = docs.documents().get(documentId=doc_id, includeTabsContent=True).execute()

    if tab_id:
        body_content = _get_tab_content(doc, tab_id)
        target_tab_id = tab_id
    else:
        tabs = doc.get("tabs", [])
        if tabs:
            first_tab = tabs[0]
            target_tab_id = first_tab.get("tabProperties", {}).get("tabId")
            body_content = first_tab.get("documentTab", {}).get("body", {}).get("content", [])
        else:
            body_content = doc.get("body", {}).get("content", [])
            target_tab_id = None

    if not body_content:
        return

    requests = []
    for elem in body_content:
        if "paragraph" not in elem:
            continue
        para = elem["paragraph"]
        para_style = para.get("paragraphStyle", {})
        named_style = para_style.get("namedStyleType", "NORMAL_TEXT")

        if named_style in ("HEADING_1", "TITLE"):
            target = style["h1"]
        elif named_style == "HEADING_2":
            target = style["h2"]
        elif named_style in ("HEADING_3", "HEADING_4"):
            target = style["h3"]
        else:
            target = style["body"]

        start = elem.get("startIndex", 0)
        end = elem.get("endIndex", start)
        if end - 1 <= start:
            continue

        text_style = {
            "weightedFontFamily": {"fontFamily": target["fontFamily"]},
            "fontSize": {"magnitude": target["fontSize"], "unit": "PT"},
        }
        if target.get("bold"):
            text_style["bold"] = True

        req = {
            "updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end - 1},
                "textStyle": text_style,
                "fields": "weightedFontFamily,fontSize,bold",
            }
        }
        if target_tab_id:
            req["updateTextStyle"]["range"]["tabId"] = target_tab_id
        requests.append(req)

        # Add spacing before headings for visual breathing room
        if named_style in ("HEADING_1", "HEADING_2", "HEADING_3", "TITLE"):
            space_before = 12 if named_style in ("HEADING_1", "TITLE") else 8
            para_req = {
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end - 1},
                    "paragraphStyle": {
                        "spaceAbove": {"magnitude": space_before, "unit": "PT"},
                        "spaceBelow": {"magnitude": 4, "unit": "PT"},
                    },
                    "fields": "spaceAbove,spaceBelow",
                }
            }
            if target_tab_id:
                para_req["updateParagraphStyle"]["range"]["tabId"] = target_tab_id
            requests.append(para_req)

    if requests:
        _batch_execute(docs, doc_id, requests)


# --- Read Mode ---

def read_doc(doc_id: str, tab_id: str | None = None) -> str:
    """Read document content as plain text."""
    docs, _ = get_services()
    doc = docs.documents().get(documentId=doc_id, includeTabsContent=True).execute()

    if tab_id:
        body_content = _get_tab_content(doc, tab_id)
    else:
        tabs = doc.get("tabs", [])
        if tabs:
            body_content = tabs[0].get("documentTab", {}).get("body", {}).get("content", [])
        else:
            body_content = doc.get("body", {}).get("content", [])

    text_parts = []
    for elem in body_content:
        if "paragraph" in elem:
            for pe in elem["paragraph"].get("elements", []):
                text_parts.append(pe.get("textRun", {}).get("content", ""))

    return "".join(text_parts)


def list_tabs(doc_id: str) -> list[dict]:
    """List all tabs in a document. Returns [{id, title}]."""
    docs, _ = get_services()
    doc = docs.documents().get(documentId=doc_id, includeTabsContent=True).execute()

    tabs = []
    for tab in doc.get("tabs", []):
        props = tab.get("tabProperties", {})
        tabs.append({
            "id": props.get("tabId", ""),
            "title": props.get("title", "Untitled"),
        })
    return tabs


# --- Format/Clean Mode ---

def format_doc(doc_id: str, preset: str = "casual-notes", tab_id: str | None = None) -> dict:
    """Apply formatting cleanup to an existing document.

    Returns a summary of changes: {headings_fixed, patterns_bolded, ...}
    """
    docs, _ = get_services()
    style = PRESETS.get(preset, PRESETS["casual-notes"])

    doc = docs.documents().get(documentId=doc_id, includeTabsContent=True).execute()

    # With includeTabsContent=True, content lives under tabs
    if tab_id:
        body_content = _get_tab_content(doc, tab_id)
        target_tab_id = tab_id
    else:
        # Use first tab by default
        tabs = doc.get("tabs", [])
        if tabs:
            first_tab = tabs[0]
            target_tab_id = first_tab.get("tabProperties", {}).get("tabId")
            body_content = first_tab.get("documentTab", {}).get("body", {}).get("content", [])
        else:
            body_content = doc.get("body", {}).get("content", [])
            target_tab_id = None

    if not body_content:
        return {"headings_fixed": 0, "patterns_bolded": 0}

    requests = []
    headings_fixed = 0
    patterns_bolded = 0

    for elem in body_content:
        if "paragraph" not in elem:
            continue

        para = elem["paragraph"]
        para_style = para.get("paragraphStyle", {})
        named_style = para_style.get("namedStyleType", "NORMAL_TEXT")

        start = elem.get("startIndex", 0)
        end = elem.get("endIndex", start)
        if end - 1 <= start:
            continue

        # Apply font preset
        if named_style in ("HEADING_1", "TITLE"):
            target = style[f"h1"]
            headings_fixed += 1
        elif named_style == "HEADING_2":
            target = style["h2"]
            headings_fixed += 1
        elif named_style in ("HEADING_3", "HEADING_4"):
            target = style["h3"]
            headings_fixed += 1
        else:
            target = style["body"]

        text_style = {
            "weightedFontFamily": {"fontFamily": target["fontFamily"]},
            "fontSize": {"magnitude": target["fontSize"], "unit": "PT"},
        }
        fields = "weightedFontFamily,fontSize"

        req = {
            "updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end - 1},
                "textStyle": text_style,
                "fields": fields,
            }
        }
        if target_tab_id:
            req["updateTextStyle"]["range"]["tabId"] = target_tab_id
        requests.append(req)

        # Add spacing before headings
        if named_style in ("HEADING_1", "HEADING_2", "HEADING_3", "TITLE"):
            space_before = 12 if named_style in ("HEADING_1", "TITLE") else 8
            para_req = {
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end - 1},
                    "paragraphStyle": {
                        "spaceAbove": {"magnitude": space_before, "unit": "PT"},
                        "spaceBelow": {"magnitude": 4, "unit": "PT"},
                    },
                    "fields": "spaceAbove,spaceBelow",
                }
            }
            if target_tab_id:
                para_req["updateParagraphStyle"]["range"]["tabId"] = target_tab_id
            requests.append(para_req)

        # Auto-bold patterns
        full_text = ""
        for pe in para.get("elements", []):
            full_text += pe.get("textRun", {}).get("content", "")

        for pattern in style.get("bold_patterns", []):
            idx = full_text.find(pattern)
            if idx != -1:
                bold_start = start + idx
                bold_end = bold_start + len(pattern)
                if bold_end > bold_start:
                    bold_req = {
                        "updateTextStyle": {
                            "range": {"startIndex": bold_start, "endIndex": bold_end},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    }
                    if target_tab_id:
                        bold_req["updateTextStyle"]["range"]["tabId"] = target_tab_id
                    requests.append(bold_req)
                    patterns_bolded += 1

        # Auto-bold Jira keys
        for match in re.finditer(r"(RHOAIUX|RHAISTRAT|RHOAIENG)-\d+", full_text):
            jira_start = start + match.start()
            jira_end = start + match.end()
            if jira_end > jira_start:
                bold_req = {
                    "updateTextStyle": {
                        "range": {"startIndex": jira_start, "endIndex": jira_end},
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                }
                if target_tab_id:
                    bold_req["updateTextStyle"]["range"]["tabId"] = target_tab_id
            requests.append(bold_req)
            patterns_bolded += 1

    if requests:
        _batch_execute(docs, doc_id, requests)

    summary = {
        "headings_fixed": headings_fixed,
        "patterns_bolded": patterns_bolded,
        "total_requests": len(requests),
    }
    print(f"Formatted doc {doc_id}: {headings_fixed} headings, {patterns_bolded} patterns bolded")
    return summary


# --- Edit helpers ---

def insert_text(doc_id: str, text: str, index: int = 1, tab_id: str | None = None):
    """Insert text at a specific index in the document."""
    docs, _ = get_services()
    location = {"index": index}
    if tab_id:
        location["tabId"] = tab_id
    requests = [{"insertText": {"location": location, "text": text}}]
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


def bold_text(doc_id: str, start: int, end: int, tab_id: str | None = None):
    """Apply bold to a range of text."""
    docs, _ = get_services()
    range_obj = {"startIndex": start, "endIndex": end}
    if tab_id:
        range_obj["tabId"] = tab_id
    requests = [{
        "updateTextStyle": {
            "range": range_obj,
            "textStyle": {"bold": True},
            "fields": "bold",
        }
    }]
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


def find_text_index(doc_id: str, search_text: str, tab_id: str | None = None) -> int | None:
    """Find the character index of a text string in the document."""
    docs, _ = get_services()
    doc = docs.documents().get(documentId=doc_id, includeTabsContent=True).execute()

    if tab_id:
        body_content = _get_tab_content(doc, tab_id)
    else:
        body_content = doc.get("body", {}).get("content", [])

    running_text = ""
    index_map = []

    for elem in body_content:
        if "paragraph" in elem:
            for pe in elem["paragraph"].get("elements", []):
                content = pe.get("textRun", {}).get("content", "")
                start_idx = pe.get("startIndex", 0)
                for i, char in enumerate(content):
                    index_map.append(start_idx + i)
                running_text += content

    pos = running_text.find(search_text)
    if pos != -1 and pos < len(index_map):
        return index_map[pos]
    return None


# --- Internal helpers ---

def _get_tab_content(doc: dict, tab_id: str) -> list:
    """Get the body content for a specific tab."""
    for tab in doc.get("tabs", []):
        props = tab.get("tabProperties", {})
        if props.get("tabId") == tab_id:
            return tab.get("documentTab", {}).get("body", {}).get("content", [])
    return []


def _batch_execute(docs, doc_id: str, requests: list, chunk_size: int = 100):
    """Execute batch requests in chunks to avoid API limits."""
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i:i + chunk_size]
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": chunk}
        ).execute()


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Google Docs writer with typography presets")
    parser.add_argument("--setup", action="store_true", help="Run OAuth setup")

    subparsers = parser.add_subparsers(dest="command")

    create_p = subparsers.add_parser("create", help="Create a new document")
    create_p.add_argument("--title", required=True)
    create_p.add_argument("--preset", default="casual-notes", choices=PRESETS.keys())
    create_p.add_argument("--content-file", required=True, help="Path to markdown content")

    format_p = subparsers.add_parser("format", help="Format an existing document")
    format_p.add_argument("--doc-id", required=True)
    format_p.add_argument("--preset", default="casual-notes", choices=PRESETS.keys())
    format_p.add_argument("--tab-id", default=None)

    read_p = subparsers.add_parser("read", help="Read document content")
    read_p.add_argument("--doc-id", required=True)
    read_p.add_argument("--tab-id", default=None)

    tabs_p = subparsers.add_parser("tabs", help="List document tabs")
    tabs_p.add_argument("--doc-id", required=True)

    args = parser.parse_args()

    if args.setup:
        get_credentials(force_setup=True)
        return

    if args.command == "create":
        content = Path(args.content_file).read_text()
        create_doc(title=args.title, content_md=content, preset=args.preset)

    elif args.command == "format":
        doc_id = extract_doc_id(args.doc_id)
        format_doc(doc_id, preset=args.preset, tab_id=args.tab_id)

    elif args.command == "read":
        doc_id = extract_doc_id(args.doc_id)
        print(read_doc(doc_id, tab_id=args.tab_id))

    elif args.command == "tabs":
        doc_id = extract_doc_id(args.doc_id)
        for tab in list_tabs(doc_id):
            print(f"  {tab['id']}: {tab['title']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
