#!/usr/bin/env python3
"""
Google Doc collaboration sync -- push drafts, pull comments, reply to comments.

All write operations require explicit confirmation via --confirm flag.
The skill should only pass --confirm after the user has approved the action.

Usage:
    gdoc_sync.py push <file> --title "Title" [--share email1 email2] [--confirm]
    gdoc_sync.py pull <file>
    gdoc_sync.py reply <file> --comment-id <id> --reply-text "response" [--confirm]
    gdoc_sync.py update <file> [--confirm]
    gdoc_sync.py status [<file>]
"""

import argparse
import json
import os
import sys
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

HOME = os.path.expanduser("~")
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINKS_FILE = os.path.join(WORKSPACE_ROOT, ".gdoc_links.json")


def _resolve_credential_dir():
    """Find OAuth credentials."""
    candidates = [
        (os.path.join(WORKSPACE_ROOT, "credentials"), "oauth_credentials.json"),
        (os.path.join(HOME, ".config", "google"), "credentials.json"),
        (os.path.join(HOME, ".config", "google"), "oauth_credentials.json"),
    ]
    env_dir = os.environ.get("GOOGLE_CREDENTIALS_DIR")
    if env_dir:
        expanded = os.path.expanduser(env_dir)
        candidates.insert(0, (expanded, "credentials.json"))
        candidates.insert(1, (expanded, "oauth_credentials.json"))

    for d, filename in candidates:
        if os.path.exists(os.path.join(d, filename)):
            return d, filename

    print("ERROR: No OAuth credentials found. Searched:")
    for d, f in candidates:
        print(f"  {os.path.join(d, f)}")
    print("\nSet GOOGLE_CREDENTIALS_DIR env var or place credentials in one of the above paths.")
    sys.exit(1)


CREDS_DIR, _OAUTH_FILENAME = _resolve_credential_dir()
CREDS_FILE = os.path.join(CREDS_DIR, _OAUTH_FILENAME)
TOKEN_FILE = os.path.join(CREDS_DIR, "token_docs_write.json")


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                print(f"ERROR: {CREDS_FILE} not found")
                print("Download OAuth credentials from Google Cloud Console")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE) as f:
            return json.load(f)
    return {}


def save_links(links):
    with open(LINKS_FILE, "w") as f:
        json.dump(links, f, indent=2)


def resolve_file_key(filepath):
    """Get a stable relative path key for tracking."""
    abs_path = os.path.abspath(filepath)
    if abs_path.startswith(WORKSPACE_ROOT):
        return os.path.relpath(abs_path, WORKSPACE_ROOT)
    return abs_path


def markdown_to_doc_requests(md_content):
    """Convert markdown to Google Docs API batchUpdate requests."""
    requests = []
    lines = md_content.split("\n")
    insert_index = 1

    for line in lines:
        heading_level = None
        text = line

        if line.startswith("# "):
            heading_level = "HEADING_1"
            text = line[2:].strip().replace("**", "")
        elif line.startswith("## "):
            heading_level = "HEADING_2"
            text = line[3:].strip()
        elif line.startswith("### "):
            heading_level = "HEADING_3"
            text = line[4:].strip()
        elif line.startswith("#### "):
            heading_level = "HEADING_4"
            text = line[5:].strip()

        text_to_insert = text + "\n"

        requests.append(
            {
                "insertText": {
                    "location": {"index": insert_index},
                    "text": text_to_insert,
                }
            }
        )

        if heading_level:
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": insert_index,
                            "endIndex": insert_index + len(text_to_insert),
                        },
                        "paragraphStyle": {"namedStyleType": heading_level},
                        "fields": "namedStyleType",
                    }
                }
            )

        if text.startswith("**") and ":**" in text:
            bold_end = text.index(":**") + 1
            bold_text = text[2:bold_end]
            requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": insert_index,
                            "endIndex": insert_index + len(bold_text),
                        },
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                }
            )

        insert_index += len(text_to_insert)

    return requests


