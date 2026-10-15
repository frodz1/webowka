const UNITS = [
  [60, 'sek.'],
  [60, 'min.'],
  [24, 'godz.'],
  [30, 'dni'],
  [12, 'mies.'],
];

export function timeAgo(iso) {
  let diff = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 10) return 'przed chwilą';
  for (const [size, label] of UNITS) {
    if (diff < size) return `${Math.floor(diff)} ${label} temu`;
    diff /= size;
  }
  return `${Math.floor(diff)} lat temu`;
}

export function commentsLabel(n) {
  if (n === 1) return '1 komentarz';
  const last = n % 10;
  const tens = n % 100;
  return last >= 2 && last <= 4 && (tens < 12 || tens > 14) ? `${n} komentarze` : `${n} komentarzy`;
}

export function domainOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}
