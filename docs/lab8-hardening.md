# L8 — Zabezpieczenia infrastruktury — hardening

## Zakres i zmiany przed/po

Backend już działał jako `app`. Caddy uruchamiał się jako root na porcie 80 kontenera. Po L8 Caddy działa jako `caddy:caddy` (UID/GID 10001) i nasłuchuje na 8080. Host nadal wystawia domyślnie 8080 lokalnie oraz 80 na VM OCI. TLS kończy się na load balancerze OCI. GitHub Actions zachowuje skany L6, podpisy cosign i wdrożenie sekwencyjne. Cloudflare pośredniczy w ruchu, a Suricata monitoruje interfejs VM.

Oba kontenery aplikacji miały zapisywalny główny system plików i domyślny zestaw capabilities Dockera. Teraz mają `read_only`, `cap_drop: [ALL]` i `no-new-privileges`. Gunicorn umieszcza pliki heartbeat w `/tmp` (tmpfs 16 MiB). Caddy ma zapisywalne tmpfs `/data` (16 MiB) i `/config` (4 MiB), dostępne dla jego UID. To stan ulotny, bo certyfikaty są na load balancerze, a przy starcie Caddy czyta wersjonowany Caddyfile. Jeśli Caddy przejmie TLS, katalog danych musi być trwały. [Katalogi Caddy](https://caddyserver.com/docs/conventions#file-locations) · [Ustawienia Gunicorna](https://gunicorn.org/reference/settings/)

Domyślne limity to 384 MiB dla Pythona i trzech workerów Gunicorna (dwóch na OCI) oraz 128 MiB dla Caddy obsługującego pliki statyczne i proxy. Limit 128 PID na usługę daje zapas na procesy i wątki. Rotacja `json-file` do trzech plików po 10 MB ogranicza zużycie dysku do około 30 MB na kontener. Limity są wartościami startowymi, a zmienne do ich zmiany opisano w [`tools/.env.example`](../tools/.env.example).

`cloud-init` przygotowuje VM bez wpisywania poświadczeń do user-data. Job `deploy` pobiera sekrety środowiska `production` i przy pierwszym wdrożeniu tworzy `tools/.env` w trybie `600`. Przy kolejnych wdrożeniach podmienia sekrety i tag obrazu, zachowując pozostałe wpisy.

## Zabezpieczenia i wyniki

Podstawą są zalecenia producentów, bez oceny zgodności z całym benchmarkiem.

| Zabezpieczenie | Komponent | Źródło | Weryfikacja | Wynik |
| --- | --- | --- | --- | --- |
| Procesy nonroot | Gunicorn, Caddy | [Dockerfile `USER`](https://docs.docker.com/build/building/best-practices/#user) | `docker compose top`, efektywny UID PID 1 | Gunicorn i workery UID 999, Caddy UID 10001 |
| Usunięcie capabilities i blokada uzyskania nowych uprawnień | Backend, frontend | [Docker Compose `cap_drop`](https://docs.docker.com/reference/compose-file/container-spec/#cap_drop), [`security_opt`](https://docs.docker.com/reference/compose-file/container-spec/#security_opt) | `docker inspect` i `/proc/1/status` | `CapEff`, `CapPrm` i `CapBnd` wyzerowane, `NoNewPrivs: 1` |
| Główny system plików tylko do odczytu i kontrolowany zapis | Backend, frontend | [Docker Compose `read_only`](https://docs.docker.com/reference/compose-file/container-spec/#read_only), [Docker tmpfs](https://docs.docker.com/engine/storage/tmpfs/) | `docker inspect`, `/proc/1/mountinfo`, zapis pliku próbnego | Główny system plików `ro`, zapis działa w `/tmp`, `/data` i `/config` |
| Limity i rotacja logów | Backend, frontend | [Docker Compose](https://docs.docker.com/reference/compose-file/container-spec/#pids_limit), [Docker `json-file`](https://docs.docker.com/engine/logging/drivers/json-file/) | `docker inspect` i limity w cgroup | 384/128 MiB, po 128 PID, ustawiona rotacja `10m` × 3 |
| Mniejszy kontekst budowania | Backend, frontend | [Docker `.dockerignore`](https://docs.docker.com/build/concepts/context/#dockerignore-files) | Przegląd obu plików `.dockerignore` i budowa obrazów | Wykluczono typowe pliki środowiska, klucze i artefakty. Lockfile frontendu i testy backendu są dostępne |
| Sekrety poza user-data | VM, GitHub Actions | [cloud-init](https://docs.cloud-init.io/en/latest/explanation/hardening.html#no-plain-text-passwords), [GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) | Przegląd user-data i kroku zapisu `.env`, test na pliku tymczasowym | Pierwszy zapis i aktualizacja z trybem `600` potwierdzone lokalnie |
| SSH, poprawki systemu, `.env`, Docker i nasłuch | VM OCI | [Oracle OCI Compute](https://docs.oracle.com/en/solutions/oci-security-checklist/compute-security1.html), [OpenSSH `sshd`](https://man.openbsd.org/sshd), [dostęp do Dockera](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) | `sudo sh tools/audit-vm.sh` na każdej VM | Nie sprawdzono |

## Wyjątki

- **PostgreSQL 16 w lokalnym Compose** zapisuje dane, WAL i stan klastra do wolumenu `pgdata`. Pozostawiono dotychczasowy tryb pracy kontenera. Produkcja używa zarządzanego PostgreSQL. [Układ plików PostgreSQL 16](https://www.postgresql.org/docs/16/storage-file-layout.html)
- **Suricata** używa `network_mode: host`, aby AF_PACKET widział interfejs VM. Zachowano `NET_RAW` dla gniazd pakietowych, `NET_ADMIN` dla operacji sieciowych i `SYS_NICE` dla ustawień planisty. Reguły i alerty są zapisywane w istniejących wolumenach. [Suricata AF_PACKET](https://docs.suricata.io/en/suricata-8.0.8/capture-hardware/af-packet.html) · [Docker host networking](https://docs.docker.com/engine/network/drivers/host/) · [Linux capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)

## Wyniki testów

- Na Docker Engine 29.5.3 (`linux/arm64`) zbudowano backend, frontend i obraz profilu testowego. Oba warianty Compose przeszły `config -q`. Porównanie konfiguracji potwierdziło identyczne ustawienia ochrony usług i zachowanie portów hosta. `caddy validate` zakończył się wynikiem `Valid configuration`.
- Strona zwróciła HTTP 200, a `/api/health` zwrócił `{"status":"ok"}`. Profil `test` przeszedł **32 testy** na osobnej bazie. Pytest zgłosił ostrzeżenia o krótkim deweloperskim kluczu JWT testów i o braku zapisu cache w `/srv`.
- **Trivy 0.76.2** przeszedł dla obu obrazów z filtrami CI i istniejącym `.trivyignore`. `npm audit --omit=dev --audit-level=high` zakończył się kodem 0 i zgłosił dwie podatności umiarkowanej wagi w React Router. [GHSA-wrjc-x8rr-h8h6](https://github.com/advisories/GHSA-wrjc-x8rr-h8h6) · [GHSA-337j-9hxr-rhxg](https://github.com/advisories/GHSA-337j-9hxr-rhxg)
- Składnia YAML workflow i cloud-init oraz składnia skryptów shellowych przeszły sprawdzenie. Filtry SSH i APT skryptu audytu sprawdzono na danych przykładowych. **Niewykonane** są sprawdzenie schematu przez `cloud-init schema -c tools/cloud-init.yaml --annotate`, pełny przebieg GitHub Actions i ręczny audyt VM. [Walidacja cloud-init](https://docs.cloud-init.io/en/latest/howto/debug_user_data.html)

## Demonstracja w osobnym projekcie Compose

Polecenia z katalogu głównego używają osobnego wolumenu PostgreSQL i publikują port wyłącznie na loopbacku. Dane w poleceniach są testowe.

```sh
export IMAGE_TAG=lab8-$$ FRONTEND_PORT=127.0.0.1:18080 DOCKER_DEFAULT_PLATFORM=linux/arm64
export POSTGRES_USER=questlog POSTGRES_DB=questlog POSTGRES_PASSWORD=questlog SECRET_KEY=lab8-local-test
LAB8_PROJECT=questlog-l8-$$
lab8() { docker compose --env-file /dev/null -p "$LAB8_PROJECT" -f tools/docker-compose.yml "$@"; }

lab8 --profile test config -q
DATABASE_URL='postgresql://lab8@db/questlog?sslmode=require' SECRET_KEY=lab8-placeholder \
  docker compose --env-file /dev/null -f tools/docker-compose.cloud.yml config -q
lab8 --profile test build backend frontend tests
lab8 up -d --no-build --wait
curl -fsS --retry 20 --retry-all-errors --retry-delay 1 http://127.0.0.1:18080/api/health
lab8 --profile test run --rm tests
lab8 exec -T frontend caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
lab8 top backend frontend
for service in backend frontend; do
  docker inspect --format 'read_only={{.HostConfig.ReadonlyRootfs}} {{json .HostConfig.LogConfig}}' \
    "$(lab8 ps -q "$service")"
  lab8 exec -T "$service" grep -E '^(Uid|CapEff|CapPrm|CapBnd|NoNewPrivs):' /proc/1/status
done
lab8 --profile test down -v
```

Trivy z istniejącego jobu `smoke` dla obu lokalnie zbudowanych obrazów (po ich zbudowaniu, z tym samym `IMAGE_TAG`).

```sh
for service in backend frontend; do
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:/repo:ro" -w /repo \
    aquasec/trivy:0.76.2 image --no-progress --severity HIGH,CRITICAL --ignore-unfixed \
    --exit-code 1 "ghcr.io/frodz1/questlog-$service:$IMAGE_TAG"
done
```

## Do sprawdzenia na obu VM i w OCI

- [ ] Uruchomić `cd /opt/questlog && sudo sh tools/audit-vm.sh` na obu VM. Porównać wersje systemu, daty lokalnych indeksów i poprawki. Audyt sprawdza kandydatów z repozytoriów security w symulacji APT dla Ubuntu/Debiana. Pakiet z nowszym kandydatem z innego repozytorium może wymagać osobnej oceny. Dla innego systemu użyć dokumentacji producenta wykrytej dystrybucji. [Ubuntu Security](https://documentation.ubuntu.com/security/security-updates/) · [Debian Security](https://www.debian.org/security/)
- [ ] Sprawdzić klucze SSH i skuteczną konfigurację dostępu dla administratorów. Dla reguł `Match` można przekazać do skryptu argument w formacie `user=ubuntu,addr=192.0.2.10,host=client.example,laddr=10.0.0.10,lport=22`, po podstawieniu parametrów rzeczywistego połączenia. [OpenSSH `sshd -T -C`](https://man.openbsd.org/sshd#C)
- [ ] Sprawdzić tryb `600` i właściciela `.env`. Przejrzeć dostęp do gniazda Docker, szczególnie członkostwo w grupie `docker` i dostęp konta runnera `gha`, np. `sudo -u gha docker --host unix:///var/run/docker.sock version --format '{{.Server.Version}}'`. [Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
- [ ] Porównać nasłuchy i publikowane porty z regułami hosta, NSG i Security Lists. Sprawdzić, czy SSH jest ograniczone do dozwolonych źródeł, VM przyjmuje ruch aplikacji od load balancera na 80/tcp, a dostęp do 443/tcp na load balancerze jest ograniczony do Cloudflare. [OCI Networking Security](https://docs.oracle.com/en-us/iaas/Content/Security/Reference/networking_security.htm)
- [ ] Po wdrożeniu sprawdzić na każdej VM `curl -fsS http://localhost/api/health` i stan usług poleceniem `cd /opt/questlog/tools && docker compose -f docker-compose.cloud.yml ps`.
- [ ] Zweryfikować ustawienia IMDSv2 i ustalić, czy starsze user-data zawierało rzeczywiste sekrety. Jeśli tak, zaplanować ich rotację. [OCI Compute Security](https://docs.oracle.com/en-us/iaas/Content/Security/Reference/compute_security.htm)
