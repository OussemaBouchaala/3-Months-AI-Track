# Two ways to write a timing context manager, and proof that cleanup always runs.
import time
from contextlib import contextmanager


class Timer:
    """with Timer("label"): ...   prints "label: 0.1234s" when the block ends, even on error."""

    def __init__(self, label):
        self.label = label

    def __enter__(self):
        # TODO: save the start time on self, then return self
        ...

    def __exit__(self, exc_type, exc, tb):
        # TODO: set self.elapsed, print f"{self.label}: {self.elapsed:.4f}s"
        #       and return False so any exception keeps propagating
        ...


@contextmanager
def timer(label):
    """Same behaviour as Timer, written as a generator."""
    start = time.perf_counter()
    # TODO: wrap the yield in try/finally and print the elapsed time in finally
    yield


if __name__ == "__main__":
    with Timer("class"):
        sum(range(1_000_000))

    with timer("generator"):
        sum(range(1_000_000))

    # 3. Cleanup on error: the timing line must still print, and the error must still reach us.
    try:
        with timer("failing block"):
            raise ValueError("boom")
    except ValueError:
        print("ValueError still propagated")
