"""The action your agent will take: booking a property visit.

The agency's **rules live here, in code**, not in the prompt. A prompt can be ignored
or tricked; an API that refuses a Sunday visit cannot. The agent can only *ask* this
API, and the API decides.

1. `VisitIn`: what a booking request must look like (Pydantic checks it).
2. `check_rules`: the handbook's rules, as a list of problems.
3. `book_visit`: `POST /visits`. Applies the rules, refuses double bookings, stores the visit.
4. `list_visits`: `GET /visits`, optionally for one phone number.

Running the file books a few visits with FastAPI's `TestClient` (no server needed).
To serve it for real, run in a terminal: `uvicorn visits_api:app --port 8003 --reload`.
"""
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Dar Yasmine visits")
VISITS = []          # kept in memory: a real service would use Postgres


class VisitIn(BaseModel):
    """A booking request. FastAPI refuses a request that doesn't match (status 422).

    - `name`: at least 2 characters.
    - `phone`: 8 to 12 digits, optionally starting with `+` (`22123456` or `+21622123456`).
    - `listing_ids`: at least one property.
    - `when`: a date and time; the text `"2026-11-04T10:00"` is converted to a `datetime`.

    Example:
        >>> VisitIn(name="Amel", phone="22123456", listing_ids=["L7"], when="2026-11-04T10:00").when
        datetime.datetime(2026, 11, 4, 10, 0)
        >>> try:
        ...     VisitIn(name="Amel", phone="call me", listing_ids=["L7"], when="2026-11-04T10:00")
        ... except Exception as e:
        ...     print(type(e).__name__)
        ValidationError
    """
    name: str = Field(min_length=2)
    phone: str = Field(pattern=r"^\+?\d{8,12}$")
    listing_ids: list[str] = Field(min_length=1)
    when: datetime


def check_rules(visit, now):
    """The handbook's visit rules. Returns the list of problems (empty = OK).

    Every rule is checked, so the customer learns **all** the problems at
    once instead of fixing them one by one:

    - closed on Sunday (`weekday()` is 0 for Monday ... 6 for Sunday);
    - opening hours 9:00-18:00 (a visit can start at 17:30, not at 18:00);
    - book at least 24 hours in advance;
    - at most 3 properties per visit.

    `now` is a parameter instead of `datetime.now()` inside, so the rules can
    be tested with a fixed date.

    Example (now is Monday 2 Nov 2026 at noon):
        >>> now = datetime(2026, 11, 2, 12, 0)
        >>> ok = VisitIn(name="Amel", phone="22123456", listing_ids=["L7"], when=datetime(2026, 11, 4, 10, 0))
        >>> check_rules(ok, now)
        []
        >>> bad = VisitIn(name="Amel", phone="22123456", listing_ids=["a", "b", "c", "d"], when=datetime(2026, 11, 2, 20, 0))
        >>> check_rules(bad, now)
        ['outside opening hours (9:00-18:00)', 'book at least 24 hours in advance', 'at most 3 properties per visit']
    """
    problems = []
    if visit.when.weekday() == 6:
        problems.append("closed on Sunday")
    if not 9 <= visit.when.hour < 18:
        problems.append("outside opening hours (9:00-18:00)")
    if visit.when - now < timedelta(hours=24):
        problems.append("book at least 24 hours in advance")
    if len(visit.listing_ids) > 3:
        problems.append("at most 3 properties per visit")
    return problems


@app.post("/visits", status_code=201)
def book_visit(visit: VisitIn):
    """`POST /visits`: book a visit, or explain why not.

    - Broken rules: **422** with the list of problems.
    - The same property already booked at the same time: **409** (conflict).
      `set(a) & set(b)` is the set of properties both visits share.
    - Otherwise: store the visit with a new id and return it, status **201** (created).

    Example (`TestClient` calls the API like a browser would, without a server):
        >>> from fastapi.testclient import TestClient
        >>> client = TestClient(app)
        >>> when = (datetime.now() + timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0)
        >>> when += timedelta(days=1) if when.weekday() == 6 else timedelta(0)
        >>> r = client.post("/visits", json={"name": "Amel", "phone": "22123456", "listing_ids": ["L9"], "when": when.isoformat()})
        >>> r.status_code, r.json()["listing_ids"]
        (201, ['L9'])
        >>> r = client.post("/visits", json={"name": "Sami", "phone": "98765432", "listing_ids": ["L9"], "when": when.isoformat()})
        >>> r.status_code, r.json()
        (409, {'detail': 'slot already taken'})
    """
    problems = check_rules(visit, datetime.now())
    if problems:
        raise HTTPException(422, detail={"problems": problems})
    if any(v["when"] == visit.when and set(v["listing_ids"]) & set(visit.listing_ids) for v in VISITS):
        raise HTTPException(409, detail="slot already taken")
    record = {"id": len(VISITS) + 1, **visit.model_dump()}
    VISITS.append(record)
    return record


@app.get("/visits")
def list_visits(phone: str | None = None):
    """`GET /visits`: all visits, or with `?phone=...` only that customer's visits.

    Example:
        >>> VISITS[:] = [{"id": 1, "phone": "22123456"}, {"id": 2, "phone": "98765432"}]
        >>> list_visits(phone="98765432")
        [{'id': 2, 'phone': '98765432'}]
        >>> len(list_visits())
        2
    """
    return [v for v in VISITS if phone is None or v["phone"] == phone]


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    day = datetime.now() + timedelta(days=3)
    if day.weekday() == 6:
        day += timedelta(days=1)
    at = lambda hour: day.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat()
    requests = [
        ("a normal booking", {"name": "Amel", "phone": "22123456", "listing_ids": ["L7"], "when": at(10)}),
        ("7 in the morning", {"name": "Sami", "phone": "98765432", "listing_ids": ["L2"], "when": at(7)}),
        ("same flat, same time", {"name": "Sami", "phone": "98765432", "listing_ids": ["L7"], "when": at(10)}),
        ("a bad phone number", {"name": "Sami", "phone": "call me", "listing_ids": ["L2"], "when": at(11)}),
    ]
    for label, body in requests:
        r = client.post("/visits", json=body)
        print(f"{label:<22} -> {r.status_code}  {r.json() if r.status_code != 422 or 'problems' in str(r.json()) else 'invalid request'}")
    print("Amel's visits:", [v["id"] for v in client.get("/visits", params={"phone": "22123456"}).json()])
