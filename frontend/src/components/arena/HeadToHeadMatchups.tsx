import { useEffect, useState } from "react"
import { AlertTriangle, Swords } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { EmptyState } from "@/components/shared/EmptyState"
import { StrategyBadge } from "@/components/shared/StrategyBadge"
import { getRewardHistory } from "@/lib/api"
import type { RewardHistoryEntry } from "@/lib/types"
import { strategyFromName } from "@/lib/strategy"
import { cn } from "@/lib/utils"

interface Matchup {
  question: string
  entries: RewardHistoryEntry[]
  winner: string
}

const MAX_SHOWN = 6

// A "matchup" is a real question that happened to be run under two or more
// different strategies (e.g. via Compare, or asked again under a different
// strategy) — nothing is simulated to create one. The winner is whichever
// entry has the higher recorded reward, i.e. the lower real latency
// (RewardFunction.compute = 1 / (1 + latency)).
export function HeadToHeadMatchups() {
  const [matchups, setMatchups] = useState<Matchup[] | null>(null)
  const [winTally, setWinTally] = useState<Record<string, number>>({})
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getRewardHistory()
      .then((history) => {
        const byQuestion = new Map<string, Map<string, RewardHistoryEntry>>()

        for (const entry of history) {
          const byRetriever = byQuestion.get(entry.question) ?? new Map<string, RewardHistoryEntry>()
          // Keep the latest attempt per retriever for a given question so a
          // re-run doesn't count the same matchup twice.
          byRetriever.set(entry.retriever, entry)
          byQuestion.set(entry.question, byRetriever)
        }

        const tally: Record<string, number> = {}
        const found: Matchup[] = []

        for (const [question, byRetriever] of byQuestion) {
          const entries = [...byRetriever.values()]
          if (entries.length < 2) continue

          const winner = entries.reduce((best, e) => (e.reward > best.reward ? e : best)).retriever
          tally[winner] = (tally[winner] ?? 0) + 1
          found.push({ question, entries, winner })
        }

        setMatchups(found.reverse())
        setWinTally(tally)
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load matchups"))
  }, [])

  return (
    <GlassCard>
      <div className="mb-4 flex items-start justify-between flex-wrap gap-2">
        <div>
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Head-to-Head Matchups</h3>
          <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
            Real questions run under more than one strategy — winner is the faster real latency
          </p>
        </div>
        {matchups && matchups.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap">
            {Object.entries(winTally)
              .sort((a, b) => b[1] - a[1])
              .map(([retriever, wins]) => (
                <span key={retriever} className="inline-flex items-center gap-1 text-[10px] font-mono-nums text-[var(--color-text-secondary)]">
                  <StrategyBadge strategy={retriever} size="sm" />
                  {wins}
                </span>
              ))}
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 text-xs text-[var(--color-danger)]">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {matchups && matchups.length === 0 && !error && (
        <EmptyState
          icon={Swords}
          title="No matchups yet"
          description="Ask the same question under two different strategies (e.g. from the Compare tab) to see a head-to-head."
        />
      )}

      {matchups && matchups.length > 0 && (
        <div className="space-y-3">
          {matchups.slice(0, MAX_SHOWN).map((m, i) => (
            <div key={i} className="rounded-xl border border-white/5 bg-white/[0.02] px-4 py-3">
              <p className="text-xs text-[var(--color-text-secondary)] truncate mb-2">{m.question}</p>
              <div className="flex flex-wrap gap-2">
                {[...m.entries]
                  .sort((a, b) => b.reward - a.reward)
                  .map((entry) => {
                    const isWinner = entry.retriever === m.winner
                    const meta = strategyFromName(entry.retriever)
                    return (
                      <div
                        key={entry.retriever}
                        className={cn(
                          "flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-[11px]",
                          isWinner ? "bg-white/10" : "bg-white/[0.03]"
                        )}
                        style={isWinner ? { boxShadow: `inset 0 0 0 1px ${meta.color}55` } : undefined}
                      >
                        <StrategyBadge strategy={entry.retriever} size="sm" />
                        <span className="font-mono-nums text-[var(--color-text-primary)]">{entry.latency.toFixed(3)}s</span>
                        {isWinner && <span className="text-[10px]" style={{ color: meta.color }}>WIN</span>}
                      </div>
                    )
                  })}
              </div>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  )
}
