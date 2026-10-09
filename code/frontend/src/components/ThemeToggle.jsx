import { useState } from 'react';

const KEY = 'questlog_theme';

function currentTheme() {
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
}

/** Przełącznik jasny/ciemny motyw; wybór zapamiętany w localStorage. */
export default function ThemeToggle() {
  const [theme, setTheme] = useState(currentTheme);

  function toggle() {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(KEY, next);
    } catch {
      /* tryb prywatny – motyw obowiązuje do końca sesji */
    }
    setTheme(next);
  }

  const label = theme === 'dark' ? 'Przełącz na jasny motyw' : 'Przełącz na ciemny motyw';
  return (
    <button className="theme-toggle" onClick={toggle} aria-label={label} title={label}>
      <svg className="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
      </svg>
      <svg className="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </svg>
    </button>
  );
}
