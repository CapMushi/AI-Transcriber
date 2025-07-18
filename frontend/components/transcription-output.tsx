import { useState, useEffect } from "react"
import { GlassCard } from "@/components/glass-card"
import { cn } from "@/lib/utils"
import { Languages, Target, Clock, Zap, Download, Info } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"
import { TranscriptionResponse } from "@/lib/api"
import React from "react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface TranscriptionOutputProps {
  transcription?: TranscriptionResponse | null
}

export function TranscriptionOutput({ transcription }: TranscriptionOutputProps) {
  const { 
    isTranscribing, 
    transcriptionProgress, 
    uploadedFile, 
    downloadTranscription,
    availableModels,
    loadAvailableModels,
    transcribeFile
  } = useWhisperContext()
  const [showDownloadPopup, setShowDownloadPopup] = useState(false)
  const [showInfoPopup, setShowInfoPopup] = useState(false)
  const [selectedModel, setSelectedModel] = useState('base')

  // Load available models on component mount
  React.useEffect(() => {
    loadAvailableModels()
  }, [loadAvailableModels])

  // Handle clicking outside popups
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element
      if (!target.closest('[data-popup]')) {
        setShowDownloadPopup(false)
        setShowInfoPopup(false)
      }
    }

    if (showDownloadPopup || showInfoPopup) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showDownloadPopup, showInfoPopup])

  // Handle model change and trigger transcription if file is ready
  const handleModelChange = async (newModel: string) => {
    setSelectedModel(newModel)
    
    // If we have a file and no transcription, trigger transcription with new model
    if (uploadedFile && !transcription && !isTranscribing) {
      console.log('🔄 Model changed to:', newModel, '- triggering transcription')
      await transcribeFile(newModel, 'auto')
    }
  }

  // Download handlers
  const handleDownloadTXT = async () => {
    if (!transcription) return
    await downloadTranscription('txt', 'transcription')
    setShowDownloadPopup(false)
  }

  const handleDownloadJSON = async () => {
    if (!transcription) return
    await downloadTranscription('json', 'transcription')
    setShowDownloadPopup(false)
  }

  const handleDownloadSRT = async () => {
    if (!transcription) return
    await downloadTranscription('srt', 'transcription')
    setShowDownloadPopup(false)
  }

  // Check if download button should be enabled
  const isDownloadEnabled = uploadedFile && transcription && !isTranscribing

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
      {/* Top-right corner buttons */}
      <div className="absolute top-4 right-4 z-10 flex gap-2 items-center">
        {/* Model Selection Dropdown */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-light-gray/70 whitespace-nowrap">Model:</label>
          <select
            value={selectedModel}
            onChange={(e) => handleModelChange(e.target.value)}
            disabled={isTranscribing}
            className="bg-dark-secondary/95 backdrop-blur-md border border-dark-secondary/30 rounded-lg px-3 py-2 text-xs text-light-gray focus:border-accent-orange/50 focus:outline-none min-w-[90px] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg appearance-none"
            style={{
              borderRadius: '8px',
              backgroundImage: `url("data:image/svg+xml,%3csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m1 1 4 4 4-4' stroke='%23ffffff' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3e%3c/svg%3e")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 8px center',
              backgroundSize: '10px 6px',
              paddingRight: '24px'
            }}
          >
            {availableModels?.available_models.map((model) => (
              <option key={model} value={model} className="bg-dark-secondary/95 text-light-gray rounded">
                {model.charAt(0).toUpperCase() + model.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Download Button */}
        <div className="relative" data-popup>
          <button
            onClick={() => {
              if (!isDownloadEnabled) {
                // Show error popup
                return
              }
              setShowDownloadPopup(!showDownloadPopup)
            }}
            disabled={!isDownloadEnabled}
            className={cn(
              "p-2 rounded-md transition-all duration-200 flex items-center gap-1 text-xs",
              isDownloadEnabled
                ? "bg-accent-orange/20 border border-accent-orange/30 text-accent-orange hover:bg-accent-orange/30 hover:scale-105"
                : "bg-dark-secondary/20 border border-dark-secondary/30 text-light-gray/50 cursor-not-allowed"
            )}
            title={!uploadedFile ? "Please upload a file first" : !transcription ? "Please transcribe the file first" : "Download transcription"}
          >
            <Download className="h-3 w-3" />
            Download
          </button>

          {/* Download Popup */}
          {showDownloadPopup && isDownloadEnabled && (
            <div data-popup className="absolute top-full right-0 mt-2 bg-dark-secondary/95 backdrop-blur-md border border-dark-secondary/30 rounded-lg p-3 shadow-lg z-20 min-w-[140px]">
              <div className="space-y-2">
                <button
                  onClick={handleDownloadTXT}
                  className="w-full text-left px-3 py-2 text-xs text-light-gray hover:bg-accent-orange/20 hover:text-accent-orange rounded-md transition-all duration-200 flex items-center gap-2 hover:scale-[1.02]"
                >
                  <Download className="h-3 w-3" />
                  Download TXT
                </button>
                <button
                  onClick={handleDownloadJSON}
                  className="w-full text-left px-3 py-2 text-xs text-light-gray hover:bg-accent-orange/20 hover:text-accent-orange rounded-md transition-all duration-200 flex items-center gap-2 hover:scale-[1.02]"
                >
                  <Download className="h-3 w-3" />
                  Download JSON
                </button>
                <button
                  onClick={handleDownloadSRT}
                  className="w-full text-left px-3 py-2 text-xs text-light-gray hover:bg-accent-orange/20 hover:text-accent-orange rounded-md transition-all duration-200 flex items-center gap-2 hover:scale-[1.02]"
                >
                  <Download className="h-3 w-3" />
                  Download SRT
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Info Button */}
        <div className="relative" data-popup>
          <button
            onClick={() => setShowInfoPopup(!showInfoPopup)}
            className="p-2 rounded-md transition-all duration-200 bg-accent-orange/20 border border-accent-orange/30 text-accent-orange hover:bg-accent-orange/30 flex items-center gap-1 text-xs"
            title="Transcription information"
          >
            <Info className="h-3 w-3" />
            Info
          </button>

          {/* Info Popup */}
          {showInfoPopup && (
            <div data-popup className="absolute top-full right-0 mt-2 bg-dark-secondary/95 backdrop-blur-md border border-dark-secondary/30 rounded-lg p-3 shadow-lg z-20 min-w-[140px]">
              <div className="space-y-2 text-xs text-light-gray">
                <div className="flex items-center gap-2">
            <Languages className="h-3 w-3 text-accent-orange" />
            <span>Language: {transcription.language}</span>
          </div>
                <div className="flex items-center gap-2">
            <Target className="h-3 w-3 text-accent-orange" />
            <span>Confidence: {transcription.confidence.toFixed(1)}%</span>
          </div>
                <div className="flex items-center gap-2">
            <Clock className="h-3 w-3 text-accent-orange" />
            <span>Time: {transcription.processing_time.toFixed(1)}s</span>
          </div>
                {transcription.model_used && (
                  <div className="flex items-center gap-2">
                    <Zap className="h-3 w-3 text-accent-orange" />
                    <span>Model: {transcription.model_used}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
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
        <TooltipProvider>
          <div className="text-light-gray text-sm leading-relaxed">
            {transcription.segments.map((segment, index) => (
              <Tooltip key={index}>
                <TooltipTrigger asChild>
                  <span
                    className={cn(
                      "inline-block p-1 m-0.5 rounded-md transition-all duration-200",
                      "bg-dark-secondary/[0.3] hover:bg-accent-orange/[0.15] hover:scale-[1.02] cursor-pointer border border-transparent hover:border-accent-orange/30",
                    )}
                  >
                    {segment.text}{" "}
                  </span>
                </TooltipTrigger>
                <TooltipContent 
                  className="bg-dark-secondary/95 backdrop-blur-md border border-dark-secondary/30 text-light-gray shadow-lg"
                  side="top"
                  sideOffset={8}
                >
                  <div className="flex items-center gap-2 text-xs">
                    <Clock className="h-3 w-3 text-accent-orange" />
                    <span>
                      {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                    </span>
                  </div>
                </TooltipContent>
              </Tooltip>
            ))}
          </div>
        </TooltipProvider>
      </div>
    </GlassCard>
  )
}
