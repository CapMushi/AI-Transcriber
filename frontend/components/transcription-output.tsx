import { GlassCard } from "@/components/glass-card"
import { cn } from "@/lib/utils"
import { Languages, Target, Clock, Zap } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"
import { TranscriptionResponse } from "@/lib/api"

interface TranscriptionOutputProps {
  transcription?: TranscriptionResponse | null
}

export function TranscriptionOutput({ transcription }: TranscriptionOutputProps) {
  const { isTranscribing, transcriptionProgress } = useWhisperContext()

  if (isTranscribing) {
    return (
      <GlassCard opacity="medium" blur="lg" className="relative p-4 w-full h-full flex flex-col border-dark-secondary/30">
        <h2 className="text-lg font-semibold text-light-gray mb-4 flex items-center gap-2">
          <div className="p-1 rounded-full bg-accent-orange/20 border border-accent-orange/30">
            <Zap className="h-4 w-4 text-accent-orange" />
          </div>
          Transcribing...
        </h2>
        
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="text-center">
            <div className="mb-4">
              <div className="w-16 h-16 border-4 border-accent-orange/30 border-t-accent-orange rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-light-gray text-sm">Processing audio with Whisper AI...</p>
            </div>
            
            <div className="w-full max-w-xs">
              <div className="flex items-center justify-between text-sm text-light-gray mb-2">
                <span>Progress</span>
                <span>{transcriptionProgress}%</span>
              </div>
              <div className="w-full bg-dark-secondary/30 rounded-full h-2">
                <div
                  className="bg-accent-orange h-2 rounded-full transition-all duration-300"
                  style={{ width: `${transcriptionProgress}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </GlassCard>
    )
  }

  if (!transcription) {
    return (
      <GlassCard opacity="medium" blur="lg" className="relative p-4 w-full h-full flex flex-col border-dark-secondary/30">
        <h2 className="text-lg font-semibold text-light-gray mb-4 flex items-center gap-2">
          <div className="p-1 rounded-full bg-accent-orange/20 border border-accent-orange/30">
            <Languages className="h-4 w-4 text-accent-orange" />
          </div>
          Transcription
        </h2>
        
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="text-center text-light-gray/60">
            <Languages className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">Upload a file and click transcribe to see results here</p>
          </div>
        </div>
      </GlassCard>
    )
  }

  return (
    <GlassCard opacity="medium" blur="lg" className="relative p-4 w-full h-full flex flex-col border-dark-secondary/30">
      <div className="absolute top-4 right-4 z-10">
        <GlassCard opacity="low" blur="sm" className="p-2 text-xs text-light-gray border-dark-secondary/20">
          <div className="flex items-center gap-1 mb-1">
            <Languages className="h-3 w-3 text-accent-orange" />
            <span>Language: {transcription.language}</span>
          </div>
          <div className="flex items-center gap-1 mb-1">
            <Target className="h-3 w-3 text-accent-orange" />
            <span>Confidence: {transcription.confidence.toFixed(1)}%</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3 text-accent-orange" />
            <span>Time: {transcription.processing_time.toFixed(1)}s</span>
          </div>
        </GlassCard>
      </div>

      <h2 className="text-lg font-semibold text-light-gray mb-4 flex items-center gap-2">
        <div className="p-1 rounded-full bg-accent-orange/20 border border-accent-orange/30">
          <Languages className="h-4 w-4 text-accent-orange" />
        </div>
        Transcription
        {transcription.model_used && (
          <span className="text-xs text-accent-orange/70 ml-2">
            (Model: {transcription.model_used})
          </span>
        )}
      </h2>

      {/* Internal scrollable area with custom scrollbar - flex-1 to take remaining space */}
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar min-h-0">
        <p className="text-light-gray text-sm leading-relaxed">
          {transcription.segments.map((segment, index) => (
            <span
              key={index}
              className={cn(
                "inline-block p-1 m-0.5 rounded-md transition-all duration-200",
                "bg-dark-secondary/[0.3] hover:bg-accent-orange/[0.15] hover:scale-[1.02] cursor-pointer border border-transparent hover:border-accent-orange/30",
              )}
              title={`Start: ${segment.start.toFixed(1)}s, End: ${segment.end.toFixed(1)}s`}
            >
              {segment.text}{" "}
            </span>
          ))}
        </p>
      </div>
    </GlassCard>
  )
}
