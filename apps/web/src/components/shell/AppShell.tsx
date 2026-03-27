import { Outlet } from "react-router-dom";
import { SideNav } from "./SideNav";

export function AppShell() {
  return (
    <div style={styles.shell}>
      <SideNav />
      <main style={styles.main}>
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
  main: {
    flex: 1,
    overflow: "auto",
    padding: "var(--space-8)",
  },
} as const;
