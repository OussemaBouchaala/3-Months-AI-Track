# One-command deployment
**Topic:** Docker Compose for the full stack: database with health check, model server, API, volumes, env file.

## Real example
Why `depends_on` alone isn't enough (a different stack, the same race):

```python
import time
db_ready_at = time.time() + 3          # Postgres takes ~3 s to accept connections after its container starts
def api_start(wait_for_health):
    if wait_for_health:
        while time.time() < db_ready_at:
            time.sleep(0.5)
    return "connected" if time.time() >= db_ready_at else "connection refused, container exits"
print("depends_on only:     ", api_start(False))
print("condition: healthy:  ", api_start(True))
```

`depends_on: [db]` waits for the container to start, not for Postgres to be ready. `condition: service_healthy` waits for the health check.

## How to read this file
The file in the editor is the complete compose file that starts the whole project on the agency's PC. Read it service by service; the comments explain each line:

1. **`db`**: Postgres with pgvector, a data volume, and a `pg_isready` health check.
2. **`ollama`**: the model server, with a volume so models are downloaded once.
3. **`api`**: built from your Dockerfile, port 8000, settings from `.env`, the other services reached by **name** (`db`, `ollama`), `depends_on` with `condition: service_healthy`, restart, and its own health check.
4. **`volumes:`** at the bottom declares the named volumes.

## See it working
In your project folder (with a Dockerfile and a `.env`): `docker compose up -d --build`, then `docker compose ps` (all services healthy), then run the day 56 smoke test against http://127.0.0.1:8000.

Press **Check** under the editor to see the rules a reliable compose file follows.
