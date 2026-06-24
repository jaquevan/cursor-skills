"""
Dispatches tasks from the Claw to target repos and manages the bidirectional
conversation between the Claw and repo agents via BRAIN_TASKS.md.

Usage:
  python3 scripts/dispatch_task.py <repo> <task_description> [--context "..."]
  python3 scripts/dispatch_task.py <repo> --reply <task_number> --reply-message "response"
  python3 scripts/dispatch_task.py <repo> --complete <task_number>
  python3 scripts/dispatch_task.py <repo> --list
  python3 scripts/dispatch_task.py --check-replies

BRAIN_TASKS.md lives in the repo root. Both the Claw and the repo agent
write into it using a conversation loop (Claw: / Agent: turns).
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

HEADER_TEMPLATE = """# Claw Tasks

Tasks and messages from the [Claw](../my-cursor-claw/) -- Evan's daily productivity system.
**Agents working in this repo:** check here on startup for pending tasks. You can
reply by appending `> **Agent:** your message` inside the task's blockquote.

---

"""


def resolve_repos_dir(cli_value: str | None) -> Path:
    if cli_value:
        return Path(os.path.expanduser(cli_value))
    return Path.home() / "Desktop"


def get_tasks_file(repo_name: str, repos_dir: Path) -> Path:
    repo_dir = repos_dir / repo_name
    if not repo_dir.is_dir():
        print(f"Error: repo '{repo_name}' not found at {repo_dir}", file=sys.stderr)
        sys.exit(1)
    return repo_dir / "BRAIN_TASKS.md"


def read_tasks(tasks_file: Path) -> list[dict]:
    """Parse BRAIN_TASKS.md into structured task list with conversation threads."""
    if not tasks_file.is_file():
        return []

    tasks = []
    current_task = None
    content = tasks_file.read_text()

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("- [ ] ") or stripped.startswith("- [x] "):
            completed = stripped.startswith("- [x] ")
            text = stripped[6:]
            current_task = {
                "text": text,
                "completed": completed,
                "thread": [],
            }
            tasks.append(current_task)
        elif stripped.startswith("> ") and current_task is not None:
            current_task["thread"].append(stripped[2:])
        elif stripped == ">" and current_task is not None:
            current_task["thread"].append("")
        elif stripped == "" and current_task is not None:
            current_task = None

    return tasks


def write_tasks(tasks_file: Path, tasks: list[dict]):
    """Write structured tasks back to BRAIN_TASKS.md."""
    lines = [HEADER_TEMPLATE]

    for task in tasks:
        checkbox = "[x]" if task["completed"] else "[ ]"
        lines.append(f"- {checkbox} {task['text']}")
        for thread_line in task.get("thread", []):
            if thread_line == "":
                lines.append(">")
            else:
                lines.append(f"> {thread_line}")
        lines.append("")

    tasks_file.write_text("\n".join(lines))


def last_speaker(task: dict) -> str | None:
    """Determine who spoke last in a task's thread."""
    for line in reversed(task.get("thread", [])):
        if line.startswith("**Agent:**"):
            return "agent"
        if line.startswith("**Claw:**") or line.startswith("*Dispatched"):
            return "claw"
    return None


def has_unread_agent_reply(task: dict) -> bool:
    """True if the agent replied and the Claw hasn't responded yet."""
    return last_speaker(task) == "agent"


def add_task(repo_name: str, description: str, repos_dir: Path, context: str = None):
    tasks_file = get_tasks_file(repo_name, repos_dir)
    tasks = read_tasks(tasks_file)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    thread = [
        f"**Claw:** {description}",
        f"*Dispatched on {timestamp}*",
    ]
    if context:
        thread.append(context)
    thread.append("")

    tasks.append({
        "text": description,
        "completed": False,
        "thread": thread,
    })
    write_tasks(tasks_file, tasks)
    print(f"Task added to {tasks_file}")
    print(f"  - [ ] {description}")


