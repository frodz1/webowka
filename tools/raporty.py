"""Generator raportów projektowych QuestLog (L1, L5, L6), każdy na 2 strony A4.

Uruchom z katalogu głównego repo: python3 tools/raporty.py
"""
import shutil

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

S = "/System/Library/Fonts/Supplemental/"
for name, f in {"R": "Arial", "B": "Arial Bold", "I": "Arial Italic", "G": "Georgia Bold",
                "GI": "Georgia Italic", "M": "Courier New"}.items():
    pdfmetrics.registerFont(TTFont(name, f"{S}{f}.ttf"))
pdfmetrics.registerFontFamily("R", normal="R", bold="B", italic="I", boldItalic="B")

INK, GREY, GOLD = HexColor("#1b2230"), HexColor("#6b7280"), HexColor("#8a6d1f")
HEAD, ZEBRA, RULE = HexColor("#1e2533"), HexColor("#f4f1ea"), HexColor("#d6d3cc")
SEV = {"CRITICAL": "#b42318", "HIGH": "#c4560c", "MODERATE": "#a16207", "WARN": "#a16207",
       "ERROR": "#b42318", "WARNING": "#a16207", "OK": "#15803d"}
TEAM = "Kamil Sztabert · Wiktor Gruszczyński · Kaja Kamieniecka · Filip Rodziewicz"

body = ParagraphStyle("b", fontName="R", fontSize=9, leading=12.2, textColor=INK)
small = ParagraphStyle("s", parent=body, fontSize=7.9, leading=10)
cellh = ParagraphStyle("h", parent=small, fontName="B", textColor=white)
bullet = ParagraphStyle("u", parent=body, leftIndent=12, bulletIndent=0, spaceAfter=1.5)


def code(s):
    return f'<font name="M" size="8.2">{s}</font>'


def sev(s):
    return f'<font name="B" color="{SEV[s]}">{s}</font>'


def P(s, st=body):
    return Paragraph(s, st)


def section(no, title):
    return P(f'<font name="R" size="9.5" color="#8a6d1f">{no}</font>&nbsp;&nbsp;<font name="G" size="14.5">{title}</font>',
             ParagraphStyle("x", parent=body, leading=19, spaceBefore=7, spaceAfter=3, keepWithNext=1))


def sub(title):
    return P(f"<b>{title}</b>", ParagraphStyle("y", parent=body, spaceBefore=4, spaceAfter=2, keepWithNext=1))


def bullets(items):
    return [Paragraph(i, bullet, bulletText="■") for i in items]


def table(head, rows, widths):
    data = ([[P(h, cellh) for h in head]] if head else []) + [[P(c, small) if isinstance(c, str) else c for c in r] for r in rows]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE)]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HEAD))
    st += [("BACKGROUND", (0, i), (-1, i), ZEBRA) for i in range(1 + bool(head), len(data), 2)]
    t.setStyle(TableStyle(st))
    return t


def header(subtitle, rows):
    info = Table([[P(f"<b>{k}</b>", small), P(v, small)] for k, v in rows], colWidths=[28 * mm, 146 * mm])
    info.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE), ("LINEABOVE", (0, 0), (-1, 0), 0.5, RULE),
                              ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return [P('<font name="G" size="30">QuestLog</font>', ParagraphStyle("t", parent=body, leading=34)),
            P(f'<font name="GI" size="12.5" color="#6b7280">{subtitle}</font>',
              ParagraphStyle("st", parent=body, leading=16, spaceAfter=6)),
            info]


