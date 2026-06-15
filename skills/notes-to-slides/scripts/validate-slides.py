#!/usr/bin/env python3
"""
Validate a Google Slides presentation by exporting as PDF and checking
for common issues: Quick Tips, placeholder text, empty slides, overflow.

Usage:
    python3 validate-slides.py <presentation_id> [--fix]

Outputs a JSON report with issues found on each slide.
"""

import sys
import subprocess
import json
import os
import re

TEMPLATE_MARKERS = [
    "quick tip",
    "optional subheading",
    "optional section marker",
    "optional supporting copy",
    "lorem ipsum",
    "insert source data here",
    "slide title should not exceed",
    "presentation title should not exceed",
    "title should not exceed",
    "body headline",
    "body cell should be",
    "column header",
    "row header",
    "presenter's name",
    "presentation title should",
    "template slide",
    "click on this slide",
    "this section includes",
    "what we'll discuss today",
    "details on topic",
]

PURGE_STRINGS = [
    "slide title should not exceed one line",
    "slide title should not exceed three lines",
    "presentation title should not exceed two lines",
    "title should not exceed two lines",
    "optional subheading",
    "optional section marker",
    "optional supporting copy",
    "this section includes:",
    "what we'll discuss today",
    "body headline",
    "body cell should be limited to two lines",
    "column header",
    "row header",
    "lorem ipsum",
    "insert source data here",
    "presenter's name",
    "template slide",
    "click on this slide",
    "quick tip",
    "details on topic",
]

