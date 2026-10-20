import re
P = var("PHONE")
ph = lambda s: bool(P) and [m.group() for m in re.finditer(P, s)]
check("PHONE matches +216 98 123 456, 98123456 and 00216 71.234.567", lambda: ph("tel +216 98 123 456") == ["+216 98 123 456"] and ph("98123456") == ["98123456"] and ph("x 00216 71.234.567 y") == ["00216 71.234.567"])
check("PHONE rejects a CIN (starts with 0/1) and a 9-digit number", lambda: ph("09876543") == [] and ph("981234567") == [])
C = var("CIN")
check("CIN matches 8 digits starting with 0 or 1, alone", lambda: bool(C) and re.findall(C, "CIN 09876543 et 12345678") == ["09876543", "12345678"] and re.findall(C, "123456789") == [])
fp = fn("find_pii")
text = "RIB 08006000123456789012, tel 98123456, mail a.b@x.tn, CIN 01234567"
check("find_pii finds the 4 kinds, sorted by position", lambda: [k for k, *_ in fp(text)] == ["RIB", "PHONE", "EMAIL", "CIN"])
check("no phone or CIN found inside the RIB", lambda: len(fp("RIB 08 006 0001234567890 12")) == 1)
sc = fn("scrub")
check("scrub masks with numbered placeholders", lambda: sc("call 98123456 or 22333444")[0] == "call [PHONE_1] or [PHONE_2]")
check("same value -> same placeholder", lambda: sc("98123456, again 98123456")[0] == "[PHONE_1], again [PHONE_1]")
def _shared():
    t1, m = sc("a 98123456")
    t2, m = sc("b 22333444 and 98123456", m)
    return t2 == "b [PHONE_2] and [PHONE_1]" and m["[PHONE_2]"] == "22333444"
check("the mapping is reused across documents", _shared)
sn = fn("scrub_names")
check("scrub_names: whole words, case-insensitive", lambda: (lambda t: t.count("[NAME_") == 2 and "Salmane no" in t and "alma said" not in t)(sn("salma said Salma; Salmane no", ["Salma"])[0]))
rs = fn("restore")
check("restore(scrub(x)) == x", lambda: (lambda t, m: rs(t, m))(*sc(text)) == text)
