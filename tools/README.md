# QuestLog – uruchamianie (Docker)

Cała aplikacja (PostgreSQL + backend Flask + frontend React/Caddy) startuje jako zespół kontenerów z jednego pliku [`docker-compose.yml`](docker-compose.yml).

## Wymagania

- Docker Desktop (lub Docker Engine) z wtyczką Compose v2 (`docker compose`)

## Szybki start

```bash
cd tools
docker compose up -d --build
```

Po chwili aplikacja jest dostępna pod adresem **http://localhost:8080**.

| Usługa     | Opis                                            | Adres                   |
|------------|-------------------------------------------------|-------------------------|
| `frontend` | React (build Vite) serwowany przez Caddy ([`Caddyfile`](../code/frontend/Caddyfile)); Caddy przekazuje `/api/*` do backendu | http://localhost:8080 (jedyny port wystawiony na hosta) |
| `backend`  | Flask + gunicorn, REST API                      | tylko w sieci Dockera (`backend:5000`) |
| `db`       | PostgreSQL 16 (dane w wolumenie `pgdata`)       | tylko w sieci Dockera   |

API jest dostępne przez Caddy, np. `curl http://localhost:8080/api/health`.

Tabele tworzą się automatycznie przy starcie backendu ([`schema.sql`](../code/backend/schema.sql)).

## Dane testowe (opcjonalnie)

[`seed.sql`](seed.sql) wypełnia bazę: 12 użytkowników, 24 wpisy (AI, piłka nożna, motoryzacja w stylu polskich for, parodia forum z jaskiniowcami, film, kuchnia, muzyka), liczne komentarze (wątki zagnieżdżone, jeden usunięty) oraz głosy.

```bash
docker compose exec -T db psql -U questlog -d questlog < seed.sql
```

**Uwaga:** skrypt najpierw czyści tabele `users`, `posts`, `comments` i `votes`, więc nadpisze dotychczasowe dane. Loginy i hasła użytkowników testowych są w [`users.txt`](users.txt) (np. `ada` / `Ada!2026`).

## Testy backendu

```bash
docker compose --profile test run --rm tests
```

Testy działają na osobnej bazie `questlog_test`, więc nie ruszają danych aplikacji.

## Przydatne polecenia

```bash
docker compose logs -f backend     # logi backendu
docker compose ps                  # stan kontenerów
docker compose down                # zatrzymanie (dane zostają)
docker compose down -v             # zatrzymanie i usunięcie bazy
docker compose up -d --build       # przebudowa po zmianach w kodzie
```

## Konfiguracja

Domyślne wartości działają bez żadnych plików. Aby je zmienić (port `FRONTEND_PORT`, hasło bazy, klucz JWT), skopiuj [`.env.example`](.env.example) do `tools/.env` i edytuj. **Przed wdrożeniem poza własny komputer ustaw własny `SECRET_KEY`.**

## Praca bez Dockera (opcjonalnie)

```bash
# baza (porty bazy i backendu nie są wystawione na hosta – do pracy lokalnej
# dodaj tymczasowo `ports: ["5432:5432"]` do usługi db w docker-compose.yml)
docker compose up -d db

# backend (Python 3.12)
cd ../code/backend
pip install -r requirements.txt
DATABASE_URL=postgresql://questlog:questlog@localhost:5432/questlog python -m app.init_db
flask --app "app:create_app()" run --port 5000

# frontend (proxy /api -> localhost:5000)
cd ../frontend
npm install
npm run dev     # http://localhost:5173
```

## API (skrót)

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| POST | `/api/auth/register`, `/api/auth/login` | rejestracja / logowanie (zwraca token JWT) |
| GET | `/api/auth/me` | bieżący użytkownik |
| GET | `/api/posts?sort=hot\|new\|best&tag=&page=` | tablica znalezisk |
| POST / PUT / DELETE | `/api/posts`, `/api/posts/:id` | dodawanie, edycja, usuwanie własnych wpisów |
| POST | `/api/posts/:id/vote`, `/api/comments/:id/vote` | `{"value": 1 \| -1 \| 0}` (0 cofa głos) |
| GET / POST | `/api/posts/:id/comments` | lista komentarzy (`parent_id` buduje drzewo) / nowy komentarz lub odpowiedź |
| PUT / DELETE | `/api/comments/:id` | edycja / usuwanie własnych komentarzy |
| GET | `/api/me/posts`, `/api/me/comments` | „Moje treści” |
| GET | `/api/tags` | popularne tagi |

Tokeny przekazujemy nagłówkiem `Authorization: Bearer <token>`.

