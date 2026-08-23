import { AUTO_META, STRATEGIES, strategyFromName, strategyFromRetrievalType } from "@/lib/strategy"
import type { RetrievalType, Strategy } from "@/lib/types"
import { cn } from "@/lib/utils"

interface StrategyBadgeProps {
  strategy?: Strategy | string
  retrievalType?: RetrievalType
  auto?: boolean
  size?: "sm" | "md"
  className?: string
}

export function StrategyBadge({ strategy, retrievalType, auto, size = "md", className }: StrategyBadgeProps) {
  if (auto) {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full font-mono font-semibold gradient-auto text-white",
          size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-3 py-1 text-xs",
          className
        )}
      >
        <AUTO_META.icon className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} />
        {AUTO_META.short}
      </span>
    )
  }

  const meta = strategy ? strategyFromName(strategy) : retrievalType ? strategyFromRetrievalType(retrievalType) : STRATEGIES.traditional
  const Icon = meta.icon

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-mono font-semibold",
        size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-3 py-1 text-xs",
        className
      )}
      style={{
        color: meta.color,
        background: `${meta.color}1a`,
        border: `1px solid ${meta.color}40`,
      }}
    >
      <Icon className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} />
      {meta.short}
    </span>
  )
}
