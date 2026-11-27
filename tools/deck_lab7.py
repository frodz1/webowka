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
STRIPE = HexColor("#f7f5fd")

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


def bullets(y, items, col, x=54, width=W - 128, size=11, gap=7):
    for b in items:
        c.setFillColor(col)
        c.circle(x, y + 4, 2.6, stroke=0, fill=1)
        y = wrap(x + 10, y, b, width, size) - gap
    return y


def rows(y, items, h=48, gap=10, mark=True):
    """Lista pasków nazwa + opis (+ opcjonalny dopisek po prawej) z ptaszkiem albo bez."""
    for name, how, col, *ref in items:
        box(48, y - h + 8, W - 96, h, white, EDGE)
        c.setFillColor(col)
        c.roundRect(48, y - h + 8, 5, h, 2.5, stroke=0, fill=1)
        text(68, y - 9, name, 12, "B", INK)
        if ref:
            text(W - 96, y - 9, ref[0], 8.5, "B", col, "r")
        wrap(68, y - 26, how, W - 170, 9.5)
        if mark:
            check(W - 78, y - h / 2 + 8, col)
        y -= h + gap
    return y


def sections(x, y, parts, width, size):
    """Bloki „ETYKIETA” + tekst jeden pod drugim (przed / teraz / dlaczego); zwraca y pod ostatnim."""
    for label, body in parts:
        text(x, y, label, 7.5, "B", ACCENT)
        y = wrap(x, y - 11, body, width, size, color=INK if label == "TERAZ" else SLATE) - 5
    return y


def cards(y, items, h=112, size=9.5):
    """Karty w jednym rzędzie: (tytuł, kolor, opis albo lista sekcji (etykieta, tekst))."""
    n = len(items)
    cw = (W - 96 - (n - 1) * 14) / n
    for i, (name, col, body) in enumerate(items):
        x = 48 + i * (cw + 14)
        box(x, y - h, cw, h + 8, white, EDGE)
        c.setFillColor(col)
        c.roundRect(x, y - h, cw, 4, 2, stroke=0, fill=1)
        text(x + 14, y - 16, name, 13, "B", col)
        if isinstance(body, str):
            wrap(x + 14, y - 36, body, cw - 28, size)
        else:
            sections(x + 14, y - 36, body, cw - 28, size)
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


def table(y, header, data, xs, rh=25, size=9.5, bold_cols=()):
    """Tabela w białej ramce: nagłówek + wiersze w paski; xs = lewe krawędzie kolumn."""
    n = len(data) + 1
    box(48, y - n * rh + 4, W - 96, n * rh + 4, white, EDGE)
    for x, h in zip(xs, header):
        text(x, y - 12, h, 8, "B", ACCENT)
    for i, row in enumerate(data, start=1):
        yy = y - i * rh
        if i % 2 == 0:
            c.setFillColor(STRIPE)
            c.rect(49, yy - rh + 5, W - 98, rh, stroke=0, fill=1)
        for j, (x, cell) in enumerate(zip(xs, row)):
            text(x, yy - 12, cell, size, "B" if j in bold_cols else "R", INK if cell != "—" else SLATE)
    return y - n * rh


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
text(56, 120, "Co zmieniłem, dlaczego i jak to działa  ·  questlog.com.pl", 10, "R", SLATE)
c.showPage()

# ------------------------------------------------- 2. wymagania i realizacja
y = slide("Wymagania zadania", "co było do zrobienia")
rows(y, [
    ("Bezpieczeństwo w kodzie", "Polityka haseł, blokada konta, limity żądań, sesje z unieważnianiem, log zdarzeń "
     "bezpieczeństwa", ACCENT, "slajdy 5–6"),
    ("Konfiguracja aplikacji", "TLS na każdym odcinku połączenia, nagłówki bezpieczeństwa, limity i timeouty, "
     "twarde warunki trybu produkcyjnego", TEAL, "slajd 7"),
    ("Konfiguracja środowiska", "Cloudflare: WAF, CDN, Anti-DDoS, rate limit (IPS); Suricata na VM (IDS); "
     "zapory OCI tylko dla Cloudflare", AMBER, "slajdy 8–10"),
    ("Implementacja i prezentacja", "Wszystko działa na produkcji, sprawdzone testami z zewnątrz i w CI; ten deck "
     "i pokaz na żywo", LILAC, "slajdy 11–13"),
], h=50)
c.showPage()

