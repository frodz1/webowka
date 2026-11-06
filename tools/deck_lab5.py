"""Generator prezentacji Lab5-Questlog.pdf (format i paleta jak w QuestLog.pdf z L1)."""
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = 720, 405.36
INK = HexColor("#1b1535")
BG = HexColor("#f1eefb")
ACCENT = HexColor("#7c5cff")
AMBER = HexColor("#f5a524")
SLATE = HexColor("#64748b")
TEAL = HexColor("#2dd4bf")
LILAC = HexColor("#a78bfa")

S = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("B", S + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("R", S + "Arial.ttf"))

c = canvas.Canvas("Lab5-Questlog.pdf", pagesize=(W, H))
page = 0


def text(x, y, s, size=11, font="R", color=INK, align="l"):
    c.setFont(font, size)
    c.setFillColor(color)
    {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[align](x, y, s)


def wrap(x, y, s, width, size=10, font="R", color=SLATE, leading=None):
    """Łamie tekst na szerokość width i zwraca y pod ostatnią linią."""
    leading = leading or size * 1.35
    c.setFont(font, size)
    c.setFillColor(color)
    line = ""
    for word in s.split():
        trial = f"{line} {word}".strip()
        if pdfmetrics.stringWidth(trial, font, size) > width and line:
            c.drawString(x, y, line)
            y -= leading
            line = word
        else:
            line = trial
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def check(x, y, col, size=7):
    """Ptaszek rysowany kreskami — Arial nie ma glifu U+2713."""
    c.setStrokeColor(col)
    c.setLineWidth(2.4)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x + size * 0.42, y - size * 0.46)
    p.lineTo(x + size * 1.25, y + size * 0.62)
    c.drawPath(p, stroke=1, fill=0)


def box(x, y, w, h, fill=white, stroke=None, r=7, lw=1.2):
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, stroke=1 if stroke else 0, fill=1)


def slide(title, kicker=None):
    """Zaczyna jasny slajd z nagłówkiem; zwraca y, od którego rysujemy treść."""
    global page
    page += 1
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if kicker:
        text(48, H - 44, kicker.upper(), 8, "B", ACCENT)
    text(48, H - 72, title, 22, "B", INK)
    c.setStrokeColor(AMBER)
    c.setLineWidth(3)
    c.line(48, H - 84, 48 + 46, H - 84)
    text(W - 48, 26, str(page), 9, "B", LILAC, "r")
    return H - 112


def arrow(x1, y1, x2, y2, color=LILAC, lw=1.4, head=5):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)
    if y1 == y2:  # poziomo
        d = 1 if x2 > x1 else -1
        p = c.beginPath()
        p.moveTo(x2, y2)
        p.lineTo(x2 - d * head, y2 + head * 0.6)
        p.lineTo(x2 - d * head, y2 - head * 0.6)
    else:  # pionowo
        d = 1 if y2 > y1 else -1
        p = c.beginPath()
        p.moveTo(x2, y2)
        p.lineTo(x2 + head * 0.6, y2 - d * head)
        p.lineTo(x2 - head * 0.6, y2 - d * head)
    p.close()
    c.drawPath(p, stroke=0, fill=1)



def bullets(y, items, col):
    for b in items:
        c.setFillColor(col)
        c.circle(54, y + 4, 2.6, stroke=0, fill=1)
        y = wrap(64, y, b, W - 128, 11.5) - 9
    return y


EDGE = HexColor("#e2d9f7")

# ---------------------------------------------------------------- 1. tytuł
page += 1
c.setFillColor(INK)
c.rect(0, 0, W, H, stroke=0, fill=1)
c.setFillColor(ACCENT)
c.circle(W - 70, H - 60, 120, stroke=0, fill=1)
c.setFillColor(INK)
c.circle(W - 70, H - 60, 104, stroke=0, fill=1)
text(56, 232, "QuestLog", 46, "B", white)
text(56, 200, "Od pull requesta do produkcji bez logowania na serwer.", 13, "R", LILAC)
c.setStrokeColor(AMBER)
c.setLineWidth(3)
c.line(56, 176, 56 + 60, 176)
text(56, 142, "L5. Proces CI/CD", 13, "B", white)
text(56, 120, "GitHub Actions  ·  self-hosted runnery na OCI  ·  questlog.com.pl", 10, "R", SLATE)
c.showPage()

