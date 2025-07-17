"use client"

import { AlertCircle, X } from "lucide-react"
import { GlassCard } from "@/components/glass-card"

interface ErrorDisplayProps {
  error: string | null
  onClear: () => void
}

export function ErrorDisplay({ error, onClear }: ErrorDisplayProps) {
  if (!error) return null

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <GlassCard opacity="medium" blur="lg" className="p-4 border-red-500/30">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-red-300 mb-1">Error</h3>
            <p className="text-sm text-red-200">{error}</p>
          </div>
          <button
            onClick={onClear}
            className="text-red-400 hover:text-red-300 flex-shrink-0"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </GlassCard>
    </div>
  )
} 