def build(path, label, story):
    def frame(c, doc):
        c.saveState()
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(18 * mm, 284 * mm, 192 * mm, 284 * mm)
        c.line(18 * mm, 13 * mm, 192 * mm, 13 * mm)
        c.setFont("B", 7.5)
        c.setFillColor(GOLD)
        c.drawString(18 * mm, 286 * mm, "RAPORT PROJEKTOWY")
        c.setFont("R", 7.5)
        c.setFillColor(GREY)
        c.drawRightString(192 * mm, 286 * mm, label)
        c.drawString(18 * mm, 9.5 * mm, f"QuestLog — raport {label}")
        c.drawRightString(192 * mm, 9.5 * mm, str(doc.page))
        c.restoreState()

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm,
                            bottomMargin=18 * mm, title=f"QuestLog — raport {label}", author="QuestLog")
    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    assert doc.page <= 2, f"{path}: {doc.page} stron (limit 2)"


# --------------------------------------------------------------------------- L1
def l1():
    return [
        *header("Znajdź. Oceń. Skomentuj. — lekki serwis społecznościowy typu link-aggregator z głosowaniem na "
                "treści i drzewiastymi komentarzami", [
                    ("Raport", "L1 · Wybór aplikacji do implementacji"),
                    ("Przygotowano", "16 października 2026 · wersja robocza 1.0")]),

        section("01", "Czym jest QuestLog"),
        P("QuestLog to lekki serwis społecznościowy typu link-aggregator, zbudowany wokół trzech prostych mechanizmów: "
          "zgłaszania znalezisk, głosowania na nie oraz prowadzenia dyskusji w komentarzach. Projekt łączy najważniejsze "
          "elementy aplikacji webowej z kontem użytkownika — od rejestracji, przez tablicę treści, po system ocen i "
          "wielopoziomową dyskusję."),
        *bullets([
            "<b>Tablica znalezisk.</b> Użytkownicy wrzucają ciekawe linki i krótkie teksty na wspólną listę.",
            "<b>Głosy decydują.</b> Społeczność ocenia treści głosami w górę i w dół, wynosząc najlepsze wpisy na szczyt.",
            "<b>Dyskusja pod każdym wpisem.</b> Komentarze w formie drzewka, z nieograniczoną liczbą poziomów odpowiedzi.",
        ]),
        Spacer(1, 3),
        table(None, [[[P(n, ParagraphStyle("k", parent=body, fontName="G", fontSize=15, leading=17)), P(t, small)]
                      for n, t in [("3", "warstwy architektury: React, Flask, PostgreSQL"),
                                   ("4", "tabele w bazie: użytkownicy, wpisy, komentarze, głosy"),
                                   ("∞", "poziomów zagnieżdżenia odpowiedzi w komentarzach")]]], [58, 58, 58]),

        section("02", "Jak to działa"),
        table(["Krok", "Opis"], [
            ["<b>01 Konto</b>", "Użytkownik zakłada konto i loguje się — dodawanie wpisów, głosowanie i komentowanie "
             "wymagają zalogowania."],
            ["<b>02 Tablica</b>", "Przegląda tablicę znalezisk sortowaną według: gorące, najnowsze albo najlepsze."],
            ["<b>03 Dodawanie</b>", "Dodaje nowy wpis — link lub krótki tekst, opcjonalnie z tagiem tematycznym."],
            ["<b>04 Głosowanie</b>", "Oddaje głos (upvote albo downvote), a wynik aktualizuje się natychmiast."],
            ["<b>05 Komentarze</b>", "Dołącza do dyskusji — odpowiedzi układają się w drzewko pod znaleziskiem."],
        ], [32, 142]),

        section("03", "Funkcjonalności"),
        table(["Obszar", "Zakres"], [
            ["<b>Konto</b>", "Rejestracja i logowanie; dodawanie, głosowanie i komentowanie tylko po zalogowaniu."],
            ["<b>Tablica</b>", "Sortowanie wpisów: gorące, najnowsze, najlepsze."],
            ["<b>Nowy wpis</b>", "Tytuł, link lub krótki tekst, opcjonalnie tag tematyczny."],
            ["<b>Głosowanie</b>", "Upvote i downvote zarówno na wpisy, jak i na komentarze."],
            ["<b>Komentarze</b>", "Drzewiaste odpowiedzi z opcją przełączenia na widok płaski."],
            ["<b>Moje treści</b>", "Edycja i usuwanie własnych wpisów oraz komentarzy."],
        ], [32, 142]),

        section("04", "Komentarze drzewiaste"),
        P("Wyzwaniem projektu jest struktura komentarzy w formie drzewa, w której każda odpowiedź może mieć kolejne "
          f"odpowiedzi bez ograniczenia głębokości. Każdy komentarz ma pole {code('parent_id')}: puste oznacza komentarz "
          "główny, wypełnione wskazuje komentarz nadrzędny."),
        Spacer(1, 3),
        table(["Komentarz", "parent_id"], [
            ["Komentarz A", "brak"], ["&nbsp;&nbsp;&nbsp;→ Odpowiedź A1", "A"],
            ["&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ Odpowiedź A1a", "A1"], ["Komentarz B", "brak"],
        ], [87, 87]),

        section("05", "Technologie"),
        table(["React — front-end", "Python + Flask — back-end", "PostgreSQL — baza w kontenerze Docker"], [
            ["Komponenty: tablica, wpis, drzewo komentarzy, formularze.", "Prosty REST API i logika głosowania.",
             "Jedno polecenie na start, zapytania w zwykłym SQL."],
        ], [58, 58, 58]),

        section("06", "Model danych"),
        table(["User", "Post", "Comment", "Vote"], [
            ["id, username, email, password_hash, created_at", "id, title, url, body, author_id, created_at",
             "id, post_id, author_id, parent_id, body, created_at", "id, user_id, post_id lub comment_id, "
             "value (+1 / −1)"],
        ], [43.5, 43.5, 43.5, 43.5]),
        Spacer(1, 3),
        P("Kluczowe jest ograniczenie na poziomie bazy danych: jeden użytkownik może oddać tylko jeden głos na dany "
          "element (wpis lub komentarz), co gwarantuje spójność wyników głosowania."),

        section("07", "Kod na GitHubie"),
        *bullets([
            "<b>Historia zmian</b> — można wrócić do każdej wcześniejszej wersji kodu.",
            "<b>Praca w zespole</b> — osobne branche i pull requesty dla poszczególnych funkcjonalności.",
            "<b>Kopia zapasowa</b> w chmurze; <b>portfolio</b> — projekt widoczny na profilu.",
        ]),

        section("08", "Dlaczego ten projekt"),
        *bullets([
            "<b>Pełny cykl wytwarzania:</b> logowanie, formularze, CRUD, API i baza danych — komplet elementów typowej "
            "aplikacji webowej.",
            "<b>Ciekawe wyzwania techniczne:</b> drzewo komentarzy i unikalność głosu na poziomie SQL.",
            "<b>Łatwa rozbudowa:</b> zakres prac można dopasować do dostępnego czasu.",
        ]),
        Spacer(1, 2),
        P("<b>Kierunki rozwoju (na później):</b> system punktów XP i poziomów użytkowników, kategorie tematyczne wpisów "
          "oraz wyszukiwarka działająca po tagach."),
    ]


