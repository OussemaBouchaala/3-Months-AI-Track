# Write both decorators from memory, Run to see them work, then Check.
import functools
import time


def timed(fn):
    """Decorator: print "<name> took 0.1234s" after each call and return fn's result.
    Use @functools.wraps(fn) so the decorated function keeps its __name__."""
    # TODO: define wrapper(*args, **kwargs) inside, time the call, return wrapper
    ...


def retry(times=3):
    """Decorator WITH an argument: call the function up to `times` times until it
    stops raising. If every attempt raises, re-raise the last exception."""
    def decorator(fn):
        # TODO: define wrapper(*args, **kwargs) with a loop over range(times), return wrapper
        ...
    return decorator


@timed
def slow_sum(n):
    return sum(range(n))


@timed
def nap(seconds):
    time.sleep(seconds)
    return seconds


if __name__ == "__main__":
    print(slow_sum(1_000_000), "| name kept:", slow_sum.__name__)
    print(nap(0.1))

    attempts = {"n": 0}

    @retry(times=3)
    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ConnectionError("not yet")
        return "ok"

    print(flaky(), "after", attempts["n"], "attempts")
