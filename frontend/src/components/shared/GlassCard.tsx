import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface GlassCardProps {
  children: ReactNode
  className?: string
  accentColor?: string
  dense?: boolean
  hover?: boolean
}

export function GlassCard({ children, className, accentColor, dense, hover = true }: GlassCardProps) {
  return (
    <div
      className={cn(
        "glass rounded-2xl relative overflow-hidden",
        dense ? "p-4" : "p-6",
        hover && "glass-hover transition-shadow",
        className
      )}
      style={
        accentColor
          ? ({
              boxShadow: `inset 0 0 0 1px transparent`,
            } as React.CSSProperties)
          : undefined
      }
      onMouseEnter={(e) => {
        if (!accentColor) return
        e.currentTarget.style.boxShadow = `0 0 0 1px ${accentColor}33, 0 0 24px -4px ${accentColor}55`
      }}
      onMouseLeave={(e) => {
        if (!accentColor) return
        e.currentTarget.style.boxShadow = ""
      }}
    >
      {accentColor && (
        <span
          className="absolute left-0 top-0 bottom-0 w-[3px]"
          style={{ background: accentColor }}
        />
      )}
      {children}
    </div>
  )
}
