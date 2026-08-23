import { useState } from "react"
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts"
import { Play, Loader2, Gauge, AlertTriangle } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { EmptyState } from "@/components/shared/EmptyState"
import { runBenchmark } from "@/lib/api"
import type { BenchmarkResult } from "@/lib/types"
import { STRATEGIES } from "@/lib/strategy"

export function BenchmarkRunner() {
  const [text, setText] = useState("What is Redis?\nWhat is this document about?")
  const [results, setResults] = useState<BenchmarkResult[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run() {
    const questions = text.split("\n").map((q) => q.trim()).filter(Boolean)
    if (questions.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const all = (await Promise.all(questions.map((q) => runBenchmark(q)))).flat()
      setResults(all)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Benchmark failed")
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const aggregate = results
    ? Object.values(
        results.reduce<Record<string, { rag_name: string; total: number; count: number }>>((acc, r) => {
          acc[r.rag_name] ??= { rag_name: r.rag_name, total: 0, count: 0 }
          acc[r.rag_name].total += r.latency
          acc[r.rag_name].count += 1
          return acc
        }, {})
      ).map((v) => ({ rag_name: v.rag_name, avg_latency: Number((v.total / v.count).toFixed(3)) }))
    : []

  return (
    <GlassCard>
      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-1">Benchmark Runner</h3>
      <p className="text-xs text-[var(--color-text-muted)] mb-4">
        Batch a list of questions across Traditional vs Hybrid RAG
      </p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        placeholder="One question per line..."
        className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono outline-none focus:border-white/25 resize-none"
      />

      <button
        onClick={run}
        disabled={loading}
        className="mt-3 inline-flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg bg-white/10 text-[var(--color-text-primary)] hover:bg-white/15 transition-colors disabled:opacity-40"
      >
        {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
        Run benchmark
      </button>

      {error && (
        <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/10 px-4 py-3 text-xs text-[var(--color-text-secondary)]">
          <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {!results && !loading && !error && (
        <div className="mt-4">
          <EmptyState icon={Gauge} title="No benchmark run yet" />
        </div>
      )}

      {results && (
        <div className="mt-5 space-y-5">
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aggregate} layout="vertical" margin={{ left: 8, right: 24 }}>
                <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" tick={{ fill: "var(--color-text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} />
                <YAxis
                  type="category"
                  dataKey="rag_name"
                  tick={{ fill: "var(--color-text-secondary)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={90}
                />
                <Tooltip
                  contentStyle={{ background: "var(--color-bg-tertiary)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "var(--color-text-primary)" }}
                />
                <Bar dataKey="avg_latency" radius={[0, 4, 4, 0]} fill={STRATEGIES.traditional.color} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-[var(--color-text-muted)] text-left border-b border-white/10">
                  <th className="font-normal pb-2 pr-3">Strategy</th>
                  <th className="font-normal pb-2 pr-3">Question</th>
                  <th className="font-normal pb-2 pr-3">Latency</th>
                  <th className="font-normal pb-2">Chunks</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-2 pr-3 text-[var(--color-text-secondary)]">{r.rag_name}</td>
                    <td className="py-2 pr-3 text-[var(--color-text-secondary)] max-w-56 truncate">{r.question}</td>
                    <td className="py-2 pr-3 font-mono-nums text-[var(--color-text-primary)]">{r.latency.toFixed(3)}s</td>
                    <td className="py-2 font-mono-nums text-[var(--color-text-primary)]">{r.retrieved_chunks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </GlassCard>
  )
}
