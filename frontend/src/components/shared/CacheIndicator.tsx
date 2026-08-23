import { Zap } from "lucide-react"
import { cn } from "@/lib/utils"

export function CacheIndicator({ hit }: { hit?: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-mono text-xs rounded-full px-2 py-0.5 border",
        hit
          ? "text-[var(--color-success)] border-[var(--color-success)]/40 bg-[var(--color-success)]/10"
          : "text-[var(--color-text-muted)] border-white/10 bg-white/5"
      )}
      title={hit ? "Served from cache" : "Cache miss"}
    >
      <Zap className={cn("w-3 h-3", hit && "animate-pulse-glow")} />
      {hit ? "cached" : "live"}
    </span>
  )
}
