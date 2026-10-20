# The action your agent will take: booking a visit. The RULES live here, in code, not in the prompt.
# Run in your TERMINAL:  uvicorn visits_api:app --port 8003 --reload
# Check drives it with FastAPI's TestClient, no server needed.
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Dar Yasmine visits")
VISITS = []          # in memory: a real service would use Postgres


class VisitIn(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(pattern=r"^\+?\d{8,12}$")     # Tunisian numbers: 8 digits, or +216 and 8 digits
    listing_ids: list[str] = Field(min_length=1)
    when: datetime


def check_rules(visit, now):
    """The handbook's visit rules. Return a list of problems (empty list = OK):
      - "closed on Sunday"                      if visit.when is a Sunday (weekday() == 6)
      - "outside opening hours (9:00-18:00)"    if the visit starts before 9:00 or at/after 18:00
      - "book at least 24 hours in advance"     if visit.when - now < 24 hours
      - "at most 3 properties per visit"        if more than 3 listing_ids"""
    # TODO
    ...


@app.post("/visits", status_code=201)
def book_visit(visit: VisitIn):
    """Check the rules against datetime.now(). Problems -> HTTPException(422, detail={"problems": [...]}).
    The same listing already booked at the same time -> HTTPException(409, detail="slot already taken").
    Otherwise store {"id": len(VISITS) + 1, **visit.model_dump()} in VISITS and return it."""
    # TODO
    ...


@app.get("/visits")
def list_visits(phone: str | None = None):
    """All visits, or only those with this phone number."""
    # TODO
    ...
