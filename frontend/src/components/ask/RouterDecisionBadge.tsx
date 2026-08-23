import { Info } from "lucide-react"
import * as Tooltip from "@radix-ui/react-tooltip"
import { StrategyBadge } from "@/components/shared/StrategyBadge"

export function RouterDecisionBadge({ strategy }: { strategy: string }) {
  return (
    <div className="inline-flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)]">
      <span>Routed to</span>
      <StrategyBadge strategy={strategy} size="sm" />
      <Tooltip.Provider delayDuration={150}>
        <Tooltip.Root>
          <Tooltip.Trigger asChild>
            <button className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]">
              <Info className="w-3.5 h-3.5" />
            </button>
          </Tooltip.Trigger>
          <Tooltip.Portal>
            <Tooltip.Content
              side="top"
              className="glass rounded-lg px-3 py-2 text-xs max-w-64 text-[var(--color-text-secondary)] z-50"
              sideOffset={6}
            >
              This route was chosen by the LLM-based classifier, or (when the embedding
              router is active) an 80/20 blend of question-embedding similarity and the
              bandit's learned average reward per strategy.
              <Tooltip.Arrow className="fill-[var(--color-bg-secondary)]" />
            </Tooltip.Content>
          </Tooltip.Portal>
        </Tooltip.Root>
      </Tooltip.Provider>
    </div>
  )
}
