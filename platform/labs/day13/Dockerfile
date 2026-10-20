# Image for your extraction API (service.py from day11). Copy service.py into this folder first.
FROM python:3.11-slim

WORKDIR /app

# TODO: COPY requirements.txt, then RUN pip install --no-cache-dir -r requirements.txt
#       (copying requirements first lets Docker cache the install layer)

# TODO: COPY service.py .

EXPOSE 8002

# TODO: CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8002"]
#       0.0.0.0, not 127.0.0.1: inside a container, 127.0.0.1 is unreachable from outside
