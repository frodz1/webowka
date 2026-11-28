// Ustawia motyw przed renderem (osobny plik, żeby CSP nie wymagało unsafe-inline).
try {
  var t = localStorage.getItem('questlog_theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.dataset.theme = t;
} catch (e) {}