# ------------------------------------------------- 3. przed → po
y = slide("L7 w skrócie: przed → po", "co się zmieniło")
table(y, ["OBSZAR", "PRZED L7", "PO L7"], [
    ("Hasła", "min. 6 znaków, bez górnej granicy", "10–128 znaków, hash atrapy dla nieznanego loginu"),
    ("Logowanie", "dowolnie wiele prób", "blokada 5 prób / 15 min + limity flask-limiter"),
    ("Sesje", "JWT na 7 dni, nie do unieważnienia", "JWT 24 h + tabela sessions, wylogowanie w bazie"),
    ("Log bezpieczeństwa", "brak", "zdarzenia jako JSON na stdout"),
    ("IP klienta", "Flask widział adres proxy", "CF-Connecting-IP → Caddy → ProxyFix"),
    ("Caddy", "nagłówki z L6", "+ HSTS, COOP/CORP, body 128 KB, timeouty"),
    ("Baza (Neon)", "TLS zależny od DATABASE_URL", "bez sslmode=require backend nie startuje"),
    ("Brzeg sieci", "rekord A prosto na LB, Let's Encrypt", "proxy Cloudflare: WAF, rate limit, DDoS, CDN"),
    ("Zapory OCI", "LB otwarty dla całego internetu", "443 tylko z Cloudflare, SSH z jednego adresu"),
    ("IDS", "brak", "Suricata 8 na obu VM"),
], [66, 210, 420], rh=22, size=9, bold_cols=(0,))
c.showPage()

# ------------------------------------------------------ 4. ścieżka ruchu
y = slide("Ścieżka żądania po L7", "każda warstwa ma własną ochronę")
nodes = [
    ("Klient", "przeglądarka", ["HTTPS (TLS 1.2+)", "HSTS, CSP"], SLATE, False),
    ("Cloudflare", "brzeg sieci", ["WAF + rate limit", "Anti-DDoS, CDN"], AMBER, True),
    ("LB OCI", "138.2.185.106", ["nsg-lb: tylko IP", "Cloudflare, cert", "Origin CA"], ACCENT, True),
    ("VM ×2", "Caddy → Flask", ["nsg-app: tylko z LB", "Suricata (IDS)", "kod: sesje, limity"], TEAL, True),
    ("Neon", "PostgreSQL", ["sslmode=require", "wymuszane przy", "starcie"], LILAC, True),
]
bw, gap = 108, 21
for i, (name, sub, prot, col, new) in enumerate(nodes):
    x = 48 + i * (bw + gap)
    box(x, 196, bw, 52, white, col, lw=1.6)
    text(x + bw / 2, 228, name, 12, "B", INK, "c")
    text(x + bw / 2, 210, sub, 7.8, "R", SLATE, "c")
    if new:
        text(x + bw - 4, 252, "zmiany w L7", 7, "B", AMBER, "r")
    if i < len(nodes) - 1:
        arrow(x + bw + 2, 222, x + bw + gap - 2, 222)
    yy = 178
    for p in prot:
        text(x + bw / 2, yy, p, 8.2, "R", INK, "c")
        yy -= 12
c.setStrokeColor(HexColor("#d6cbf2"))
c.setLineWidth(1)
c.setDash(3, 3)
c.roundRect(300, 120, 248, 146, 8, stroke=1, fill=0)
c.setDash()
text(308, 131, "OCI Frankfurt  ·  Always Free", 7.5, "B", LILAC)
bullets(98, [
    "Wejście prosto na IP load balancera kończy się timeoutem — jedyna droga do aplikacji prowadzi przez Cloudflare.",
    "Szyfrowane są wszystkie odcinki z internetu. LB → VM celowo bez TLS: prywatna sieć VCN, a Suricata "
    "widzi dzięki temu treść żądań.",
], AMBER, size=10, gap=5)
c.showPage()

