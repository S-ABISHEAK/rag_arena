import { useState } from "react"
import { PdfUploadPanel } from "@/components/ingest/PdfUploadPanel"
import { DirectoryIndexButton } from "@/components/ingest/DirectoryIndexButton"
import { IndexStatusCard } from "@/components/ingest/IndexStatusCard"
import { ResetIndexButton } from "@/components/ingest/ResetIndexButton"

export function IngestPage() {
  const [refreshKey, setRefreshKey] = useState(0)

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">Ingest documents</h2>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          Upload a PDF or index the default folder. Each document is chunked, embedded, summarized
          page-by-page, and mined for entities — so this can take a little while.
        </p>
      </div>

      <PdfUploadPanel onComplete={() => setRefreshKey((k) => k + 1)} />

      <div className="flex items-center justify-between flex-wrap gap-3">
        <DirectoryIndexButton onComplete={() => setRefreshKey((k) => k + 1)} />
        <ResetIndexButton onReset={() => setRefreshKey((k) => k + 1)} />
      </div>

      <div>
        <h3 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide mb-3">
          Current index
        </h3>
        <IndexStatusCard refreshKey={refreshKey} />
      </div>
    </div>
  )
}
