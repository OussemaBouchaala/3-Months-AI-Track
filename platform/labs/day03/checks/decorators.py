timed, retry = fn("timed"), fn("retry")


def add(a, b):
    """adds"""
    return a + b


wrapped = timed(add)
check("timed(f) returns a function", callable(wrapped), "timed must `return wrapper`.")
check("the timed function still returns the result", lambda: wrapped(2, 3) == 5)
check("the timed function prints how long it took",
      lambda: "add" in printed(wrapped, 2, 3)[1] and "s" in printed(wrapped, 2, 3)[1],
      'Print something like f"{fn.__name__} took {elapsed:.4f}s".')
check("functools.wraps keeps the name and docstring",
      lambda: wrapped.__name__ == "add" and wrapped.__doc__ == "adds", "Put @functools.wraps(fn) above wrapper.")

calls = {"n": 0}


def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise ConnectionError("not yet")
    return "ok"


r = retry(times=3)(flaky) if callable(retry(times=3)) else None
check("retry(times=3) returns a decorator", r is not None and callable(r),
      "retry(times) returns decorator; decorator(fn) returns wrapper.")
check("retry succeeds on the 3rd attempt", lambda: r() == "ok" and calls["n"] == 3)

tries = {"n": 0}


def always_fails():
    tries["n"] += 1
    raise ValueError("boom")


def gives_up():
    try:
        retry(times=3)(always_fails)()
    except ValueError:
        return tries["n"] == 3
    return False


check("retry re-raises after exactly 3 failed attempts", gives_up,
      "After the loop, `raise` the last exception you caught.")
check("retry also keeps the function name", lambda: retry(times=2)(add).__name__ == "add")
