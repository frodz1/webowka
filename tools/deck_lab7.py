"""Generator prezentacji Lab7-Questlog.pdf (format i paleta jak w Lab5-Questlog.pdf)."""
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
EDGE = HexColor("#e2d9f7")
RED = HexColor("#e5484d")
CODE_BG = HexColor("#221b40")

S = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("B", S + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("R", S + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("M", S + "Courier New.ttf"))

c = canvas.Canvas("Lab7-Questlog.pdf", pagesize=(W, H))
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
    d = 1 if x2 > x1 else -1  # tylko poziome strzałki
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - d * head, y2 + head * 0.6)
    p.lineTo(x2 - d * head, y2 - head * 0.6)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def bullets(y, items, col, x=54, width=W - 128, size=11):
    for b in items:
        c.setFillColor(col)
        c.circle(x, y + 4, 2.6, stroke=0, fill=1)
        y = wrap(x + 10, y, b, width, size) - 7
    return y


def rows(y, items, h=48, gap=10):
    """Lista pasków nazwa + opis z ptaszkiem (jak „Wymagania” w L5)."""
    for name, how, col in items:
        box(48, y - h + 8, W - 96, h, white, EDGE)
        c.setFillColor(col)
        c.roundRect(48, y - h + 8, 5, h, 2.5, stroke=0, fill=1)
        text(68, y - 9, name, 12, "B", INK)
        wrap(68, y - 26, how, W - 160, 9.5)
        check(W - 78, y - h / 2 + 8, col)
        y -= h + gap
    return y


def cards(y, items, h=112, size=9.5):
    """Karty w jednym rzędzie: (tytuł, opis, kolor)."""
    n = len(items)
    cw = (W - 96 - (n - 1) * 14) / n
    for i, (name, desc, col) in enumerate(items):
        x = 48 + i * (cw + 14)
        box(x, y - h, cw, h + 8, white, EDGE)
        c.setFillColor(col)
        c.roundRect(x, y - h, cw, 4, 2, stroke=0, fill=1)
        text(x + 14, y - 16, name, 13, "B", col)
        wrap(x + 14, y - 36, desc, cw - 28, size)
    return y - h - 22


def code_box(x, y, w, lines, size=7.6, title=None):
    """Ciemne pole z tekstem o stałej szerokości; y = górna krawędź."""
    lh = size * 1.45
    h = len(lines) * lh + 18 + (14 if title else 0)
    box(x, y - h, w, h, CODE_BG, r=6)
    yy = y - 14
    if title:
        text(x + 12, yy, title, 7.5, "B", LILAC)
        yy -= 14
    for ln, col in lines:
        text(x + 12, yy, ln, size, "M", col)
        yy -= lh
    return y - h


def dark_page():
    global page
    page += 1
    c.setFillColor(INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)


# ---------------------------------------------------------------- 1. tytuł
dark_page()
c.setFillColor(ACCENT)
c.circle(W - 70, H - 60, 120, stroke=0, fill=1)
c.setFillColor(INK)
c.circle(W - 70, H - 60, 104, stroke=0, fill=1)
text(56, 232, "QuestLog", 46, "B", white)
text(56, 200, "Trzy warstwy ochrony: kod, aplikacja i środowisko.", 13, "R", LILAC)
c.setStrokeColor(AMBER)
c.setLineWidth(3)
c.line(56, 176, 56 + 60, 176)
text(56, 142, "L7. Elementy bezpieczeństwa (kod i konfiguracja)", 13, "B", white)
text(56, 120, "Flask + Caddy  ·  Cloudflare  ·  OCI  ·  Suricata  ·  questlog.com.pl", 10, "R", SLATE)
c.showPage()

# ------------------------------------------------- 2. wymagania i realizacja
y = slide("Wymagania zadania", "co było do zrobienia")
rows(y, [
    ("Bezpieczeństwo w kodzie", "Polityka haseł, blokada konta, limity żądań, sesje z unieważnianiem, log zdarzeń "
     "bezpieczeństwa", ACCENT),
    ("Konfiguracja aplikacji", "TLS na każdym odcinku połączenia, nagłówki bezpieczeństwa, limity i timeouty, "
     "twarde warunki trybu produkcyjnego", TEAL),
    ("Konfiguracja środowiska", "Cloudflare: WAF, CDN, Anti-DDoS, rate limit (IPS); Suricata na VM (IDS); "
     "zapory OCI tylko dla Cloudflare", AMBER),
    ("Implementacja i prezentacja", "Wszystko działa na produkcji, sprawdzone testami z zewnątrz; ten deck "
     "i pokaz na żywo", LILAC),
], h=50)
c.showPage()

