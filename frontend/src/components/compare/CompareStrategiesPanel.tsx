import { useState } from "react"
import * as Checkbox from "@radix-ui/react-checkbox"
import { Check, Play, Loader2, Scale, AlertTriangle } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { EmptyState } from "@/components/shared/EmptyState"
import { AnswerCard } from "@/components/ask/AnswerCard"
import { STRATEGIES } from "@/lib/strategy"
import { queryByStrategy } from "@/lib/api"
import type { QueryResult } from "@/lib/types"
import type { StrategyKey } from "@/lib/types"
import { cn } from "@/lib/utils"

const OPTIONS: Exclude<StrategyKey, "auto">[] = ["traditional", "hybrid", "pageindex", "graph"]

export function CompareStrategiesPanel() {
  const [question, setQuestion] = useState("")
  const [selected, setSelected] = useState<Set<Exclude<StrategyKey, "auto">>>(
    new Set(["traditional", "hybrid"])
  )
  const [results, setResults] = useState<QueryResult[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  function toggle(key: Exclude<StrategyKey, "auto">) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  async function run() {
    if (!question.trim() || selected.size < 2) return
    setLoading(true)
    setError(null)
    try {
      const outcomes = await Promise.all(
        Array.from(selected).map((strategy) => queryByStrategy(strategy, question.trim()))
      )
      setResults(outcomes)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed")
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <GlassCard>
      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-1">Compare Strategies</h3>
      <p className="text-xs text-[var(--color-text-muted)] mb-4">
        Run the same question through multiple strategies side-by-side
      </p>

      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question to compare..."
        className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none focus:border-white/25 mb-3"
      />

      <div className="flex items-center gap-4 flex-wrap mb-4">
        {OPTIONS.map((key) => {
          const meta = STRATEGIES[key]
          const checked = selected.has(key)
          return (
            <label key={key} className="flex items-center gap-2 cursor-pointer">
              <Checkbox.Root
                checked={checked}
                onCheckedChange={() => toggle(key)}
                className="w-4 h-4 rounded border border-white/20 flex items-center justify-center data-[state=checked]:bg-white/20"
                style={checked ? { borderColor: meta.color, background: `${meta.color}33` } : undefined}
              >
                <Checkbox.Indicator>
                  <Check className="w-3 h-3" style={{ color: meta.color }} />
                </Checkbox.Indicator>
              </Checkbox.Root>
              <span className="text-xs" style={{ color: checked ? meta.color : "var(--color-text-secondary)" }}>
                {meta.label}
              </span>
            </label>
          )
        })}

        <button
          onClick={run}
          disabled={loading || !question.trim() || selected.size < 2}
          className={cn(
            "ml-auto inline-flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg transition-colors",
            "bg-white/10 text-[var(--color-text-primary)] hover:bg-white/15 disabled:opacity-40"
          )}
        >
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
          Run comparison
        </button>
      </div>

      {error && (
        <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/10 px-4 py-3 text-xs text-[var(--color-text-secondary)]">
          <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {!results && !loading && !error && (
        <EmptyState icon={Scale} title="No comparison yet" description="Select at least two strategies and run a question." />
      )}

      {results && (
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${results.length}, minmax(0, 1fr))` }}>
          {results.map((r, i) => (
            <AnswerCard key={i} result={r} showEvaluate={false} />
          ))}
        </div>
      )}
    </GlassCard>
  )
}
