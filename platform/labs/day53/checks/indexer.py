import hashlib, tempfile
from pathlib import Path
tmp = Path(tempfile.mkdtemp())
(tmp / "a.pdf").write_bytes(b"%PDF one")
(tmp / "b.txt").write_text("deux", encoding="utf-8")
(tmp / "c.xlsx").write_bytes(b"skip me")
fh = fn("file_hash")
check("file_hash is the sha256 of the bytes", lambda: fh(tmp / "a.pdf") == hashlib.sha256(b"%PDF one").hexdigest())
bm = fn("build_manifest")
check("build_manifest: matching files only, name -> hash", lambda: sorted(bm(tmp)) == ["a.pdf", "b.txt"] and bm(tmp)["b.txt"] == hashlib.sha256("deux".encode()).hexdigest())
pl = fn("plan")
old = {"a.pdf": "h1", "b.txt": "h2", "gone.pdf": "h3", "same.md": "h4"}
new = {"a.pdf": "h1x", "b.txt": "h2", "new.docx": "h5", "same.md": "h4", "aa.txt": "h6"}
check("plan: add, update, delete, unchanged", lambda: pl(old, new) == {"add": ["aa.txt", "new.docx"], "update": ["a.pdf"], "delete": ["gone.pdf"], "unchanged": 2})
check("plan from an empty manifest adds everything", lambda: pl({}, new)["add"] == sorted(new) and pl({}, new)["unchanged"] == 0)
bt = fn("batched")
check("batched: sizes 3,3,1 in order", lambda: list(bt(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]] and list(bt([], 3)) == [])
ap = fn("apply_plan")
log = []
def _run():
    log.clear()
    r = ap({"add": ["n1"], "update": ["u1"], "delete": ["d1"], "unchanged": 5}, lambda n: log.append(("del", n)), lambda n: (log.append(("idx", n)), 4)[1])
    return r
check("apply_plan returns counts", lambda: _run() == {"deleted": 2, "indexed": 2, "chunks": 8})
check("updated files are deleted before being re-indexed", lambda: (_run(), log.index(("del", "u1")) < log.index(("idx", "u1")))[1] and ("idx", "d1") not in log)
