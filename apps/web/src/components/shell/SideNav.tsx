import { NavLink } from "react-router-dom";
import { Icon, type IconName } from "../ui/Icon";

type NavItem = {
  label: string;
  to: string;
  icon: IconName;
};

type SideNavProps = {
  /** True when rendered as a fixed overlay (mobile / tablet). */
  overlay?: boolean;
  /** Called when the user requests to close the nav (overlay mode only). */
  onClose?: () => void;
};

const NAV_ITEMS: NavItem[] = [
  { label: "Library", to: "/library", icon: "library" },
  { label: "Pantry", to: "/pantry", icon: "pantry" },
  { label: "Intake", to: "/intake", icon: "intake" },
  { label: "Settings", to: "/settings", icon: "settings" },
];

export function SideNav({ overlay = false, onClose }: SideNavProps) {
  return (
    <nav
      style={{ ...styles.nav, ...(overlay ? styles.navOverlay : {}) }}
      aria-label="Primary navigation"
    >
      <div style={styles.brand}>
        <span style={styles.brandText}>Galley</span>
        {overlay && onClose && (
          <button
            style={styles.closeBtn}
            onClick={onClose}
            aria-label="Close navigation"
          >
            <Icon name="close" size={16} />
          </button>
        )}
      </div>

      <ul style={styles.list}>
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              onClick={overlay ? onClose : undefined}
              style={({ isActive }) => ({
                ...styles.link,
                ...(isActive ? styles.linkActive : {}),
              })}
            >
              <Icon name={item.icon} size={15} />
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

const styles = {
  nav: {
    width: "var(--nav-width)",
    minWidth: "var(--nav-width)",
    height: "100dvh",
    background: "var(--bg-base)",
    borderRight: "1px solid var(--border-primary)",
    display: "flex",
    flexDirection: "column" as const,
    padding: "var(--space-6) 0",
    position: "sticky" as const,
    top: 0,
  },
  // Overlay variant — fixed, full-height, above backdrop
  navOverlay: {
    position: "fixed" as const,
    top: 0,
    left: 0,
    height: "100dvh",
    zIndex: 30,
  },
  brand: {
    padding: "0 var(--space-6) var(--space-8)",
    borderBottom: "1px solid var(--border-subtle)",
    marginBottom: "var(--space-6)",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  brandText: {
    fontFamily: "var(--font-display)",
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    color: "var(--text-secondary)",
  },
  closeBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--text-tertiary)",
    fontSize: "var(--text-base)",
    padding: "var(--space-1)",
    lineHeight: 1,
  },
  list: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    padding: "0 var(--space-3)",
  },
  link: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-2)",
    padding: "var(--space-2) var(--space-3)",
    borderRadius: "var(--radius-sm)",
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    transition: "color var(--transition-fast), background var(--transition-fast)",
    letterSpacing: "var(--tracking-normal)",
  },
  linkActive: {
    color: "var(--text-primary)",
    background: "var(--bg-panel)",
  },
} as const;
