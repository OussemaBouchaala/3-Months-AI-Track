import re
code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
check("runs on push to main and on pull requests", lambda: re.search(r"^on:\s*\n", code, re.M) and re.search(r"^\s+push:\s*\n\s+branches:\s*\[?\s*[\"']?main", code, re.M) and re.search(r"^\s+pull_request:", code, re.M))
check("checks out the code", lambda: "actions/checkout@v" in code)
check("sets up Python 3.12 with pip cache", lambda: re.search(r"actions/setup-python@v\d", code) and re.search(r"python-version:\s*[\"']?3\.1[1-3]", code) and re.search(r"cache:\s*[\"']?pip", code))
check("installs requirements", lambda: re.search(r"pip install.*-r requirements\.txt", code))
check("lints with ruff", lambda: re.search(r"ruff check", code))
check("runs the tests with pytest", lambda: re.search(r"(python -m )?pytest", code) and not re.search(r"pytest.*(\|\|\s*true|--exitfirst=0)", code))
def job(name):
    m = re.search(rf"^  {name}:\s*\n((?:(?:    .*|\s*)\n)*)", code + "\n", re.M)
    return m.group(1) if m else ""
check("a docker job that needs the test job and builds the image", lambda: re.search(r"needs:\s*\[?\s*test", job("docker")) and re.search(r"docker build", job("docker")))
check("no secrets written in the workflow", lambda: not re.search(r"sk-[A-Za-z0-9]{8,}|password:\s*\S{6,}", code, re.I))