# ------------------------------------------------- 2. wymagania i realizacja
y = slide("Wymagania zadania", "co było do zrobienia")
rows = [
    ("Projekt procesu CI/CD", "Jeden pipeline w GitHub Actions: CI na każdym PR, CD po merge'u do main", ACCENT),
    ("Automatyczna weryfikacja", "Testy API na PostgreSQL 16, build frontu, smoke test całego stacku w Dockerze", TEAL),
    ("Automatyczne wdrożenie", "Rolling deploy na app1 i app2 z health checkiem po każdej maszynie", AMBER),
    ("Prezentacja implementacji", "Ten deck oraz przebieg na żywo w zakładce Actions repozytorium", LILAC),
]
for name, how, col in rows:
    box(48, y - 46, W - 96, 54, white, EDGE)
    c.setFillColor(col)
    c.roundRect(48, y - 46, 5, 54, 2.5, stroke=0, fill=1)
    text(68, y - 10, name, 12, "B", INK)
    wrap(68, y - 28, how, W - 150, 9.5)
    check(W - 78, y - 24, col)
    y -= 66
c.showPage()

# ------------------------------------------------------ 3. schemat pipeline'u
y = slide("Pipeline", ".github/workflows/ci-cd.yml")
# Pull request
box(48, 195, 110, 42, white, ACCENT, lw=1.6)
text(103, 220, "Pull request", 10.5, "B", INK, "c")
text(103, 205, "lub push na main", 7.5, "R", SLATE, "c")
arrow(158, 216, 178, 216)
# CI
c.setStrokeColor(LILAC)
c.setLineWidth(1.4)
c.line(180, 161, 180, 271)
c.line(370, 161, 370, 271)
for by, name, sub in ((250, "backend", "pytest + Postgres 16"), (195, "frontend", "npm ci + vite build"), (140, "smoke", "compose up + /api/health")):
    box(198, by, 150, 42, white, HexColor("#cfc3ef"))
    text(273, by + 25, name, 10.5, "B", INK, "c")
    text(273, by + 10, sub, 7.5, "R", SLATE, "c")
    arrow(180, by + 21, 196, by + 21)
    c.setStrokeColor(LILAC)
    c.line(348, by + 21, 370, by + 21)
arrow(370, 216, 390, 216)
# bramka
box(392, 195, 120, 42, white, AMBER, lw=1.6)
text(452, 220, "Bramka", 10.5, "B", INK, "c")
text(452, 205, "main + 3 × zielone", 7.5, "R", SLATE, "c")
arrow(512, 216, 552, 216)
# CD
for by, name in ((195, "deploy app1"), (115, "deploy app2")):
    box(554, by, 118, 42, white, TEAL, lw=1.6)
    text(613, by + 25, name, 10.5, "B", INK, "c")
    text(613, by + 10, "self-hosted runner", 7.5, "R", SLATE, "c")
arrow(613, 193, 613, 159)
text(620, 172, "health OK", 7.5, "B", TEAL)
# ramki środowisk
c.setStrokeColor(HexColor("#d6cbf2"))
c.setLineWidth(1)
c.setDash(3, 3)
c.roundRect(170, 128, 210, 172, 8, stroke=1, fill=0)
c.roundRect(542, 104, 142, 156, 8, stroke=1, fill=0)
c.setDash()
text(178, 290, "ubuntu-latest  ·  GitHub", 7.5, "B", LILAC)
text(550, 250, "OCI  ·  environment production", 7, "B", LILAC)
y = 82
y = bullets(y, [
    "Na pull requeście działa tylko CI; job deploy jest pomijany, a ruleset blokuje merge przy czerwonym checku.",
    "Rollback to git revert na main — pipeline sam wdroży poprzednią wersję.",
], AMBER)
c.showPage()

# ------------------------------------------------------ 4. CI
y = slide("Ciągła integracja", "co sprawdzamy na każdym PR")
cards = [
    ("backend", "11 testów API na prawdziwym PostgreSQL 16 uruchomionym jako kontener usługi.", ACCENT),
    ("frontend", "npm ci + vite build: zależności z lockfile'a i kompilacja całej aplikacji React.", LILAC),
    ("smoke", "docker compose up --wait całego stacku i zapytanie przez Caddy do /api/health.", TEAL),
]
for i, (name, desc, col) in enumerate(cards):
    x = 48 + i * 212
    box(x, y - 104, 196, 112, white, EDGE)
    c.setFillColor(col)
    c.roundRect(x, y - 104, 196, 4, 2, stroke=0, fill=1)
    text(x + 18, y - 22, name, 15, "B", col)
    wrap(x + 18, y - 46, desc, 162, 9.5)
y -= 136
bullets(y, [
    "Joby idą równolegle na maszynach GitHuba; cache pip i npm skraca kolejne przebiegi.",
    "Nowy commit w PR anuluje poprzedni przebieg (concurrency), więc nie czekamy na nieaktualne wyniki.",
    "Smoke test buduje te same Dockerfile'e, które trafiają na produkcję — błąd w obrazie wychodzi przed merge'em.",
], ACCENT)
c.showPage()

