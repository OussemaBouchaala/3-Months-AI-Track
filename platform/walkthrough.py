"""Study mode: split a documented lab file into walkthrough steps, and run one step's examples.

A study file documents each function with a docstring like this:

    def agreement(a, b):
        \"\"\"Share of positions where a and b hold the same label.

        Plain-English explanation (Markdown is fine).

        Example:
            >>> agreement([1, 0, 1], [1, 1, 1])
            0.67
        \"\"\"

`steps(code)` turns the file into one step per function or class (explanation, code
without the docstring, and the >>> examples). Run as a script, this module imports a
lab file and runs the examples of one step, printing the results as JSON:

    python walkthrough.py <file.py> <qualified name>
"""
import ast
import doctest
import inspect
import io
import json
import re
import sys
import textwrap
import traceback
from contextlib import redirect_stderr, redirect_stdout

MARK = "@@BENCH_EXAMPLES@@"
_parser = doctest.DocTestParser()


def _split_doc(doc: str):
    """Docstring -> (explanation in Markdown, examples as [{"source", "want"}], the example's note).

    The note is the text in brackets after "Example", e.g. "Example (a lazy judge):"."""
    doc = inspect.cleandoc(doc or "")
    lines, text = doc.splitlines(), []
    for line in lines:
        if line.strip().startswith(">>>"):
            break
        text.append(line)
    while text and not text[-1].strip():
        text.pop()
    note = ""
    m = re.match(r"^Examples?\b\s*(?:\((.*)\))?\s*:$", text[-1].strip()) if text else None
    if m:
        text.pop()
        note = m.group(1) or ""
    examples = [{"source": e.source.rstrip("\n"), "want": e.want.replace("<BLANKLINE>", "").rstrip("\n")}
                for e in _parser.get_examples(doc)]
    return "\n".join(text).strip(), examples, note


def _code_without_doc(code_lines, node):
    start, end = node.lineno, node.end_lineno
    if node.decorator_list:
        start = node.decorator_list[0].lineno
    body = node.body
    skip = set()
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        skip = set(range(body[0].lineno, body[0].end_lineno + 1))
    return textwrap.dedent("\n".join(code_lines[i - 1] for i in range(start, end + 1) if i not in skip)).rstrip()


def _signature(node):
    if isinstance(node, ast.ClassDef):
        return f"class {node.name}"
    return f"{node.name}({ast.unparse(node.args)})"


def steps(code: str) -> dict:
    """The walkthrough of a file: {"intro", "steps": [...], "main"} or {"error"}."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"error": f"Line {exc.lineno}: {exc.msg}"}
    code_lines = code.splitlines()
    intro, _, _ = _split_doc(ast.get_docstring(tree) or "")
    out, main = [], ""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            text, examples, note = _split_doc(ast.get_docstring(node) or "")
            out.append({"name": node.name, "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                        "signature": _signature(node), "explain": text, "examples": examples, "note": note,
                        "code": _code_without_doc(code_lines, node)})
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and ast.get_docstring(sub) \
                            and not sub.name.startswith("__"):
                        text, examples, note = _split_doc(ast.get_docstring(sub))
                        out.append({"name": f"{node.name}.{sub.name}", "kind": "method",
                                    "signature": f"{node.name}.{_signature(sub)}", "explain": text,
                                    "examples": examples, "note": note, "code": _code_without_doc(code_lines, sub)})
        elif isinstance(node, ast.If) and "__main__" in ast.unparse(node.test):
            main = "\n".join(code_lines[node.lineno - 1:node.end_lineno])
    return {"intro": intro, "steps": out, "main": main}


def _normalize(s: str) -> str:
    return " ".join(s.split())


def run_examples(path: str, qualname: str) -> list:
    """Import the file (its __main__ block does not run) and run one step's examples."""
    import importlib.util
    import os

    sys.path.insert(0, os.getcwd())
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    obj = module
    for part in qualname.split("."):
        obj = getattr(obj, part)
    _, examples, _ = _split_doc(inspect.getdoc(obj) or "")
    globs = dict(module.__dict__)
    results = []
    for ex in examples:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                exec(compile(ex["source"], "<example>", "single"), globs)
            got, error = buf.getvalue().rstrip("\n"), False
        except Exception as exc:
            tb = traceback.format_exception_only(type(exc), exc)[-1].strip()
            got, error = (buf.getvalue() + tb).rstrip("\n"), True
        ok = ex["want"] == "" if not got else _normalize(got) == _normalize(ex["want"])
        if ex["want"].startswith("Traceback"):
            ok = error and _normalize(ex["want"].splitlines()[-1]) == _normalize(got.splitlines()[-1])
        results.append({**ex, "got": got, "ok": ok, "error": error})
    return results


if __name__ == "__main__":
    try:
        payload = {"results": run_examples(sys.argv[1], sys.argv[2])}
    except Exception:
        payload = {"error": traceback.format_exc(limit=3)}
    print(MARK + json.dumps(payload))
