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

### Skany bezpieczeństwa (L6)

| Rodzaj | Narzędzie | Gdzie | Blokuje gdy |
|--------|-----------|-------|-------------|
| SAST | Semgrep 1.184 (`p/default`) | job `sast` | jakiekolwiek znalezisko |
| Sekrety | Gitleaks 8.30 (cała historia gita) | job `secrets` | jakikolwiek sekret |
| SCA | `pip-audit`, `npm audit --omit=dev` | joby `backend`, `frontend` | znana podatność (npm: od HIGH) |
| Obrazy | Trivy 0.76 | job `smoke`, przed pushem | HIGH/CRITICAL z poprawką; wyjątki w [`.trivyignore`](../.trivyignore) (z datą wygaśnięcia) |
| DAST | OWASP ZAP 2.17 baseline | job `smoke`, na działającym stosie | każde ostrzeżenie poza [`zap-rules.tsv`](zap-rules.tsv); raport HTML jako artefakt `zap-report` |
| Podpis | cosign (para kluczy) | `smoke` podpisuje na `main`, `deploy` weryfikuje | brak/zły podpis = brak wdrożenia |

Lokalnie, np. Trivy: `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.76.2 image ghcr.io/frodz1/questlog-backend:dev`.

Jednorazowo – klucz cosign (prywatny tylko w sekretach repo, publiczny w gicie):

```bash
cd tools
docker run --rm -it -v "$PWD:/w" -w /w ghcr.io/sigstore/cosign/cosign:v3.1.4 generate-key-pair
gh secret set COSIGN_PRIVATE_KEY < cosign.key && gh secret set COSIGN_PASSWORD   # hasło podane wyżej
rm cosign.key && git add cosign.pub
```

Ręczna weryfikacja: `cosign verify --key tools/cosign.pub ghcr.io/frodz1/questlog-backend:<sha>`.

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
- Rules → ruleset `main`: wymagany PR i zielone checki `backend`, `frontend`, `sast`, `secrets`, `smoke`.

## Bezpieczeństwo środowiska (L7)

Ścieżka ruchu: klient → **Cloudflare** (WAF, CDN, Anti-DDoS) → load balancer OCI (TLS) → VM: Caddy → Flask, a na VM **Suricata** (IDS) podsłuchuje ruch.

Cloudflare (plan Free, konfiguracja w panelu/API, poza repo):
- SSL **Full (strict)**, Always Use HTTPS, min. TLS 1.2; HSTS wysyła Caddy.
- WAF: Cloudflare Free Managed Ruleset + reguła `xss-sqli-query` (blokuje `<script`, `union select`, `' or '1'='1` w query).
- Rate limiting `login-limit`: `POST /api/auth/login` > 5 / 10 s z jednego IP → blokada.
- Anti-DDoS L7 (stale włączone), CDN dla `/assets/*` (Caddy wysyła `Cache-Control: immutable`).
- Caddy bierze adres klienta z `CF-Connecting-IP`; `nsg-lb` wpuszcza na 443 tylko [zakresy IP Cloudflare](https://www.cloudflare.com/ips-v4).

Suricata 8 (usługa `suricata` w `docker-compose.cloud.yml`, tryb IDS – tylko alarmuje):
- af-packet na karcie VM (`enp0s6`, inna: `SURICATA_IFACE` w `tools/.env`). TLS kończy się na LB, więc Suricata widzi odszyfrowany HTTP, łącznie z body.
- Reguły: ET Open (pobierane przy starcie przez `suricata-update`) + [`suricata/local.rules`](suricata/local.rules): SQLi/XSS w body API, `.env`/`.git`, ruch z pominięciem Cloudflare.
- W logu tylko alerty, bez treści żądań; adres klienta w polu `alert.xff` (z `CF-Connecting-IP`).
- Zmiana plików w `tools/suricata/` nie restartuje kontenera przy deployu: po wdrożeniu `cd /opt/questlog/tools && sudo docker compose -f docker-compose.cloud.yml restart suricata`.

```bash
# podgląd alertów na VM
sudo docker exec questlog-suricata-1 tail -f /var/log/suricata/eve.json \
  | jq -c '{t: .timestamp, sid: .alert.signature_id, msg: .alert.signature, klient: .alert.xff, url: .http.url}'
```
