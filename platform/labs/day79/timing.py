"""Most demos run long: people speak more slowly on camera, and the app takes 4 seconds to
answer, not 0.

Parse the demo script (day 78), estimate each scene's speaking time, and compare it with
real rehearsal laps from a stopwatch.

1. `LAPS` and `SCENE`: your stopwatch laps, and the pattern of a scene heading.
2. `to_seconds` and `fmt`: "1:05" <-> 65.
3. `parse_script`: the scenes, with their planned time and spoken text.
4. `speaking_seconds` and `too_long`: the estimate on paper.
5. `compare`: plan vs reality, scene by scene.
"""
import re

LAPS = []   # your rehearsal laps per scene, e.g. ["0:24", "0:51", "0:33", ...]
# "## Scene 2 - Live question (0:45)" then its text, up to the next "## " or the end.
SCENE = re.compile(r"^## Scene \d+\s*[-–:]\s*(.+?)\s*\((\d+):(\d{2})\)\s*\n(.*?)(?=^## |\Z)", re.M | re.S)


def to_seconds(mmss):
    """"1:05" -> 65. Plain seconds "45" work too.

    Example:
        >>> to_seconds("1:05"), to_seconds("0:20"), to_seconds("45")
        (65, 20, 45)
    """
    if ":" in mmss:
        m, s = mmss.split(":")
        return int(m) * 60 + int(s)
    return int(mmss)


def fmt(seconds):
    """65 -> "1:05". A negative difference keeps its sign: -7 -> "-0:07".
    `:02d` pads the seconds to two digits.

    Example:
        >>> fmt(65), fmt(7), fmt(-7), fmt(300)
        ('1:05', '0:07', '-0:07', '5:00')
    """
    sign = "-" if seconds < 0 else ""
    seconds = abs(int(round(seconds)))
    return f"{sign}{seconds // 60}:{seconds % 60:02d}"


def parse_script(md):
    """The scenes of a demo script: title, planned seconds, spoken text.

    HTML comments (your notes) and `Screen:` lines (what's shown, not said)
    are removed, so only the words you'll speak are counted. `re.M` makes
    `^` match at each line start; `re.S` lets `.` cross newlines.

    Example:
        >>> md = "## Scene 1 - Hook (0:20)\\nForty questions a day.\\nScreen: WhatsApp\\n## Scene 2 – Live (1:05)\\n<!-- slowly -->I paste it."
        >>> parse_script(md)
        [{'title': 'Hook', 'planned': 20, 'spoken': 'Forty questions a day.'}, {'title': 'Live', 'planned': 65, 'spoken': 'I paste it.'}]
    """
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out = []
    for m in SCENE.finditer(md):
        spoken = "\n".join(l for l in m.group(4).splitlines() if not l.strip().startswith("Screen:")).strip()
        out.append({"title": m.group(1), "planned": int(m.group(2)) * 60 + int(m.group(3)), "spoken": spoken})
    return out


def speaking_seconds(text, wpm=130, waits=0.0):
    """How long the text takes to say, plus the seconds you wait for the screen.

    130 words per minute is a calm demo pace (normal talk is 150+). `waits`
    is the time the app takes to answer on screen: you can't talk it away.

    Example:
        >>> speaking_seconds("one two three " * 10, wpm=120)
        15.0
        >>> speaking_seconds("a b", 120, waits=4)
        5.0
    """
    return len(text.split()) / wpm * 60 + waits


def too_long(scenes, wpm=130, waits=None):
    """The scenes whose estimate (with their waits) is over the plan.

    Example:
        >>> scenes = [{"title": "A", "planned": 10, "spoken": "word " * 30}, {"title": "B", "planned": 30, "spoken": "word " * 30}]
        >>> too_long(scenes), too_long(scenes, waits={"B": 20})
        (['A'], ['A', 'B'])
    """
    waits = waits or {}
    return [s["title"] for s in scenes if speaking_seconds(s["spoken"], wpm, waits.get(s["title"], 0)) > s["planned"]]


def compare(scenes, laps):
    """Plan vs stopwatch, one line per scene, then the total, with signed
    differences ("+0:07" over, "-0:05" under).

    Example:
        >>> scenes = [{"title": "Hook", "planned": 20}, {"title": "Live question", "planned": 65}]
        >>> print("\\n".join(compare(scenes, [27, 60])))
        Hook: planned 0:20, actual 0:27, +0:07
        Live question: planned 1:05, actual 1:00, -0:05
        TOTAL: planned 1:25, actual 1:27, +0:02
    """
    lines = []
    for s, lap in zip(scenes, laps):
        d = lap - s["planned"]
        lines.append(f"{s['title']}: planned {fmt(s['planned'])}, actual {fmt(lap)}, {'+' if d >= 0 else ''}{fmt(d)}")
    p, a = sum(s["planned"] for s in scenes), sum(laps)
    lines.append(f"TOTAL: planned {fmt(p)}, actual {fmt(a)}, {'+' if a - p >= 0 else ''}{fmt(a - p)}")
    return lines


if __name__ == "__main__":
    from pathlib import Path
    script = Path("../day78/demo_script.md")
    md = script.read_text(encoding="utf-8") if script.exists() else (
        "## Scene 1 - Hook (0:20)\nRental agents answer about 40 repeated client questions a day. I built an assistant that "
        "answers them in seconds, with the source.\n## Scene 2 - Live question in Derja (0:45)\nA client writes in Derja. "
        "I paste it as is. The answer comes back in Derja in four seconds, with its source.\n")
    scenes = parse_script(md)
    waits = {"Live question in Derja": 5, "Follow-up": 4}          # seconds the app takes to answer on screen
    for s in scenes:
        est = speaking_seconds(s["spoken"], waits=waits.get(s["title"], 0))
        print(f"{s['title'][:32]:32} planned {fmt(s['planned'])}  estimated {fmt(est)}")
    print("over time on paper:", too_long(scenes, waits=waits) or "none")
    laps = [to_seconds(x) for x in LAPS] or [s["planned"] + [7, -3, 12, 9, -2, 15, 4, 0][i % 8] for i, s in enumerate(scenes)]   # demos run long
    print("\n" + ("your laps:" if LAPS else "example laps (put your stopwatch laps in LAPS at the top):"))
    print("\n".join(compare(scenes, laps)))
