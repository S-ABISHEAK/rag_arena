import { useState } from "react"
import { AlertTriangle, X } from "lucide-react"
import { StrategyScoreBoard } from "@/components/arena/StrategyScoreBoard"
import { EmbeddingRouterInspector } from "@/components/arena/EmbeddingRouterInspector"
import { RewardHistoryTable } from "@/components/arena/RewardHistoryTable"

export function ArenaPage() {
  const [bannerVisible, setBannerVisible] = useState(true)

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      {bannerVisible && (
        <div className="flex items-start gap-3 rounded-xl border border-[var(--color-warning)]/30 bg-[var(--color-warning)]/10 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-[var(--color-warning)] shrink-0 mt-0.5" />
          <p className="text-xs text-[var(--color-text-secondary)] flex-1">
            Scores reflect seed values until the reward-learning loop is fully wired to live queries.
          </p>
          <button onClick={() => setBannerVisible(false)} className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <StrategyScoreBoard />
      <EmbeddingRouterInspector />
      <RewardHistoryTable />
    </div>
  )
}
