import { useState } from "react"
import { ChevronDown, FileText } from "lucide-react"
import * as Accordion from "@radix-ui/react-accordion"
import type { Source } from "@/lib/types"
import { cn } from "@/lib/utils"

export function SourceList({ sources }: { sources: Source[] }) {
  const [open, setOpen] = useState<string | undefined>(undefined)

  if (!sources.length) return null

  return (
    <Accordion.Root type="single" collapsible value={open} onValueChange={setOpen} className="mt-4 space-y-2">
      <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wide mb-2">
        Sources ({sources.length})
      </div>
      {sources.map((s, i) => (
        <Accordion.Item
          key={(s.chunk_id ?? "chunk") + i}
          value={(s.chunk_id ?? "chunk") + i}
          className="rounded-xl border border-white/10 overflow-hidden"
        >
          <Accordion.Header>
            <Accordion.Trigger className="w-full flex items-center justify-between gap-3 px-3 py-2.5 text-left hover:bg-white/5 transition-colors group">
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="w-3.5 h-3.5 text-[var(--color-text-muted)] shrink-0" />
                <span className="text-xs text-[var(--color-text-secondary)] truncate">{s.source}</span>
                <span className="font-mono-nums text-xs text-[var(--color-text-muted)] shrink-0">
                  p.{s.page}
                </span>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-[var(--color-text-muted)] shrink-0 transition-transform group-data-[state=open]:rotate-180" />
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-3 pb-3">
            <blockquote className={cn("text-xs text-[var(--color-text-secondary)] italic border-l-2 border-white/10 pl-3")}>
              {s.snippet ?? "No preview available."}
            </blockquote>
            <div className="font-mono text-[10px] text-[var(--color-text-muted)] mt-2">{s.chunk_id}</div>
          </Accordion.Content>
        </Accordion.Item>
      ))}
    </Accordion.Root>
  )
}
