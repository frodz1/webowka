/** Numery stron do pokazania: wszystkie dla krótkich list, w przeciwnym razie 1, 2, …, n z oknem wokół bieżącej. */
export function pageItems(page, pages) {
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1);
  const shown = new Set([1, 2, pages, page - 1, page, page + 1]);
  const nums = [...shown].filter((n) => n >= 1 && n <= pages).sort((a, b) => a - b);
  const items = [];
  nums.forEach((n, i) => {
    if (i > 0 && n - nums[i - 1] > 1) items.push('gap');
    items.push(n);
  });
  return items;
}

export default function Pagination({ page, pages, onChange }) {
  if (pages <= 1) return null;
  return (
    <nav className="pager" aria-label="Strony">
      <button className="page-btn" disabled={page <= 1} onClick={() => onChange(page - 1)} aria-label="Poprzednia strona">
        ←
      </button>
      {pageItems(page, pages).map((item, i) =>
        item === 'gap' ? (
          <span key={`gap-${i}`} className="page-gap">
            …
          </span>
        ) : (
          <button
            key={item}
            className={`page-btn ${item === page ? 'active' : ''}`}
            onClick={() => onChange(item)}
            aria-label={`Strona ${item}`}
            aria-current={item === page ? 'page' : undefined}
          >
            {item}
          </button>
        ),
      )}
      <button className="page-btn" disabled={page >= pages} onClick={() => onChange(page + 1)} aria-label="Następna strona">
        →
      </button>
    </nav>
  );
}
