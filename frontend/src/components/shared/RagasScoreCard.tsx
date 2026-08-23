import { useState } from "react"
import { Sparkles, Loader2, AlertTriangle } from "lucide-react"
import { evaluateRagas } from "@/lib/api"
import type { RagasScore } from "@/lib/types"
import { cn } from "@/lib/utils"

function bandColor(score: number | null) {
  if (score === null) return "var(--color-text-muted)"
  if (score >= 0.75) return "var(--color-success)"
  if (score >= 0.5) return "var(--color-warning)"
  return "var(--color-danger)"
}

function Gauge({ label, score, approximate }: { label: string; score: number | null; approximate?: boolean }) {
  const pct = score ?? 0
  const circumference = 2 * Math.PI * 28
  const offset = circumference * (1 - pct)
  const color = bandColor(score)

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-20 h-20">
        <svg viewBox="0 0 68 68" className="w-20 h-20 -rotate-90">
          <circle cx="34" cy="34" r="28" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
          <circle
            cx="34"
            cy="34"
            r="28"
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeDasharray={approximate ? "4 3" : circumference}
            strokeDashoffset={score === null ? circumference : offset}
            strokeLinecap="round"
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center font-mono-nums text-sm font-semibold">
          {score !== null ? Math.round(score * 100) : "—"}
        </div>
      </div>
      <div className="text-center">
        <div className="text-xs text-[var(--color-text-secondary)]">{label}</div>
        {approximate && <div className="text-[10px] text-[var(--color-warning)]">approximate</div>}
      </div>
    </div>
  )
}

interface RagasScoreCardProps {
  question: string
  answer: string
  context: string[]
}

export function RagasScoreCard({ question, answer, context }: RagasScoreCardProps) {
  const [score, setScore] = useState<RagasScore | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run() {
    setLoading(true)
    setError(null)
    try {
      const result = await evaluateRagas(question, answer, context)
      setScore(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed")
    } finally {
      setLoading(false)
    }
  }

  if (error) {
    return (
      <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/10 px-4 py-3 text-xs text-[var(--color-text-secondary)]">
        <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
        {error}
      </div>
    )
  }

  if (!score && !loading) {
    return (
      <button
        onClick={run}
        className={cn(
          "mt-4 inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-white/10",
          "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-white/5 transition-colors"
        )}
      >
        <Sparkles className="w-3.5 h-3.5" />
        Evaluate this answer
      </button>
    )
  }

  if (loading) {
    return (
      <div className="mt-4 flex items-center gap-2 text-xs text-[var(--color-text-muted)]">
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
        Scoring with RAGAS...
      </div>
    )
  }

  if (score!.error) {
    return (
      <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/10 px-4 py-3 text-xs text-[var(--color-text-secondary)]">
        <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
        {score!.error}
      </div>
    )
  }

  return (
    <div className="mt-4 flex items-center gap-6 rounded-xl border border-white/10 p-4">
      <Gauge label="Faithfulness" score={score!.faithfulness} approximate={score!.approximate} />
      <Gauge label="Answer Relevancy" score={score!.answer_relevancy} approximate={score!.approximate} />
    </div>
  )
}
