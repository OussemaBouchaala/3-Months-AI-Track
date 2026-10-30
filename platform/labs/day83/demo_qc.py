"""You recorded the demo. Before publishing, check it like a reviewer would: length, pace,
filler words, and dead air while the app thinks.

The input is the video's subtitles (`.srt`): from YouTube Studio's auto-captions
(Subtitles -> Download), or from Whisper (`whisper demo.mp4 --output_format srt`).
An `.srt` file is blocks like this:

    2
    00:00:04,500 --> 00:00:08,000
    So I built an assistant.

1. `FILLERS` and `TIME`: the filler words, and the timestamp pattern.
2. `to_seconds` and `parse_srt`: read the subtitles.
3. `words_per_minute`, `count_fillers`, `long_pauses`: the measurements.
4. `verdict`: everything to fix before publishing.
"""
import re

FILLERS = ["euh", "heu", "um", "uh", "en fait", "genre", "du coup", "basically", "you know", "like", "يعني"]
TIME = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


def to_seconds(ts):
    """`"00:01:02,500"` -> 62.5. SRT uses a comma before the milliseconds;
    some tools write a dot, so both work.

    Example:
        >>> to_seconds("00:01:02,500"), to_seconds("01:00:00.250")
        (62.5, 3600.25)
    """
    h, m, s, ms = map(int, TIME.match(ts.strip()).groups())
    return h * 3600 + m * 60 + s + ms / 1000


def parse_srt(text):
    """The subtitles as `[{"index", "start", "end", "text"}]`.

    - Windows files use `\\r\\n` line endings and may start with a BOM
      (an invisible `\\ufeff`): normalize both first.
    - Blocks are separated by blank lines. A block must have an index, a
      `start --> end` line, and text (several lines joined with a space).
      A malformed block is skipped, not a crash.

    Example:
        >>> srt = "\\ufeff1\\r\\n00:00:00,000 --> 00:00:04,000\\r\\nRental agents answer forty\\r\\nquestions a day.\\r\\n\\r\\nbroken block\\r\\n"
        >>> parse_srt(srt)
        [{'index': 1, 'start': 0.0, 'end': 4.0, 'text': 'Rental agents answer forty questions a day.'}]
    """
    subs = []
    for block in re.split(r"\n\s*\n", text.lstrip("﻿").replace("\r\n", "\n").strip()):
        lines = block.strip().split("\n")
        if len(lines) < 3 or not lines[0].strip().isdigit() or "-->" not in lines[1]:
            continue
        start, end = lines[1].split("-->")
        subs.append({"index": int(lines[0]), "start": to_seconds(start), "end": to_seconds(end), "text": " ".join(l.strip() for l in lines[2:])})
    return subs


def words_per_minute(subs):
    """Speaking pace: words divided by the time subtitles are on screen
    (pauses excluded), per minute. 130-160 is comfortable to follow.

    Example (20 words in 9.5 seconds of speech):
        >>> words_per_minute([{"start": 0, "end": 4, "text": "w " * 7}, {"start": 4.5, "end": 8, "text": "w " * 8}, {"start": 13, "end": 15, "text": "w " * 5}])
        126
    """
    spoken = sum(s["end"] - s["start"] for s in subs)
    return round(sum(len(s["text"].split()) for s in subs) / spoken * 60) if spoken else 0


def count_fillers(subs, fillers=FILLERS):
    """How often each filler occurs, most frequent first (only those found).

    `(?<!\\w)` and `(?!\\w)` mean "no letter just before / after": a whole
    word or phrase, so "like" inside "likely" doesn't count. This works for
    Arabic too, where `\\b` is less reliable.

    Example:
        >>> count_fillers([{"text": "Euh, so I built, en fait, an assistant. It will likely work, like this, like that"}])
        {'like': 2, 'euh': 1, 'en fait': 1}
    """
    text = " ".join(s["text"] for s in subs).lower()
    counts = {f: len(re.findall(rf"(?<!\w){re.escape(f)}(?!\w)", text)) for f in fillers}
    return dict(sorted(((f, n) for f, n in counts.items() if n), key=lambda kv: -kv[1]))


