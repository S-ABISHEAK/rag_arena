import { Clock } from "lucide-react"
import { formatMs } from "@/lib/utils"

export function LatencyChip({ latency }: { latency?: number }) {
  return (
    <span className="inline-flex items-center gap-1 font-mono text-xs text-[var(--color-text-secondary)] bg-white/5 border border-white/10 rounded-full px-2 py-0.5">
      <Clock className="w-3 h-3" />
      {formatMs(latency)}
    </span>
  )
}
