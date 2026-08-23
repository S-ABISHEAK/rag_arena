import { useMemo } from "react"
import { STRATEGIES } from "@/lib/strategy"

interface GraphContextPanelProps {
  context: string
}

function parseNodes(context: string): { nodes: string[]; edges: [string, string][] } {
  const lines = context.split("\n").filter(Boolean)
  const nodes = new Set<string>()
  const edges: [string, string][] = []

  for (const line of lines) {
    if (line.startsWith("Entity:")) {
      nodes.add(line.replace("Entity:", "").trim())
      continue
    }
    const parts = line.split(" ")
    if (parts.length >= 3) {
      const source = parts[0]
      const target = parts[parts.length - 1]
      nodes.add(source)
      nodes.add(target)
      edges.push([source, target])
    }
  }
  return { nodes: Array.from(nodes).slice(0, 8), edges: edges.slice(0, 8) }
}

export function GraphContextPanel({ context }: GraphContextPanelProps) {
  const { nodes, edges } = useMemo(() => parseNodes(context), [context])
  const color = STRATEGIES.graph.color

  const positions = useMemo(() => {
    const cx = 150
    const cy = 90
    const r = 65
    return nodes.map((n, i) => {
      const angle = (i / Math.max(nodes.length, 1)) * Math.PI * 2
      return { node: n, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }
    })
  }, [nodes])

  return (
    <div className="mt-4 space-y-3">
      <blockquote className="text-xs text-[var(--color-text-secondary)] italic border-l-2 pl-3 whitespace-pre-line" style={{ borderColor: `${color}55` }}>
        {context}
      </blockquote>

      {nodes.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-black/20 p-3 overflow-x-auto">
          <svg viewBox="0 0 300 180" className="w-full h-44">
            {edges.map(([a, b], i) => {
              const from = positions.find((p) => p.node === a)
              const to = positions.find((p) => p.node === b)
              if (!from || !to) return null
              return (
                <line
                  key={i}
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke={color}
                  strokeOpacity={0.35}
                  strokeWidth={1.5}
                />
              )
            })}
            {positions.map((p, i) => (
              <g key={i}>
                <circle cx={p.x} cy={p.y} r={4} fill={color} className="animate-pulse-glow" style={{ color }} />
                <text
                  x={p.x}
                  y={p.y - 8}
                  textAnchor="middle"
                  fontSize={7}
                  fontFamily="var(--font-mono)"
                  fill="var(--color-text-secondary)"
                >
                  {p.node.length > 14 ? p.node.slice(0, 14) + "…" : p.node}
                </text>
              </g>
            ))}
          </svg>
        </div>
      )}
    </div>
  )
}