# ------------------------------------------------------ 5. kod: logowanie
y = slide("Kod: logowanie i konta", "routes_auth.py  ·  validation.py  ·  extensions.py")
y = cards(y, [
    ("Hasła", ACCENT, [
        ("PRZED", "min. 6 znaków; nieznany login kończył sprawdzanie od razu, bez liczenia hasha."),
        ("TERAZ", "10–128 znaków; dla nieznanego loginu liczony jest hash atrapy (DUMMY_HASH)."),
        ("DLACZEGO", "krótkie hasła łatwo złamać, a czas odpowiedzi zdradzał, czy konto istnieje."),
    ]),
    ("Blokada konta", AMBER, [
        ("PRZED", "dowolnie wiele prób na jedno konto."),
        ("TERAZ", "5. błędne hasło blokuje konto na 15 min (failed_logins, locked_until); kolejna próba → 429."),
        ("DLACZEGO", "zgadywanie z wielu IP omija limity per IP; licznik w bazie działa na obu VM."),
    ]),
    ("Limity żądań", TEAL, [
        ("PRZED", "brak."),
        ("TERAZ", "flask-limiter: logowanie 10/min, rejestracja 10/h, reszta API 300/min z jednego IP."),
        ("DLACZEGO", "zalewanie API i masowa rejestracja. Liczniki są w pamięci procesu, więc na "
                     "logowaniu twardy limit trzyma Cloudflare."),
    ]),
], h=172, size=8.5)
bullets(y, [
    "Przed L7 Flask widział adres proxy, nie klienta — limit per IP objąłby wszystkich naraz. Teraz Caddy bierze "
    "CF-Connecting-IP (ufa tylko sieci 10.0.0.0/16), a Flask czyta go przez ProxyFix (1 hop).",
], ACCENT, size=9.5)
c.showPage()

# ------------------------------------------------------ 6. kod: sesje i monitoring
y = slide("Kod: sesje i monitoring", "auth.py  ·  tabela sessions  ·  security_log.py")
box(48, y - 184, 310, 192, white, EDGE)
text(66, y - 16, "Sesje po stronie serwera", 13, "B", ACCENT)
sections(66, y - 36, [
    ("PRZED", "JWT ważny 7 dni i bezstanowy: wylogowanie tylko kasowało token w przeglądarce, a skradziony "
              "token działał do wygaśnięcia."),
    ("TERAZ", "token niesie jti = id wiersza w sessions; każde żądanie sprawdza revoked_at IS NULL. "
              "TTL 24 h, strona „Sesje” (IP, przeglądarka, last_seen): wyloguj jedną lub wszystkie inne."),
    ("JAK", "wylogowanie = UPDATE sessions SET revoked_at = now(), token od razu przestaje działać; "
            "last_seen zapisywany najwyżej raz na minutę; stare sesje usuwane przy logowaniu."),
], 274, 8.8)
code_box(378, y + 8, 294, [
    ('{"event":"login_failed","ip":"84.40.239.174"}', white),
    ('{"event":"account_locked","user_id":7,', white),
    ('   "minutes":15}', white),
    ('{"event":"session_revoked","user_id":7}', white),
    ('{"event":"denied","status":429,', white),
    ('   "path":"/api/auth/login"}', white),
], title="LOG BEZPIECZEŃSTWA (JSON NA STDOUT)")
bullets(y - 118, [
    "Przed L7 nie było śladu prób logowania. Teraz: rejestracja, logowanie udane i nieudane, blokada, "
    "wylogowanie, unieważnienie sesji, a w after_request każde 401/403/429.",
    "Jedna linia JSON z IP i czasem — docker logs | jq albo SIEM.",
    "21 nowych testów (test_security.py, test_sessions.py) w CI.",
], TEAL, x=384, width=280, size=9, gap=5)
c.showPage()

