import { useState } from "react"
import { Play, Loader2, SearchCode, AlertTriangle } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { EmptyState } from "@/components/shared/EmptyState"
import { embeddingRouterScores } from "@/lib/api"
import type { StrategyScore } from "@/lib/types"
import { strategyFromName } from "@/lib/strategy"
import { cn } from "@/lib/utils"

export function EmbeddingRouterInspector() {
  const [question, setQuestion] = useState("")
  const [scores, setScores] = useState<StrategyScore[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run() {
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    try {
      const result = await embeddingRouterScores(question.trim())
      setScores(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Routing inspection failed")
      setScores(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <GlassCard>
      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-1">Embedding Router Inspector</h3>
      <p className="text-xs text-[var(--color-text-muted)] mb-4">
        See why a question would be routed the way it is
      </p>

      <div className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          placeholder="Paste a question to inspect routing..."
          className="flex-1 bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-xs outline-none focus:border-white/25"
        />
        <button
          onClick={run}
          disabled={loading || !question.trim()}
          className="shrink-0 inline-flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg bg-white/10 text-[var(--color-text-primary)] hover:bg-white/15 transition-colors disabled:opacity-40"
        >
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
          Run
        </button>
      </div>

      {error && (
        <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/10 px-4 py-3 text-xs text-[var(--color-text-secondary)]">
          <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {!scores && !loading && !error && (
        <EmptyState icon={SearchCode} title="No question inspected yet" description="Run a question to see per-strategy scoring." />
      )}

      {scores && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-xs font-mono-nums">
            <thead>
              <tr className="text-[var(--color-text-muted)] text-left border-b border-white/10">
                <th className="font-sans font-normal pb-2 pr-3">Strategy</th>
                <th className="font-sans font-normal pb-2 pr-3">Embedding</th>
                <th className="font-sans font-normal pb-2 pr-3">Reward</th>
                <th className="font-sans font-normal pb-2">Final</th>
              </tr>
            </thead>
            <tbody>
              {scores.map((s, i) => {
                const meta = strategyFromName(s.strategy)
                const winner = i === 0
                return (
                  <tr
                    key={s.strategy}
                    className={cn("border-b border-white/5 relative", winner && "bg-white/5")}
                  >
                    <td className="py-2 pr-3 relative">
                      {winner && (
                        <span className="absolute left-0 top-0 bottom-0 w-[3px]" style={{ background: meta.color }} />
                      )}
                      <span className="pl-2 font-sans" style={{ color: meta.color }}>
                        {meta.label}
                      </span>
                    </td>
                    <td className="py-2 pr-3 text-[var(--color-text-secondary)]">
                      {s.embedding_score?.toFixed(3) ?? "—"}
                    </td>
                    <td className="py-2 pr-3 text-[var(--color-text-secondary)]">{s.reward_score.toFixed(3)}</td>
                    <td className="py-2 text-[var(--color-text-primary)] font-semibold">
                      {s.final_score?.toFixed(3) ?? "—"}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </GlassCard>
  )
}
