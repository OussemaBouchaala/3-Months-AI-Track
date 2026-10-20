ts = fn("to_seconds")
check("to_seconds with comma or dot", lambda: ts("00:01:02,500") == 62.5 and ts("01:00:00.250") == 3600.25)
ps = fn("parse_srt")
SRT = "﻿1\r\n00:00:00,000 --> 00:00:04,000\r\nRental agents answer forty\r\nquestions a day.\r\n\r\n2\r\n00:00:04,500 --> 00:00:08,000\r\nEuh, so I built, en fait, an assistant.\r\n\r\nbroken block\r\n\r\n3\r\n00:00:13,000 --> 00:00:15,000\r\nIt answers يعني in Derja.\r\n"
check("parse_srt: blocks, times, multi-line text, CRLF and BOM", lambda: [(s["index"], s["start"], s["end"]) for s in ps(SRT)] == [(1, 0.0, 4.0), (2, 4.5, 8.0), (3, 13.0, 15.0)] and ps(SRT)[0]["text"] == "Rental agents answer forty questions a day.")
wp = fn("words_per_minute")
check("words per minute over time on screen", lambda: wp(ps(SRT)) == round(20 / 9.5 * 60) and wp([]) == 0)
cf = fn("count_fillers")
check("count_fillers: whole words and phrases, Arabic too", lambda: sorted(cf(ps(SRT)).items()) == [("en fait", 1), ("euh", 1), ("يعني", 1)])
check("'like' inside 'likely' is not a filler", lambda: cf([{"text": "It will likely work, like this, like that"}]) == {"like": 2})
lp = fn("long_pauses")
check("long_pauses: gaps of 3 s or more after a subtitle", lambda: lp(ps(SRT)) == [(2, 5.0)] and lp(ps(SRT), min_gap=6) == [])
vd = fn("verdict")
def subs(n, words, gap=0.0, dur=4.0, text=None):
    out, t = [], 0.0
    for i in range(n):
        out.append({"index": i + 1, "start": t, "end": t + dur, "text": text or " ".join(["word"] * words)})
        t += dur + gap
    return out
check("verdict: a good recording is ready", lambda: vd(subs(60, 9)) == [])
check("verdict: too long and too fast", lambda: vd(subs(90, 13)) == ["too long (6:00)", "too fast (195 wpm)"])
check("verdict: too short, too slow, fillers, pauses", lambda: vd(subs(20, 5, gap=3.5, text="euh um so we go")) == ["too short (2:26)", "too slow (75 wpm)", "too many fillers (16.4 per minute)", "19 pauses over 3 s"])
