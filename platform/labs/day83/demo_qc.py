# You recorded the demo. Before publishing, check it like a reviewer would: length, pace, filler words,
# and dead air while the app thinks. Input: the video's subtitles (.srt), from YouTube Studio's auto-captions
# (Subtitles -> Download) or from Whisper (whisper demo.mp4 --output_format srt).
import re

FILLERS = ["euh", "heu", "um", "uh", "en fait", "genre", "du coup", "basically", "you know", "like", "يعني"]
TIME = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


def to_seconds(ts):
    """"00:01:02,500" -> 62.5 (comma or dot before the milliseconds)."""
    # TODO
    ...


def parse_srt(text):
    """Blocks separated by blank lines: an index line, "start --> end", then 1+ text lines.
    Return [{"index": int, "start": s, "end": s, "text": lines joined with a space}]. Skip malformed blocks.
    Handle Windows line endings and a BOM at the start."""
    # TODO
    ...


def words_per_minute(subs):
    """Total words / total time on screen of the subtitles (sum of end - start), per minute. Rounded to 0 decimals.
    Empty -> 0."""
    # TODO
    ...


def count_fillers(subs, fillers=FILLERS):
    """{filler: count} for fillers that occur (whole words/phrases, case-insensitive), most frequent first."""
    # TODO
    ...


def long_pauses(subs, min_gap=3.0):
    """[(index of the subtitle BEFORE the gap, gap rounded to 1 decimal)] where the next subtitle starts min_gap or more
    seconds after this one ends."""
    # TODO
    ...


def verdict(subs):
    """List of problems: "too long (5:20)" / "too short (2:40)" outside 3:00-5:00 (duration = last end);
    "too fast (182 wpm)" above 170, "too slow (98 wpm)" below 110; "too many fillers (5.2 per minute)" above 3 per
    minute of duration (1 decimal); "N pauses over 3 s" if any. [] = ready to publish."""
    # TODO
    ...


if __name__ == "__main__":
    import sys
    subs = parse_srt(open(sys.argv[1] if len(sys.argv) > 1 else "demo.srt", encoding="utf-8").read())
    print(len(subs), "subtitles,", words_per_minute(subs), "wpm, fillers:", count_fillers(subs))
    print("pauses:", long_pauses(subs))
    print("\n".join(verdict(subs)) or "Ready to publish.")