# ------------------------------------------------------ 3. ścieżka ruchu
y = slide("Ścieżka żądania", "każda warstwa ma własną ochronę")
nodes = [
    ("Klient", "przeglądarka", ["HTTPS (TLS 1.2+)", "HSTS, CSP"], SLATE),
    ("Cloudflare", "brzeg sieci", ["WAF + rate limit", "Anti-DDoS, CDN"], AMBER),
    ("LB OCI", "138.2.185.106", ["nsg-lb: tylko IP", "Cloudflare, cert", "Origin CA"], ACCENT),
    ("VM ×2", "Caddy → Flask", ["nsg-app: tylko z LB", "Suricata (IDS)", "kod: sesje, limity"], TEAL),
    ("Neon", "PostgreSQL", ["sslmode=require", "wymuszane przy", "starcie"], LILAC),
]
bw, gap = 108, 21
for i, (name, sub, prot, col) in enumerate(nodes):
    x = 48 + i * (bw + gap)
    box(x, 196, bw, 52, white, col, lw=1.6)
    text(x + bw / 2, 228, name, 12, "B", INK, "c")
    text(x + bw / 2, 210, sub, 7.8, "R", SLATE, "c")
    if i < len(nodes) - 1:
        arrow(x + bw + 2, 222, x + bw + gap - 2, 222)
    yy = 178
    for p in prot:
        text(x + bw / 2, yy, p, 8.2, "R", INK, "c")
        yy -= 12
c.setStrokeColor(HexColor("#d6cbf2"))
c.setLineWidth(1)
c.setDash(3, 3)
c.roundRect(300, 126, 248, 132, 8, stroke=1, fill=0)
c.setDash()
text(308, 262, "OCI Frankfurt  ·  Always Free", 7.5, "B", LILAC)
bullets(98, [
    "Wejście prosto na IP load balancera kończy się timeoutem — jedyna droga do aplikacji prowadzi przez Cloudflare.",
    "Szyfrowane są wszystkie odcinki z internetu; ruch LB → VM idzie w prywatnej sieci VCN, gdzie widzi go Suricata.",
], AMBER, size=10)
c.showPage()

# ------------------------------------------------------ 4. kod: logowanie
y = slide("Kod: logowanie i konta", "code/backend/app")
y = cards(y, [
    ("Hasła", "10–128 znaków, hash werkzeug (scrypt z solą). Przy nieznanym loginie liczony jest hash atrapy, "
     "więc czas odpowiedzi nie zdradza, czy konto istnieje.", ACCENT),
    ("Blokada konta", "5 nieudanych prób = konto zablokowane na 15 minut. Licznik w bazie, więc działa na obu "
     "VM i przetrwa restart.", AMBER),
    ("Limity żądań", "flask-limiter: logowanie 10/min, rejestracja 10/h, reszta API 300/min z jednego IP. "
     "Odpowiedź 429 z czytelnym komunikatem.", TEAL),
], h=118)
bullets(y, [
    "Adres IP klienta pochodzi z CF-Connecting-IP (Caddy + ProxyFix) — podrobiony X-Forwarded-For nie obejdzie "
    "limitów ani blokady.",
    "Odpowiedzi API mają Cache-Control: no-store; body żądania ograniczone do 64 KB w Flasku i 128 KB w Caddy.",
], ACCENT, size=10)
c.showPage()

# ------------------------------------------------------ 5. kod: sesje i monitoring
y = slide("Kod: sesje i monitoring", "tabela sessions + log zdarzeń")
box(48, y - 196, 300, 204, white, EDGE)
text(66, y - 16, "Sesje po stronie serwera", 13, "B", ACCENT)
bullets(y - 40, [
    "Każdy token JWT ma identyfikator sesji (jti) sprawdzany w bazie przy każdym żądaniu.",
    "Wylogowanie unieważnia sesję w bazie, a nie tylko usuwa token w przeglądarce.",
    "Strona „Sesje”: IP, przeglądarka, ostatnia aktywność; „wyloguj” jedną lub wszystkie inne.",
    "Token wygasa po 24 h; stare sesje są czyszczone przy logowaniu.",
], ACCENT, x=72, width=260, size=9.5)
code_box(372, y + 8, 300, [
    ('{"event":"login_failed","ip":"84.40.239.174"}', white),
    ('{"event":"account_locked","user_id":7,', white),
    ('   "minutes":15}', white),
    ('{"event":"session_revoked","user_id":7}', white),
    ('{"event":"denied","status":429,', white),
    ('   "path":"/api/auth/login"}', white),
], title="LOG BEZPIECZEŃSTWA (JSON NA STDOUT)")
bullets(y - 120, [
    "Zdarzenia: rejestracja, logowanie udane i nieudane, blokada, wylogowanie, unieważnienie sesji, każde 401/403/429.",
    "Jedna linia JSON — gotowe do docker logs | jq albo systemu SIEM.",
], TEAL, x=378, width=280, size=9.5)
c.showPage()

