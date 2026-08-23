import { useEffect, useState } from "react"
import { AlertTriangle } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { getModelConfig } from "@/lib/api"
import type { ModelConfig } from "@/lib/types"

const LABELS: Record<keyof ModelConfig, string> = {
  llm_model: "LLM_MODEL",
  embedding_model: "EMBEDDING_MODEL",
  chunk_size: "CHUNK_SIZE",
  chunk_overlap: "CHUNK_OVERLAP",
  top_k: "TOP_K",
  qdrant_collection: "QDRANT_COLLECTION",
}

export function ModelConfigCard() {
  const [config, setConfig] = useState<ModelConfig | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getModelConfig()
      .then(setConfig)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load config"))
  }, [])

  if (error) {
    return (
      <GlassCard>
        <div className="flex items-start gap-2 text-xs text-[var(--color-danger)]">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          {error}
        </div>
      </GlassCard>
    )
  }

  if (!config) return null

  return (
    <GlassCard>
      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Model Configuration</h3>
      <div className="rounded-xl bg-black/30 border border-white/10 p-4 font-mono text-xs space-y-2">
        {(Object.keys(config) as (keyof ModelConfig)[]).map((key) => (
          <div key={key} className="flex justify-between gap-4">
            <span className="text-[var(--color-text-muted)]">{LABELS[key]}</span>
            <span className="text-[var(--color-text-primary)] truncate">{String(config[key])}</span>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}
