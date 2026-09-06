import { useState } from "react"
import { Info, X } from "lucide-react"
import { ArenaOverviewStats } from "@/components/arena/ArenaOverviewStats"
import { StrategyScoreBoard } from "@/components/arena/StrategyScoreBoard"
import { LatencyByStrategyChart } from "@/components/arena/LatencyByStrategyChart"
import { HeadToHeadMatchups } from "@/components/arena/HeadToHeadMatchups"
import { EmbeddingRouterInspector } from "@/components/arena/EmbeddingRouterInspector"
import { RewardHistoryTable } from "@/components/arena/RewardHistoryTable"

export function ArenaPage() {
  const [bannerVisible, setBannerVisible] = useState(true)

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      {bannerVisible && (
        <div className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3">
          <Info className="w-4 h-4 text-[var(--color-text-muted)] shrink-0 mt-0.5" />
          <p className="text-xs text-[var(--color-text-secondary)] flex-1">
            A strategy's leaderboard score is a real average of its recorded query latencies — but it only
            replaces the 0.65 cold-start baseline once that strategy has at least 5 recorded queries.
          </p>
          <button onClick={() => setBannerVisible(false)} className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <ArenaOverviewStats />
      <StrategyScoreBoard />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LatencyByStrategyChart />
        <HeadToHeadMatchups />
      </div>

      <EmbeddingRouterInspector />
      <RewardHistoryTable />
    </div>
  )
}
