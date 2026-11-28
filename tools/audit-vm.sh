#!/bin/sh
# Ręczny audyt VM OCI. Opcjonalny argument to kontekst połączenia dla sshd -T -C.
export LC_ALL=C

# Uruchom polecenie odczytu i oznacz brak dostępu lub narzędzia.
show() {
  label=$1
  shift
  if output=$("$@" 2>/dev/null); then
    printf '%s\n' "$output"
  else
    printf '%s: nie sprawdzono\n' "$label"
  fi
}

printf '\nSystem i jądro\n'
if [ -r /etc/os-release ]; then
  . /etc/os-release
  printf '%s (ID=%s, VERSION_ID=%s)\n' "${PRETTY_NAME:-?}" "${ID:-?}" "${VERSION_ID:-?}"
else
  echo 'Dystrybucja: nie sprawdzono (brak odczytu /etc/os-release).'
fi
show 'Jądro' uname -srmo

printf '\nEfektywna konfiguracja SSH\n'
if [ -n "${1:-}" ]; then
  set -- -C "$1"
else
  set --
  echo 'Ustawienia globalne. Reguły Match wymagają podania kontekstu połączenia.'
fi
if ssh_config=$(/usr/sbin/sshd -T "$@" 2>/dev/null); then
  printf '%s\n' "$ssh_config" | grep -E \
    -e '^(port|permitrootlogin|allowusers|allowgroups|denyusers|denygroups) ' \
    -e '^(passwordauthentication|kbdinteractiveauthentication|pubkeyauthentication|authenticationmethods|permitemptypasswords) '
else
  echo 'SSH: nie sprawdzono (sshd -T nie działa z tymi uprawnieniami lub parametrami).'
fi

printf '\nAktualizacje bezpieczeństwa (lokalne indeksy)\n'
case "${ID:-}" in
  ubuntu|debian)
    security_index=
    for index in /var/lib/apt/lists/*-security_InRelease /var/lib/apt/lists/*-security_Release; do
      [ -r "$index" ] || continue
      security_index=yes
      show 'Data indeksu bezpieczeństwa' stat -c 'Data indeksu bezpieczeństwa: %y' "$index"
    done
    if [ -n "$security_index" ] && upgrades=$(apt-get -s --with-new-pkgs \
        -o Dir::Cache::pkgcache= -o Dir::Cache::srcpkgcache= upgrade 2>/dev/null); then
      printf '%s\n' "$upgrades" | awk '
        /^Inst / && / (Ubuntu[^ ]*|Debian(-Security)?):[^ ]*-security([ \/,)]|$)/ { print; count++ }
        END { printf "Kandydaci z repozytorium security w symulacji APT: %d\n", count }'
    else
      echo 'Aktualizacje: nie sprawdzono (brak czytelnych indeksów security lub błąd symulacji APT).'
    fi
    ;;
  *)
    echo 'Aktualizacje: nie sprawdzono (dobierz metodę do wykrytej dystrybucji).'
    ;;
esac

printf '\nUprawnienia konfiguracji aplikacji\n'
env_file=/opt/questlog/tools/.env
if [ -f "$env_file" ] && [ ! -L "$env_file" ]; then
  show '.env' stat -c '.env: tryb=%a (oczekiwany 600), właściciel=%U, grupa=%G' "$env_file"
else
  echo '.env: nie sprawdzono (brak dostępu do zwykłego pliku).'
fi

printf '\nDostęp do lokalnego Dockera (%s)\n' "$(id -un)"
show 'Grupa docker' getent group docker
show 'Gniazdo Dockera' stat -c 'Gniazdo Dockera: tryb=%a, właściciel=%U, grupa=%G' /var/run/docker.sock
show 'Dostęp do Dockera' docker --host unix:///var/run/docker.sock version \
  --format 'Dostęp do Dockera: tak (serwer {{.Server.Version}})'

printf '\nNasłuch TCP/UDP na hoście\n'
show 'Porty' ss -lntu
