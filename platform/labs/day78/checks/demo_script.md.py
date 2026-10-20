import re
clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
scenes = [(m.group(1).strip(), int(m.group(2)) * 60 + int(m.group(3)), m.group(4)) for m in re.finditer(r"^## Scene \d+\s*[-–:]\s*(.+?)\s*\((\d+):(\d{2})\)\s*\n(.*?)(?=^## |\Z)", clean, re.M | re.S)]
total = lambda: sum(s for _, s, _ in scenes)
check("no TODO comments left", "TODO" not in src)
check("at least 5 scenes in the '## Scene N - Title (m:ss)' format", lambda: len(scenes) >= 5)
check("total between 3:00 and 5:00", lambda: 180 <= total() <= 300)
check("the first scene is a hook of 30 seconds or less", lambda: scenes[0][1] <= 30 and not re.search(r"my name is|je m'appelle|je suis \w+ et", scenes[0][2], re.I))
check("every scene says something and shows something (Screen:)", lambda: all(re.search(r"^Screen:\s*\S", body, re.M) and len(re.sub(r"^Screen:.*$", "", body, flags=re.M).split()) >= 8 for _, _, body in scenes))
text = lambda: "\n".join(b for _, _, b in scenes)
check("a question in Arabic script or Derja/Arabizi on screen", lambda: re.search(r"[؀-ۿ]", text()) or re.search(r"\b\w*[379]\w*\b", text()))
check("shows a source/citation, a confirmation and an 'I don't know'", lambda: re.search(r"source|citation|\[\d\]", text(), re.I) and re.search(r"confirm", text(), re.I) and re.search(r"don.t know|je ne sais pas|IDK", text(), re.I))
check("shows a number from the evaluation", lambda: re.search(r"\d?\.\d{2}\s*\[|\d+\s*%", text()))
check("no scene longer than 1:30", lambda: all(s <= 90 for _, s, _ in scenes))
