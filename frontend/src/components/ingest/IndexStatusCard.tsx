import { useEffect, useState } from "react"
import { AlertTriangle, Boxes, FileStack, GitBranch, Share2 } from "lucide-react"
import { StatTile } from "@/components/shared/StatTile"
import { getIndexStatus } from "@/lib/api"
import type { IndexStatus } from "@/lib/types"

export function IndexStatusCard({ refreshKey }: { refreshKey?: number }) {
  const [status, setStatus] = useState<IndexStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setError(null)
    getIndexStatus()
      .then(setStatus)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load index status"))
  }, [refreshKey])

  if (error) {
    return (
      <div className="flex items-center gap-2 text-xs text-[var(--color-danger)]">
        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
        {error}
      </div>
    )
  }

  if (!status) return null

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatTile label="Chunks" value={status.chunk_count} icon={Boxes} accentColor="var(--color-traditional)" />
      <StatTile label="Pages" value={status.page_count} icon={FileStack} accentColor="var(--color-pageindex)" />
      <StatTile label="Graph Nodes" value={status.graph_node_count} icon={Share2} accentColor="var(--color-graph)" />
      <StatTile label="Graph Edges" value={status.graph_edge_count} icon={GitBranch} accentColor="var(--color-graph)" />
    </div>
  )
}