## CI/CD (GitHub Actions)

Pipeline: [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml).

| Job | Kiedy | Co robi |
|-----|-------|---------|
| `backend` | każdy PR i push na `main` | `pytest` na PostgreSQL 16 (kontener usługi) |
| `frontend` | każdy PR i push na `main` | `npm ci` + `npm run build` |
| `smoke` | każdy PR i push na `main` | buduje obrazy `backend` i `frontend` (runner arm64), uruchamia je z Postgresem i sprawdza `curl /api/health`; na `main` po zielonym teście wypycha **te same** obrazy do GHCR |
| `deploy (app1)` → `deploy (app2)` | push na `main`, gdy CI jest zielone | rolling: `git reset --hard <sha>`, zapis `.env`, `compose pull` + `up -d` (obrazy z GHCR, **bez budowania na maszynie**), health check; padnie app1 → app2 zostaje na starej wersji |

Rollback: `git revert` na `main` – pipeline zbuduje i wdroży poprzednią wersję. Szybciej, bez budowania: na maszynie ustaw w `tools/.env` `IMAGE_TAG=<sha wcześniejszego commita>` i wykonaj `docker compose -f docker-compose.cloud.yml pull && docker compose -f docker-compose.cloud.yml up -d` (obrazy z tagiem SHA zostają w rejestrze).

Deploy wykonują **self-hosted runnery** na maszynach (łączą się z GitHubem wychodząco, więc port 22 zostaje otwarty tylko dla jednego IP). Sekrety (`DATABASE_URL`, `SECRET_KEY`) są przechowywane w GitHubie jako *environment secrets* środowiska `production` (Settings → Environments → production) i dostępne tylko dla jobu `deploy` z gałęzi `main`. Przy każdym wdrożeniu job zapisuje je do `/opt/questlog/tools/.env` (prawa 600), więc `SECRET_KEY` jest zawsze identyczny na obu maszynach. Rotacja: `gh secret set SECRET_KEY --env production`, potem redeploy. Pozostałe wpisy w `.env` (np. `WEB_CONCURRENCY`) zostają nietknięte. Kopii zapasowej `.env` nie robimy – źródłem prawdy są sekrety w GitHubie.

### Rejestr obrazów (GHCR)

Obrazy: `ghcr.io/frodz1/questlog-backend` i `ghcr.io/frodz1/questlog-frontend`, tag = pełny SHA commita (niezmienny, ślad do kodu). Budowane są raz, w jobie `smoke`, na runnerze `ubuntu-24.04-arm`, bo maszyny w OCI są arm64. Publikuje je tylko push na `main` (tokenem joba, bez dodatkowych sekretów); PR-y niczego nie wypychają. Maszyny logują się do GHCR tokenem joba `deploy` (`packages: read`) tylko na czas pobrania. Etykieta `org.opencontainers.image.source` w Dockerfile'ach wiąże pakiet z repozytorium, dzięki czemu `GITHUB_TOKEN` może go pobrać.

Lokalnie nic się nie zmienia: `docker compose up -d --build` buduje te same obrazy z tagiem `dev`. Nowe pakiety w GHCR są domyślnie prywatne; jeśli `compose pull` zwróci `denied`, w Packages → pakiet → *Package settings* dodaj repozytorium `webowka` w „Manage Actions access” (rola Read) albo ustaw pakiet jako publiczny.

### Jednorazowa konfiguracja runnera (na każdej VM, `--name`/`--labels` = `app1` lub `app2`)

```bash
sudo useradd -m -G docker gha && sudo chown -R gha /opt/questlog
sudo -iu gha bash -c '
  mkdir runner && cd runner
  V=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep -oP "\"tag_name\": \"v\K[^\"]+")
  curl -sL https://github.com/actions/runner/releases/download/v$V/actions-runner-linux-arm64-$V.tar.gz | tar xz
  ./config.sh --url https://github.com/frodz1/webowka --token <TOKEN> --name app1 --labels app1 --unattended'
cd /home/gha/runner && sudo ./svc.sh install gha && sudo ./svc.sh start
```

Token: Settings → Actions → Runners → New self-hosted runner (albo `gh api -X POST repos/frodz1/webowka/actions/runners/registration-token -q .token`).

### Ustawienia repozytorium

- Actions → General → Fork pull request workflows: **Require approval for all outside collaborators** (repo jest publiczne – cudzy PR nie może odpalić kodu na naszych VM).
- Environments → `production`: wdrożenia tylko z gałęzi `main`.
- Rules → ruleset `main`: wymagany PR i zielone checki `backend`, `frontend`, `smoke`.
