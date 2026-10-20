"""Runs one exercise file, then its check script, and reports pass/fail per check.

Usage (Bench calls this for you): python checker.py <your_file> <check_file>

The check script runs with these names available:
    ns          your file's globals (functions, variables) after it ran
    src         your file's source text
    out         everything your file printed while it ran
    check(label, condition, hint="")
                condition is a bool or a zero-argument callable; a callable that
                raises counts as a failure and its error is shown
    fn(name)    your function `name`, or a clear failure if it isn't defined
    var(name)   your variable `name`, or a clear failure if it isn't defined
    printed(f, *args, **kwargs) -> (result, text printed during the call)
    approx(a, b, tol=1e-6)
    filled(value, min_len=1) -> True when an answer variable isn't left empty

Your file runs with __name__ == "bench_check", so code under
`if __name__ == "__main__":` is skipped: checks call your functions directly.
Python files only; other files (Dockerfile, YAML, Markdown) are checked as text.
"""
import contextlib
import io
import json
import os
import sys
import traceback
import types

MARK = "@@BENCH_CHECKS@@"


class CheckFailed(Exception):
    pass


def main():
    target, check_file = sys.argv[1], sys.argv[2]
    real_stdout = sys.stdout
    results = []
    src = open(target, encoding="utf-8").read()
    ns = {}
    buf = io.StringIO()

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.show = lambda *a, **k: None
    except ImportError:
        pass

    sys.path.insert(0, os.path.dirname(os.path.abspath(target)))

    if target.endswith(".py"):
        mod = types.ModuleType("bench_check")
        mod.__file__ = target
        sys.modules["bench_check"] = mod
        try:
            code = compile(src, target, "exec")
            with contextlib.redirect_stdout(buf):
                exec(code, mod.__dict__)
            ns = mod.__dict__
            results.append({"label": "Your file runs without errors", "ok": True})
        except BaseException as exc:  # noqa: BLE001 - report anything the user's code raises
            if isinstance(exc, KeyboardInterrupt):
                raise
            tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
            user_tb = [line for line in tb if target in line or not line.startswith("  File")]
            results.append({
                "label": "Your file runs without errors", "ok": False,
                "detail": "".join(user_tb[-4:]).strip(),
                "hint": "Fix this error first (a TODO left as `...` often causes it), then press Check again.",
            })
            finish(real_stdout, results, buf.getvalue())
            return

    out = buf.getvalue()

    def check(label, condition, hint=""):
        entry = {"label": label}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                ok = condition() if callable(condition) else condition
            entry["ok"] = bool(ok)
        except CheckFailed as exc:
            entry["ok"] = False
            entry["detail"] = str(exc)
        except Exception as exc:  # noqa: BLE001
            entry["ok"] = False
            entry["detail"] = f"{type(exc).__name__}: {exc}"
        if not entry["ok"] and hint:
            entry["hint"] = hint
        results.append(entry)
        return entry["ok"]

    def fn(name):
        f = ns.get(name)
        if not callable(f):
            raise CheckFailed(f"Define a function called `{name}`.")
        return f

    def var(name):
        if name not in ns:
            raise CheckFailed(f"Define a variable called `{name}`.")
        return ns[name]

    def printed(f, *args, **kwargs):
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            result = f(*args, **kwargs)
        return result, b.getvalue()

    def approx(a, b, tol=1e-6):
        return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(b))

    def filled(value, min_len=1):
        if value is None or value is Ellipsis:
            return False
        if isinstance(value, str):
            return len(value.strip()) >= min_len
        try:
            return len(value) >= min_len
        except TypeError:
            return True

    env = {"ns": ns, "src": src, "out": out, "check": check, "fn": fn, "var": var,
           "printed": printed, "approx": approx, "filled": filled, "CheckFailed": CheckFailed,
           "__name__": "bench_checks"}
    try:
        check_src = open(check_file, encoding="utf-8").read()
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(check_src, "checks", "exec"), env)
    except CheckFailed as exc:
        results.append({"label": "Your file has the names the checks look for", "ok": False, "detail": str(exc),
                        "hint": "Keep the function and variable names from the starter. If this file was written "
                                "from an older starter, save your work elsewhere and press Reset to starter."})
    except Exception as exc:  # noqa: BLE001 - a broken check script shouldn't hide results
        results.append({"label": "Check script", "ok": False,
                        "detail": f"The checks stopped early: {type(exc).__name__}: {exc}"})
    finish(real_stdout, results, out)


def finish(stream, results, out):
    stream.write("\n" + MARK + json.dumps({"results": results, "stdout": out[-20_000:]}) + "\n")
    stream.flush()


if __name__ == "__main__":
    main()
