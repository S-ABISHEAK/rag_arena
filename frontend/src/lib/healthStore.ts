// Shared connection-health polling. TopBar, ConnectionHealthPanel, and
// CacheStatusIndicator all need this data, but each doing its own
// useEffect+fetch meant every page load fired 2-3 separate /health
// requests (which itself calls Groq's API) instead of one shared poll.
import { useEffect, useState } from "react"
import { getConnectionHealth } from "./api"
import type { ConnectionHealth } from "./types"

const POLL_INTERVAL_MS = 30000

let cached: ConnectionHealth[] = []
const listeners = new Set<(data: ConnectionHealth[]) => void>()
let pollStarted = false

function notify(data: ConnectionHealth[]) {
  cached = data
  listeners.forEach((listener) => listener(data))
}

async function poll() {
  try {
    const data = await getConnectionHealth()
    notify(data)
  } catch {
    // Keep the last known state rather than clearing it on a transient
    // poll failure — a blip shouldn't flash every dot to "disconnected".
  }
}

function ensurePolling() {
  if (pollStarted) return
  pollStarted = true
  poll()
  setInterval(poll, POLL_INTERVAL_MS)
}

export function useConnectionHealth(): ConnectionHealth[] {
  const [health, setHealth] = useState<ConnectionHealth[]>(cached)

  useEffect(() => {
    ensurePolling()
    listeners.add(setHealth)
    if (cached.length) setHealth(cached)
    return () => {
      listeners.delete(setHealth)
    }
  }, [])

  return health
}
