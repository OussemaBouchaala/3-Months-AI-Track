pe = fn("parse_env_file")
text = '# comment\n\nexport DATABASE_URL = "postgresql://u:p@db:5432/rag"\nTOP_K=8\nLLM_API_KEY=\'sk-abc123456789\'\nbroken line\nEMPTY=\n'
check("parse_env_file: comments, export, spaces, quotes", lambda: pe(text) == {"DATABASE_URL": "postgresql://u:p@db:5432/rag", "TOP_K": "8", "LLM_API_KEY": "sk-abc123456789", "EMPTY": ""})
check("an = inside the value is kept", lambda: pe("URL=a=b") == {"URL": "a=b"})
co = fn("coerce")
check("coerce: int, float, str", lambda: co("8", int) == 8 and co("2.5", float) == 2.5 and co(" x ", str) == " x ")
def _bool_err():
    try:
        co("maybe", bool)
    except ValueError:
        return True
    return False
check("coerce: booleans, strict", lambda: co("Yes", bool) is True and co("0", bool) is False and co("OFF", bool) is False and _bool_err())
check("coerce: comma lists", lambda: co(" http://a , http://b,, ", list) == ["http://a", "http://b"] and co("", list) == [])
ls = fn("load_settings")
check("precedence: environment > .env > default", lambda: (lambda s: s["TOP_K"] == 3 and s["DATABASE_URL"].startswith("postgresql://u") and s["RERANK"] is True and s["MAX_LATENCY_S"] == 10.0)(ls({"TOP_K": "3"}, text)))
def _errors():
    try:
        ls({"TOP_K": "five", "RERANK": "maybe"}, "")
    except ValueError as e:
        m = str(e)
        return "DATABASE_URL is required" in m and "TOP_K" in m and "RERANK" in m
    return False
check("all problems reported at once", _errors)
rd = fn("redacted")
s = {"DATABASE_URL": "postgresql://u:secret@db:5432/rag", "LLM_API_KEY": "short", "TOP_K": 5}
check("redacted hides secrets, keeps the last 4 chars of long ones", lambda: rd(s) == {"DATABASE_URL": "***/rag", "LLM_API_KEY": "***", "TOP_K": 5})
check("empty secrets stay empty", lambda: rd({"LLM_API_KEY": ""})["LLM_API_KEY"] == "")