# ------------------------------------------------------ 7. konfiguracja aplikacji
y = slide("Konfiguracja aplikacji", "Caddyfile  ·  config.py  ·  entrypoint.sh")
seg = [("przeglądarka → Cloudflare", "cert Cloudflare, TLS 1.2+, Always HTTPS", AMBER),
       ("Cloudflare → LB", "Full (strict): CF sprawdza cert Origin CA", ACCENT),
       ("LB → VM", "prywatna sieć VCN, tylko z nsg-lb", TEAL),
       ("backend → Neon", "bez sslmode=require nie startuje", LILAC)]
for i, (top, bot, col) in enumerate(seg):
    x = 48 + i * 160
    box(x, y - 44, 148, 52, white, EDGE)
    c.setFillColor(col)
    c.roundRect(x, y - 44, 148, 4, 2, stroke=0, fill=1)
    text(x + 12, y - 12, top, 9.5, "B", INK)
    wrap(x + 12, y - 26, bot, 126, 8.3)
y -= 66
text(48, y, "NOWE W L7", 8, "B", ACCENT)
text(452, y, "Z L6, BEZ ZMIAN (SKAN ZAP W CI)", 8, "B", SLATE)
yy = y - 18
for k, v in [("HSTS, 1 rok", "przeglądarka nie zejdzie do HTTP"),
             ("COOP / CORP: same-origin", "obca strona nie sięgnie do okna i zasobów"),
             ("body 128 KB (Caddy), 64 KB (Flask)", "duże żądania nie zapchają pamięci"),
             ("timeouty: nagłówki 10 s, body 15 s, odpowiedź 30 s", "powolne połączenia (Slowloris) nie "
              "zajmą serwera"),
             ("Cache-Control: no-store na /api", "dane konta nie zostają w cache"),
             ("APP_ENV=production", "SECRET_KEY własny i ≥ 32 znaki, inaczej start się przerywa — "
              "tym kluczem podpisywane są JWT")]:
    check(50, yy + 3, TEAL, 6)
    text(66, yy, k, 9, "B", INK)
    yy = wrap(66, yy - 11, v, 360, 8.5) - 5
yy = y - 18
for k in ["Content-Security-Policy", "X-Frame-Options: DENY", "X-Content-Type-Options", "Referrer-Policy",
          "Permissions-Policy", "nagłówek Server usunięty"]:
    text(452, yy, "·  " + k, 9, "R", SLATE)
    yy -= 16
c.showPage()

# ------------------------------------------------------ 8. Cloudflare
y = slide("Środowisko: Cloudflare", "plan Free  ·  WAF, IPS, Anti-DDoS, CDN")
wrap(48, y, "Przed L7: rekord A wskazywał prosto na LB z certyfikatem Let's Encrypt — nic nie filtrowało ruchu "
     "przed serwerem. Teraz domena idzie przez proxy Cloudflare (SSL Full strict).", W - 96, 10, color=INK)
y -= 36
y = cards(y, [
    ("WAF", AMBER, "Free Managed Ruleset + własna reguła xss-sqli-query: <script, union select, ' or '1'='1 "
     "w adresie → 403."),
    ("Rate limit", ACCENT, "login-limit: więcej niż 5 × POST /api/auth/login w 10 s z jednego IP → 429 przez "
     "10 s, zanim żądanie dotrze do serwera."),
    ("Anti-DDoS", RED, "Ochrona L3/4/7 stale włączona. Działa tylko dlatego, że serwer nie ma wejścia "
     "z pominięciem Cloudflare (slajd 9)."),
    ("CDN", TEAL, "/assets/* z Cache-Control: immutable (pliki z hashem w nazwie) → serwowane z cache "
     "Cloudflare (cf-cache-status: HIT)."),
], h=112, size=8.6)
bullets(y, [
    "IPS = Cloudflare: stoi w ścieżce ruchu i blokuje. IDS = Suricata na VM: tylko wykrywa i alarmuje (slajd 10).",
    "HSTS wysyła tylko Caddy, Cloudflare go nie dokłada (jedna wartość w jednym miejscu). Konfiguracja przez API "
    "tokenem ograniczonym do jednej strefy.",
], AMBER, size=9.5, gap=5)
c.showPage()

