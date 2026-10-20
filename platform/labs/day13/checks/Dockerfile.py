import re

code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
check("Starts FROM a slim Python image", re.search(r"^FROM\s+python:3\.\d+-slim", code, re.M) is not None)
check("Installs requirements.txt with pip", lambda: re.search(r"^COPY\s+requirements\.txt", code, re.M)
      and re.search(r"^RUN\s+pip install.*-r\s+requirements\.txt", code, re.M),
      "COPY requirements.txt .  then  RUN pip install --no-cache-dir -r requirements.txt")
check("Copies requirements before the code (layer caching)",
      lambda: code.index("requirements.txt") < code.index("service.py"))
check("Copies service.py", re.search(r"^COPY\s+.*service\.py", code, re.M) is not None)
check("Runs uvicorn on 0.0.0.0:8002", lambda: re.search(r"^CMD.*uvicorn.*service:app.*0\.0\.0\.0.*8002", code, re.M),
      'CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8002"]')
