import { clsx } from "clsx"
import type { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatMs(ms?: number) {
  if (ms === undefined || ms === null) return "—"
  return `${Math.round(ms)}ms`
}

export function formatPct(n?: number) {
  if (n === undefined || n === null) return "—"
  return `${Math.round(n * 100)}%`
}
