# Postgres + pgvector in one command
**Topic:** a database with a vector column, started with Docker like Week 2's service.

## Real example
A Compose file for Redis, used as a cache by a web app. Same three ideas you need: an image, a published port, a named volume:

```yaml
services:
  cache:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
volumes:
  redisdata:
```

## Your mission
Run Postgres with pgvector on port 5432, with its data in a named volume.

## Steps
1. `image: pgvector/pgvector:pg17` (Postgres 17 with the extension installed).
2. `ports: - "5432:5432"`.
3. `volumes: - pgdata:/var/lib/postgresql/data`.
4. In a terminal, in `day17`: `docker compose up -d`, then `pip install "psycopg[binary]"` in your venv.

## Done when
**Check** passes and `docker compose ps` shows the db running.
