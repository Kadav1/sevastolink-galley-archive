import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppShell } from "../components/shell/AppShell";
import { LibraryPage } from "../pages/LibraryPage";
import { RecipePage } from "../pages/RecipePage";
import { KitchenPage } from "../pages/KitchenPage";
import { IntakePage } from "../pages/IntakePage";
import { ManualEntryPage } from "../pages/ManualEntryPage";
import { PasteTextPage } from "../pages/PasteTextPage";
import { SettingsPage } from "../pages/SettingsPage";
import { PantryPage } from "../pages/PantryPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/library" replace /> },
      { path: "library", element: <LibraryPage /> },
      { path: "recipe/:slug", element: <RecipePage /> },
      { path: "pantry", element: <PantryPage /> },
      { path: "intake", element: <IntakePage /> },
      { path: "intake/manual", element: <ManualEntryPage /> },
      { path: "intake/paste", element: <PasteTextPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
  // Kitchen mode — full-screen, no shell nav
  {
    path: "/recipe/:slug/kitchen",
    element: <KitchenPage />,
  },
]);
