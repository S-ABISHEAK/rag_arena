import { ModelConfigCard } from "@/components/settings/ModelConfigCard"
import { ConnectionHealthPanel } from "@/components/dashboard/ConnectionHealthPanel"

export function SettingsPage() {
  return (
    <div className="max-w-2xl mx-auto px-6 py-10 space-y-6">
      <ModelConfigCard />
      <ConnectionHealthPanel />
    </div>
  )
}
