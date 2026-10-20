"""Loads exercises from labs/<day folder>/.

    labs/day01/defaults.py           starter code shown in the editor
    labs/day01/briefs/defaults.py.md guided description shown beside the editor (optional)
    labs/day01/checks/defaults.py    check script run by the Check button (optional)

A brief starts with "# Title"; the rest is Markdown. Non-Python files keep their
name and get `.py` added for the check (labs/day13/checks/Dockerfile.py).
For briefs, both briefs/<stem>.md and briefs/<name>.md are accepted.
"""
from pathlib import Path

LABS = Path(__file__).resolve().parent / "labs"


def check_path(folder: str, name: str) -> Path:
    return LABS / folder / "checks" / (name if name.endswith(".py") else name + ".py")


def brief_path(folder: str, name: str) -> Path:
    stem = LABS / folder / "briefs" / (Path(name).stem + ".md")
    full = LABS / folder / "briefs" / (name + ".md")
    return full if full.exists() or not name.endswith(".py") else stem


def lab(folder: str, name: str, task=None) -> dict:
    """One exercise of a day.

    task: index (or list of indexes) of the day's tasks that this exercise completes
    once all of its checks pass.
    """
    brief, title = "", name
    path = brief_path(folder, name)
    if path.exists():
        text = path.read_text(encoding="utf-8").strip()
        first, _, rest = text.partition("\n")
        if first.startswith("# "):
            title, brief = first[2:].strip(), rest.strip()
        else:
            brief = text
    tasks = [] if task is None else [task] if isinstance(task, int) else list(task)
    return {
        "name": name,
        "title": title,
        "brief": brief,
        "starter": (LABS / folder / name).read_text(encoding="utf-8"),
        "has_check": check_path(folder, name).exists(),
        "tasks": tasks,
    }
