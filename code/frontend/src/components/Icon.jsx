/**
 * Zestaw ikon SVG. Wszystkie dziedziczą kolor tekstu (`currentColor`) i rozmiar
 * ustawiany przez CSS (`.icon`), więc wstawia się je bez propsów.
 */
const Svg = ({ children, ...rest }) => (
  <svg
    className="icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...rest}
  >
    {children}
  </svg>
);

export const ChevronUp = (p) => (
  <Svg {...p}>
    <path d="M6 15l6-6 6 6" />
  </Svg>
);

export const ChevronDown = (p) => (
  <Svg {...p}>
    <path d="M6 9l6 6 6-6" />
  </Svg>
);

export const CommentIcon = (p) => (
  <Svg {...p}>
    <path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
  </Svg>
);

export const Clock = (p) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </Svg>
);

export const Plus = (p) => (
  <Svg {...p}>
    <path d="M12 5v14M5 12h14" />
  </Svg>
);

export const Pencil = (p) => (
  <Svg {...p}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" />
  </Svg>
);

export const Trash = (p) => (
  <Svg {...p}>
    <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6" />
  </Svg>
);

export const LinkIcon = (p) => (
  <Svg {...p}>
    <path d="M10 13a5 5 0 0 0 7.5.5l3-3A5 5 0 0 0 13.5 3.5l-1.7 1.7" />
    <path d="M14 11a5 5 0 0 0-7.5-.5l-3 3A5 5 0 0 0 10.5 20.5l1.7-1.7" />
  </Svg>
);

export const Inbox = (p) => (
  <Svg {...p}>
    <path d="M22 12h-6l-2 3h-4l-2-3H2" />
    <path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.7 1.1z" />
  </Svg>
);

export const ArrowLeft = (p) => (
  <Svg {...p}>
    <path d="M19 12H5M12 19l-7-7 7-7" />
  </Svg>
);
