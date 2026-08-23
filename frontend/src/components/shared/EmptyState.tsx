import type { LucideIcon } from "lucide-react"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
}

export function EmptyState({ icon: Icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-14 px-6">
      <div className="w-12 h-12 rounded-xl glass flex items-center justify-center mb-4">
        <Icon className="w-5 h-5 text-[var(--color-text-muted)]" />
      </div>
      <p className="text-sm font-medium text-[var(--color-text-secondary)]">{title}</p>
      {description && (
        <p className="text-xs text-[var(--color-text-muted)] mt-1.5 max-w-xs">{description}</p>
      )}
    </div>
  )
}
