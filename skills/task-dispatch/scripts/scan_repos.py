"""
Scans ~/Desktop/ for recent activity across four sources:
  1. Git commit history
  2. Claude Code session logs (~/.claude/projects/)
  3. Cursor agent transcripts (~/.cursor/projects/)
  4. BRAIN_TASKS.md files with pending tasks and unread agent replies

Outputs a markdown summary suitable for inclusion in a daily briefing.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

CC_PROJECTS_DIR = Path.home() / ".claude" / "projects"
CURSOR_PROJECTS_DIR = Path.home() / ".cursor" / "projects"

DEFAULT_DAYS = 7
CURSOR_PROJECT_PREFIX = "Users-<YOUR_USERNAME>-Desktop-"


def resolve_repos_dir(cli_value: str | None) -> Path:
    if cli_value:
        return Path(os.path.expanduser(cli_value))
    return Path.home() / "Desktop"


def get_git_activity(repos_dir: Path, days: int) -> list[dict]:
    """Get recent git commits across all repos."""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    results = []

    for repo_dir in sorted(repos_dir.iterdir()):
        git_dir = repo_dir / ".git"
        if not git_dir.is_dir():
            continue

        try:
            output = subprocess.check_output(
                [
                    "git", "-C", str(repo_dir), "log",
                    "--oneline", "--all", f"--since={since}",
                    "--format=%H|%ai|%s"
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except subprocess.CalledProcessError:
            continue

        if not output:
            continue

        commits = []
        for line in output.splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({
                    "hash": parts[0][:8],
                    "date": parts[1][:10],
                    "message": parts[2],
                })

        if commits:
            results.append({
                "repo": repo_dir.name,
                "path": str(repo_dir),
                "commits": commits,
            })

    return results


def parse_cc_sessions(repos_dir: Path, days: int) -> list[dict]:
    """Parse Claude Code session logs for recent conversations."""
    if not CC_PROJECTS_DIR.is_dir():
        return []

    cutoff = datetime.now().timestamp() - (days * 86400)
    results = []

    for project_dir in sorted(CC_PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        project_name = project_dir.name
        for prefix in ["-Users-<YOUR_USERNAME>-Desktop-", "-Users-<YOUR_USERNAME>-repos-"]:
            if prefix in project_name:
                project_name = project_name.split(prefix, 1)[1]
                break

        for jsonl_file in project_dir.glob("*.jsonl"):
            if jsonl_file.stat().st_mtime < cutoff:
                continue

            session_info = _extract_session_summary(jsonl_file)
            if session_info:
                session_info["project"] = project_name
                results.append(session_info)

    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return results


def parse_cursor_transcripts(repos_dir: Path, days: int) -> list[dict]:
    """Parse Cursor agent transcripts for recent conversations."""
    if not CURSOR_PROJECTS_DIR.is_dir():
        return []

    cutoff = datetime.now().timestamp() - (days * 86400)
    results = []

    for project_dir in sorted(CURSOR_PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        project_name = project_dir.name
        if not project_name.startswith(CURSOR_PROJECT_PREFIX):
            for prefix in ["Users-<YOUR_USERNAME>-", "Users-<YOUR_USERNAME>-repos-"]:
                if project_name.startswith(prefix):
                    project_name = project_name[len(prefix):]
                    break
        else:
            project_name = project_name[len(CURSOR_PROJECT_PREFIX):]

        transcripts_dir = project_dir / "agent-transcripts"
        if not transcripts_dir.is_dir():
            continue

        for session_dir in transcripts_dir.iterdir():
            if not session_dir.is_dir():
                continue

            for jsonl_file in session_dir.glob("*.jsonl"):
                if jsonl_file.stat().st_mtime < cutoff:
                    continue

                session_info = _extract_session_summary(jsonl_file)
                if session_info:
                    session_info["project"] = project_name
                    session_info["source"] = "cursor"
                    results.append(session_info)

    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return results


def _extract_session_summary(jsonl_path: Path) -> dict | None:
    """Extract the first user prompt and timestamp from a JSONL session file."""
    try:
        mtime = jsonl_path.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)

        first_user_prompt = None
        with open(jsonl_path) as f:
            for line in f:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                role = data.get("role") or data.get("type")
                if role != "user":
                    continue

                msg = data.get("message", data)
                content = msg.get("content", "")

                if isinstance(content, list):
                    texts = [
                        c.get("text", "")
                        for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    ]
                    text = " ".join(texts)
                else:
                    text = str(content)

                text = text.strip()
                for tag in ["<user_query>", "</user_query>", "<local-command-caveat>"]:
                    text = text.replace(tag, "")
                text = text.strip()

                if len(text) > 10:
                    first_user_prompt = text[:300]
                    break

        if not first_user_prompt:
            return None

        return {
            "timestamp": mtime,
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M"),
            "prompt": first_user_prompt,
            "source": "claude-code",
            "file": str(jsonl_path),
        }
    except Exception:
        return None


def check_brain_tasks(repos_dir: Path) -> list[dict]:
    """Check for BRAIN_TASKS.md files across repos, including unread agent replies."""
    results = []
    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        tasks_file = repo_dir / "BRAIN_TASKS.md"
        if not tasks_file.is_file():
            continue

        try:
            content = tasks_file.read_text().strip()
            if not content:
                continue

            tasks = _parse_tasks_with_threads(content)
            pending = [t for t in tasks if not t["completed"]]
            needs_reply = [t for t in tasks if _has_unread_agent_reply(t)]

            if pending or needs_reply:
                results.append({
                    "repo": repo_dir.name,
                    "path": str(tasks_file),
                    "pending_tasks": [t["text"] for t in pending],
                    "needs_reply": needs_reply,
                })
        except Exception:
            continue
    return results


def _parse_tasks_with_threads(content: str) -> list[dict]:
    """Parse BRAIN_TASKS.md content into tasks with conversation threads."""
    tasks = []
    current_task = None

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ] ") or stripped.startswith("- [x] "):
            completed = stripped.startswith("- [x] ")
            current_task = {
                "text": stripped[6:],
                "completed": completed,
                "thread": [],
            }
            tasks.append(current_task)
        elif (stripped.startswith("> ") or stripped == ">") and current_task is not None:
            current_task["thread"].append(stripped[2:] if stripped.startswith("> ") else "")
        elif stripped == "" and current_task is not None:
            current_task = None

    return tasks


def _has_unread_agent_reply(task: dict) -> bool:
    """True if the last substantive message in the thread is from Agent."""
    for line in reversed(task.get("thread", [])):
        if line.startswith("**Agent:**"):
            return True
        if line.startswith("**Claw:**") or line.startswith("*Dispatched"):
            return False
    return False


def format_markdown(
    git_activity: list[dict],
    cc_sessions: list[dict],
    cursor_sessions: list[dict],
    brain_tasks: list[dict],
    days: int,
) -> str:
    """Format all activity into a markdown section."""
    lines = [f"## Project Activity (last {days} days)\n"]

    repos_with_replies = [item for item in brain_tasks if item.get("needs_reply")]
    if repos_with_replies:
        lines.append("### Agent Replies (need response)\n")
        for item in repos_with_replies:
            lines.append(f"**{item['repo']}**")
            for task in item["needs_reply"]:
                lines.append(f"- **Task:** {task['text']}")
                for thread_line in task["thread"]:
                    if thread_line:
                        lines.append(f"  > {thread_line}")
            lines.append("")
        lines.append("")

    if brain_tasks:
        lines.append("### Dispatched Tasks (pending in repos)\n")
        for item in brain_tasks:
            reply_flag = " -- **has agent reply**" if item.get("needs_reply") else ""
            lines.append(f"**{item['repo']}**{reply_flag} (`{item['path']}`)")
            for task in item["pending_tasks"]:
                lines.append(f"- [ ] {task}")
            lines.append("")
        lines.append("")

    all_sessions = cc_sessions + cursor_sessions
    if all_sessions:
        all_sessions.sort(key=lambda x: x["timestamp"], reverse=True)
        lines.append("### Agent Sessions\n")
        lines.append("| Date | Repo | Tool | What was happening |")
        lines.append("|------|------|------|--------------------|")
        for s in all_sessions[:20]:
            tool = "CC" if s["source"] == "claude-code" else "Cursor"
            prompt = s["prompt"][:100].replace("|", "/").replace("\n", " ")
            lines.append(f"| {s['date']} | {s['project']} | {tool} | {prompt} |")
        lines.append("")

    if git_activity:
        lines.append("### Git Commits\n")
        for repo_info in git_activity:
            lines.append(f"**{repo_info['repo']}**")
            for c in repo_info["commits"][:5]:
                lines.append(f"- `{c['hash']}` {c['message']} ({c['date']})")
            if len(repo_info["commits"]) > 5:
                lines.append(f"- ... and {len(repo_info['commits']) - 5} more")
            lines.append("")

    if not git_activity and not all_sessions and not brain_tasks:
        lines.append("*No recent activity detected across repos.*\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan repos for recent activity")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Number of days to look back")
    parser.add_argument("--repos-dir", type=str, default=None,
                        help="Path to repos directory (default: ~/Desktop/)")
    args = parser.parse_args()

    repos_dir = resolve_repos_dir(args.repos_dir)

    if not repos_dir.is_dir():
        print(f"Repos directory not found: {repos_dir}", file=sys.stderr)
        sys.exit(1)

    git_activity = get_git_activity(repos_dir, args.days)
    cc_sessions = parse_cc_sessions(repos_dir, args.days)
    cursor_sessions = parse_cursor_transcripts(repos_dir, args.days)
    brain_tasks = check_brain_tasks(repos_dir)

    output = format_markdown(git_activity, cc_sessions, cursor_sessions, brain_tasks, args.days)
    print(output)


if __name__ == "__main__":
    main()
