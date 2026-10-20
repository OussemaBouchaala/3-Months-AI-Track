from datetime import datetime, timedelta

from fastapi.testclient import TestClient

VisitIn, rules = var("VisitIn"), fn("check_rules")
now = datetime(2026, 11, 2, 12, 0)      # a Monday, noon
v = lambda when, ids=("L1",): VisitIn(name="Amel", phone="22123456", listing_ids=list(ids), when=when)
check("a Wednesday 10:00, two days ahead, is fine", lambda: rules(v(datetime(2026, 11, 4, 10, 0)), now) == [])
check("Sunday is refused", lambda: "closed on Sunday" in rules(v(datetime(2026, 11, 8, 10, 0)), now))
check("8:30 and 18:00 are outside hours, 17:30 is fine", lambda: "outside opening hours (9:00-18:00)" in rules(v(datetime(2026, 11, 4, 8, 30)), now)
      and "outside opening hours (9:00-18:00)" in rules(v(datetime(2026, 11, 4, 18, 0)), now) and rules(v(datetime(2026, 11, 4, 17, 30)), now) == [])
check("less than 24 hours ahead is refused", lambda: "book at least 24 hours in advance" in rules(v(datetime(2026, 11, 3, 10, 0)), now))
check("more than 3 properties is refused", lambda: "at most 3 properties per visit" in rules(v(datetime(2026, 11, 4, 10, 0), ["a", "b", "c", "d"]), now))
check("several problems are all reported", lambda: len(rules(v(datetime(2026, 11, 2, 20, 0), list("abcd")), now)) == 3)

app, VISITS = var("app"), var("VISITS")
client = TestClient(app)


def future(days=3, hour=10):
    d = datetime.now() + timedelta(days=days)
    while d.weekday() == 6:
        d += timedelta(days=1)
    return d.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat()


body = lambda **kw: {"name": "Amel", "phone": "22123456", "listing_ids": ["L7"], "when": future(), **kw}
check("POST /visits -> 201 with an id", lambda: (VISITS.clear(), client.post("/visits", json=body()))[1].status_code == 201 and VISITS and "id" in VISITS[0])
check("a broken rule -> 422 with the problems", lambda: (lambda r: r.status_code == 422 and "outside opening hours (9:00-18:00)" in r.json()["detail"]["problems"])(client.post("/visits", json=body(when=future(4, 7)))))
check("an invalid phone -> 422 (Pydantic)", lambda: client.post("/visits", json=body(phone="call me")).status_code == 422)
check("same listing, same time -> 409", lambda: (VISITS.clear(), client.post("/visits", json=body(listing_ids=["L9"], when=future(5))), client.post("/visits", json=body(name="Sami", listing_ids=["L9"], when=future(5))))[2].status_code == 409)
check("GET /visits filters by phone", lambda: (VISITS.clear(), client.post("/visits", json=body(when=future(3, 11))), client.post("/visits", json=body(phone="98765432", when=future(3, 12))))
      and [x["phone"] for x in client.get("/visits", params={"phone": "98765432"}).json()] == ["98765432"] and len(client.get("/visits").json()) == 2)
