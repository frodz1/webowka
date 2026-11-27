/** Migający placeholder na czas wczytywania. */
export default function Skeleton({ lines = 1, width }) {
  return Array.from({ length: lines }, (_, i) => (
    <span key={i} className="skeleton" style={{ width: width ?? (i === lines - 1 && lines > 1 ? '60%' : '100%') }} />
  ));
}

export function SkeletonCard() {
  return (
    <div className="card post-card skeleton-card" aria-hidden="true">
      <div className="votes-spacer" />
      <div className="post-main">
        <Skeleton width="72%" />
        <div className="skeleton-lines">
          <Skeleton lines={2} />
        </div>
        <Skeleton width="38%" />
      </div>
    </div>
  );
}

/** Lista placeholderów wpisów. */
export function SkeletonList({ count = 5 }) {
  return (
    <div role="status" aria-label="Wczytywanie">
      {Array.from({ length: count }, (_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
