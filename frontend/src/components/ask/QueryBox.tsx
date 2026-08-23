import { useState, type KeyboardEvent } from "react"
import { ArrowUp, Loader2 } from "lucide-react"
import type { StrategyMeta } from "@/lib/strategy"
import { cn } from "@/lib/utils"

interface QueryBoxProps {
  onSubmit: (question: string) => void
  loading?: boolean
  activeStrategy: StrategyMeta
}

export function QueryBox({ onSubmit, loading, activeStrategy }: QueryBoxProps) {
  const [value, setValue] = useState("")

  function submit() {
    if (!value.trim() || loading) return
    onSubmit(value.trim())
    setValue("")
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="glass rounded-2xl p-2 flex items-end gap-2">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your documents..."
        rows={1}
        className="flex-1 bg-transparent resize-none outline-none text-sm px-3 py-2.5 placeholder:text-[var(--color-text-muted)] max-h-32"
      />
      <button
        onClick={submit}
        disabled={loading || !value.trim()}
        className={cn(
          "shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-colors",
          value.trim() && !loading ? "text-white" : "text-[var(--color-text-muted)] bg-white/5"
        )}
        style={value.trim() && !loading ? { background: activeStrategy.color } : undefined}
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUp className="w-4 h-4" />}
      </button>
    </div>
  )
}
