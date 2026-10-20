from datetime import datetime, timedelta
aid = fn("action_id")
check("action_id: 16 hex, stable, depends on args", lambda: len(aid("t", {"a": 1})) == 16 and aid("t", {"a": 1, "b": 2}) == aid("t", {"b": 2, "a": 1}) and aid("t", {"a": 1}) != aid("t", {"a": 2}))
Args = var("BookVisitArgs")
pv = fn("preview")
good = {"listing_id": "L12", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"}
check("preview is a plain French sentence with day, date, time, client", lambda: pv("book_visit", Args(**good)) == "Réserver une visite du bien L12 le samedi 05/12 à 10:00 pour Amel (22123456).")
Desk = var("ActionDesk")
clock = {"t": datetime(2026, 12, 1, 9, 0)}
runs = []
def execute(tool, args):
    runs.append(args)
    if args["listing_id"] == "L99":
        raise RuntimeError("409 slot taken")
    return {"id": len(runs)}
mk = lambda: Desk(execute, now=lambda: clock["t"])
def _propose():
    d = mk()
    return d, d.propose("book_visit", good)
check("propose valid args -> needs_confirmation with id and preview", lambda: (lambda r: r["status"] == "needs_confirmation" and len(r["action_id"]) == 16 and r["preview"].startswith("Réserver"))(_propose()[1]))
check("propose: unknown tool and invalid args -> invalid with errors", lambda: mk().propose("delete_all", {}) == {"status": "invalid", "errors": ["unknown tool"]} and (lambda r: r["status"] == "invalid" and any(e.startswith("phone") for e in r["errors"]))(mk().propose("book_visit", dict(good, phone="call me"))))
def _once():
    runs.clear()
    d, p = _propose()
    a, b = d.confirm(p["action_id"]), d.confirm(p["action_id"])
    return a["status"] == "done" and b == {"status": "already_done", "result": a["result"]} and len(runs) == 1
check("confirm executes exactly once; a second click returns the same result", _once)
check("execute receives JSON-ready args (when as a string)", lambda: (_once(), isinstance(runs[0]["when"], str))[1])
check("confirm of an unknown id -> unknown, nothing executed", lambda: (runs.clear(), mk().confirm("nope"))[1] == {"status": "unknown"} and runs == [])
def _expired():
    d, p = _propose()
    clock["t"] += timedelta(minutes=11)
    try:
        return d.confirm(p["action_id"]) == {"status": "expired"} and d.confirm(p["action_id"]) == {"status": "unknown"}
    finally:
        clock["t"] -= timedelta(minutes=11)
check("after 10 minutes the pending action expires", _expired)
def _failed():
    d = mk()
    p = d.propose("book_visit", dict(good, listing_id="L99"))
    r = d.confirm(p["action_id"])
    return r["status"] == "failed" and "409" in r["error"] and p["action_id"] in d.pending
check("a failed execution stays pending for a retry", _failed)
def _audit():
    d, p = _propose()
    d.confirm(p["action_id"]); d.confirm(p["action_id"]); d.cancel("x")
    return [e["status"] for e in d.audit] == ["proposed", "done", "already_done"] and d.audit[0]["at"] == "2026-12-01T09:00:00"
check("the audit log records each outcome", _audit)
check("cancel removes a pending action", lambda: (lambda d, p: d.cancel(p["action_id"]) and d.confirm(p["action_id"]) == {"status": "unknown"})(*_propose()))
