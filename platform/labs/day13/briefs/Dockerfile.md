# Containerize the API
**Topic:** copy requirements first so Docker caches the install layer.

## Real example
The Dockerfile for a small Flask app. Same order you'll use: dependencies first (cached), code second, a start command last:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
```

Build and run it with `docker build -t blog .` then `docker run -p 5000:5000 blog`.

## Your mission
Write a small image for `service.py`.

## Steps
1. `COPY requirements.txt .` then `RUN pip install --no-cache-dir -r requirements.txt`.
2. `COPY service.py .`
3. `CMD` uvicorn on `0.0.0.0` port `8002`.

## Done when
**Check** reads the file and finds each step in the right order.
