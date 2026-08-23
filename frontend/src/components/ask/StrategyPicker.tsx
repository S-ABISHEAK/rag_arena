import { AUTO_META, STRATEGIES } from "@/lib/strategy"
import type { StrategyKey } from "@/lib/types"
import { cn } from "@/lib/utils"

const OPTIONS: StrategyKey[] = ["auto", "traditional", "hybrid", "pageindex", "graph"]

interface StrategyPickerProps {
  value: StrategyKey
  onChange: (value: StrategyKey) => void
}

export function StrategyPicker({ value, onChange }: StrategyPickerProps) {
  return (
    <div className="glass inline-flex items-center gap-1 rounded-full p-1 mx-auto">
      {OPTIONS.map((key) => {
        const meta = key === "auto" ? AUTO_META : STRATEGIES[key]
        const Icon = meta.icon
        const active = value === key

        return (
          <button
            key={key}
            onClick={() => onChange(key)}
            className={cn(
              "relative flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all",
              active ? "text-white" : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            )}
            style={
              active
                ? key === "auto"
                  ? undefined
                  : { background: `${meta.color}2a`, boxShadow: `0 0 0 1px ${meta.color}66` }
                : undefined
            }
          >
            {active && key === "auto" && (
              <span className="absolute inset-0 rounded-full gradient-auto -z-10" />
            )}
            <Icon className="w-3.5 h-3.5" style={!active ? undefined : key !== "auto" ? { color: meta.color } : undefined} />
            {meta.label}
          </button>
        )
      })}
    </div>
  )
}
