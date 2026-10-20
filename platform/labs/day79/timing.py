# Most demos run long: people speak more slowly on camera, and the app takes 4 s to answer, not 0.
# Parse the script, estimate each scene's speaking time, and compare with real rehearsal laps.
import re

LAPS = []   # your rehearsal laps per scene, e.g. ["0:24", "0:51", "0:33", ...]
SCENE = re.compile(r"^## Scene \d+\s*[-–:]\s*(.+?)\s*\((\d+):(\d{2})\)\s*\n(.*?)(?=^## |\Z)", re.M | re.S)


def to_seconds(mmss):
    """"1:05" -> 65. Also accepts plain seconds "45" -> 45."""
    # TODO
    ...


def fmt(seconds):
    """65 -> "1:05"; negative values keep the sign: -7 -> "-0:07"."""
    # TODO
    ...


def parse_script(md):
    """[{"title", "planned": seconds, "spoken": the scene text without HTML comments and without "Screen:" lines}]"""
    # TODO
    ...


def speaking_seconds(text, wpm=130, waits=0.0):
    """Words / wpm * 60 plus waits (seconds the screen needs, e.g. the model answering). 130 wpm is a calm demo pace."""
    # TODO
    ...


def too_long(scenes, wpm=130, waits=None):
    """Titles of scenes whose estimated speaking time (with waits.get(title, 0)) exceeds the planned time."""
    # TODO
    ...


def compare(scenes, laps):
    """laps: real rehearsal durations per scene, in seconds, same order. Return lines
    "<title>: planned 0:20, actual 0:27, +0:07" and a last line "TOTAL: planned 3:45, actual 4:10, +0:25"."""
    # TODO
    ...


if __name__ == "__main__":
    scenes = parse_script(open("../day78/demo_script.md", encoding="utf-8").read())
    waits = {"Live question in Derja": 5, "Follow-up": 4}          # seconds the app takes to answer on screen
    print("over time on paper:", too_long(scenes, waits=waits) or "none")
    if LAPS:
        print("\n".join(compare(scenes, [to_seconds(x) for x in LAPS])))
    else:
        print("Rehearse with a stopwatch, put your laps in LAPS at the top, and run again.")