def reply_to_task(repo_name: str, task_number: int, message: str, repos_dir: Path):
    """Claw replies to an agent's message on a task."""
    tasks_file = get_tasks_file(repo_name, repos_dir)
    tasks = read_tasks(tasks_file)

    pending = [t for t in tasks if not t["completed"]]
    if task_number < 1 or task_number > len(pending):
        print(f"Error: task #{task_number} not found ({len(pending)} pending tasks)")
        sys.exit(1)

    target = pending[task_number - 1]
    target["thread"].append(f"**Claw:** {message}")
    target["thread"].append("")
    write_tasks(tasks_file, tasks)
    print(f"Replied to task in {repo_name}: {target['text']}")


def complete_task(repo_name: str, task_number: int, repos_dir: Path):
    tasks_file = get_tasks_file(repo_name, repos_dir)
    tasks = read_tasks(tasks_file)

    pending = [t for t in tasks if not t["completed"]]
    if task_number < 1 or task_number > len(pending):
        print(f"Error: task #{task_number} not found ({len(pending)} pending tasks)")
        sys.exit(1)

    target = pending[task_number - 1]
    target["completed"] = True
    write_tasks(tasks_file, tasks)
    print(f"Completed: {target['text']}")


def list_tasks(repo_name: str, repos_dir: Path):
    tasks_file = get_tasks_file(repo_name, repos_dir)
    tasks = read_tasks(tasks_file)

    if not tasks:
        print(f"No tasks in {repo_name}")
        return

    pending = [t for t in tasks if not t["completed"]]
    done = [t for t in tasks if t["completed"]]

    if pending:
        print(f"Pending ({len(pending)}):")
        for i, t in enumerate(pending, 1):
            unread = " ** UNREAD AGENT REPLY **" if has_unread_agent_reply(t) else ""
            print(f"  {i}. [ ] {t['text']}{unread}")
            for line in t.get("thread", []):
                if line:
                    print(f"       > {line}")
    if done:
        print(f"\nCompleted ({len(done)}):")
        for t in done:
            print(f"       [x] {t['text']}")


def check_all_replies(repos_dir: Path):
    """Scan all repos for BRAIN_TASKS.md files with unread agent replies."""
    found_any = False
    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        tasks_file = repo_dir / "BRAIN_TASKS.md"
        if not tasks_file.is_file():
            continue

        tasks = read_tasks(tasks_file)
        unread = [(i, t) for i, t in enumerate(tasks, 1) if has_unread_agent_reply(t)]

        if unread:
            found_any = True
            print(f"\n{'='*60}")
            print(f"  {repo_dir.name} -- {len(unread)} unread agent reply(s)")
            print(f"{'='*60}")
            for idx, task in unread:
                print(f"\n  Task #{idx}: {task['text']}")
                for line in task.get("thread", []):
                    if line:
                        print(f"    > {line}")

    if not found_any:
        print("No unread agent replies across any repos.")


def main():
    parser = argparse.ArgumentParser(description="Dispatch tasks to repos from the Claw")
    parser.add_argument("repo", nargs="?", help="Target repo name (folder under repos dir)")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--repos-dir", type=str, default=None,
                        help="Path to repos directory (default: ~/Desktop/)")
    parser.add_argument("--context", help="Additional context for the task")
    parser.add_argument("--reply", type=int, metavar="N", help="Reply to task #N")
    parser.add_argument("--reply-message", help="Claw's reply message (used with --reply)")
    parser.add_argument("--complete", type=int, metavar="N", help="Complete task #N")
    parser.add_argument("--list", action="store_true", help="List tasks")
    parser.add_argument("--check-replies", action="store_true", help="Check all repos for unread agent replies")

    args = parser.parse_args()
    repos_dir = resolve_repos_dir(args.repos_dir)

    if args.check_replies:
        check_all_replies(repos_dir)
    elif not args.repo:
        parser.print_help()
    elif args.list:
        list_tasks(args.repo, repos_dir)
    elif args.reply and args.reply_message:
        reply_to_task(args.repo, args.reply, args.reply_message, repos_dir)
    elif args.complete:
        complete_task(args.repo, args.complete, repos_dir)
    elif args.task:
        add_task(args.repo, args.task, repos_dir, args.context)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
