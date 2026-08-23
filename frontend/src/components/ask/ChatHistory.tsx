import { MessageSquare } from "lucide-react"
import type { QueryResult } from "@/lib/types"
import { strategyFromRetrievalType } from "@/lib/strategy"
import { EmptyState } from "@/components/shared/EmptyState"
import { cn } from "@/lib/utils"

interface ChatHistoryProps {
  history: QueryResult[]
  activeIndex: number | null
  onSelect: (index: number) => void
}

export function ChatHistory({ history, activeIndex, onSelect }: ChatHistoryProps) {
  if (history.length === 0) {
    return <EmptyState icon={MessageSquare} title="No questions yet" description="Your query history will appear here." />
  }

  return (
    <div className="space-y-1 p-2">
      {history.map((item, i) => {
        const meta = strategyFromRetrievalType(item.retrieval_type)
        return (
          <button
            key={i}
            onClick={() => onSelect(i)}
            className={cn(
              "w-full text-left px-3 py-2.5 rounded-xl text-xs transition-colors flex items-start gap-2",
              activeIndex === i ? "bg-white/10" : "hover:bg-white/5"
            )}
          >
            <span
              className="w-1.5 h-1.5 rounded-full mt-1 shrink-0"
              style={{ background: meta.color }}
            />
            <span className="text-[var(--color-text-secondary)] line-clamp-2">{item.question}</span>
          </button>
        )
      })}
    </div>
  )
}
