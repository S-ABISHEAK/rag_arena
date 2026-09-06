import { useEffect, useState } from "react"
import { Activity, Flame, Timer, Swords, AlertTriangle } from "lucide-react"
import { StatTile } from "@/components/shared/StatTile"
import { getRewardHistory } from "@/lib/api"
import type { RewardHistoryEntry } from "@/lib/types"

const STRATEGY_COUNT = 4
// Mirrors ContextualBandit.average_reward()'s cold-start threshold — a
// strategy's score is a real average only once it has this many recorded
// queries; below that it falls back to a fixed 0.65 baseline.
const WARM_UP_THRESHOLD = 5

// Every number here is folded out of the same /bandit/history array the
// Reward History table renders — nothing is computed or estimated outside
// of what the backend actually recorded.
export function ArenaOverviewStats() {
  const [history, setHistory] = useState<RewardHistoryEntry[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getRewardHistory()
      .then(setHistory)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load arena stats"))
  }, [])

  if (error) {
    return (
      <div className="flex items-center gap-2 text-xs text-[var(--color-danger)]">
        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
        {error}
      </div>
    )
  }

  if (!history) return null

  const byRetriever = new Map<string, RewardHistoryEntry[]>()
  for (const entry of history) {
    const list = byRetriever.get(entry.retriever) ?? []
    list.push(entry)
    byRetriever.set(entry.retriever, list)
  }

  const warmedUp = [...byRetriever.values()].filter((entries) => entries.length >= WARM_UP_THRESHOLD).length

  const avgLatencyMs =
    history.length > 0
      ? Math.round((history.reduce((sum, e) => sum + e.latency, 0) / history.length) * 1000)
      : 0

  const byQuestion = new Map<string, Set<string>>()
  for (const entry of history) {
    const retrievers = byQuestion.get(entry.question) ?? new Set<string>()
    retrievers.add(entry.retriever)
    byQuestion.set(entry.question, retrievers)
  }
  const matchupCount = [...byQuestion.values()].filter((retrievers) => retrievers.size >= 2).length

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatTile label="Queries Recorded" value={history.length} icon={Activity} accentColor="var(--color-traditional)" />
      <StatTile
        label="Strategies Warmed Up"
        value={warmedUp}
        suffix={`/ ${STRATEGY_COUNT}`}
        icon={Flame}
        accentColor="var(--color-hybrid)"
      />
      <StatTile label="Avg Latency" value={avgLatencyMs} suffix="ms" icon={Timer} accentColor="var(--color-pageindex)" />
      <StatTile label="Head-to-Head Matchups" value={matchupCount} icon={Swords} accentColor="var(--color-graph)" />
    </div>
  )
}
