import { Outlet, useLocation } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { TopBar } from "./TopBar"

const TITLES: Record<string, string> = {
  "/": "Ask",
  "/ingest": "Ingest",
  "/arena": "Arena",
  "/compare": "Compare & Evaluate",
  "/dashboard": "Dashboard",
  "/settings": "Settings",
}

// Screens that use the calm Glass + Minimal Flat treatment only.
const CALM_ROUTES = new Set(["/", "/ingest", "/settings"])

export function AppLayout() {
  const location = useLocation()
  const title = TITLES[location.pathname] ?? "RAG Arena"
  const calm = CALM_ROUTES.has(location.pathname)

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--color-bg-primary)]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar title={title} />
        <main
          className={
            calm
              ? "flex-1 overflow-y-auto"
              : "flex-1 overflow-y-auto bg-[var(--color-bg-secondary)]"
          }
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}
