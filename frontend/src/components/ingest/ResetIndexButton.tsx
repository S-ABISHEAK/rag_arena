import { useState } from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { Trash2, Loader2, AlertTriangle } from "lucide-react"
import { resetIndex } from "@/lib/api"
import { cn } from "@/lib/utils"

export function ResetIndexButton({ onReset }: { onReset?: () => void }) {
  const [open, setOpen] = useState(false)
  const [confirmText, setConfirmText] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleReset() {
    setLoading(true)
    setError(null)
    try {
      await resetIndex()
      setOpen(false)
      setConfirmText("")
      onReset?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <button className="inline-flex items-center gap-2 text-sm px-4 py-2 rounded-xl border border-[var(--color-danger)]/30 text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 transition-colors">
          <Trash2 className="w-4 h-4" />
          Reset index
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" />
        <Dialog.Content className="glass fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-2xl p-6 w-[90vw] max-w-sm z-50">
          <Dialog.Title className="text-sm font-semibold text-[var(--color-text-primary)]">
            Reset all indexed data?
          </Dialog.Title>
          <Dialog.Description className="text-xs text-[var(--color-text-secondary)] mt-2">
            This will wipe all indexed chunks, page summaries, and the entity graph. This cannot be
            undone. Type <span className="font-mono text-[var(--color-danger)]">RESET</span> to confirm.
          </Dialog.Description>
          <input
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="RESET"
            className="w-full mt-4 bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono outline-none focus:border-[var(--color-danger)]/50"
          />
          {error && (
            <div className="flex items-start gap-2 mt-3 text-xs text-[var(--color-danger)]">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              {error}
            </div>
          )}
          <div className="flex justify-end gap-2 mt-5">
            <Dialog.Close asChild>
              <button className="text-xs px-3 py-2 rounded-lg text-[var(--color-text-secondary)] hover:bg-white/5">
                Cancel
              </button>
            </Dialog.Close>
            <button
              onClick={handleReset}
              disabled={confirmText !== "RESET" || loading}
              className={cn(
                "text-xs px-3 py-2 rounded-lg inline-flex items-center gap-1.5 transition-colors",
                confirmText === "RESET"
                  ? "bg-[var(--color-danger)] text-white"
                  : "bg-white/5 text-[var(--color-text-muted)]"
              )}
            >
              {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              Confirm reset
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