# ------------------------------------------------------ 6. konfiguracja aplikacji
y = slide("Konfiguracja aplikacji", "połączenie i nagłówki")
seg = [("przeglądarka → Cloudflare", "cert Cloudflare, TLS 1.2+, Always HTTPS", AMBER),
       ("Cloudflare → LB", "Full (strict), cert Origin CA do 2041", ACCENT),
       ("LB → VM", "prywatna sieć VCN, tylko z nsg-lb", TEAL),
       ("backend → Neon", "TLS wymuszony: bez sslmode=require nie startuje", LILAC)]
for i, (top, bot, col) in enumerate(seg):
    x = 48 + i * 160
    box(x, y - 58, 148, 66, white, EDGE)
    c.setFillColor(col)
    c.roundRect(x, y - 58, 148, 4, 2, stroke=0, fill=1)
    text(x + 12, y - 12, top, 9.5, "B", INK)
    wrap(x + 12, y - 28, bot, 126, 8.5)
y -= 84
col_l = [("Content-Security-Policy", "tylko własne skrypty, bez inline"), ("Strict-Transport-Security", "1 rok"),
         ("X-Frame-Options", "DENY (clickjacking)"), ("X-Content-Type-Options", "nosniff")]
col_r = [("Referrer / Permissions-Policy", "bez kamery, mikrofonu, GPS"), ("COOP / CORP", "same-origin"),
         ("Server", "usunięty nagłówek"), ("Caddy", "body 128 KB, timeouty 10/15/30 s")]
for cx, items in ((48, col_l), (372, col_r)):
    yy = y
    for k, v in items:
        check(cx + 2, yy + 3, TEAL, 6)
        text(cx + 18, yy, k, 10, "B", INK)
        text(cx + 18, yy - 13, v, 9, "R", SLATE)
        yy -= 32
text(48, 40, "Produkcja nie wystartuje z domyślnym SECRET_KEY ani krótszym niż 32 znaki (APP_ENV=production).",
     9.5, "B", ACCENT)
c.showPage()

# ------------------------------------------------------ 7. Cloudflare
y = slide("Środowisko: Cloudflare", "plan Free  ·  WAF, IPS, Anti-DDoS, CDN")
y = cards(y, [
    ("WAF", "Cloudflare Free Managed Ruleset + reguła xss-sqli-query: <script, union select, ' or '1'='1 "
     "w parametrach adresu → 403.", AMBER),
    ("Rate limit", "login-limit: więcej niż 5 × POST /api/auth/login w 10 s z jednego IP → 429 na 10 s, "
     "zanim żądanie dotrze do serwera.", ACCENT),
    ("Anti-DDoS", "Ochrona L3/4/7 stale włączona; serwer nie ma publicznego wejścia z pominięciem "
     "Cloudflare.", RED),
    ("CDN", "/assets/* z Cache-Control: immutable — pliki JS i CSS serwowane z cache Cloudflare "
     "(cf-cache-status: HIT).", TEAL),
], h=128, size=9)
bullets(y, [
    "IPS = Cloudflare: stoi w ścieżce ruchu i blokuje. IDS = Suricata na VM: wykrywa i alarmuje (następny slajd).",
    "Konfiguracja przez API z tokenem ograniczonym do jednej strefy; HSTS zostaje w Caddy, żeby nie dublować.",
], AMBER, size=10)
c.showPage()

# ------------------------------------------------------ 8. sieć OCI
y = slide("Środowisko: zapory OCI", "Network Security Groups")
box(48, y - 120, 300, 128, white, EDGE)
text(66, y - 18, "Przed", 15, "B", SLATE)
yy = y - 44
for r in ["nsg-lb: 80 i 443 z 0.0.0.0/0", "WAF dało się ominąć: curl prosto na IP LB",
          "SSH (22) otwarte dla całego internetu", "cert Let's Encrypt — odnawiany co 90 dni"]:
    text(66, yy, "·  " + r, 10, "R", SLATE)
    yy -= 18
box(372, y - 120, 300, 128, white, TEAL, lw=1.6)
text(390, y - 18, "Po", 15, "B", TEAL)
yy = y - 44
for r in ["nsg-lb: tylko 443 z 15 zakresów Cloudflare", "nsg-app: port 80 tylko z nsg-lb",
          "SSH tylko z 2 adresów IP", "cert Origin CA ważny do 2041"]:
    text(390, yy, "·  " + r, 10, "R", INK)
    yy -= 18
bullets(y - 148, [
    "Bezpośrednie wejście na 138.2.185.106 (porty 80 i 443) kończy się timeoutem — pakiet nie dociera nawet do LB.",
    "Zakresy z cloudflare.com/ips-v4; zmiana listy przez Cloudflare wymaga aktualizacji reguł (rzadko).",
], TEAL, size=10)
c.showPage()

