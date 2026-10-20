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

## Your mission
Write the compose file that starts your whole project on the agency's PC.

## Steps
1. `db`: data volume and a `pg_isready` health check.
2. `ollama`: a models volume.
3. `api`: build, port, `env_file`, service-name URLs, `depends_on` with health, restart, health check.
4. Top-level `volumes:`.
5. In your project folder: `docker compose up -d --build`, then `docker compose ps` (all healthy), then run the day56 smoke test.

## Done when
**Check** passes and the smoke test passes against the stack started by `docker compose up`.
