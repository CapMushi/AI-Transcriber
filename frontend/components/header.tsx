import { GlassCard } from "@/components/glass-card"
import { Settings, Mic } from "lucide-react"

export function Header() {
  return (
    <div className="flex-shrink-0 bg-dark-primary/95 backdrop-blur-sm border-b border-light-gray/10 relative z-20">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <GlassCard
          opacity="medium"
          blur="md"
          className="flex items-center justify-between p-3 border-dark-secondary/30"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-full bg-accent-orange/20 border border-accent-orange/30">
              <Mic className="h-5 w-5 text-accent-orange" />
            </div>
            <h1 className="text-xl font-bold text-light-gray drop-shadow-md">Whisper AI Transcriber</h1>
          </div>
          <button
            className="p-2 rounded-full transition-colors duration-200 hover:bg-light-gray/[0.1] group border border-transparent hover:border-accent-orange/30"
            aria-label="Settings"
          >
            <Settings className="h-5 w-5 text-light-gray group-hover:rotate-90 group-hover:text-accent-orange transition-all duration-300" />
          </button>
        </GlassCard>
      </div>
    </div>
  )
}
