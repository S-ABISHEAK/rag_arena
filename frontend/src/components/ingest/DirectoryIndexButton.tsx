import { useState } from "react"
import { FolderInput, Loader2 } from "lucide-react"
import { indexDirectory } from "@/lib/api"
import { cn } from "@/lib/utils"

export function DirectoryIndexButton({ onComplete }: { onComplete?: (chunks: number) => void }) {
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<{ text: string; isError: boolean } | null>(null)

  async function run() {
    setLoading(true)
    setToast(null)
    try {
      const result = await indexDirectory()
      setToast({ text: `Indexed ${result.chunks_indexed} chunks`, isError: false })
      onComplete?.(result.chunks_indexed)
    } catch (err) {
      setToast({ text: err instanceof Error ? err.message : "Indexing failed", isError: true })
    } finally {
      setLoading(false)
      setTimeout(() => setToast(null), 6000)
    }
  }

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={run}
        disabled={loading}
        className={cn(
          "inline-flex items-center gap-2 text-sm px-4 py-2 rounded-xl border border-white/10 transition-colors",
          "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-white/5"
        )}
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FolderInput className="w-4 h-4" />}
        Index default folder
      </button>
      {toast && (
        <span
          className={cn(
            "text-xs animate-fade-in",
            toast.isError ? "text-[var(--color-danger)]" : "text-[var(--color-success)]"
          )}
        >
          {toast.text}
        </span>
      )}
    </div>
  )
}