# ------------------------------------------------------ 9. sieć OCI
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
          "SSH tylko z jednego adresu (domowego)", "cert Origin CA ważny do 2041"]:
    text(390, yy, "·  " + r, 10, "R", INK)
    yy -= 18
bullets(y - 148, [
    "Dlaczego tylko Cloudflare: inaczej wystarczy wejść prosto na IP serwera, żeby ominąć WAF, rate limit i "
    "Anti-DDoS. Teraz bezpośrednie połączenie kończy się timeoutem — pakiet nie dociera nawet do LB.",
    "Dlaczego Origin CA: odnowienie Let's Encrypt wymaga wejścia z internetu, które teraz jest zamknięte. "
    "Origin CA jest ważny do 2041 i ufa mu tylko Cloudflare.",
    "Zakresy z cloudflare.com/ips-v4; gdy Cloudflare zmieni listę, reguły trzeba zaktualizować ręcznie.",
], TEAL, size=9.5, gap=5)
c.showPage()

# ------------------------------------------------------ 10. Suricata
y = slide("Środowisko: Suricata (IDS)", "tools/suricata  ·  usługa w docker-compose.cloud.yml")
bullets(y, [
    "Suricata 8 na obu VM dostaje kopię ruchu z karty sieciowej (af-packet) i tylko alarmuje — blokowanie "
    "zostaje w Cloudflare.",
    "Dlaczego na VM: TLS kończy się na LB, więc Suricata widzi odszyfrowany HTTP — także body, którego "
    "WAF nie sprawdza.",
    "Reguły: ET Open (~53 tys., suricata-update przy starcie) + 4 własne w local.rules: SQLi i XSS w body "
    "API, .env/.git, ruch bez CF-Connecting-IP (ominięcie Cloudflare).",
    "eve.json: tylko alerty, bez treści żądań (w body logowania jest hasło); IP klienta z CF-Connecting-IP. "
    "Wyłączone reguły szumu (checksum offload, agent OCI, DNS do Neona).",
], ACCENT, width=310, size=9.3, gap=5)
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
text(48, 96, "Atak przeszedł przez WAF (body), aplikacja go odrzuciła, a Suricata zapisała ślad — obrona warstwowa.",
     9.5, "B", ACCENT)
c.showPage()

# ------------------------------------------------------ 11. weryfikacja
y = slide("Weryfikacja na produkcji", "testy z zewnątrz, 26.11.2026")
y = table(y, ["TEST", "WYNIK", "KTÓRA WARSTWA ZADZIAŁAŁA"], [
    ("Strona przez Cloudflare", "200, server: cloudflare", "Cloudflare (ruch idzie przez CF)"),
    ("curl prosto na IP LB (80, 443)", "timeout", "OCI: zapora nsg-lb"),
    ("?q=<script>, UNION SELECT, ' or '1'='1", "403", "Cloudflare WAF"),
    ("Zwykłe zapytanie", "200 — brak fałszywych alarmów", "—"),
    ("6 × logowanie w 10 s", "5 × 401, potem 429 (CF 1015)", "Cloudflare rate limit"),
    ("Plik /assets/*.js drugi raz", "cf-cache-status: HIT", "Cloudflare CDN"),
    ("SQLi / XSS w body", "401 / 400 + alert z IP klienta", "Flask + Suricata"),
    ("Podrobiony X-Forwarded-For", "ignorowany", "Caddy + Flask (CF-Connecting-IP)"),
], [66, 300, 490], rh=25, size=9.3, bold_cols=(1,))
text(48, y - 14, "Do tego w CI przy każdym PR: 21 testów pytest dla haseł, blokady, limitów, sesji i logu.", 9.5,
     "B", ACCENT)
