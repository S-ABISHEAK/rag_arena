import { useRef, useState } from "react"
import { UploadCloud, Loader2, AlertTriangle, CheckCircle2 } from "lucide-react"
import { GlassCard } from "@/components/shared/GlassCard"
import { indexUpload } from "@/lib/api"
import { cn } from "@/lib/utils"

export function PdfUploadPanel({ onComplete }: { onComplete?: (chunks: number) => void }) {
  const [dragOver, setDragOver] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "indexing" | "done" | "error">("idle")
  const [message, setMessage] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    setFileName(file.name)
    setStatus("indexing")
    setMessage(null)

    try {
      const result = await indexUpload(file)
      setStatus("done")
      setMessage(`Indexed ${result.chunks_indexed} chunks`)
      onComplete?.(result.chunks_indexed)
    } catch (err) {
      setStatus("error")
      setMessage(err instanceof Error ? err.message : "Indexing failed")
    }
  }

  return (
    <GlassCard>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          const file = e.dataTransfer.files[0]
          if (file) handleFile(file)
        }}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "rounded-xl border-2 border-dashed p-10 flex flex-col items-center justify-center gap-3 cursor-pointer transition-colors",
          dragOver ? "border-[var(--color-traditional)] bg-[var(--color-traditional)]/5" : "border-white/15 hover:border-white/25"
        )}
      >
        <UploadCloud className="w-8 h-8 text-[var(--color-text-muted)]" />
        <div className="text-center">
          <p className="text-sm text-[var(--color-text-secondary)]">
            Drag and drop a PDF, or <span className="text-[var(--color-text-primary)] underline">browse</span>
          </p>
          {fileName && <p className="text-xs font-mono text-[var(--color-text-muted)] mt-1">{fileName}</p>}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
          }}
        />
      </div>

      {status === "indexing" && (
        <div className="mt-5 flex items-center gap-2.5 text-xs text-[var(--color-text-secondary)]">
          <Loader2 className="w-4 h-4 animate-spin text-[var(--color-traditional)]" />
          Chunking, embedding, summarizing pages, and extracting graph entities — this runs as one
          request and can take a while for larger PDFs.
        </div>
      )}

      {status === "done" && (
        <div className="mt-5 flex items-center gap-2.5 text-xs text-[var(--color-success)]">
          <CheckCircle2 className="w-4 h-4" />
          {message}
        </div>
      )}

      {status === "error" && (
        <div className="mt-5 flex items-start gap-2.5 text-xs text-[var(--color-danger)]">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          {message}
        </div>
      )}
    </GlassCard>
  )
}
