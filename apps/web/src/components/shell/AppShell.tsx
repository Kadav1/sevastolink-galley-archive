import { useState } from "react";
import { Outlet } from "react-router-dom";
import { SideNav } from "./SideNav";
import { useIsDesktop } from "../../hooks/useBreakpoint";
import { Icon } from "../ui/Icon";

/** Height of the fixed mobile top bar in px. */
const TOPBAR_HEIGHT = 52;

export function AppShell() {
  const isDesktop = useIsDesktop();
  const [navOpen, setNavOpen] = useState(false);

  function openNav() { setNavOpen(true); }
  function closeNav() { setNavOpen(false); }

  return (
    <div style={styles.shell}>

      {/* ── Mobile / tablet top bar ──────────────────────────────────────── */}
      {!isDesktop && (
        <header style={styles.topBar}>
          <span style={styles.topBarBrand}>Galley</span>
          <button
            style={styles.hamburger}
            onClick={openNav}
            aria-label="Open navigation"
            aria-expanded={navOpen}
          >
            <Icon name="menu" size={20} />
          </button>
        </header>
      )}

      {/* ── Backdrop (mobile overlay only) ──────────────────────────────── */}
      {!isDesktop && navOpen && (
        <div
          style={styles.backdrop}
          onClick={closeNav}
          aria-hidden="true"
        />
      )}

      {/* ── Navigation ───────────────────────────────────────────────────── */}
      {/*
          Desktop: always visible, in-flow sidebar.
          Mobile:  only rendered when open; position:fixed overlay.
      */}
      {(isDesktop || navOpen) && (
        <SideNav
          overlay={!isDesktop}
          onClose={isDesktop ? undefined : closeNav}
        />
      )}

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <main
        style={{
          ...styles.main,
          paddingTop: isDesktop
            ? "var(--space-8)"
            : `${TOPBAR_HEIGHT + 16}px`,
          paddingLeft: isDesktop ? "var(--space-8)" : "var(--space-4)",
          paddingRight: isDesktop ? "var(--space-8)" : "var(--space-4)",
        }}
      >
        <Outlet />
      </main>
    </div>
  );
}

const styles = {
  shell: {
    display: "flex",
    minHeight: "100dvh",
    background: "var(--bg-graphite)",
  },

  // ── Mobile top bar ────────────────────────────────────────────────────────
  topBar: {
    position: "fixed" as const,
    top: 0,
    left: 0,
    right: 0,
    height: TOPBAR_HEIGHT,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 var(--space-4)",
    background: "var(--bg-base)",
    borderBottom: "1px solid var(--border-primary)",
    zIndex: 10,
  },
  topBarBrand: {
    fontFamily: "var(--font-display)",
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    color: "var(--text-secondary)",
  },
  hamburger: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--text-secondary)",
    padding: "var(--space-2)",
    borderRadius: "var(--radius-sm)",
  },

  // ── Backdrop ──────────────────────────────────────────────────────────────
  backdrop: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0, 0, 0, 0.55)",
    zIndex: 20,
  },

  // ── Main content area ─────────────────────────────────────────────────────
  main: {
    flex: 1,
    overflow: "auto",
    paddingBottom: "var(--space-8)",
    minWidth: 0, // prevent flex children from overflowing
  },
} as const;
