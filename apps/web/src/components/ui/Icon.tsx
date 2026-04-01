/**
 * Icon — inline SVG icon set for navigation and UI chrome.
 *
 * Usage:
 *   <Icon name="library" size={16} />
 */

export type IconName =
  | "library"
  | "pantry"
  | "intake"
  | "settings"
  | "menu"
  | "close"
  | "chevron-left"
  | "star"
  | "star-filled";

interface Props {
  name: IconName;
  size?: number;
  /** Accessible label. Omit if icon is decorative (has adjacent text). */
  label?: string;
}

const PATHS: Record<IconName, string> = {
  // Open book
  library:
    "M4 19V6a2 2 0 0 1 2-2h12v13H6a2 2 0 0 0-2 2zm0 0a2 2 0 0 0 2 2h12M9 7h6M9 11h4",
  // Bowl with ingredients
  pantry:
    "M6 9H4a1 1 0 0 0-1 1v1a7 7 0 0 0 14 0v-1a1 1 0 0 0-1-1h-2M8 9V5a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v4M12 14v3M10 17h4",
  // Inbox / tray with down arrow
  intake:
    "M8 16H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-3M12 12v6M9 15l3 3 3-3",
  // Gear / cog
  settings:
    "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm7-3a7 7 0 0 1-.09 1.13l1.71 1.34a.4.4 0 0 1 .1.51l-1.62 2.81a.4.4 0 0 1-.49.17l-2.02-.81a7.2 7.2 0 0 1-1.95 1.13l-.3 2.15a.41.41 0 0 1-.4.35h-3.24a.41.41 0 0 1-.4-.35l-.3-2.15a7.2 7.2 0 0 1-1.95-1.13l-2.02.81a.4.4 0 0 1-.49-.17l-1.62-2.81a.4.4 0 0 1 .1-.51l1.71-1.34A7.15 7.15 0 0 1 5 12c0-.39.03-.77.09-1.13L3.38 9.53a.4.4 0 0 1-.1-.51l1.62-2.81a.4.4 0 0 1 .49-.17l2.02.81A7.2 7.2 0 0 1 9.36 5.72l.3-2.15A.41.41 0 0 1 10.06 3.22h3.24a.41.41 0 0 1 .4.35l.3 2.15a7.2 7.2 0 0 1 1.95 1.13l2.02-.81a.4.4 0 0 1 .49.17l1.62 2.81a.4.4 0 0 1-.1.51l-1.71 1.34c.06.36.09.74.09 1.13z",
  // Hamburger menu
  menu: "M4 6h16M4 12h16M4 18h16",
  // X
  close: "M18 6 6 18M6 6l12 12",
  // Left chevron
  "chevron-left": "M15 18l-6-6 6-6",
  // Star outline
  star: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z",
  // Star filled
  "star-filled":
    "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z",
};

export function Icon({ name, size = 16, label }: Props) {
  const path = PATHS[name];
  const isFilled = name === "star-filled";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={isFilled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? "img" : undefined}
      style={{ display: "block", flexShrink: 0 }}
    >
      <path d={path} />
    </svg>
  );
}
