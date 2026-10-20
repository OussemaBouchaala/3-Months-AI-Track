# Check the recording
**Topic:** parse the video's subtitles and measure length, speaking pace, filler words and dead air before publishing.

## Real example
Pace and fillers from a podcast transcript (different recording, same measures):

```python
import re
lines = [(0.0, 5.0, "So, um, today we talk about solar panels"), (5.5, 9.0, "and, um, whether they pay off in Tunisia."),
         (14.0, 17.0, "Basically yes, after six years.")]
words = sum(len(t.split()) for _, _, t in lines)
spoken = sum(e - s for s, e, _ in lines)
print(round(words / spoken * 60), "words per minute")
print("um:", sum(len(re.findall(r"\bum\b", t.lower())) for _, _, t in lines))
print("dead air:", [round(b[0] - a[1], 1) for a, b in zip(lines, lines[1:]) if b[0] - a[1] >= 3])
```

Five seconds of silence feels like forever in a video. It usually means you were waiting for the app: cut it in editing.

## Your mission
Record the demo (Saturday), get its subtitles, and fix what the numbers show before publishing.

## Steps
1. `to_seconds`, `parse_srt` (CRLF, BOM, broken blocks).
2. `words_per_minute`, `count_fillers` (whole words only), `long_pauses`.
3. `verdict`.
4. Record with OBS (free) at 1080p, upload unlisted to YouTube, download the auto-captions as .srt (or run Whisper). **Run** `python demo_qc.py demo.srt`. Re-record or cut until it prints "Ready to publish."

## Done when
**Check** passes and your recording passes `verdict`.
