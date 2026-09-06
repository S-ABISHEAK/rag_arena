import { useEffect, useState } from "react"
import { BarChart, Bar, Cell, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts"
import { AlertTriangle, Timer } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { EmptyState } from "@/components/shared/EmptyState"
import { getRewardHistory } from "@/lib/api"
import { strategyFromName } from "@/lib/strategy"

interface LatencyBar {
  strategy: string
  label: string
  color: string
  avg_latency: number
  count: number
}

export function LatencyByStrategyChart() {
  const [bars, setBars] = useState<LatencyBar[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getRewardHistory()
      .then((history) => {
        const grouped = new Map<string, { total: number; count: number }>()
        for (const entry of history) {
          const agg = grouped.get(entry.retriever) ?? { total: 0, count: 0 }
          agg.total += entry.latency
          agg.count += 1
          grouped.set(entry.retriever, agg)
        }

        const rows = [...grouped.entries()]
          .map(([strategy, agg]) => {
            const meta = strategyFromName(strategy)
            return {
              strategy,
              label: meta.label,
              color: meta.color,
              avg_latency: Number((agg.total / agg.count).toFixed(3)),
              count: agg.count,
            }
          })
          .sort((a, b) => a.avg_latency - b.avg_latency)

        setBars(rows)
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load latency data"))
  }, [])

  return (
    <GlassCard>
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Latency by Strategy</h3>
        <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
          Average real query latency, computed from recorded queries
        </p>
      </div>

      {error && (
        <div className="flex items-start gap-2 text-xs text-[var(--color-danger)]">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {bars && bars.length === 0 && !error && (
        <EmptyState icon={Timer} title="No queries recorded yet" description="Run questions against the strategies to populate this chart." />
      )}

      {bars && bars.length > 0 && (
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={bars} layout="vertical" margin={{ left: 8, right: 24 }}>
              <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.06)" horizontal={false} />
              <XAxis
                type="number"
                unit="s"
                tick={{ fill: "var(--color-text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <Tooltip
                contentStyle={{ background: "var(--color-bg-tertiary)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "var(--color-text-primary)" }}
                formatter={(value, _name, item) => [
                  `${Number(value).toFixed(3)}s (n=${(item.payload as LatencyBar).count})`,
                  "Avg latency",
                ]}
              />
              <Bar dataKey="avg_latency" radius={[0, 4, 4, 0]} barSize={18}>
                {bars.map((bar) => (
                  <Cell key={bar.strategy} fill={bar.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </GlassCard>
  )
}