c.showPage()

# ------------------------------------------------------ 12. macierz atak × warstwa
y = slide("Atak → która warstwa zatrzymuje", "obrona warstwowa w jednej tabeli")
table(y, ["ATAK", "CLOUDFLARE", "OCI (NSG)", "CADDY", "FLASK", "SURICATA"], [
    ("Zgadywanie hasła", "limit 5 / 10 s", "—", "—", "blokada + limit", "—"),
    ("Kradzież tokenu", "—", "—", "CSP (bez XSS)", "unieważn. sesji", "—"),
    ("XSS / SQLi w adresie", "WAF → 403", "—", "CSP", "SQL z param.", "—"),
    ("XSS / SQLi w body", "—", "—", "CSP", "walidacja, param.", "alert 1000001/2"),
    ("Ominięcie Cloudflare", "—", "timeout", "—", "—", "alert 1000004"),
    ("DDoS", "Anti-DDoS", "tylko CF", "timeouty, 128 KB", "limit 300/min", "—"),
    ("Sfałszowany X-Fwd-For", "CF-Conn.-IP", "tylko CF", "bierze CF-IP", "ProxyFix", "—"),
], [62, 190, 284, 362, 458, 560], rh=28, size=8.8, bold_cols=(0,))
text(48, 52, "Wyłączenie jednej warstwy nie otwiera drogi — za nią stoi kolejna. Suricata tylko wykrywa (IDS).",
     9.5, "B", ACCENT)
c.showPage()

# ------------------------------------------------------ 13. demo
y = slide("Pokaz na żywo", "kolejność: akcja → oczekiwany wynik")
rows(y, [
    ("1. Sesje", "Zaloguj w Chrome i Firefox → Chrome: „Sesje” → „wyloguj” Firefoxa → następne żądanie "
     "w Firefoksie: 401.", ACCENT),
    ("2. Blokada konta", "5 × złe hasło co ~3 s (401) → 6. próba: 429 „Zbyt wiele nieudanych prób”; "
     "docker logs questlog-backend-1 | grep account_locked.", AMBER),
    ("3. WAF i rate limit", "curl 'https://questlog.com.pl/?q=<script>' → 403; 6 × POST /api/auth/login "
     "w 10 s → 429 (1015).", TEAL),
    ("4. Ominięcie Cloudflare", "curl -m 5 -k https://138.2.185.106 → timeout (zapora nsg-lb).", RED),
    ("5. IDS", "POST /api/auth/login z „union select” w body → 401; tail eve.json (questlog-suricata-1) "
     "→ sid 1000001 z prawdziwym IP.", LILAC),
], h=42, gap=6)
text(48, 40, "Krok 2 z przerwami, bo 6 prób w 10 s zatrzyma wcześniej Cloudflare. Plan B: zrzuty ekranu i slajd 11.",
     9.5, "B", ACCENT)
c.showPage()

# ------------------------------------------------------ 14. ograniczenia
y = slide("Ograniczenia", "świadome kompromisy")
rows(y, [
    ("Suricata tylko alarmuje", "Niczego nie blokuje, a alerty trzeba przeczytać w eve.json — brak "
     "automatycznych powiadomień.", AMBER),
    ("LB → VM bez TLS", "Ruch w prywatnej sieci VCN jest jawny — świadomie, żeby IDS widział treść.", ACCENT),
    ("Limity Flaska w pamięci procesu", "4 procesy (2 VM × 2 workery) liczą osobno: realnie do 4× luźniej. "
     "Wspólny Redis by to naprawił.", TEAL),
    ("Ręczna lista IP Cloudflare", "Gdy Cloudflare zmieni zakresy, reguły nsg-lb trzeba zaktualizować ręcznie.",
     LILAC),
    ("Brak 2FA", "Wyciek hasła = dostęp do konta, dopóki właściciel go nie zmieni.", RED),
], h=44, gap=6, mark=False)
c.showPage()

# ------------------------------------------------------ 15. podziękowanie
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