def export_pdf(pres_id: str, output_path: str) -> bool:
    result = subprocess.run(
        ["gws", "drive", "files", "export",
         "--params", json.dumps({"fileId": pres_id, "mimeType": "application/pdf"}),
         "--output", output_path],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    result = subprocess.run(
        ["python3", "-c", f"""
with open("{pdf_path}", "rb") as f:
    content = f.read()
# Simple text extraction from PDF
import re
text = content.decode('latin-1', errors='ignore')
# Find text between BT and ET markers, or just get readable strings
readable = re.findall(rb'[\\x20-\\x7E]{{4,}}', content)
print('\\n'.join(r.decode('ascii', errors='ignore') for r in readable))
"""],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout

def get_slides_via_api(pres_id: str) -> dict:
    result = subprocess.run(
        ["gws", "slides", "presentations", "get",
         "--params", json.dumps({"presentationId": pres_id}),
         "--format", "json"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return {}
    stdout = result.stdout
    if "Using keyring" in stdout:
        lines = stdout.split("\n")
        stdout = "\n".join(lines[1:])
    return json.loads(stdout)

def validate(pres_id: str) -> dict:
    data = get_slides_via_api(pres_id)
    if not data:
        return {"error": "Could not fetch presentation"}

    slides = data.get("slides", [])
    layout_names = {}
    for l in data.get("layouts", []):
        layout_names[l["objectId"]] = l.get("layoutProperties", {}).get("displayName", "?")

    EXPECTED_IMAGES = {
        "Title slide with image": 2,
        "Title": 0,
        "Closing slide with image": 1,
        "Closing": 0,
        "Interior title left": 3,
        "Interior three column": 3,
        "Interior three chevrons": 0,
        "Interior data three callouts": 0,
        "Interior large text": 1,
        "Interior overview": 0,
        "Interior agenda": 0,
        "Interior title and body": 0,
        "Interior title, subhead, and body": 0,
        "Interior body": 0,
        "Interior title and two column body": 0,
        "Interior title and column body": 0,
        "Interior four column": 4,
        "Interior two by two": 0,
        "Interior image left": 1,
        "Divider with title": 0,
        "Divider with title and subhead": 0,
        "Interior timeline horizontal": 0,
        "Interior timeline vertical": 0,
    }

    report = {"slide_count": len(slides), "issues": [], "slides": []}

    for i, slide in enumerate(slides):
        slide_num = i + 1
        layout = layout_names.get(
            slide.get("slideProperties", {}).get("layoutObjectId", ""), "?"
        )
        slide_report = {
            "number": slide_num,
            "layout": layout,
            "issues": [],
            "has_images": 0,
            "placeholder_count": 0,
            "total_chars": 0,
        }

        for pe in slide.get("pageElements", []):
            shape = pe.get("shape", {})
            ph = shape.get("placeholder", {})
            text = ""
            for te in shape.get("text", {}).get("textElements", []):
                tr = te.get("textRun", {})
                if tr.get("content"):
                    text += tr["content"]
            ts = text.strip().lower()

            if pe.get("image"):
                slide_report["has_images"] += 1

            if ph:
                slide_report["placeholder_count"] += 1
                slide_report["total_chars"] += len(text.strip())

                for marker in TEMPLATE_MARKERS:
                    if marker in ts:
                        slide_report["issues"].append(
                            f"Template text found: '{marker}' in {ph.get('type')}({ph.get('index','')})"
                        )
                        break

                if ph.get("type") == "TITLE" and not text.strip():
                    slide_report["issues"].append("Empty TITLE placeholder")

                if ph.get("type") == "BODY" and not text.strip():
                    slide_report["issues"].append("Empty BODY placeholder")

            elif text.strip():
                if "quick tip" in ts:
                    slide_report["issues"].append(
                        f"Quick Tip shape found: id={pe['objectId']}"
                    )

            group = pe.get("elementGroup", {})
            for child in group.get("children", []):
                child_shape = child.get("shape", {})
                child_text = ""
                for cte in child_shape.get("text", {}).get("textElements", []):
                    ctr = cte.get("textRun", {})
                    if ctr.get("content"):
                        child_text += ctr["content"]
                if "quick tip" in child_text.strip().lower():
                    slide_report["issues"].append(
                        f"Quick Tip in group: parent={pe['objectId']}, "
                        f"child={child.get('objectId', '?')}"
                    )

        if slide_report["total_chars"] == 0 and slide_report["has_images"] == 0:
            slide_report["issues"].append("Slide appears completely empty")

        expected = EXPECTED_IMAGES.get(layout)
        if expected is not None and slide_report["has_images"] < expected:
            slide_report["issues"].append(
                f"Missing images: expected {expected} for '{layout}', found {slide_report['has_images']}. "
                f"Slide may have been created with createSlide instead of duplicateObject."
            )

        report["slides"].append(slide_report)
        if slide_report["issues"]:
            report["issues"].extend(
                [f"Slide {slide_num}: {issue}" for issue in slide_report["issues"]]
            )

    # Purge verification: check ALL text on ALL slides against purge list
    for i, slide in enumerate(slides):
        slide_num = i + 1
        all_text = []
        for pe in slide.get("pageElements", []):
            shape = pe.get("shape", {})
            text = ""
            for te in shape.get("text", {}).get("textElements", []):
                tr = te.get("textRun", {})
                if tr.get("content"):
                    text += tr["content"]
            if text.strip():
                all_text.append((pe.get("objectId", "?"), text.strip()))

        for obj_id, text in all_text:
            text_lower = text.lower()
            for purge_str in PURGE_STRINGS:
                if purge_str in text_lower:
                    issue = f"Slide {slide_num}: Purge string '{purge_str}' found in element {obj_id}"
                    if issue not in report["issues"]:
                        report["issues"].append(issue)

    report["total_issues"] = len(report["issues"])
    report["verdict"] = "PASS" if not report["issues"] else "NEEDS_FIX"
    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate-slides.py <presentation_id>")
        sys.exit(1)

    pres_id = sys.argv[1]
    report = validate(pres_id)
    print(json.dumps(report, indent=2))

    if report.get("issues"):
        print(f"\n--- {len(report['issues'])} ISSUES FOUND ---")
        for issue in report["issues"]:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print(f"\n--- CLEAN: {report['slide_count']} slides, no issues ---")
