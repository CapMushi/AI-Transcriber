import { GlassCard } from "@/components/glass-card"
import { Loader2, Mic } from "lucide-react"

interface LoadingIndicatorProps {
  isLoading: boolean
}

export function LoadingIndicator({ isLoading }: LoadingIndicatorProps) {
  if (!isLoading) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-dark-primary/[0.8] backdrop-blur-sm">
      <GlassCard opacity="medium" blur="lg" className="p-10 flex flex-col items-center gap-6 border-dark-secondary/30">
        <div className="relative">
          <Loader2 className="h-16 w-16 animate-spin text-accent-orange" />
          <Mic className="h-8 w-8 text-light-gray absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
        </div>
        <p className="text-light-gray text-xl font-semibold">Processing your audio...</p>
        <p className="text-light-gray/80 text-sm">This may take a moment.</p>
      </GlassCard>
    </div>
  )
}