# ------------------------------------------------------ 9. Suricata
y = slide("Środowisko: Suricata (IDS)", "tools/suricata  ·  usługa w docker-compose.cloud.yml")
bullets(y, [
    "Suricata 8 na obu VM dostaje kopię ruchu z karty sieciowej (af-packet) i tylko alarmuje.",
    "TLS kończy się na LB, więc widzi odszyfrowany HTTP — także body, którego WAF nie sprawdza.",
    "Reguły: ET Open (~53 tys., odświeżane przy starcie) + 4 własne: SQLi i XSS w body API, .env/.git, "
    "ruch z pominięciem Cloudflare.",
    "W logu tylko alerty, bez treści żądań (w body logowania jest hasło); IP klienta z CF-Connecting-IP.",
], ACCENT, width=300, size=9.5)
code_box(392, y + 8, 280, [
    ("sid 1000001  QUESTLOG SQLi w body", AMBER),
    ("  klient 84.40.239.174", white),
    ("  POST /api/auth/login  → 401", white),
    ("sid 2053468  ET WEB_SERVER UNION", AMBER),
    ("  SELECT in HTTP Request Body", white),
    ("sid 1000002  QUESTLOG XSS w body", AMBER),
    ("  POST /api/auth/register → 400", white),
    ("sid 1000003  .env/.git  + ET INFO", AMBER),
    ("  GET /.env", white),
], title="ALERTY Z PRODUKCJI (EVE.JSON, APP1)")
text(48, 52, "Atak przeszedł przez WAF (body), aplikacja go odrzuciła, a Suricata zapisała ślad — obrona warstwowa.",
     9.5, "B", ACCENT)
c.showPage()

# ------------------------------------------------------ 10. weryfikacja
y = slide("Weryfikacja na produkcji", "testy z zewnątrz, 26.11.2026")
tests = [
    ("Strona przez Cloudflare", "200, server: cloudflare"),
    ("curl prosto na IP LB (80, 443)", "timeout"),
    ("?q=<script>, UNION SELECT, ' or '1'='1", "403 (WAF)"),
    ("Zwykłe zapytanie", "200 — brak fałszywych alarmów"),
    ("6 × logowanie w 10 s", "5 × 401, potem 429 (Cloudflare 1015)"),
    ("Plik /assets/*.js drugi raz", "cf-cache-status: HIT"),
    ("SQLi / XSS w body", "401 / 400 + alert Suricaty z IP klienta"),
    ("Podrobiony X-Forwarded-For", "ignorowany — liczy się CF-Connecting-IP"),
]
rh = 25
box(48, y - len(tests) * rh + 4, W - 96, len(tests) * rh + 4, white, EDGE)
for i, (t, r) in enumerate(tests):
    yy = y - i * rh
    if i % 2:
        c.setFillColor(HexColor("#f7f5fd"))
        c.rect(49, yy - rh + 5, W - 98, rh, stroke=0, fill=1)
    text(66, yy - 12, t, 10, "R", INK)
    text(400, yy - 12, r, 10, "B", INK)
    check(W - 74, yy - 9, TEAL, 6)
c.showPage()

# ------------------------------------------------------ 11. demo
y = slide("Pokaz na żywo", "kolejność")
rows(y, [
    ("1. Sesje", "Logowanie w dwóch przeglądarkach → strona „Sesje” → „wyloguj” drugą: tam token przestaje działać",
     ACCENT),
    ("2. Blokada konta", "5 złych haseł → komunikat o blokadzie; w logu login_failed i account_locked", AMBER),
    ("3. WAF i rate limit", "questlog.com.pl/?q=<script> → 403; seria logowań → 429 od Cloudflare", TEAL),
    ("4. Ominięcie Cloudflare", "curl https://138.2.185.106 → timeout (zapora nsg-lb)", RED),
    ("5. IDS", "SQLi w body logowania → alert w eve.json z prawdziwym IP klienta", LILAC),
], h=44, gap=8)
c.showPage()

# ------------------------------------------------------ 12. podziękowanie
dark_page()
c.setFillColor(ACCENT)
c.circle(80, 70, 120, stroke=0, fill=1)
c.setFillColor(INK)
c.circle(80, 70, 104, stroke=0, fill=1)
text(W - 56, 212, "Dziękuję za uwagę", 38, "B", white, "r")
c.setStrokeColor(AMBER)
c.setLineWidth(3)
c.line(W - 56 - 60, 190, W - 56, 190)
text(W - 56, 158, "questlog.com.pl", 14, "B", LILAC, "r")
text(W - 56, 136, "QuestLog  ·  L7. Elementy bezpieczeństwa", 10, "R", SLATE, "r")
c.showPage()

c.save()
print("gotowe")
