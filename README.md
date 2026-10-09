# QuestLog

Tablica znalezisk (lekki klon Reddita i Wykopu): użytkownicy dodają linki i krótkie teksty, głosują w górę/w dół, a pod każdym wpisem toczy się dyskusja w drzewku komentarzy.

- **Front-end:** React (Vite)
- **Back-end:** Python (Flask), zwykły SQL (psycopg)
- **Baza danych:** PostgreSQL w kontenerze Docker

## Struktura repozytorium

```
code/backend    API Flask, schemat SQL, testy
code/frontend   aplikacja React
tools/          docker-compose i instrukcje uruchomienia
```

## Uruchomienie

```bash
cd tools
docker compose up -d --build
```

Aplikacja: http://localhost:8080 — szczegóły, dane demo i testy w [tools/README.md](tools/README.md).
