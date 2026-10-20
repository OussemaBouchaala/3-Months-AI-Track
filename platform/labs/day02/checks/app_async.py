import inspect
import re

app = var("app")
paths = {getattr(r, "path", None) for r in app.routes}
for p in ["/blocking", "/awaiting", "/threaded", "/fixed"]:
    check(f"GET {p} exists", p in paths, "Keep the @app.get(...) decorators from the starter.")


def body(name):
    return re.sub(r"#.*", "", inspect.getsource(fn(name)))


check("/blocking is async def and calls time.sleep(2)",
      lambda: inspect.iscoroutinefunction(fn("blocking")) and "time.sleep(2)" in body("blocking"))
check("/awaiting is async def and awaits asyncio.sleep(2)",
      lambda: inspect.iscoroutinefunction(fn("awaiting")) and re.search(r"await\s+asyncio\.sleep\(\s*2", body("awaiting")),
      "Without `await`, asyncio.sleep(2) only creates a coroutine and never waits.")
check("/threaded is a plain def that calls time.sleep(2)",
      lambda: not inspect.iscoroutinefunction(fn("threaded")) and "time.sleep(2)" in body("threaded"))
check("/fixed is async def and awaits run_in_threadpool(time.sleep, 2)",
      lambda: inspect.iscoroutinefunction(fn("fixed"))
      and re.search(r"await\s+run_in_threadpool\(\s*time\.sleep\s*,\s*2", body("fixed")),
      "Pass the function and its argument separately: run_in_threadpool(time.sleep, 2).")