# --------------------------------------------------------------------------- L5
def l5():
    return [
        *header("Proces CI/CD w GitHub Actions: ciągła integracja i ciągłe wdrażanie", [
            ("Zespół", TEAM),
            ("Repozytorium", f"github.com/frodz1/webowka (workflow: {code('.github/workflows/ci-cd.yml')})"),
            ("Produkcja", "https://questlog.com.pl — dwie instancje OCI za load balancerem, baza Neon Postgres (L3)"),
            ("Data", "6 listopada 2026 · wersja 1.0 · stan na dzień sporządzenia raportu")]),

        section("01", "Cel i zakres"),
        P("Celem było wdrożenie procesu CI/CD dla aplikacji QuestLog (React, Flask, PostgreSQL), w którym każda zmiana "
          "jest weryfikowana automatycznie, a po zatwierdzeniu trafia na produkcję bez ręcznych kroków na serwerach. "
          "Całość działa na GitHubie (repozytorium, Actions, sekrety, reguły ochrony) i obejmuje infrastrukturę z L3. "
          "Czasy w sekcji 03 pochodzą z rzeczywistych przebiegów pipeline’u."),

        section("02", "Przebieg procesu"),
        table(None, [["<b>Pull request</b><br/>push do main", "<b>CI</b> (GitHub, równolegle)<br/>backend · frontend · "
                      "smoke", "<b>Bramka</b><br/>main + 3× zielone", "<b>CD</b> (self-hosted, OCI)<br/>deploy app1 → "
                      "deploy app2, health check, fail-fast"]], [36, 46, 34, 58]),
        Spacer(1, 3),
        P("Zmiana trafia na osobną gałąź i do pull requesta, gdzie uruchamiają się trzy niezależne kontrole; merge do "
          "main jest możliwy dopiero po ich pozytywnym wyniku. Po merge’u ten sam kod jest wdrażany kolejno na obie "
          "instancje. Na pull requestach job deploy jest pomijany."),

        section("03", "Integracja ciągła (CI)"),
        table(["Job", "Środowisko", "Co weryfikuje", "Czas"], [
            ["<b>backend</b>", "ubuntu-latest, PostgreSQL 16 (kontener usługi)",
             f"11 testów API (pytest) na osobnej bazie {code('questlog_test')}", "22–27 s"],
            ["<b>frontend</b>", "ubuntu-latest, Node 22", f"{code('npm ci')} (wersje z lockfile) i {code('vite build')}",
             "9–17 s"],
            ["<b>smoke</b>", "ubuntu-24.04-arm (arm64), Docker Compose", f"budowa obrazów, start stosu, "
             f"{code('GET /api/health')} przez Caddy; na main push przetestowanych obrazów do GHCR", "—"],
        ], [20, 46, 92, 16]),
        Spacer(1, 3),
        *bullets([
            "Joby działają równolegle, zależności pip i npm są buforowane; nowy commit w PR anuluje poprzedni przebieg.",
            "Obrazy ze smoke testu są tymi samymi, które trafiają na produkcję — po zielonym teście na main są "
            "wypychane do rejestru bez ponownego budowania.",
            "Dane bazy w jobie backend są jednorazowe: kontener istnieje tylko na czas testu.",
        ]),

        section("04", "Ciągłe wdrażanie (CD)"),
        P(f"Job {code('deploy')} rusza tylko po pushu do main i tylko gdy backend, frontend i smoke zakończyły się "
          "sukcesem. Wykonują go self-hosted runnery na obu instancjach OCI (etykiety app1, app2), jako usługi systemd "
          "na koncie bez sudo."),
        *bullets([
            f"<b>Rolling deploy:</b> macierz {code('host: [app1, app2]')} z {code('max-parallel: 1')} — gdy jedna maszyna "
            "jest aktualizowana, ruch obsługuje druga. <b>Fail-fast:</b> błąd na app1 zatrzymuje proces, app2 zostaje "
            "na działającej wersji.",
            f"<b>Kroki:</b> {code('git reset --hard')} do commita z CI, zapis sekretów i tagu obrazu, "
            f"{code('docker compose pull')} i {code('up -d')}, health check (30 prób co 2 s), sprzątanie obrazów.",
            "<b>Self-hosted runner:</b> reguła sieciowa z L3 dopuszcza SSH z jednego IP; runner łączy się z GitHubem "
            "wychodząco, więc nie otwieramy portów.",
            "<b>Rejestr:</b> obrazy budowane raz (arm64), publikowane do GHCR z tagiem SHA commita tylko z main; maszyny "
            "je pobierają tokenem joba. <b>Rollback:</b> git revert na main — pipeline wdraża poprzednią wersję.",
            "<b>Kolejka:</b> wdrożenia na tę samą maszynę nie nakładają się i nie są przerywane.",
        ]),

        section("05", "Zarządzanie sekretami"),
        *bullets([
            f"{code('DATABASE_URL')} i {code('SECRET_KEY')} to environment secrets środowiska production — dostępne "
            "tylko dla jobu deploy z gałęzi main, nie trafiają do przebiegów PR z forków.",
            f"Przy wdrożeniu zapisywane do {code('/opt/questlog/tools/.env')} (prawa 600), atomowo; pusty sekret "
            "przerywa wdrożenie. Jeden SECRET_KEY na obu instancjach (warunek poprawności JWT).",
            f"Rotacja: {code('gh secret set SECRET_KEY --env production')} i ponowne wdrożenie.",
            "W repozytorium i historii gita nie ma poświadczeń produkcyjnych; .env, .env.local i .neon są ignorowane. "
            "Usunięto też stare kopie sekretów z maszyn.",
        ]),

        section("06", "Kontrola zmian i bezpieczeństwo"),
        table(["Mechanizm", "Ustawienie", "Skutek"], [
            ["<b>Ruleset na main</b>", "wymagany PR; checki backend, frontend, smoke; zakaz usuwania i force-push",
             "do main trafia tylko zweryfikowany kod"],
            ["<b>Environment production</b>", "wdrożenia wyłącznie z gałęzi main", "inna gałąź nie wdroży na produkcję"],
            ["<b>PR z forków</b>", "zatwierdzenie dla każdego zewnętrznego współtwórcy",
             "obcy kod nie uruchomi się na runnerach"],
            ["<b>Token workflow</b>", code("permissions: contents: read"), "minimalne uprawnienia pipeline’u"],
        ], [36, 80, 58]),

        section("07", "Ograniczenia i podsumowanie"),
        *bullets([
            "Brak testów interfejsu (komponenty/E2E); smoke test obejmuje tylko /api/health.",
            "Obrazy tylko arm64, brak polityki retencji w GHCR; rollback ręczny (git revert); przez kilkanaście sekund "
            "wdrożenia instancje działają na różnych wersjach.",
            "Ruleset nie wymaga review (0) i administrator może go ominąć; runner na publicznym repo wymaga utrzymania.",
        ]),
        Spacer(1, 3),
        P("Zaimplementowano pełny proces CI/CD: trzy równoległe kontrole wymuszane regułami repozytorium oraz "
          "automatyczne, rolling wdrożenie na dwie instancje z health checkiem i zatrzymaniem w razie błędu. Sekrety są "
          "przechowywane centralnie w GitHubie, a zmiana przechodzi od merge’a do produkcji bez logowania na serwery. "
          "Proces działa produkcyjnie: kolejne zmiany z main były wdrażane automatycznie na obie instancje."),
        Spacer(1, 4),
        P(f"<b>Załączniki w repozytorium:</b> {code('.github/workflows/ci-cd.yml')} (pipeline), "
          f"{code('tools/README.md')} (sekcja CI/CD, konfiguracja runnerów), {code('Lab5-Questlog.pdf')} "
          "(prezentacja).", small),
    ]