# ------------------------------------------------------ 5. dlaczego self-hosted
y = slide("Ciągłe wdrażanie", "dlaczego self-hosted runner")
box(48, y - 110, 300, 118, white, EDGE)
text(66, y - 18, "SSH z GitHuba", 15, "B", SLATE)
yy = y - 44
for r in ["port 22 otwarty dla puli adresów GitHuba", "klucz SSH w sekretach repozytorium", "łamie regułę nsg-app z L3"]:
    text(66, yy, "·  " + r, 10, "R", SLATE)
    yy -= 18
box(372, y - 110, 300, 118, white, TEAL, lw=1.6)
text(390, y - 18, "Runner na VM", 15, "B", TEAL)
yy = y - 44
for r in ["łączy się z GitHubem wychodząco (443)", "żadnych nowych reguł w sieci", "sekrety zostają w .env na maszynie"]:
    text(390, yy, "·  " + r, 10, "R", SLATE)
    yy -= 18
y -= 134
bullets(y, [
    "Każda maszyna ma własny runner z etykietą app1 lub app2 — job wskazuje maszynę etykietą.",
    "Runner działa jako usługa systemd na koncie gha w grupie docker, bez uprawnień roota.",
    "Logi wdrożenia, czas i wersja widoczne w GitHubie, bez logowania się na serwer.",
], TEAL)
c.showPage()

# ------------------------------------------------------ 6. rolling deploy
y = slide("Rolling deploy", "jedna maszyna naraz, druga trzyma ruch")
chain = [("git reset --hard", "dokładnie ten commit, który przeszedł CI", AMBER), ("compose up --build", "przebudowa obrazów na maszynie", LILAC), ("curl /api/health", "15 prób co 2 s", ACCENT), ("następna maszyna", "dopiero po zielonym health checku", TEAL)]
for i, (top, bot, col) in enumerate(chain):
    x = 48 + i * 162
    box(x, y - 74, 146, 82, white, EDGE)
    c.setFillColor(col)
    c.roundRect(x, y - 74, 146, 4, 2, stroke=0, fill=1)
    wrap(x + 14, y - 16, top, 120, 11, "B", INK)
    wrap(x + 14, y - 40, bot, 120, 9.5)
    if i < 3:
        arrow(x + 148, y - 32, x + 160, y - 32)
y -= 100
bullets(y, [
    "Gdy app1 restartuje kontenery, health check load balancera kieruje cały ruch na app2.",
    "Padnie app1 — app2 w ogóle nie startuje i dalej serwuje starą, działającą wersję.",
    "Wdrożenia na tę samą maszynę nie nakładają się: kolejny merge czeka w kolejce.",
    "Schemat bazy tworzy się idempotentnie przy starcie backendu, więc deploy nie wymaga ręcznych migracji.",
], AMBER)
c.showPage()

# ------------------------------------------------------ 7. bezpieczeństwo
y = slide("Zabezpieczenia", "kto i co może wdrożyć")
rows = [
    ("Ruleset na main", "zmiany tylko przez PR, merge wymaga zielonych backend, frontend i smoke", ACCENT),
    ("Environment production", "wdrożenie możliwe wyłącznie z gałęzi main", TEAL),
    ("PR z forków", "wymagają zatwierdzenia — obcy kod nie trafi na nasze runnery", AMBER),
    ("Minimalne uprawnienia", "token workflow tylko do odczytu, brak sekretów w GitHubie", LILAC),
]
for name, how, col in rows:
    box(48, y - 46, W - 96, 54, white, EDGE)
    c.setFillColor(col)
    c.roundRect(48, y - 46, 5, 54, 2.5, stroke=0, fill=1)
    text(68, y - 10, name, 12, "B", INK)
    wrap(68, y - 28, how, W - 150, 9.5)
    check(W - 78, y - 24, col)
    y -= 66
c.showPage()

# ------------------------------------------------------ 8. podziękowanie
page += 1
c.setFillColor(INK)
c.rect(0, 0, W, H, stroke=0, fill=1)
c.setFillColor(ACCENT)
c.circle(80, 70, 120, stroke=0, fill=1)
c.setFillColor(INK)
c.circle(80, 70, 104, stroke=0, fill=1)
text(W - 56, 212, "Dziękuję za uwagę", 38, "B", white, "r")
c.setStrokeColor(AMBER)
c.setLineWidth(3)
c.line(W - 56 - 60, 190, W - 56, 190)
text(W - 56, 158, "github.com/frodz1/webowka/actions", 14, "B", LILAC, "r")
text(W - 56, 136, "QuestLog  ·  L5. Proces CI/CD", 10, "R", SLATE, "r")
c.showPage()

c.save()
print("gotowe")
