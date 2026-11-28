#!/bin/sh
# Ręczny audyt VM OCI. Opcjonalny argument to kontekst połączenia dla sshd -T -C.
export LC_ALL=C

printf '\nSystem i jądro\n'
if [ -r /etc/os-release ]; then
  . /etc/os-release
  printf '%s (ID=%s, VERSION_ID=%s)\n' "${PRETTY_NAME:-?}" "${ID:-?}" "${VERSION_ID:-?}"
else
  echo 'Dystrybucja: nie sprawdzono (brak odczytu /etc/os-release).'
fi
uname -srmo

printf '\nEfektywna konfiguracja SSH\n'
if [ -n "${1:-}" ]; then
  set -- -C "$1"
else
  set --
  echo 'Ustawienia globalne. Reguły Match wymagają podania kontekstu połączenia.'
fi
if ssh_config=$(/usr/sbin/sshd -T "$@" 2>/dev/null); then
  printf '%s\n' "$ssh_config" | awk '
    /^(port|permitrootlogin|passwordauthentication|kbdinteractiveauthentication|pubkeyauthentication|authenticationmethods|permitemptypasswords) / ||
    /^(allowusers|allowgroups|denyusers|denygroups) /'
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
      stat -c 'Data indeksu bezpieczeństwa: %y' "$index"
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
if [ -L "$env_file" ]; then
  echo '.env: nie sprawdzono (ścieżka jest dowiązaniem symbolicznym).'
elif [ -f "$env_file" ] && mode=$(stat -c '%a' "$env_file" 2>/dev/null); then
  stat -c '.env: tryb=%a właściciel=%U grupa=%G' "$env_file"
  [ "$mode" = 600 ] || echo '.env: oczekiwany tryb 600.'
else
  echo '.env: nie sprawdzono (brak pliku lub dostępu do metadanych).'
fi

printf '\nDostęp do lokalnego Dockera (%s)\n' "$(id -un)"
getent group docker 2>/dev/null || echo 'Grupa docker: nie sprawdzono (brak wpisu lub dostępu).'
stat -c 'Gniazdo Docker: tryb=%a właściciel=%U grupa=%G' /var/run/docker.sock 2>/dev/null ||
  echo 'Gniazdo Docker: nie sprawdzono (brak ścieżki lub dostępu).'
if version=$(docker --host unix:///var/run/docker.sock version --format '{{.Server.Version}}' 2>/dev/null); then
  printf 'Dostęp do demona Docker: tak (serwer %s).\n' "$version"
else
  echo 'Dostęp do demona Docker: nie sprawdzono (brak dostępu, klienta lub demona).'
fi

printf '\nNasłuch TCP/UDP na hoście\n'
ss -lntu 2>/dev/null || echo 'Porty: nie sprawdzono (brak ss lub dostępu).'
