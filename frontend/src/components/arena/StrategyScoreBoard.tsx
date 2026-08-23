import { useEffect, useState } from "react"
import { AlertTriangle } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { getBanditScores } from "@/lib/api"
import type { StrategyScore } from "@/lib/types"
import { strategyFromName } from "@/lib/strategy"
import { cn } from "@/lib/utils"

const RANK_LABEL = ["1st", "2nd", "3rd", "4th"]

export function StrategyScoreBoard({ compact = false }: { compact?: boolean }) {
  const [scores, setScores] = useState<StrategyScore[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getBanditScores()
      .then((data) => setScores([...data].sort((a, b) => b.reward_score - a.reward_score)))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load scores"))
  }, [])

  const max = Math.max(...scores.map((s) => s.reward_score), 0.01)

  return (
    <GlassCard>
      {!compact && (
        <div className="mb-5">
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Strategy Leaderboard</h3>
          <p className="text-xs text-[var(--color-text-muted)] mt-0.5">Live bandit average reward per strategy</p>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 text-xs text-[var(--color-danger)] mb-3">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      <div className={cn("space-y-3", compact && "space-y-2")}>
        {scores.map((s, i) => {
          const meta = strategyFromName(s.strategy)
          const Icon = meta.icon
          return (
            <div key={s.strategy} className="flex items-center gap-3">
              <span className="font-mono text-[10px] text-[var(--color-text-muted)] w-7 shrink-0">
                {RANK_LABEL[i]}
              </span>
              <Icon className="w-3.5 h-3.5 shrink-0" style={{ color: meta.color }} />
              <span className="text-xs text-[var(--color-text-secondary)] w-20 shrink-0">{meta.label}</span>
              <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
                <div
                  className="h-full rounded-full animate-bar-grow origin-left"
                  style={{ width: `${(s.reward_score / max) * 100}%`, background: meta.color }}
                />
              </div>
              <span className="font-mono-nums text-xs text-[var(--color-text-primary)] w-12 text-right shrink-0">
                {s.reward_score.toFixed(3)}
              </span>
            </div>
          )
        })}
      </div>
    </GlassCard>
  )
}
