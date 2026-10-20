import time

Timer, timer = var("Timer"), fn("timer")


def use_class():
    with Timer("cls") as t:
        time.sleep(0.05)
    return t


check("Timer's __enter__ returns the Timer (so `as t` works)", lambda: isinstance(use_class(), Timer),
      "End __enter__ with `return self`.")
check("Timer stores elapsed seconds on self.elapsed", lambda: 0.04 < use_class().elapsed < 1)
check("Timer prints its label when the block ends", lambda: "cls" in printed(use_class)[1])


def class_on_error():
    try:
        with Timer("cls-err"):
            raise ValueError("boom")
    except ValueError:
        return True
    return False


check("Timer lets the exception propagate", lambda: printed(class_on_error)[0],
      "__exit__ must return False (or None).")
check("Timer still prints when the block raises", lambda: "cls-err" in printed(class_on_error)[1])


def gen_ok():
    with timer("gen"):
        time.sleep(0.01)


def gen_err():
    try:
        with timer("gen-err"):
            raise ValueError("boom")
    except ValueError:
        return True
    return False


check("timer prints its label", lambda: "gen" in printed(gen_ok)[1], "Print in a `finally:` after the yield.")
check("timer still prints when the block raises", lambda: "gen-err" in printed(gen_err)[1],
      "Put the yield inside try: ... finally: print(...).")
check("timer lets the exception propagate", lambda: printed(gen_err)[0])
