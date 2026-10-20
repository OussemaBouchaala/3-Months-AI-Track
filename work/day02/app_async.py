# Run this one in your TERMINAL, not with the Run button:
#   cd day02
#   uvicorn app_async:app --port 8001
from fastapi import FastAPI
import asyncio,time

app = FastAPI()

# 1. GET /blocking   -> async def + time.sleep(2)
@app.get("/blocking")
async def blocking():
    time.sleep(2)
# 2. GET /awaiting   -> async def + await asyncio.sleep(2)
@app.get("/awaiting")
async def awaiting():
    await asyncio.sleep(2)
# 3. GET /threaded   -> plain def + time.sleep(2)
@app.get("/threaded")
def threaded():
    time.sleep(2)
# 4. GET /fixed      -> async def that runs time.sleep(2) via run_in_threadpool
#    (from fastapi.concurrency import run_in_threadpool)
from fastapi.concurrency import run_in_threadpool
@app.get("/fixed")
async def fixed():
    await run_in_threadpool(time.sleep,2)