cf = fn("chunk_fixed")
check("chunk_fixed('abcdefghij', 4, 1) -> ['abcd', 'defg', 'ghij']", lambda: cf("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"],
      "Start positions 0, 3, 6: step = size - overlap. Stop when a piece reaches the end.")
check("no overlap: plain slices", lambda: cf("abcdef", 2, 0) == ["ab", "cd", "ef"])
check("the last piece may be shorter", lambda: cf("abcdefgh", 4, 1) == ["abcd", "defg", "gh"])
check("text shorter than size -> one chunk", lambda: cf("hi", 400, 80) == ["hi"])
check("empty text -> []", lambda: cf("", 10, 2) == [])
check("neighbours share exactly `overlap` characters",
      lambda: all(a[-80:] == b[:80] for a, b in zip(cf("".join(str(i % 10) for i in range(1000)), 400, 80), cf("".join(str(i % 10) for i in range(1000)), 400, 80)[1:])))

md = "# Title\nintro\n\n## Fees\nBuyers pay 2%.\n\n## الضمان\nشهرين\n"
sbh = fn("split_by_heading")
check("split_by_heading finds each '## ' section", lambda: sbh(md) == [("Fees", "Buyers pay 2%."), ("الضمان", "شهرين")],
      "Ignore the part before the first '## '. Strip heading and body.")

cbh = fn("chunk_by_heading")
check("chunk_by_heading: one chunk per short section, ids c0, c1",
      lambda: [c["id"] for c in cbh(md)] == ["c0", "c1"] and cbh(md)[0]["heading"] == "Fees")
check("each chunk's text starts with its heading", lambda: cbh(md)[1]["text"].startswith("الضمان\n"))
big = "# T\n\n## Long\n" + ("word " * 300)
check("long sections are split with chunk_fixed", lambda: len(cbh(big, max_chars=600)) >= 3 and all(c["heading"] == "Long" for c in cbh(big, max_chars=600)))
check("no empty chunks", lambda: all(c["text"].strip() for c in cbh(big)))
