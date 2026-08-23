import { Database, Layers, Cpu } from "lucide-react"
import { useConnectionHealth } from "@/lib/healthStore"
import { cn } from "@/lib/utils"

const SERVICE_ICON = {
  Qdrant: Database,
  Redis: Layers,
  Groq: Cpu,
} as const

export function TopBar({ title }: { title: string }) {
  const health = useConnectionHealth()

  return (
    <header className="h-16 shrink-0 glass border-b border-white/10 flex items-center justify-between px-6">
      <h1 className="text-sm font-semibold text-[var(--color-text-primary)]">{title}</h1>
      <div className="flex items-center gap-4">
        {health.map((h) => {
          const Icon = SERVICE_ICON[h.service]
          return (
            <div key={h.service} className="flex items-center gap-1.5" title={`${h.service} · last checked ${h.last_checked}`}>
              <Icon className="w-3.5 h-3.5 text-[var(--color-text-muted)]" />
              <span
                className={cn(
                  "w-1.5 h-1.5 rounded-full",
                  h.connected ? "bg-[var(--color-success)] animate-pulse-glow" : "bg-[var(--color-danger)]"
                )}
              />
              <span className="text-xs text-[var(--color-text-muted)] font-mono hidden sm:inline">{h.service}</span>
            </div>
          )
        })}
      </div>
    </header>
  )
}
