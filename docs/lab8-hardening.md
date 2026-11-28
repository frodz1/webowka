# L8 — Zabezpieczenia infrastruktury

Hardening to ograniczanie uprawnień i zasobów do tego, czego aplikacja potrzebuje.

## Co zmieniliśmy

- **Kto uruchamia aplikację.** Caddy wcześniej działał jako root. Teraz działa jako użytkownik `caddy` i słucha na porcie 8080 wewnątrz kontenera. Port hosta to 8080 lokalnie i 80 na VM. Backend już wcześniej działał jako użytkownik `app`.
- **Co aplikacja może zrobić.** Docker usuwa dodatkowe uprawnienia systemowe (`cap_drop`) i blokuje uzyskanie nowych (`no-new-privileges`). Pliki obrazu są tylko do odczytu. Gunicorn zapisuje pliki kontrolne workerów w `/tmp`, a Caddy ma miejsce na dane i konfigurację w `/data` i `/config`. Te katalogi są w pamięci (`tmpfs`). Certyfikaty HTTPS są na load balancerze OCI.
- **Ile zasobów może zużyć.** Backend ma 384 MiB pamięci, bo uruchamia kilka workerów Pythona. Caddy ma 128 MiB na obsługę strony i przekazywanie żądań. Każdy z tych dwóch kontenerów ma limit 128 procesów i wątków łącznie. Docker przechowuje do trzech plików logów po około 10 MB, żeby logi nie zużywały całego dysku. Limity zmienia się w `tools/.env`. Nazwy zmiennych są w [`tools/.env.example`](../tools/.env.example).
- **Skąd biorą się sekrety.** Wcześniejszy szablon `cloud-init` prosił o wpisanie sekretów podczas tworzenia VM. Teraz GitHub Actions dostarcza je przy wdrożeniu i zapisuje w `.env`, który może odczytać i zmienić tylko właściciel (tryb `600`). Pliki takie jak `.env` i klucze są wykluczone z danych przekazywanych do budowania obrazów przez `.dockerignore`.

