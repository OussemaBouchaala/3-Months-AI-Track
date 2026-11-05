import time
from contextlib import contextmanager

times = {}

@contextmanager
def stage(name):
    start = time.perf_counter()
    try:
        yield
    finally:
        times[name] = times.get(name, 0.0) + time.perf_counter() - start

with stage("embed"):
    time.sleep(0.05)
with stage("generate"):
    time.sleep(0.2)
print({k: round(v, 2) for k, v in times.items()})