def cmd_push(args):
    """Create a new Google Doc from a local markdown file."""
    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    with open(args.file) as f:
        content = f.read()

    file_key = resolve_file_key(args.file)
    links = load_links()

    if file_key in links:
        print(f"WARNING: This file is already linked to a Google Doc:")
        print(f"  Doc: {links[file_key]['url']}")
        print(f"  Use 'update' to push changes to the existing doc,")
        print(f"  or remove the entry from .gdoc_links.json to create a new one.")
        sys.exit(1)

    title = args.title or os.path.splitext(os.path.basename(args.file))[0]

    print("=" * 60)
    print(f"PUSH PREVIEW")
    print(f"  File:  {args.file}")
    print(f"  Title: {title}")
    if args.share:
        print(f"  Share with: {', '.join(args.share)}")
    print(f"  Content length: {len(content)} chars, {len(content.splitlines())} lines")
    print("=" * 60)

    if not args.confirm:
        print("\nDry run -- no changes made. Pass --confirm to execute.")
        return

    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    doc_requests = markdown_to_doc_requests(content)
    if doc_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": doc_requests}
        ).execute()

    if args.share:
        for email in args.share:
            drive_service.permissions().create(
                fileId=doc_id,
                body={
                    "type": "user",
                    "role": "commenter",
                    "emailAddress": email.strip(),
                },
                sendNotificationEmail=True,
            ).execute()
            print(f"  Shared with {email.strip()} (commenter)")

    links[file_key] = {
        "doc_id": doc_id,
        "url": doc_url,
        "title": title,
        "created": datetime.now().isoformat(),
        "shared_with": args.share or [],
    }
    save_links(links)

    print(f"\nCreated: {doc_url}")
    print(f"Tracked in .gdoc_links.json as: {file_key}")


def cmd_pull(args):
    """Pull comments from the linked Google Doc."""
    file_key = resolve_file_key(args.file)
    links = load_links()

    if file_key not in links:
        print(f"ERROR: No Google Doc linked to {args.file}")
        print("Use 'push' first to create a linked doc.")
        sys.exit(1)

    doc_id = links[file_key]["doc_id"]
    doc_url = links[file_key]["url"]
    title = links[file_key].get("title", "Untitled")

    creds = get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    comments_response = (
        drive_service.comments()
        .list(fileId=doc_id, fields="comments(*)", includeDeleted=False)
        .execute()
    )

    comments = comments_response.get("comments", [])

    if not comments:
        print(f"No comments on: {title}")
        print(f"Doc: {doc_url}")
        return

    open_count = sum(1 for c in comments if not c.get("resolved", False))
    resolved_count = sum(1 for c in comments if c.get("resolved", False))

    output_lines = [
        f"## Google Doc Comments",
        f"**Doc:** [{title}]({doc_url})",
        f"**Last synced:** {datetime.now().strftime('%Y-%m-%d %I:%M %p')}",
        f"**Open:** {open_count} | **Resolved:** {resolved_count}",
        "",
    ]

    for comment in comments:
        resolved = comment.get("resolved", False)
        author = comment.get("author", {}).get("displayName", "Unknown")
        content = comment.get("content", "")
        comment_id = comment.get("id", "")
        quoted_content = comment.get("quotedFileContent", {}).get("value", "")
        created = comment.get("createdTime", "")

        status_tag = " (resolved)" if resolved else ""
        output_lines.append(f"### Comment from {author}{status_tag}")
        output_lines.append(f"**Comment ID:** `{comment_id}`")

        if quoted_content:
            output_lines.append(f'**On:** "{quoted_content.strip()}"')

        output_lines.append(f"> {content}")

        replies = comment.get("replies", [])
        for reply in replies:
            reply_author = reply.get("author", {}).get("displayName", "Unknown")
            reply_content = reply.get("content", "")
            if reply_content:
                output_lines.append(f"> **{reply_author}:** {reply_content}")

        if not resolved:
            output_lines.append("")

        output_lines.append("")

    print("\n".join(output_lines))


def cmd_reply(args):
    """Reply to a specific comment on the linked Google Doc."""
    file_key = resolve_file_key(args.file)
    links = load_links()

    if file_key not in links:
        print(f"ERROR: No Google Doc linked to {args.file}")
        sys.exit(1)

    doc_id = links[file_key]["doc_id"]
    title = links[file_key].get("title", "Untitled")

    print("=" * 60)
    print("REPLY PREVIEW")
    print(f"  Doc:        {title}")
    print(f"  Comment ID: {args.comment_id}")
    print(f"  Reply:      {args.reply_text}")
    print("=" * 60)

    if not args.confirm:
        print("\nDry run -- no changes made. Pass --confirm to execute.")
        return

    creds = get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    drive_service.replies().create(
        fileId=doc_id,
        commentId=args.comment_id,
        fields="id,content,author",
        body={"content": args.reply_text},
    ).execute()

    print(f"\nReply posted to comment {args.comment_id}.")


