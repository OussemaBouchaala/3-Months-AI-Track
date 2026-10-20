ts, fm = fn("to_seconds"), fn("fmt")
check("to_seconds", lambda: ts("1:05") == 65 and ts("0:20") == 20 and ts("45") == 45)
check("fmt, including negatives", lambda: fm(65) == "1:05" and fm(7) == "0:07" and fm(-7) == "-0:07" and fm(300) == "5:00")
ps = fn("parse_script")
MD = """# Demo
<!-- notes -->
## Scene 1 - Hook (0:20)
Forty questions a day, five minutes each.
Screen: WhatsApp
## Scene 2 – Live question (1:05)
<!-- say it slowly -->
I paste the Derja question and the answer comes back with its source.
Screen: the page
"""
check("parse_script: titles and planned seconds", lambda: [(s["title"], s["planned"]) for s in ps(MD)] == [("Hook", 20), ("Live question", 65)])
check("parse_script: spoken text without Screen: lines or comments", lambda: ps(MD)[0]["spoken"] == "Forty questions a day, five minutes each." and "slowly" not in ps(MD)[1]["spoken"] and "Screen" not in ps(MD)[1]["spoken"])
sp = fn("speaking_seconds")
check("speaking_seconds: words at wpm plus waits", lambda: approx(sp("one two three " * 10, wpm=120), 15) and approx(sp("a b", 120, waits=4), 5))
tl = fn("too_long")
long_scene = [{"title": "A", "planned": 10, "spoken": "word " * 30}, {"title": "B", "planned": 30, "spoken": "word " * 30}]
check("too_long flags scenes over their plan, with waits", lambda: tl(long_scene) == ["A"] and tl(long_scene, waits={"B": 20}) == ["A", "B"])
cp = fn("compare")
check("compare: per scene and total, signed differences", lambda: cp(ps(MD), [27, 60]) == ["Hook: planned 0:20, actual 0:27, +0:07", "Live question: planned 1:05, actual 1:00, -0:05", "TOTAL: planned 1:25, actual 1:27, +0:02"])
