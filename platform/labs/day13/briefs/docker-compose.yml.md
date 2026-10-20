# Two services, one command
**Topic:** inside Compose, containers reach each other by service name, not `localhost`.

## Real example
A web app with its Postgres database. Notice the app reaches the database by **service name** (`db`), and the data lives in a named volume:

```yaml
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://app:secret@db:5432/app
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  pgdata:
```

## Your mission
Run the API and Ollama together with `docker compose up --build`.

## Steps
1. In `api`: `OLLAMA_URL: http://ollama:11434`.
2. In `ollama`: `image: ollama/ollama` and a volume `ollama:/root/.ollama`.
3. Declare the volume at the bottom under `volumes:`.

## Done when
**Check** finds the service name URL, the image and the named volume.
