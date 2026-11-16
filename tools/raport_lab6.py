"""Generator raportu QuestLog_raport_L6.pdf (układ jak raport L5). Uruchom z katalogu głównego repo."""
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
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

body = ParagraphStyle("b", fontName="R", fontSize=9.5, leading=13.2, textColor=INK, alignment=TA_LEFT)
small = ParagraphStyle("s", parent=body, fontSize=8.3, leading=10.8)
cellh = ParagraphStyle("h", parent=small, fontName="B", textColor=white)
cap = ParagraphStyle("c", parent=small, fontName="I", textColor=GREY, alignment=1)
bullet = ParagraphStyle("u", parent=body, leftIndent=13, bulletIndent=0, spaceAfter=2.5)


def code(s):
    return f'<font name="M" size="8.6">{s}</font>'


def sev(s):
    return f'<font name="B" color="{SEV[s]}">{s}</font>'


def P(s, st=body):
    return Paragraph(s, st)


def section(no, title):
    return [P(f'<font name="R" size="10" color="#8a6d1f">{no}</font>&nbsp;&nbsp;<font name="G" size="17">{title}</font>',
              ParagraphStyle("x", parent=body, leading=22, spaceBefore=9, spaceAfter=4, keepWithNext=1))]


def sub(title):
    return P(f'<font name="B" size="10.5">{title}</font>', ParagraphStyle("y", parent=body, spaceBefore=6, spaceAfter=3, keepWithNext=1))


def bullets(items):
    return [Paragraph(i, bullet, bulletText="■") for i in items]


def table(head, rows, widths):
    data = [[P(h, cellh) for h in head]] + [[P(c, small) for c in r] for r in rows]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), HEAD), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
          ("LINEBELOW", (0, 1), (-1, -1), 0.5, RULE)]
    st += [("BACKGROUND", (0, i), (-1, i), ZEBRA) for i in range(2, len(data), 2)]
    t.setStyle(TableStyle(st))
    return t


