import { useState } from "react"
import { AlertTriangle, MessageSquareText } from "lucide-react"
import { StrategyPicker } from "@/components/ask/StrategyPicker"
import { QueryBox } from "@/components/ask/QueryBox"
import { AnswerCard } from "@/components/ask/AnswerCard"
import { ChatHistory } from "@/components/ask/ChatHistory"
import { EmptyState } from "@/components/shared/EmptyState"
import { AUTO_META, STRATEGIES } from "@/lib/strategy"
import { queryByStrategy } from "@/lib/api"
import { useAskStore } from "@/lib/askStore"

export function AskPage() {
  const { strategy, history, activeIndex, setStrategy, addResult, setActiveIndex } = useAskStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const activeMeta = strategy === "auto" ? AUTO_META : STRATEGIES[strategy]
  const activeResult = activeIndex !== null ? history[activeIndex] : null

  async function handleSubmit(question: string) {
    setLoading(true)
    setError(null)
    try {
      const result = await queryByStrategy(strategy, question)
      addResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex">
      <div className="hidden lg:flex flex-col w-64 border-r border-white/10 shrink-0">
        <div className="px-4 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide">
          History
        </div>
        <div className="flex-1 overflow-y-auto">
          <ChatHistory history={history} activeIndex={activeIndex} onSelect={setActiveIndex} />
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex justify-center py-6 shrink-0">
          <StrategyPicker value={strategy} onChange={setStrategy} />
        </div>

        <div className="flex-1 overflow-y-auto px-6">
          <div className="max-w-[800px] mx-auto pb-6">
            {error && (
              <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/10 px-4 py-3 text-xs text-[var(--color-text-secondary)]">
                <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
                {error}
              </div>
            )}
            {activeResult ? (
              <AnswerCard key={activeIndex} result={activeResult} />
            ) : (
              <EmptyState
                icon={MessageSquareText}
                title="Ask a question about your indexed documents"
                description="Pick a strategy above, or leave it on Auto and let the router decide for you."
              />
            )}
          </div>
        </div>

        <div className="px-6 pb-6 pt-2 shrink-0">
          <div className="max-w-[800px] mx-auto">
            <QueryBox onSubmit={handleSubmit} loading={loading} activeStrategy={activeMeta} />
          </div>
        </div>
      </div>
    </div>
  )
}
