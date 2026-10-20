# Run this app in your TERMINAL, not with the Run button:
#   cd day02
#   uvicorn app_async:app --port 8001
# Press Check any time: it inspects your endpoints without starting the server.
import asyncio
import time

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

app = FastAPI()


@app.get("/blocking")
async def blocking():
    # TODO: wait 2 seconds with time.sleep (this blocks the event loop on purpose)
    ...
    return {"endpoint": "blocking"}


@app.get("/awaiting")
async def awaiting():
    # TODO: wait 2 seconds WITHOUT blocking, using asyncio.sleep
    ...
    return {"endpoint": "awaiting"}


@app.get("/threaded")
def threaded():  # plain def: FastAPI runs it in a thread pool
    # TODO: wait 2 seconds with time.sleep
    ...
    return {"endpoint": "threaded"}


@app.get("/fixed")
async def fixed():
    # TODO: run time.sleep(2) through run_in_threadpool, and await it
    ...
    return {"endpoint": "fixed"}
