import { GlassCard } from "@/components/shared/GlassCard"
import { StrategyBadge } from "@/components/shared/StrategyBadge"
import { LatencyChip } from "@/components/shared/LatencyChip"
import { CacheIndicator } from "@/components/shared/CacheIndicator"
import { RagasScoreCard } from "@/components/shared/RagasScoreCard"
import { SourceList } from "./SourceList"
import { GraphContextPanel } from "./GraphContextPanel"
import { PageSelectionTrail } from "./PageSelectionTrail"
import { RouterDecisionBadge } from "./RouterDecisionBadge"
import { strategyFromRetrievalType } from "@/lib/strategy"
import type { QueryResult } from "@/lib/types"

interface AnswerCardProps {
  result: QueryResult
  showEvaluate?: boolean
}

export function AnswerCard({ result, showEvaluate = true }: AnswerCardProps) {
  const meta = strategyFromRetrievalType(result.retrieval_type)

  return (
    <GlassCard accentColor={meta.color} className="animate-fade-in">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <StrategyBadge retrievalType={result.retrieval_type} />
          {result.selected_strategy && <RouterDecisionBadge strategy={result.selected_strategy} />}
        </div>
        <div className="flex items-center gap-2">
          <CacheIndicator hit={result.cache_hit} />
          <LatencyChip latency={result.latency} />
        </div>
      </div>

      <p className="text-sm leading-relaxed text-[var(--color-text-primary)]">{result.answer}</p>

      {result.retrieval_type === "graph" && result.context && (
        <GraphContextPanel context={result.context} />
      )}

      {result.retrieval_type === "pageindex_v2" && result.selected_pages && (
        <PageSelectionTrail pages={result.selected_pages} />
      )}

      {result.sources && result.sources.length > 0 && <SourceList sources={result.sources} />}

      {showEvaluate && (
        <RagasScoreCard
          question={result.question}
          answer={result.answer}
          context={result.sources?.map((s) => s.snippet ?? "") ?? []}
        />
      )}
    </GlassCard>
  )
}
