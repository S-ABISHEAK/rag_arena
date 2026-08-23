import { useState } from "react"
import { getPages } from "@/lib/api"
import type { PageSummary } from "@/lib/types"
import { STRATEGIES } from "@/lib/strategy"
import { cn } from "@/lib/utils"

export function PageSelectionTrail({ pages }: { pages: number[] }) {
  const [expanded, setExpanded] = useState<number | null>(null)
  const [summaries, setSummaries] = useState<PageSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const color = STRATEGIES.pageindex.color

  async function toggle(page: number) {
    if (expanded === page) {
      setExpanded(null)
      return
    }
    if (summaries.length === 0) {
      try {
        const data = await getPages()
        setSummaries(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load page summaries")
      }
    }
    setExpanded(page)
  }

  return (
    <div className="mt-4">
      <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wide mb-2">
        Selected Pages
      </div>
      <div className="flex flex-wrap gap-2">
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => toggle(p)}
            className={cn(
              "font-mono text-xs px-2.5 py-1 rounded-lg border transition-colors",
              expanded === p ? "text-white" : "hover:bg-white/5"
            )}
            style={{
              borderColor: `${color}55`,
              background: expanded === p ? `${color}33` : `${color}14`,
              color: expanded === p ? undefined : color,
            }}
          >
            p.{p}
          </button>
        ))}
      </div>
      {error && <p className="mt-2 text-xs text-[var(--color-danger)]">{error}</p>}

      {expanded !== null && !error && (
        <div className="mt-2 rounded-xl border border-white/10 p-3 text-xs text-[var(--color-text-secondary)]">
          {summaries.find((s) => s.page_number === expanded)?.summary ?? "No summary available for this page."}
        </div>
      )}
    </div>
  )
}
