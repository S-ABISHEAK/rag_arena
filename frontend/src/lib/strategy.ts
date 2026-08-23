import type { RetrievalType, Strategy, StrategyKey } from "./types"
import { Zap, Layers, FileStack, GitBranch, Sparkles } from "lucide-react"
import type { LucideIcon } from "lucide-react"

export interface StrategyMeta {
  key: StrategyKey
  label: string
  short: string
  color: string
  icon: LucideIcon
}

export const STRATEGIES: Record<Exclude<StrategyKey, "auto">, StrategyMeta> = {
  traditional: {
    key: "traditional",
    label: "Traditional",
    short: "TRAD",
    color: "var(--color-traditional)",
    icon: Zap,
  },
  hybrid: {
    key: "hybrid",
    label: "Hybrid",
    short: "HYBRID",
    color: "var(--color-hybrid)",
    icon: Layers,
  },
  pageindex: {
    key: "pageindex",
    label: "PageIndex",
    short: "PAGE",
    color: "var(--color-pageindex)",
    icon: FileStack,
  },
  graph: {
    key: "graph",
    label: "Graph",
    short: "GRAPH",
    color: "var(--color-graph)",
    icon: GitBranch,
  },
}

export const AUTO_META: StrategyMeta = {
  key: "auto",
  label: "Auto",
  short: "AUTO",
  color: "var(--color-traditional)",
  icon: Sparkles,
}

export function strategyFromRetrievalType(type: RetrievalType): StrategyMeta {
  switch (type) {
    case "traditional":
      return STRATEGIES.traditional
    case "hybrid":
      return STRATEGIES.hybrid
    case "pageindex_v2":
      return STRATEGIES.pageindex
    case "graph":
      return STRATEGIES.graph
  }
}

export function strategyFromName(name: Strategy | string): StrategyMeta {
  switch (name.toUpperCase()) {
    case "TRADITIONAL":
      return STRATEGIES.traditional
    case "HYBRID":
      return STRATEGIES.hybrid
    case "PAGEINDEX":
      return STRATEGIES.pageindex
    case "GRAPH":
      return STRATEGIES.graph
    default:
      return STRATEGIES.traditional
  }
}
