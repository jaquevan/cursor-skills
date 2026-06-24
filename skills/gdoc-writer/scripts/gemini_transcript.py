#!/usr/bin/env python3
"""Process Gemini meeting transcripts into structured JSON for gdoc_writer.

Usage:
    python3 gemini_transcript.py <transcript_file> [--output json|markdown]
    python3 gemini_transcript.py --help

Requires:
    GEMINI_API_KEY environment variable or ~/.config/gemini/api_key file
    pip install google-genai pydantic
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed.", file=sys.stderr)
    print("Install with: pip install google-genai", file=sys.stderr)
    sys.exit(1)


class ActionItem(BaseModel):
    owner: str
    task: str
    status: str  # "pending", "in_progress", "done"


class MeetingEntry(BaseModel):
    date: str
    title: str
    attendees: list[str]
    summary: str
    decisions: list[str]
    action_items: list[ActionItem]
    key_points: list[str]
    topics_discussed: list[str]


EXTRACTION_PROMPT = """\
You are a meeting transcript analyzer. Extract structured information from the following meeting transcript.

Instructions:
- Extract attendees from the transcript header and speaker labels
- Summarize the meeting in 2-3 concise sentences
- List all decisions made (both firmly aligned and tentative)
- Extract action items with the responsible person (owner) and their task; set status to "pending" unless explicitly marked otherwise
- List key discussion points that capture the important substance
- List all topics that were discussed

If the date is present in the transcript, use it. Otherwise use today's date.
If you cannot determine a meeting title, infer one from the primary topics discussed.

Transcript:
{transcript}
"""


def get_api_key(verbose: bool = False) -> str:
    """Retrieve the Gemini API key from env var or config file."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        if verbose:
            print("Using API key from GEMINI_API_KEY env var", file=sys.stderr)
        return key

    config_path = Path.home() / ".config" / "gemini" / "api_key"
    if config_path.exists():
        key = config_path.read_text().strip()
        if key:
            if verbose:
                print(f"Using API key from {config_path}", file=sys.stderr)
            return key

    print("Error: No Gemini API key found.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Set one of:", file=sys.stderr)
    print("  1. Export GEMINI_API_KEY environment variable", file=sys.stderr)
    print("  2. Save key to ~/.config/gemini/api_key", file=sys.stderr)
    print("", file=sys.stderr)
    print("To get a key at Red Hat, visit the Source page for Gemini API access:", file=sys.stderr)
    print("  https://docs.example.com/ai-community", file=sys.stderr)
    sys.exit(1)


def read_transcript(file_path: str) -> str:
    """Read and return the transcript file contents."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def chunk_transcript(text: str, max_chars: int = 900_000) -> list[str]:
    """Split a transcript into chunks if it exceeds max size.

    Splits on double-newlines (paragraph boundaries) to avoid cutting mid-sentence.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def process_transcript(
    transcript: str, model_name: str, api_key: str, verbose: bool = False
) -> MeetingEntry:
    """Send transcript to Gemini API and return structured meeting data."""
    client = genai.Client(api_key=api_key)

    chunks = chunk_transcript(transcript)
    if verbose and len(chunks) > 1:
        print(f"Transcript split into {len(chunks)} chunks", file=sys.stderr)

    if len(chunks) == 1:
        prompt = EXTRACTION_PROMPT.format(transcript=chunks[0])
    else:
        combined_results = []
        for i, chunk in enumerate(chunks):
            if verbose:
                print(f"Processing chunk {i + 1}/{len(chunks)}...", file=sys.stderr)
            chunk_prompt = EXTRACTION_PROMPT.format(transcript=chunk)
            response = client.models.generate_content(
                model=model_name,
                contents=chunk_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MeetingEntry,
                ),
            )
            combined_results.append(json.loads(response.text))

        merge_prompt = (
            "Merge these partial meeting extractions into a single coherent meeting entry. "
            "Deduplicate attendees, combine summaries into one 2-3 sentence summary, "
            "merge decisions and action items (deduplicating), and consolidate key points.\n\n"
            f"{json.dumps(combined_results, indent=2)}"
        )
        prompt = merge_prompt

    if verbose:
        print(f"Calling {model_name}...", file=sys.stderr)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MeetingEntry,
        ),
    )

    return MeetingEntry.model_validate_json(response.text)


def format_markdown(entry: MeetingEntry) -> str:
    """Format a MeetingEntry as markdown matching the Daily Progress tab format."""
    try:
        dt = datetime.strptime(entry.date, "%Y-%m-%d")
        day_of_week = dt.strftime("%A")
        date_header = f"## {entry.date} {day_of_week}"
    except ValueError:
        date_header = f"## {entry.date}"

    lines = [
        date_header,
        "",
        f"**Meeting:** {entry.title}",
        f"**Attendees:** {', '.join(entry.attendees)}",
        "",
        "### Summary",
        entry.summary,
        "",
        "### Decisions",
    ]

    if entry.decisions:
        for decision in entry.decisions:
            lines.append(f"* {decision}")
    else:
        lines.append("* No explicit decisions recorded")

    lines.extend(["", "### Action Items"])

    if entry.action_items:
        for item in entry.action_items:
            lines.append(f"* {item.owner}: {item.task} ({item.status})")
    else:
        lines.append("* No action items identified")

    lines.extend(["", "### Key Points"])

    if entry.key_points:
        for point in entry.key_points:
            lines.append(f"* {point}")
    else:
        lines.append("* None extracted")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Process Gemini meeting transcripts into structured JSON or markdown."
    )
    parser.add_argument("transcript_file", help="Path to the transcript file")
    parser.add_argument(
        "--output",
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use (default: gemini-2.5-flash)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print debug info to stderr"
    )
    args = parser.parse_args()

    api_key = get_api_key(verbose=args.verbose)
    transcript = read_transcript(args.transcript_file)

    if args.verbose:
        print(f"Transcript length: {len(transcript)} chars", file=sys.stderr)

    try:
        entry = process_transcript(
            transcript, model_name=args.model, api_key=api_key, verbose=args.verbose
        )
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    if args.output == "json":
        print(entry.model_dump_json(indent=2))
    else:
        print(format_markdown(entry))


if __name__ == "__main__":
    main()