def cmd_update(args):
    """Update an existing linked Google Doc with current file content."""
    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    file_key = resolve_file_key(args.file)
    links = load_links()

    if file_key not in links:
        print(f"ERROR: No Google Doc linked to {args.file}")
        print("Use 'push' first to create a linked doc.")
        sys.exit(1)

    with open(args.file) as f:
        content = f.read()

    doc_id = links[file_key]["doc_id"]
    title = links[file_key].get("title", "Untitled")
    doc_url = links[file_key]["url"]

    print("=" * 60)
    print("UPDATE PREVIEW")
    print(f"  File:  {args.file}")
    print(f"  Doc:   {title}")
    print(f"  URL:   {doc_url}")
    print(f"  Content length: {len(content)} chars, {len(content.splitlines())} lines")
    print(f"  WARNING: This replaces ALL content in the Google Doc.")
    print(f"           Existing comments will remain but may lose their anchors.")
    print("=" * 60)

    if not args.confirm:
        print("\nDry run -- no changes made. Pass --confirm to execute.")
        return

    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])
    if len(body_content) > 1:
        last_elem = body_content[-1]
        end_index = last_elem.get("endIndex", 1) - 1
        if end_index > 1:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {
                            "deleteContentRange": {
                                "range": {"startIndex": 1, "endIndex": end_index}
                            }
                        }
                    ]
                },
            ).execute()

    doc_requests = markdown_to_doc_requests(content)
    if doc_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": doc_requests}
        ).execute()

    links[file_key]["last_updated"] = datetime.now().isoformat()
    save_links(links)

    print(f"\nUpdated: {doc_url}")


def cmd_status(args):
    """Show all tracked Google Doc links and their comment counts."""
    links = load_links()

    if not links:
        print("No Google Docs are currently tracked.")
        print("Use 'push' to create a linked doc from a local file.")
        return

    file_filter = resolve_file_key(args.file) if args.file else None

    if file_filter and file_filter not in links:
        print(f"No Google Doc linked to: {args.file}")
        return

    items = {file_filter: links[file_filter]} if file_filter else links

    creds = None

    for file_key, info in items.items():
        print(f"\n{'=' * 60}")
        print(f"  File:    {file_key}")
        print(f"  Title:   {info.get('title', 'Untitled')}")
        print(f"  URL:     {info.get('url', 'N/A')}")
        print(f"  Created: {info.get('created', 'Unknown')}")

        shared = info.get("shared_with", [])
        if shared:
            print(f"  Shared:  {', '.join(shared)}")

        try:
            if creds is None:
                creds = get_credentials()
            drive_service = build("drive", "v3", credentials=creds)
            comments_response = (
                drive_service.comments()
                .list(
                    fileId=info["doc_id"],
                    fields="comments(id,resolved)",
                    includeDeleted=False,
                )
                .execute()
            )
            comments = comments_response.get("comments", [])
            open_c = sum(1 for c in comments if not c.get("resolved", False))
            resolved_c = sum(1 for c in comments if c.get("resolved", False))
            print(f"  Comments: {open_c} open, {resolved_c} resolved")
        except Exception as e:
            print(f"  Comments: (could not fetch: {e})")

    print(f"\n{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description="Google Doc collaboration sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    push_parser = subparsers.add_parser("push", help="Push a local file to a new Google Doc")
    push_parser.add_argument("file", help="Path to the markdown file")
    push_parser.add_argument("--title", help="Google Doc title (defaults to filename)")
    push_parser.add_argument(
        "--share",
        nargs="*",
        help="Email addresses to share with (as commenters)",
    )
    push_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually execute (without this flag, it's a dry run)",
    )

    pull_parser = subparsers.add_parser("pull", help="Pull comments from linked Google Doc")
    pull_parser.add_argument("file", help="Path to the local file linked to a Google Doc")

    reply_parser = subparsers.add_parser("reply", help="Reply to a comment on a Google Doc")
    reply_parser.add_argument("file", help="Path to the local file linked to a Google Doc")
    reply_parser.add_argument("--comment-id", required=True, help="The comment ID to reply to")
    reply_parser.add_argument("--reply-text", required=True, help="The reply text")
    reply_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually execute (without this flag, it's a dry run)",
    )

    update_parser = subparsers.add_parser("update", help="Update linked Google Doc with current file content")
    update_parser.add_argument("file", help="Path to the markdown file")
    update_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually execute (without this flag, it's a dry run)",
    )

    status_parser = subparsers.add_parser("status", help="Show tracked Google Docs and comment counts")
    status_parser.add_argument("file", nargs="?", help="Optional: show status for a specific file only")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "push": cmd_push,
        "pull": cmd_pull,
        "reply": cmd_reply,
        "update": cmd_update,
        "status": cmd_status,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