def info(rows):
    t = Table([[P(f"<b>{k}</b>", small), P(v, small)] for k, v in rows], colWidths=[32 * mm, 138 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE), ("LINEABOVE", (0, 0), (-1, 0), 0.5, RULE),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def frame(c, doc):
    c.saveState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(20 * mm, 280 * mm, 190 * mm, 280 * mm)
    c.line(20 * mm, 15 * mm, 190 * mm, 15 * mm)
    c.setFont("B", 7.5)
    c.setFillColor(GOLD)
    c.drawString(20 * mm, 282 * mm, "RAPORT PROJEKTOWY")
    c.setFont("R", 7.5)
    c.setFillColor(GREY)
    c.drawRightString(190 * mm, 282 * mm, "L6 · Bezpieczeństwo CI/CD")
    c.drawString(20 * mm, 11 * mm, "QuestLog — raport L6 · Bezpieczeństwo CI/CD")
    c.drawRightString(190 * mm, 11 * mm, str(doc.page))
    c.restoreState()


story = [
    Spacer(1, 4),
    P('<font name="G" size="38">QuestLog</font>', ParagraphStyle("t", parent=body, leading=44)),
    P('<font name="GI" size="14" color="#6b7280">Elementy bezpieczeństwa w procesie CI/CD: SAST, SCA, DAST, '
      'sekrety, skan i podpis obrazów</font>', ParagraphStyle("st", parent=body, leading=19, spaceAfter=10)),
    info([("Zespół", "Kamil Sztabert · Wiktor Gruszczyński · Kaja Kamieniecka · Filip Rodziewicz"),
          ("Repozytorium", f"github.com/frodz1/webowka (workflow: {code('.github/workflows/ci-cd.yml')})"),
          ("Produkcja", "https://questlog.com.pl — dwie instancje OCI za load balancerem (L3), pipeline CI/CD z L5"),
          ("Data", "16 listopada 2026 · wersja 1.0 · stan na dzień sporządzenia raportu")]),

    *section("01", "Cel i zakres"),
    P("Celem było rozszerzenie pipeline’u CI/CD z L5 o automatyczne kontrole bezpieczeństwa tak, aby zmiana z "
      "podatnością, wyciekiem sekretu lub niepodpisanym obrazem nie mogła trafić na produkcję. Dodano sześć "
      "elementów: analizę statyczną kodu (SAST), analizę zależności (SCA), skan sekretów, skan obrazów Docker, "
      "skan dynamiczny działającej aplikacji (DAST) oraz podpisywanie obrazów z weryfikacją podpisu przy wdrożeniu."),
    Spacer(1, 4),
    P("Wyniki „przed” w sekcji 03 pochodzą z pierwszego uruchomienia tych samych narzędzi, w tych samych wersjach "
      "co w pipeline, na stanie repozytorium sprzed zmian (gałąź l5-registry, commit 3043e14). Wszystkie wykryte "
      "problemy poprawiono albo opisano jako świadomy wyjątek; wyniki „po” dotyczą kodu po poprawkach."),

    *section("02", "Kontrole w pipeline"),
    table(["Rodzaj", "Narzędzie", "Job / moment", "Blokuje pipeline, gdy"], [
        ["<b>SAST</b>", "Semgrep 1.184, reguły p/default", f"{code('sast')}, każdy PR i push",
         "jakiekolwiek znalezisko (--error)"],
        ["<b>Sekrety</b>", "Gitleaks 8.30", f"{code('secrets')}, cała historia gita",
         "wykryty sekret (w logach maskowany, --redact)"],
        ["<b>SCA</b>", "pip-audit 2.10, npm audit", f"{code('backend')}, {code('frontend')}",
         "znana podatność w zależnościach Pythona; npm: od HIGH w zależnościach produkcyjnych"],
        ["<b>Obrazy</b>", "Trivy 0.76", f"{code('smoke')}, po buildzie, przed startem i pushem",
         "HIGH/CRITICAL z dostępną poprawką (wyjątki: .trivyignore z datą ważności)"],
        ["<b>DAST</b>", "OWASP ZAP 2.17 (baseline)", f"{code('smoke')}, na uruchomionym stosie",
         "każde ostrzeżenie poza regułami w tools/zap-rules.tsv; raport HTML jako artefakt"],
        ["<b>Podpis</b>", "cosign 3.1 (para kluczy)", f"{code('smoke')} podpisuje (main), {code('deploy')} weryfikuje",
         "brak podpisu lub podpis innym kluczem: obraz nie zostaje uruchomiony"],
    ], [22, 40, 50, 58]),
    Spacer(1, 4),
    P(f"Job {code('deploy')} wymaga teraz pięciu zielonych jobów: {code('backend')}, {code('frontend')}, "
      f"{code('sast')}, {code('secrets')} i {code('smoke')}. Obrazy są skanowane i testowane przed publikacją, "
      "więc do GHCR trafia wyłącznie obraz, który przeszedł wszystkie kontrole.", body),

    *section("03", "Wykryte podatności i poprawki"),
    sub("SAST — Semgrep: 6 znalezisk"),
    table(["Reguła", "Poziom", "Miejsce", "Opis / poprawka"], [
        ["missing-user-entrypoint", sev("ERROR"), "code/backend/Dockerfile",
         "Kontener backendu działał jako root. Dodano użytkownika systemowego app i USER app."],
        ["github-actions-mutable-action-tag (5x)", sev("WARNING"), ".github/workflows/ci-cd.yml (checkout x3, "
         "setup-python, setup-node)", "Akcje wskazywane tagiem (@v4), który właściciel może przestawić na inny kod "
         "(atak na łańcuch dostaw, por. przejęcie trivy-action). Wszystkie akcje przypięto do pełnego SHA commita."],
    ], [40, 23, 42, 65]),
    sub("Sekrety — Gitleaks: 0 znalezisk"),
    P("Historia repozytorium nie zawiera poświadczeń (potwierdza to ustalenie z L5). Pliki .env, .env.local i .neon "
      "są ignorowane przez gita; dodatkowo ignorowany jest prywatny klucz cosign.key."),
    sub("SCA — pip-audit: 18 podatności w 2 pakietach"),
    table(["Pakiet", "Wersja", "Podatności", "Poprawka"], [
        ["PyJWT", "2.10.1", "17 wpisów (m.in. PYSEC-2026-4140…4183, GHSA-pxh4-856f-4h89): obejście uwierzytelnienia, "
         "podrobienie tokenu JWT, akceptacja pustego klucza HMAC",
         "PyJWT==2.15.* (naprawione w 2.14/2.15). Aplikacja używa PyJWT do tokenów logowania, więc to "
         "najpoważniejsze znalezisko."],
        ["pytest", "8.3.5", "PYSEC-2026-1845", "pytest==9.0.* (naprawione w 9.0.3)"],
    ], [20, 16, 72, 62]),
    Spacer(1, 3),
    P("Po aktualizacji: pip-audit „No known vulnerabilities found”, 11/11 testów API przechodzi.", small),
    sub("SCA — npm audit: 4 podatności"),
    table(["Pakiet", "Poziom", "Opis", "Decyzja"], [
        ["vite (dev)", sev("HIGH"), "Path traversal i obejścia server.fs w serwerze deweloperskim; zależny esbuild",
         "Dotyczy tylko serwera deweloperskiego (vite dev). Obraz produkcyjny zawiera wyłącznie zbudowane pliki "
         "dist/, dlatego bramka sprawdza zależności produkcyjne (--omit=dev)."],
        ["esbuild (dev)", sev("MODERATE"), "Dowolna strona może czytać odpowiedzi serwera deweloperskiego",
         "jw.; aktualizacja do vite 8 to zmiana łamiąca (sekcja 07)"],
        ["react-router,<br/>react-router-dom", sev("MODERATE"), "Open redirect przez backslash w &lt;Link&gt;/"
         "useNavigate; wstrzyknięcie konstruktora w hydracji SSR (nie używamy SSR)",
         "Poniżej progu HIGH; poprawka wymaga migracji do v7.18 (sekcja 07)"],
    ], [26, 24, 55, 65]),
    sub("Skan obrazów — Trivy: 9 podatności (1 CRITICAL, 8 HIGH)"),
    table(["Obraz / komponent", "Podatność", "Poziom", "Poprawka"], [
        ["backend: PyJWT 2.10.1", "CVE-2026-102268 (obejście uwierzytelnienia przez błędną walidację klucza)",
         sev("CRITICAL"), "aktualizacja PyJWT (jak wyżej)"],
        ["backend: PyJWT 2.10.1", "CVE-2026-102267, CVE-2026-102271, CVE-2026-32597, CVE-2026-48526, "
         "GHSA-pxh4-856f-4h89", sev("HIGH") + " x5", "aktualizacja PyJWT"],
        ["backend: zlib1g (Debian 13)", "CVE-2026-85091 (przepełnienie sterty w gz_vacate), CVE-2026-76844",
         sev("HIGH") + " x2", "Poprawka jest w Debianie (deb13u1), ale obraz bazowy python:3.12-slim jej jeszcze nie "
         "zawiera. Dodano apt-get upgrade w Dockerfile."],
        ["frontend: binarka Caddy (golang.org/x/net 0.60)", "CVE-2026-78661 (DoS przy parsowaniu HTML)", sev("HIGH"),
         "Brak wydania Caddy z poprawką (2.11.9 to najnowsza). Caddyfile nie parsuje HTML (brak templates). "
         "Wyjątek w .trivyignore, ważny do 31.01.2027; potem skan znów zablokuje pipeline."],
    ], [37, 60, 22, 51]),
    sub("DAST — OWASP ZAP baseline: 7 typów ostrzeżeń"),
    table(["ID", "Ostrzeżenie", "Liczba", "Poprawka"], [
        ["10038", "Brak Content-Security-Policy", "3",
         "CSP: default-src 'self', frame-ancestors 'none', object-src 'none' i inne. Skrypt motywu z index.html "
         "przeniesiono do public/theme.js, żeby nie dopuszczać skryptów inline."],
        ["10020", "Brak ochrony przed clickjackingiem", "3", "X-Frame-Options: DENY (oraz frame-ancestors w CSP)"],
        ["10021", "Brak X-Content-Type-Options", "5", "X-Content-Type-Options: nosniff"],
        ["10063", "Brak Permissions-Policy", "4", "Permissions-Policy: camera=(), microphone=(), geolocation=()"],
        ["10049", "Storable and Cacheable Content", "5", "Informacyjne; długi cache zasobów z hashem jest celowy (ignorowane)"],
        ["10109", "Modern Web Application", "3", "Informacyjne: wykrycie SPA (ignorowane)"],
        ["90004", "Brak Cross-Origin-Embedder-Policy", "11",
         "Aplikacja nie używa SharedArrayBuffer ani izolacji cross-origin (ignorowane)"],
    ], [13, 50, 15, 92]),
    Spacer(1, 3),
    P("Nagłówki ustawia Caddy (code/frontend/Caddyfile) dla wszystkich odpowiedzi; usunięto też nagłówek Server. "
      "Trzy ignorowane reguły mają uzasadnienie w tools/zap-rules.tsv. Pozostałe ostrzeżenia blokują pipeline.", small),

    *section("04", "Wyniki przed i po"),
    table(["Kontrola", "Przed", "Po"], [
        ["SAST (Semgrep)", "6 (1 ERROR, 5 WARNING)", sev("OK") + " 0"],
        ["Sekrety (Gitleaks)", "0", sev("OK") + " 0"],
        ["SCA Python (pip-audit)", "18 w 2 pakietach", sev("OK") + " 0"],
        ["SCA npm (npm audit, produkcyjne, od HIGH)", "0 (wszystkie 4 w zależnościach deweloperskich lub MODERATE)",
         sev("OK") + " 0; 4 w dev/MODERATE do aktualizacji"],
        ["Obrazy (Trivy, HIGH/CRITICAL)", "backend 8, frontend 1", sev("OK") + " 0 (1 udokumentowany wyjątek)"],
        ["DAST (ZAP)", "7 typów ostrzeżeń, 61 PASS", sev("OK") + " 0 ostrzeżeń, 65 PASS, 3 ignorowane"],
    ], [60, 60, 50]),

    *section("05", "Podpisywanie obrazów i klucz"),
    *bullets([
        "<b>Para kluczy cosign:</b> klucz prywatny (zaszyfrowany hasłem) i hasło są przechowywane wyłącznie jako "
        f"sekrety repozytorium ({code('COSIGN_PRIVATE_KEY')}, {code('COSIGN_PASSWORD')}). Klucz publiczny "
        f"{code('tools/cosign.pub')} jest w repozytorium, a plik cosign.key jest ignorowany przez gita.",
        "<b>Podpis:</b> po pushu do GHCR (tylko main) job smoke podpisuje każdy obraz po digeście (sha256), nie po "
        "tagu, więc podpis dotyczy dokładnie tego obrazu, który przeszedł testy i skany. Podpis jest też zapisywany "
        "w publicznym rejestrze przejrzystości Sigstore (Rekor).",
        f"<b>Weryfikacja:</b> job deploy na każdej maszynie wykonuje {code('cosign verify --key cosign.pub')} przed "
        f"{code('docker compose pull')}. Obraz bez podpisu lub podpisany innym kluczem nie zostanie uruchomiony, "
        "a rolling deploy zatrzyma się na pierwszej maszynie.",
        "<b>Rotacja klucza:</b> wygenerowanie nowej pary, podmiana sekretów i commit nowego cosign.pub; kolejne "
        "wdrożenie podpisze i zweryfikuje obrazy nowym kluczem.",
    ]),

    *section("06", "Bezpieczeństwo samego pipeline’u"),
    *bullets([
        "<b>Akcje przypięte do SHA</b> (checkout, setup-python, setup-node, upload-artifact, cosign-installer). "
        "Narzędzia skanujące uruchamiane są z obrazów o konkretnej wersji, a nie z akcji pobieranej po tagu.",
        "<b>Minimalne uprawnienia tokenu:</b> domyślnie contents: read; packages: write tylko w smoke, packages: read "
        "tylko w deploy. Klucz cosign nie wymaga dodatkowych uprawnień (np. id-token).",
        "<b>PR-y nie mają dostępu do sekretów</b> i niczego nie publikują ani nie podpisują: push, podpis i deploy "
        "działają tylko dla pushu na main. PR-y z forków wymagają zatwierdzenia (L5).",
        "<b>Logi:</b> Gitleaks maskuje znalezione sekrety (--redact), bo logi Actions publicznego repozytorium są "
        "jawne.",
        "<b>Ruleset na main:</b> do wymaganych checków należy dodać sast i secrets (obok backend, frontend, smoke).",
    ]),

    *section("07", "Ograniczenia i dalszy rozwój"),
    *bullets([
        "<b>DAST</b> to skan pasywny (baseline) bez logowania: nie atakuje aktywnie API ani stron wymagających "
        "uwierzytelnienia. Następny krok: zap-api-scan na endpointach /api z tokenem testowego użytkownika.",
        "<b>Zależności frontendu:</b> vite 5 (HIGH, tylko dev) i react-router 6 (MODERATE) wymagają aktualizacji do "
        "wersji z poprawkami (vite 6.4.4+/8, react-router 7.18+); to zmiany łamiące, zaplanowane osobno.",
        "<b>Wyjątek dla Caddy</b> wygasa 31.01.2027; do tego czasu należy zaktualizować obraz bazowy caddy:2-alpine.",
        "<b>Kontener frontendu</b> (oficjalny obraz Caddy) działa jako root, żeby nasłuchiwać na porcie 80; można "
        "przejść na port nieuprzywilejowany i USER caddy.",
        "<b>Wyniki skanów</b> są widoczne w logach jobów; nie są wysyłane w formacie SARIF do zakładki Security "
        "(code scanning), co ułatwiłoby śledzenie znalezisk w czasie.",
        "<b>Nowe CVE</b> pojawiają się bez zmian w kodzie, a skany uruchamiają się tylko przy PR i pushu; warto dodać "
        "cykliczny przebieg (schedule) dla obrazów z produkcji.",
    ]),

    *section("08", "Podsumowanie"),
    P("Pipeline z L5 został rozszerzony o sześć kontroli bezpieczeństwa, które blokują wdrożenie. Już pierwsze "
      "uruchomienie wykazało realne problemy: krytyczną podatność biblioteki JWT odpowiedzialnej za logowanie, "
      "kontener działający jako root, brak nagłówków bezpieczeństwa i akcje GitHuba pobierane po zmiennych tagach. "
      "Wszystkie zostały poprawione, a jeden wyjątek bez dostępnej poprawki jest udokumentowany i ograniczony w czasie. "
      "Na produkcję trafiają wyłącznie obrazy przeskanowane, przetestowane i podpisane, a maszyny weryfikują podpis "
      "przed uruchomieniem."),
    Spacer(1, 5),
    P(f"<b>Załączniki w repozytorium:</b> {code('.github/workflows/ci-cd.yml')} (pipeline), {code('.trivyignore')}, "
      f"{code('tools/zap-rules.tsv')}, {code('tools/cosign.pub')}, {code('tools/README.md')} (sekcja „Skany "
      "bezpieczeństwa”).", small),
]

SimpleDocTemplate("QuestLog_raport_L6.pdf", pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                  topMargin=22 * mm, bottomMargin=22 * mm, title="QuestLog — raport L6",
                  author="QuestLog").build(story, onFirstPage=frame, onLaterPages=frame)
