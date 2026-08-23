import { Database, Layers, Cpu } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { useConnectionHealth } from "@/lib/healthStore"
import { cn } from "@/lib/utils"

const SERVICE_ICON = { Qdrant: Database, Redis: Layers, Groq: Cpu } as const

export function ConnectionHealthPanel() {
  const health = useConnectionHealth()

  return (
    <GlassCard>
      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Connection Health</h3>

      {health.length === 0 && (
        <p className="text-xs text-[var(--color-text-muted)]">Checking...</p>
      )}

      <div className="space-y-3">
        {health.map((h) => {
          const Icon = SERVICE_ICON[h.service]
          return (
            <div key={h.service} className="flex items-center justify-between" title={h.detail}>
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-[var(--color-text-muted)]" />
                <span className="text-xs text-[var(--color-text-secondary)]">{h.service}</span>
                {!h.connected && h.detail && (
                  <span className="text-[10px] text-[var(--color-text-muted)] truncate max-w-40">{h.detail}</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-[var(--color-text-muted)]">{h.last_checked}</span>
                <span
                  className={cn(
                    "w-2 h-2 rounded-full",
                    h.connected ? "bg-[var(--color-success)] animate-pulse-glow" : "bg-[var(--color-danger)]"
                  )}
                />
              </div>
            </div>
          )
        })}
      </div>
    </GlassCard>
  )
}
