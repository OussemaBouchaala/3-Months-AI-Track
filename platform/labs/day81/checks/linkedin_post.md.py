import re
text = re.sub(r"<!--.*?-->", "", src, flags=re.S).strip()
lines = [l for l in text.splitlines() if l.strip()]
check("no TODO comments left", "TODO" not in src)
check("between 600 and 1,800 characters (the 'see more' sweet spot)", lambda: 600 <= len(text) <= 1800)
check("the first line is a hook under 150 characters", lambda: lines and len(lines[0]) <= 150)
check("doesn't open with 'excited/thrilled/happy to announce' or a greeting", lambda: lines and not re.match(r"(i'?m |i am )?(so )?(excited|thrilled|happy|proud|delighted)|hello|hi everyone|bonjour", lines[0].strip(), re.I))
check("at least 3 numbers", lambda: len(re.findall(r"\d+(?:[.,]\d+)?\s*%?", text)) >= 3)
check("a link to the GitHub repository", lambda: re.search(r"https?://github\.com/[\w.-]+/[\w.-]+", text))
check("mentions what failed or what you learned", lambda: re.search(r"\b(learn(ed|t)?|lesson|fail(ed|ure)?|mistake|surpris\w*|didn't|wrong)\b", text, re.I))
check("1 to 5 hashtags", lambda: 1 <= len(re.findall(r"(?<!\w)#\w+", text)) <= 5)
check("short paragraphs (none over 400 characters)", lambda: all(len(p) <= 400 for p in re.split(r"\n\s*\n", text)))
check("no Markdown formatting (LinkedIn shows it raw)", lambda: not re.search(r"\*\*|^#{1,6} |\[[^\]]+\]\(http", text, re.M))
