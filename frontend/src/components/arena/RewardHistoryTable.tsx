import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/GlassCard"
import { EmptyState } from "@/components/shared/EmptyState"
import { StrategyBadge } from "@/components/shared/StrategyBadge"
import { getRewardHistory } from "@/lib/api"
import type { RewardHistoryEntry } from "@/lib/types"
import { History, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

const PAGE_SIZE = 5

export function RewardHistoryTable() {
  const [entries, setEntries] = useState<RewardHistoryEntry[]>([])
  const [page, setPage] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getRewardHistory()
      .then(setEntries)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load reward history"))
  }, [])

  if (error) {
    return (
      <GlassCard>
        <div className="flex items-start gap-2 text-xs text-[var(--color-danger)]">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          {error}
        </div>
      </GlassCard>
    )
  }

  if (entries.length === 0) {
    return (
      <GlassCard>
        <EmptyState icon={History} title="No reward history yet" description="Recorded once queries start feeding the bandit." />
      </GlassCard>
    )
  }

  const totalPages = Math.ceil(entries.length / PAGE_SIZE)
  const pageEntries = entries.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE)

  return (
    <GlassCard>
      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Reward History</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-[var(--color-text-muted)] text-left border-b border-white/10">
              <th className="font-normal pb-2 pr-3">Question</th>
              <th className="font-normal pb-2 pr-3">Retriever</th>
              <th className="font-normal pb-2 pr-3">Latency</th>
              <th className="font-normal pb-2">Reward</th>
            </tr>
          </thead>
          <tbody>
            {pageEntries.map((entry, i) => (
              <tr key={i} className={cn("border-b border-white/5", i % 2 === 1 && "bg-white/[0.02]")}>
                <td className="py-2 pr-3 text-[var(--color-text-secondary)] max-w-64 truncate">{entry.question}</td>
                <td className="py-2 pr-3">
                  <StrategyBadge strategy={entry.retriever} size="sm" />
                </td>
                <td className="py-2 pr-3 font-mono-nums text-[var(--color-text-secondary)]">
                  {entry.latency.toFixed(3)}s
                </td>
                <td className="py-2 font-mono-nums text-[var(--color-text-primary)]">{entry.reward.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-end gap-2 mt-4">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="text-xs px-2 py-1 rounded-md text-[var(--color-text-muted)] hover:bg-white/5 disabled:opacity-30"
          >
            Prev
          </button>
          <span className="font-mono text-xs text-[var(--color-text-muted)]">
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
            className="text-xs px-2 py-1 rounded-md text-[var(--color-text-muted)] hover:bg-white/5 disabled:opacity-30"
          >
            Next
          </button>
        </div>
      )}
    </GlassCard>
  )
}
