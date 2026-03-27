import { NavLink } from "react-router-dom";

type NavItem = {
  label: string;
  to: string;
};

const NAV_ITEMS: NavItem[] = [
  { label: "Library", to: "/library" },
  { label: "Intake", to: "/intake" },
  { label: "Settings", to: "/settings" },
];

export function SideNav() {
  return (
    <nav style={styles.nav} aria-label="Primary navigation">
      <div style={styles.brand}>
        <span style={styles.brandText}>Galley</span>
      </div>

      <ul style={styles.list}>
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              style={({ isActive }) => ({
                ...styles.link,
                ...(isActive ? styles.linkActive : {}),
              })}
            >
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
  brand: {
    padding: "0 var(--space-6) var(--space-8)",
    borderBottom: "1px solid var(--border-subtle)",
    marginBottom: "var(--space-6)",
  },
  brandText: {
    fontFamily: "var(--font-display)",
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    color: "var(--text-secondary)",
  },
  list: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    padding: "0 var(--space-3)",
  },
  link: {
    display: "block",
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
