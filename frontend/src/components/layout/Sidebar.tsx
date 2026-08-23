import { NavLink } from "react-router-dom"
import { useState } from "react"
import {
  MessageSquare,
  UploadCloud,
  Swords,
  Scale,
  LayoutDashboard,
  Settings,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"
import { cn } from "@/lib/utils"

const NAV_ITEMS = [
  { to: "/", label: "Ask", icon: MessageSquare, end: true },
  { to: "/ingest", label: "Ingest", icon: UploadCloud },
  { to: "/arena", label: "Arena", icon: Swords },
  { to: "/compare", label: "Compare & Evaluate", icon: Scale },
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        "glass h-full flex flex-col shrink-0 transition-[width] duration-200 border-r border-white/10",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex items-center gap-2 px-4 h-16 shrink-0">
        <div className="w-7 h-7 rounded-lg gradient-auto shrink-0" />
        {!collapsed && (
          <span className="font-semibold text-sm tracking-tight whitespace-nowrap">RAG Arena</span>
        )}
      </div>

      <nav className="flex-1 px-2 space-y-1 mt-2">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors",
                isActive
                  ? "bg-white/10 text-[var(--color-text-primary)]"
                  : "text-[var(--color-text-secondary)] hover:bg-white/5 hover:text-[var(--color-text-primary)]"
              )
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            {!collapsed && <span className="whitespace-nowrap">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <button
        onClick={() => setCollapsed((c) => !c)}
        className="m-2 flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs text-[var(--color-text-muted)] hover:bg-white/5 hover:text-[var(--color-text-secondary)] transition-colors"
      >
        {collapsed ? <ChevronsRight className="w-4 h-4" /> : <ChevronsLeft className="w-4 h-4" />}
        {!collapsed && "Collapse"}
      </button>
    </aside>
  )
}
