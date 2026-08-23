import { useEffect, useState } from "react"
import type { LucideIcon } from "lucide-react"
import { GlassCard } from "./GlassCard"

interface StatTileProps {
  label: string
  value: number
  icon?: LucideIcon
  suffix?: string
  accentColor?: string
}

export function StatTile({ label, value, icon: Icon, suffix, accentColor }: StatTileProps) {
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    let raf: number
    const start = performance.now()
    const duration = 700
    const from = 0

    function tick(now: number) {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setDisplay(Math.round(from + (value - from) * eased))
      if (t < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [value])

  return (
    <GlassCard dense accentColor={accentColor}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-[var(--color-text-secondary)] uppercase tracking-wide">{label}</span>
        {Icon && <Icon className="w-4 h-4 text-[var(--color-text-muted)]" />}
      </div>
      <div className="font-mono-nums text-2xl font-semibold text-[var(--color-text-primary)]">
        {display.toLocaleString()}
        {suffix && <span className="text-sm text-[var(--color-text-secondary)] ml-1">{suffix}</span>}
      </div>
    </GlassCard>
  )
}
