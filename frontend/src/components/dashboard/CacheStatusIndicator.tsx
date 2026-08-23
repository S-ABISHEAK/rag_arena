import { Zap } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { useConnectionHealth } from "@/lib/healthStore"
import { cn } from "@/lib/utils"

export function CacheStatusIndicator() {
  const health = useConnectionHealth()
  const redis = health.find((h) => h.service === "Redis")
  const reachable = redis ? redis.connected : null

  return (
    <GlassCard dense>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-[var(--color-text-secondary)] uppercase tracking-wide">Cache</span>
        <Zap className={cn("w-4 h-4", reachable ? "text-[var(--color-success)] animate-pulse-glow" : "text-[var(--color-text-muted)]")} />
      </div>
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full",
            reachable === null ? "bg-[var(--color-text-muted)]" : reachable ? "bg-[var(--color-success)]" : "bg-[var(--color-danger)]"
          )}
        />
        <span className="text-sm font-mono text-[var(--color-text-primary)]">
          {reachable === null ? "Checking..." : reachable ? "Redis reachable" : "Redis unreachable"}
        </span>
      </div>
    </GlassCard>
  )
}
