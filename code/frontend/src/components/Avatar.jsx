/** Kółko z pierwszą literą nazwy; barwa wybierana deterministycznie z nazwy. */
export default function Avatar({ name, size }) {
  const label = (name ?? '?').trim();
  const hue = [...label].reduce((sum, ch) => sum + ch.charCodeAt(0), 0) % 6;
  return (
    <span className={`avatar hue-${hue}`} style={size ? { width: size, height: size, fontSize: size * 0.45 } : undefined} aria-hidden="true">
      {label.charAt(0).toUpperCase() || '?'}
    </span>
  );
}