# --------------------------------------------------------------------------- L6
def l6():
    return [
        *header("Elementy bezpieczeństwa w procesie CI/CD: SAST, SCA, DAST, sekrety, skan i podpis obrazów", [
            ("Zespół", TEAM),
            ("Repozytorium", f"github.com/frodz1/webowka · {code('.github/workflows/ci-cd.yml')} · PR #11"),
            ("Data", "16 listopada 2026 · wersja 1.2")]),

        section("01", "Cel i zakres"),
        P("Pipeline CI/CD z L5 rozszerzono o sześć kontroli bezpieczeństwa, z których każda blokuje wdrożenie: SAST, "
          "SCA, skan sekretów, skan obrazów Docker, DAST oraz podpis obrazów weryfikowany przy wdrożeniu. Na produkcję "
          "trafia tylko obraz przetestowany, przeskanowany i podpisany. Wyniki „przed” pochodzą z uruchomienia tych "
          "samych narzędzi w tych samych wersjach na kodzie sprzed zmian (commit 3043e14), a „po” z pipeline’u w "
          "GitHub Actions."),

        section("02", "Kontrole w pipeline"),
        table(["Rodzaj", "Narzędzie", "Job / moment", "Blokuje, gdy"], [
            ["<b>SAST</b>", "Semgrep 1.184 (p/default)", code("sast"), "jakiekolwiek znalezisko"],
            ["<b>Sekrety</b>", "Gitleaks 8.30", f"{code('secrets')}, cała historia gita",
             "wykryty sekret (maskowany w logu)"],
            ["<b>SCA</b>", "pip-audit 2.10, npm audit", f"{code('backend')}, {code('frontend')}",
             "znana podatność (npm: od HIGH, zależności produkcyjne)"],
            ["<b>Obrazy</b>", "Trivy 0.76", f"{code('smoke')}, po buildzie, przed pushem",
             "HIGH/CRITICAL z poprawką; wyjątki w .trivyignore z datą ważności"],
            ["<b>DAST</b>", "OWASP ZAP 2.17 baseline", f"{code('smoke')}, na działającym stosie",
             "ostrzeżenie spoza tools/zap-rules.tsv; raport HTML jako artefakt"],
            ["<b>Podpis</b>", "cosign 3.1, para kluczy", f"{code('smoke')} podpisuje, {code('deploy')} weryfikuje",
             "brak podpisu lub inny klucz: obraz nie zostaje uruchomiony"],
        ], [18, 38, 54, 64]),
        Spacer(1, 3),
        P(f"Na PR działają wszystkie skany; push do GHCR, podpis i deploy tylko na main. {code('deploy')} wymaga "
          f"zielonych {code('backend')}, {code('frontend')}, {code('sast')}, {code('secrets')} i {code('smoke')}.", small),

        section("03", "Wykryte podatności i poprawki"),
        table(["Narzędzie", "Znalezisko", "Poziom", "Poprawka"], [
            ["Semgrep", "Dockerfile backendu bez USER — aplikacja działała jako root", sev("ERROR"),
             "użytkownik systemowy app, USER app"],
            ["Semgrep", "5× akcja GitHuba po tagu (@v4) — tag można przestawić na złośliwy kod", sev("WARNING"),
             "akcje przypięte do pełnego SHA commita"],
            ["pip-audit, Trivy", "PyJWT 2.10.1: 17 wpisów, m.in. CVE-2026-102268 — obejście uwierzytelnienia, "
             "podrobienie JWT (biblioteka obsługuje logowanie)", sev("CRITICAL") + " 1<br/>" + sev("HIGH") + " 5",
             "PyJWT 2.15; testy 11/11"],
            ["pip-audit", "pytest 8.3.5: PYSEC-2026-1845", "—", "pytest 9.0"],
            ["Trivy", "zlib1g (Debian 13): CVE-2026-85091 (przepełnienie sterty), CVE-2026-76844", sev("HIGH") + " 2",
             "apt-get upgrade w Dockerfile (obraz bazowy nie miał łatki)"],
            ["Trivy", "binarka Caddy, golang.org/x/net: CVE-2026-78661 (DoS przy parsowaniu HTML)", sev("HIGH"),
             "brak wydania z poprawką; nie parsujemy HTML — wyjątek w .trivyignore do 31.01.2027"],
            ["npm audit", "vite 5 (tylko serwer deweloperski); esbuild, react-router", sev("HIGH") + " 1<br/>" +
             sev("MODERATE") + " 3", "nie trafiają do obrazu (tylko dist/) — bramka --omit=dev; aktualizacja "
             "zaplanowana"],
            ["ZAP", "brak CSP, X-Frame-Options, X-Content-Type-Options, Permissions-Policy (4 typy)", sev("WARN"),
             "nagłówki w Caddy; skrypt inline przeniesiony do theme.js (CSP bez unsafe-inline)"],
            ["ZAP", "3 typy informacyjne: cache, wykrycie SPA, COEP", "—", "ignorowane z uzasadnieniem"],
            ["Gitleaks", "brak sekretów w historii", sev("OK"), "—"],
        ], [21, 69, 23, 61]),

        section("04", "Wyniki w GitHub Actions"),
        P("Run 43851837934 (merge PR #11 do main): wszystkie joby zielone, od pushu do wdrożenia na obu maszynach "
          "3 min 27 s. Produkcja zwraca nowe nagłówki bezpieczeństwa."),
        Spacer(1, 3),
        table(["Kontrola", "Przed", "Po — wynik z logu pipeline’u"], [
            ["SAST (Semgrep)", "6", "Ran 501 rules on 62 files: <b>0 findings</b>"],
            ["Sekrety (Gitleaks)", "0", "11 commits scanned · <b>no leaks found</b>"],
            ["SCA (pip-audit)", "18", "<b>No known vulnerabilities found</b>"],
            ["SCA (npm audit, prod., ≥HIGH)", "0", "2 moderate (react-router), poniżej progu — <b>przechodzi</b>"],
            ["Obrazy (Trivy)", "1 CRITICAL, 8 HIGH", "backend i frontend: <b>0 HIGH/CRITICAL</b> (1 wyjątek)"],
            ["DAST (ZAP)", "7 typów ostrzeżeń", "8 URL-i · <b>PASS 65 · WARN 0 · FAIL 0</b> · IGNORE 3"],
            ["Podpis (cosign)", "—", "Pushing signature (oba obrazy); deploy app1 i app2: <b>The signatures were "
             "verified against the specified public key</b>, health check ok"],
        ], [42, 30, 102]),

        section("05", "Podpis obrazów i bezpieczeństwo pipeline’u"),
        *bullets([
            f"<b>Klucz:</b> prywatny (zaszyfrowany hasłem) i hasło tylko w sekretach repo; publiczny w "
            f"{code('tools/cosign.pub')}; cosign.key w .gitignore. Podpis po digeście, wpis w logu Sigstore (Rekor).",
            f"<b>Weryfikacja:</b> {code('cosign verify --key cosign.pub')} przed {code('docker compose pull')} na każdej "
            "maszynie — obraz bez podpisu nie zostanie uruchomiony, rolling deploy zatrzyma się na app1.",
            "<b>Pipeline:</b> akcje przypięte do SHA, skanery z obrazów o stałej wersji; minimalne uprawnienia tokenu "
            "(packages: write tylko w smoke); PR-y bez sekretów, niczego nie publikują ani nie podpisują.",
        ]),

        section("06", "Ograniczenia i podsumowanie"),
        *bullets([
            "ZAP baseline jest pasywny i bez logowania — kolejny krok: zap-api-scan na /api z tokenem testowym.",
            "Do aktualizacji: vite 5 i react-router 6 (zmiany łamiące); obraz Caddy przed wygaśnięciem wyjątku "
            "(31.01.2027). Kontener Caddy działa jako root (port 80). Brak cyklicznych skanów i eksportu SARIF.",
        ]),
        Spacer(1, 3),
        P("Pierwsze uruchomienie skanów wykazało realne problemy — krytyczną podatność biblioteki JWT, kontener jako "
          "root, brak nagłówków bezpieczeństwa i akcje po zmiennych tagach. Wszystkie poprawiono, a jedyny wyjątek bez "
          "dostępnej poprawki jest udokumentowany i ograniczony w czasie. Pipeline przeszedł w GitHub Actions, a "
          "produkcja działa na podpisanych i zweryfikowanych obrazach."),
    ]


if __name__ == "__main__":
    build("QuestLog_raport.pdf", "L1 · Wybór aplikacji do implementacji", l1())
    shutil.copy("QuestLog_raport.pdf", "tools/QuestLog_raport.pdf")
    build("QuestLog_raport_L5.pdf", "L5 · Proces CI/CD", l5())
    build("QuestLog_raport_L6.pdf", "L6 · Bezpieczeństwo CI/CD", l6())
