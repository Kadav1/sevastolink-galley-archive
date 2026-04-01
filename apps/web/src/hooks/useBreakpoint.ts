/**
 * Responsive breakpoints for the Galley Archive shell.
 *
 * Single threshold: desktop ≥ 1024 px.
 * Below 1024 px the shell collapses to a top-bar + overlay-nav layout.
 * This covers both phones and tablets with a single behaviour mode.
 */

import { useEffect, useState } from "react";

/** Width in px at which the layout switches to desktop (permanent sidebar). */
export const DESKTOP_BREAKPOINT = 1024;

/**
 * Returns `true` when the viewport is at least `DESKTOP_BREAKPOINT` wide.
 * Updates on window resize. SSR-safe (defaults to `true` on non-browser
 * environments so the first render matches desktop).
 */
export function useIsDesktop(): boolean {
  const [isDesktop, setIsDesktop] = useState<boolean>(() =>
    typeof window !== "undefined"
      ? window.innerWidth >= DESKTOP_BREAKPOINT
      : true
  );

  useEffect(() => {
    const mq = window.matchMedia(`(min-width: ${DESKTOP_BREAKPOINT}px)`);
    const handler = (e: MediaQueryListEvent) => setIsDesktop(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  return isDesktop;
}
