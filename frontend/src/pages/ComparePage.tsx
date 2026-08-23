import { CompareStrategiesPanel } from "@/components/compare/CompareStrategiesPanel"
import { BenchmarkRunner } from "@/components/compare/BenchmarkRunner"

export function ComparePage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      <CompareStrategiesPanel />
      <BenchmarkRunner />
    </div>
  )
}