W każdym pliku Compose blok `x-app-security` zbiera ustawienia wspólne dla frontendu i backendu. Wpis `<<: *app-security` dodaje je do usługi. Limity i katalogi do zapisu są podane przy każdej usłudze. [Wspólne fragmenty Compose](https://docs.docker.com/reference/compose-file/fragments/)

## Jak to sprawdziliśmy

Tabela odwołuje się do zaleceń producentów. Wyniki dotyczą sprawdzonych ustawień L8.

| Zabezpieczenie | Gdzie | Źródło | Jak sprawdziliśmy | Wynik |
| --- | --- | --- | --- | --- |
| Uruchomienie bez roota | Gunicorn i Caddy | [Dockerfile `USER`](https://docs.docker.com/build/building/best-practices/#user) | Lista uruchomionych procesów | Gunicorn i workery mają UID 999, Caddy ma UID 10001 |
| Mniej uprawnień | Backend i frontend | [Docker Compose](https://docs.docker.com/reference/compose-file/container-spec/#cap_drop) | `docker inspect` i status głównego procesu | Brak dodatkowych uprawnień, `NoNewPrivs: 1` |
| Pliki tylko do odczytu | Backend i frontend | [Docker tmpfs](https://docs.docker.com/engine/storage/tmpfs/) | Sprawdzenie głównego systemu plików i zapis próbny | Główny system plików jest tylko do odczytu, zapis w wyznaczonych katalogach działa |
| Limity i logi | Backend i frontend | [Limity Compose](https://docs.docker.com/reference/compose-file/container-spec/#pids_limit), [logi Dockera](https://docs.docker.com/engine/logging/drivers/json-file/) | Sprawdzenie ustawień kontenerów i limitów systemowych | Potwierdzono limity i ustawienia rotacji |
| Wykluczenie sekretów z budowania | Oba obrazy | [Docker `.dockerignore`](https://docs.docker.com/build/concepts/context/#dockerignore-files) | Przegląd plików `.dockerignore` i budowa | Oba obrazy się zbudowały, testy backendu były dostępne |
| Sekrety z GitHub Actions | VM i wdrożenie | [cloud-init](https://docs.cloud-init.io/en/latest/explanation/hardening.html#no-plain-text-passwords), [GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) | Zapis do pliku tymczasowego | Pierwszy zapis i aktualizacja zachowały tryb `600` |
| Przegląd ustawień serwera | VM OCI | [Oracle OCI](https://docs.oracle.com/en/solutions/oci-security-checklist/compute-security1.html), [OpenSSH](https://man.openbsd.org/sshd) | `sudo sh tools/audit-vm.sh` | Nie sprawdzono na VM |

### Wyniki lokalne

- Oba pliki Compose i Caddyfile przeszły walidację. Po przeniesieniu wspólnych ustawień oba warianty Compose dają taką samą konfigurację jak wcześniej. Obrazy zbudowano na ARM64. Strona odpowiedziała HTTP 200, a `/api/health` zwrócił `{"status":"ok"}`.
- **32 testy backendu przeszły.** Pytest zgłosił ostrzeżenia o krótkim kluczu testowym i braku zapisu pamięci podręcznej. Trivy przeszedł dla obu obrazów z ustawieniami z CI. Produkcyjny `npm audit` zgłosił dwie umiarkowane podatności w React Router. [GHSA-wrjc-x8rr-h8h6](https://github.com/advisories/GHSA-wrjc-x8rr-h8h6) · [GHSA-337j-9hxr-rhxg](https://github.com/advisories/GHSA-337j-9hxr-rhxg)
- Sprawdzono składnię workflow, `cloud-init` i skryptu audytu. Pełny przebieg CI i audyt VM są poza tą próbą lokalną. Walidacja narzędziem cloud-init jest **niewykonana**. Polecenie to `cloud-init schema -c tools/cloud-init.yaml --annotate`. [Walidacja cloud-init](https://docs.cloud-init.io/en/latest/howto/debug_user_data.html)

## Dlaczego baza i Suricata mają inne ustawienia

- **PostgreSQL** zapisuje dane i dziennik transakcji w wolumenie `pgdata`. Produkcja korzysta z osobnej, zarządzanej bazy. [Pliki PostgreSQL](https://www.postgresql.org/docs/16/storage-file-layout.html)
- **Suricata** obserwuje ruch na interfejsie VM. Używa sieci hosta i ma uprawnienia do przechwytywania pakietów, operacji sieciowych i ustawiania priorytetu pracy (`NET_RAW`, `NET_ADMIN`, `SYS_NICE`). Zapisuje reguły i alerty w wolumenach. [Suricata AF_PACKET](https://docs.suricata.io/en/suricata-8.0.8/capture-hardware/af-packet.html) · [Linux capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)

## Krótki pokaz lokalny

Uruchom z katalogu głównego repozytorium. Pokaz ma własną bazę, a port 18080 jest dostępny tylko z Twojego komputera.

```sh
export IMAGE_TAG=lab8-demo FRONTEND_PORT=127.0.0.1:18080

docker compose --env-file /dev/null -p questlog-l8-demo -f tools/docker-compose.yml up -d --build --wait
curl -fsS --retry 10 --retry-all-errors --retry-delay 1 http://127.0.0.1:18080/api/health
docker compose --env-file /dev/null -p questlog-l8-demo -f tools/docker-compose.yml top backend frontend

# Sprzątanie po pokazie usuwa też jego testową bazę.
docker compose --env-file /dev/null -p questlog-l8-demo -f tools/docker-compose.yml down -v
```

Pełną weryfikację Compose, Caddy i Trivy wykonuje [job `smoke`](../.github/workflows/ci-cd.yml).

## Co zostało do zrobienia na VM

- [ ] Na obu maszynach uruchomić `cd /opt/questlog && sudo sh tools/audit-vm.sh`. Skrypt wypisuje wersję systemu, ustawienia SSH, dostęp do Dockera, uprawnienia `.env` i porty, na których serwer nasłuchuje.
- [ ] Sprawdzić aktualizacje systemu. Dla Ubuntu i Debiana skrypt używa lokalnej listy pakietów, więc stara lista może dać niepełny wynik. Dla innego systemu sprawdzić zalecenia jego producenta. [Ubuntu](https://documentation.ubuntu.com/security/security-updates/) · [Debian](https://www.debian.org/security/)
- [ ] Sprawdzić dostęp po SSH, właściciela `.env` i osoby z dostępem do Dockera, w tym konto runnera `gha`. [Dostęp do Dockera](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
- [ ] Porównać porty z regułami sieci OCI. Sprawdzić, czy SSH ma ograniczony dostęp, serwer przyjmuje ruch od load balancera na porcie 80, a port 443 load balancera jest dostępny tylko dla Cloudflare. [Sieć OCI](https://docs.oracle.com/en-us/iaas/Content/Security/Reference/networking_security.htm)
- [ ] Sprawdzić IMDSv2 i ustalić, czy kiedyś wpisano prawdziwe sekrety do user-data. Jeśli tak, zaplanować ich zmianę. Po wdrożeniu sprawdzić `curl -fsS http://localhost/api/health` na obu VM. [Bezpieczeństwo OCI Compute](https://docs.oracle.com/en-us/iaas/Content/Security/Reference/compute_security.htm)
