// Chat history for the Ask page, lifted out of the page component and into
// a shared store (localStorage-backed) so it survives navigating to another
// tab and back — AskPage unmounts on route change, so plain useState inside
// it was being wiped every time.
import { useEffect, useState } from "react"
import type { QueryResult, StrategyKey } from "./types"

const STORAGE_KEY = "rag-arena-ask-state"

interface AskState {
  strategy: StrategyKey
  history: QueryResult[]
  activeIndex: number | null
}

const DEFAULT_STATE: AskState = {
  strategy: "auto",
  history: [],
  activeIndex: null,
}

function loadInitial(): AskState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return DEFAULT_STATE

    const parsed = JSON.parse(raw)
    return {
      strategy: parsed.strategy ?? DEFAULT_STATE.strategy,
      history: Array.isArray(parsed.history) ? parsed.history : [],
      activeIndex: typeof parsed.activeIndex === "number" ? parsed.activeIndex : null,
    }
  } catch {
    // Corrupt or unavailable storage (private browsing, etc.) — fall back
    // to a fresh in-memory state rather than crashing the page.
    return DEFAULT_STATE
  }
}

let state: AskState = loadInitial()
const listeners = new Set<(s: AskState) => void>()

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // Storage unavailable — the in-memory store still works for this tab.
  }
}

function setState(partial: Partial<AskState>) {
  state = { ...state, ...partial }
  persist()
  listeners.forEach((listener) => listener(state))
}

export function useAskStore() {
  const [local, setLocal] = useState(state)

  useEffect(() => {
    listeners.add(setLocal)
    return () => {
      listeners.delete(setLocal)
    }
  }, [])

  return {
    strategy: local.strategy,
    history: local.history,
    activeIndex: local.activeIndex,
    setStrategy: (strategy: StrategyKey) => setState({ strategy }),
    addResult: (result: QueryResult) => {
      setState({ history: [result, ...state.history], activeIndex: 0 })
    },
    setActiveIndex: (activeIndex: number | null) => setState({ activeIndex }),
  }
}
