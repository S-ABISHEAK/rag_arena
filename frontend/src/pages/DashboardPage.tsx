import { IndexStatusCard } from "@/components/ingest/IndexStatusCard"
import { ConnectionHealthPanel } from "@/components/dashboard/ConnectionHealthPanel"
import { CacheStatusIndicator } from "@/components/dashboard/CacheStatusIndicator"
import { StrategyScoreBoard } from "@/components/arena/StrategyScoreBoard"

export function DashboardPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      <IndexStatusCard />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <StrategyScoreBoard compact />
        </div>
        <div className="space-y-4">
          <ConnectionHealthPanel />
          <CacheStatusIndicator />
        </div>
      </div>
    </div>
  )
}