def long_pauses(subs, min_gap=3.0):
    """Silences of `min_gap` seconds or more: `(index of the subtitle before, gap)`.

    `zip(subs, subs[1:])` pairs each subtitle with the next one. A long gap
    is usually you waiting for the model: cut it in editing, or talk over it.

    Example:
        >>> long_pauses([{"index": 1, "start": 0.0, "end": 4.0}, {"index": 2, "start": 4.5, "end": 8.0}, {"index": 3, "start": 13.0, "end": 15.0}])
        [(2, 5.0)]
    """
    return [(a["index"], round(b["start"] - a["end"], 1)) for a, b in zip(subs, subs[1:]) if b["start"] - a["end"] >= min_gap]


def verdict(subs):
    """Everything to fix before publishing (`[]` = ready).

    - Duration (the last subtitle's end) between 3:00 and 5:00.
    - Pace between 110 and 170 words per minute.
    - At most 3 fillers per minute.
    - No pause over 3 seconds.

    Example (60 subtitles of 9 words, 4 s each: 4:00 at 135 wpm):
        >>> good = [{"index": i, "start": 4.0 * i, "end": 4.0 * i + 4, "text": "word " * 9} for i in range(60)]
        >>> verdict(good)
        []
        >>> verdict(good + [{"index": 99, "start": 250, "end": 330, "text": "euh " * 40}])
        ['too long (5:30)', 'too slow (109 wpm)', 'too many fillers (7.3 per minute)', '1 pauses over 3 s']
    """
    if not subs:
        return ["no subtitles"]
    dur = subs[-1]["end"]
    out = []
    mmss = f"{int(dur) // 60}:{int(dur) % 60:02d}"
    if dur > 300:
        out.append(f"too long ({mmss})")
    elif dur < 180:
        out.append(f"too short ({mmss})")
    wpm = words_per_minute(subs)
    if wpm > 170:
        out.append(f"too fast ({wpm} wpm)")
    elif wpm < 110:
        out.append(f"too slow ({wpm} wpm)")
    per_min = sum(count_fillers(subs).values()) / (dur / 60)
    if per_min > 3:
        out.append(f"too many fillers ({per_min:.1f} per minute)")
    pauses = long_pauses(subs)
    if pauses:
        out.append(f"{len(pauses)} pauses over 3 s")
    return out


def report(text):
    """The full check of one .srt text, as printed lines.

    Example (note): reads your exported subtitles.
        >>> print(report(open("demo.srt", encoding="utf-8").read()))  # doctest: +SKIP
    """
    subs = parse_srt(text)
    return "\n".join([f"{len(subs)} subtitles, {words_per_minute(subs)} wpm, fillers: {count_fillers(subs)}",
                      f"pauses: {long_pauses(subs)}", "\n".join(verdict(subs)) or "Ready to publish."])


if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "demo.srt")
    if path.exists():
        print(report(path.read_text(encoding="utf-8")))
    else:
        # Demo: a first take (a long wait for the model, fillers), written as .srt text.
        lines = ["Rental agents answer about forty client questions a day.", "Euh, so I built, en fait, an assistant for them.",
                 "A client asks in Derja about the deposit, يعني the guarantee.", "I paste the question as is.",
                 "The answer comes back in Derja with its source.", "Um, the follow-up about pets works too, like, in context.",
                 "Booking a visit asks for a confirmation first.", "On 42 held-out questions it answers 86 percent correctly."]
        t, blocks = 0.0, []
        for i, line in enumerate(lines * 7, 1):
            gap = 6.0 if i % 8 == 5 else 0.4                     # waiting for the model every few lines
            blocks.append(f"{i}\n00:{int(t) // 60:02d}:{int(t) % 60:02d},000 --> 00:{int(t + 3.5) // 60:02d}:{int(t + 3.5) % 60:02d},500\n{line}")
            t += 4 + gap
        print("--- first take (no demo.srt next to this file yet)")
        print(report("\n\n".join(blocks)))
