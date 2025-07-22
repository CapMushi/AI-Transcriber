import { useState, useEffect } from "react"
import { GlassCard } from "@/components/glass-card"
import { cn } from "@/lib/utils"
import { Languages, Target, Clock, Zap, Download, Info, Search } from "lucide-react"
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
    isStoring,
    storageProgress,
    uploadedFile, 
    primaryFile,
    secondaryFile,
    comparisonResult,
    isComparing,
    downloadTranscription,
    availableModels,
    loadAvailableModels,
    transcribeFile
  } = useWhisperContext()

  // Debug logging
  console.log('📝 TranscriptionOutput - transcription:', transcription)
  console.log('📝 TranscriptionOutput - comparisonResult:', comparisonResult)
  const [showDownloadPopup, setShowDownloadPopup] = useState(false)
  const [showInfoPopup, setShowInfoPopup] = useState(false)
  const [selectedModel, setSelectedModel] = useState('base')

  // Function to check if a segment should be highlighted based on comparison timestamps
  const shouldHighlightSegment = (segmentStart: number, segmentEnd: number): boolean => {
    if (!comparisonResult?.timestamps || !comparisonResult.found) {
      return false
    }

    return comparisonResult.timestamps.some((timestamp: any) => {
      const matchStart = timestamp.start_time
      const matchEnd = timestamp.end_time
      
      // Calculate actual overlap duration
      const overlapStart = Math.max(segmentStart, matchStart)
      const overlapEnd = Math.min(segmentEnd, matchEnd)
      const overlapDuration = Math.max(0, overlapEnd - overlapStart)
      
      // Only highlight if there's meaningful overlap (more than 0.1 seconds)
      return overlapDuration > 0.1
    })
  }

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
        
        {/* Model Selection Dropdown - Always visible */}
        <div className="absolute top-4 right-4 z-10 flex gap-2 items-center">
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
              {availableModels?.available_models?.map((model) => (
                <option key={model} value={model} className="bg-dark-secondary/95 text-light-gray rounded">
                  {model.charAt(0).toUpperCase() + model.slice(1)}
                </option>
              )) || (
                // Fallback options when models are not loaded yet
                <>
                  <option value="tiny" className="bg-dark-secondary/95 text-light-gray rounded">Tiny</option>
                  <option value="base" className="bg-dark-secondary/95 text-light-gray rounded">Base</option>
                  <option value="small" className="bg-dark-secondary/95 text-light-gray rounded">Small</option>
                  <option value="medium" className="bg-dark-secondary/95 text-light-gray rounded">Medium</option>
                  <option value="large" className="bg-dark-secondary/95 text-light-gray rounded">Large</option>
                </>
              )}
            </select>
          </div>
        </div>
        
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
      {/* Transcription Header */}
      <h2 className="text-lg font-semibold text-light-gray mb-4 flex items-center gap-2">
        <div className="p-1 rounded-full bg-accent-orange/20 border border-accent-orange/30">
          <Languages className="h-4 w-4 text-accent-orange" />
        </div>
        Transcription
      </h2>
      
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
            {availableModels?.available_models?.map((model) => (
              <option key={model} value={model} className="bg-dark-secondary/95 text-light-gray rounded">
                {model.charAt(0).toUpperCase() + model.slice(1)}
              </option>
            )) || (
              // Fallback options when models are not loaded yet
              <>
                <option value="tiny" className="bg-dark-secondary/95 text-light-gray rounded">Tiny</option>
                <option value="base" className="bg-dark-secondary/95 text-light-gray rounded">Base</option>
                <option value="small" className="bg-dark-secondary/95 text-light-gray rounded">Small</option>
                <option value="medium" className="bg-dark-secondary/95 text-light-gray rounded">Medium</option>
                <option value="large" className="bg-dark-secondary/95 text-light-gray rounded">Large</option>
              </>
            )}
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
            className="p-2 rounded-md transition-all duration-200 flex items-center gap-1 text-xs bg-dark-secondary/20 border border-dark-secondary/30 text-light-gray hover:bg-accent-orange/20 hover:border-accent-orange/30 hover:text-accent-orange hover:scale-105"
            title="Transcription Info"
          >
            <Info className="h-3 w-3" />
            Info
          </button>

          {/* Info Popup */}
          {showInfoPopup && (
            <div data-popup className="absolute top-full right-0 mt-2 bg-dark-secondary/95 backdrop-blur-md border border-dark-secondary/30 rounded-lg p-3 shadow-lg z-20 min-w-[200px]">
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <Languages className="h-3 w-3 text-accent-orange" />
                  <span className="text-light-gray">Language: <span className="text-accent-orange">{transcription?.language || 'Auto'}</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="h-3 w-3 text-accent-orange" />
                  <span className="text-light-gray">Confidence: <span className="text-accent-orange">{(transcription?.confidence || 0) * 100}%</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-3 w-3 text-accent-orange" />
                  <span className="text-light-gray">Processing: <span className="text-accent-orange">{transcription?.processing_time || 0}s</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="h-3 w-3 text-accent-orange" />
                  <span className="text-light-gray">Model: <span className="text-accent-orange">{transcription?.model_used || 'Unknown'}</span></span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Two-column layout: Transcription and Timestamp Sidebar */}
      <div className="flex gap-4 h-full mt-4">
        {/* Left Column: Transcription Content */}
        <div className="flex-1 overflow-y-auto">
          <TooltipProvider>
            <div className="text-light-gray text-sm leading-relaxed">
              {transcription.segments?.map((segment, index) => {
                const isHighlighted = shouldHighlightSegment(segment.start, segment.end)
                return (
                  <Tooltip key={index}>
                    <TooltipTrigger asChild>
                      <span
                        className={cn(
                          "inline-block p-1 m-0.5 rounded-md transition-all duration-200",
                          "cursor-pointer border border-transparent hover:border-accent-orange/30",
                          isHighlighted 
                            ? "bg-accent-orange/[0.3] border-accent-orange/50 hover:bg-accent-orange/[0.4] text-accent-orange font-medium" 
                            : "bg-dark-secondary/[0.3] hover:bg-accent-orange/[0.15]"
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
                        {isHighlighted && (
                          <span className="text-accent-orange ml-2">✓ Match</span>
                        )}
                      </div>
                    </TooltipContent>
                  </Tooltip>
                )
              }) || (
                transcription.text ? (
                  <div className="text-light-gray/80 leading-relaxed">
                    {transcription.text}
                    {comparisonResult?.found && comparisonResult?.timestamps && (
                      <div className="mt-2 p-2 bg-accent-orange/10 border border-accent-orange/20 rounded text-xs text-accent-orange">
                        ⚠️ Highlighting not available for plain text. Use segments for timestamp highlighting.
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-light-gray/60 text-center py-4">
                    <p>No transcription segments available</p>
                  </div>
                )
              )}
            </div>
          </TooltipProvider>
        </div>

        {/* Right Column: Timestamp Sidebar */}
        {comparisonResult && comparisonResult.found && comparisonResult.timestamps && comparisonResult.timestamps.length > 0 && (
          <div className="w-64 bg-dark-secondary/20 border border-dark-secondary/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
              <Search className="h-4 w-4 text-accent-orange" />
              <h3 className="text-sm font-semibold text-light-gray">Timestamps</h3>
            </div>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {comparisonResult.timestamps.map((timestamp: any, index: number) => (
                <div key={index} className="bg-dark-secondary/30 border border-dark-secondary/50 rounded p-3 hover:bg-dark-secondary/40 transition-all duration-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-accent-orange font-medium">Match {index + 1}</span>
                    <span className="text-xs text-light-gray/70">{(timestamp.end_time - timestamp.start_time).toFixed(1)}s</span>
                  </div>
                  <div className="text-xs text-light-gray">
                    <div className="flex items-center gap-1 mb-1">
                      <Clock className="h-3 w-3 text-accent-orange" />
                      <span className="text-accent-orange font-medium">
                        {timestamp.start_time.toFixed(1)}s - {timestamp.end_time.toFixed(1)}s
                      </span>
                    </div>
                    <div className="text-light-gray/80 text-xs leading-relaxed">
                      {transcription.segments?.find(seg => 
                        seg.start <= timestamp.start_time && seg.end >= timestamp.end_time
                      )?.text || "Content found in this time range"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 pt-3 border-t border-dark-secondary/30">
              <div className="text-xs text-light-gray/70">
                <div className="flex items-center justify-between mb-1">
                  <span>Confidence:</span>
                  <span className="text-accent-orange">{(comparisonResult.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Total Matches:</span>
                  <span className="text-accent-orange">{comparisonResult.timestamps.length}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Storage Progress Indicator */}
      {isStoring && (
        <div className="mt-4 p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1 rounded-full bg-green-500/20 border border-green-500/30">
              <Search className="h-4 w-4 text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-green-300">Storing Content...</h3>
          </div>
          <div className="text-light-gray text-sm">
            <p>Storing transcription chunks in Pinecone...</p>
            <div className="w-full bg-dark-secondary/30 rounded-full h-2 mt-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${storageProgress}%` }} 
              />
            </div>
            <div className="flex items-center justify-between text-xs text-light-gray mt-1">
              <span>Progress</span>
              <span>{storageProgress}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Results Summary (only when no sidebar) */}
      {comparisonResult && (!comparisonResult.found || !comparisonResult.timestamps || comparisonResult.timestamps.length === 0) && (
        <div className="mt-4 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <Search className="h-5 w-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-blue-300">Comparison Results</h3>
          </div>
          
          {comparisonResult.found ? (
            <div className="space-y-3">
              <div className="text-green-300 text-sm">
                ✅ Content found in primary file
              </div>
              <div className="text-light-gray text-sm">
                <p><span className="text-accent-orange">Confidence:</span> {(comparisonResult.confidence * 100).toFixed(1)}%</p>
                <p><span className="text-accent-orange">Matches found:</span> {comparisonResult.timestamps?.length || 0}</p>
              </div>
            </div>
          ) : (
            <div className="text-red-300 text-sm">
              ❌ Secondary content not found in primary file with 100% certainty
            </div>
          )}
        </div>
      )}

      {/* Comparison Loading */}
      {isComparing && (
        <div className="mt-4 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <Search className="h-5 w-5 text-blue-400 animate-pulse" />
            <h3 className="text-lg font-semibold text-blue-300">Comparing Content...</h3>
          </div>
          <div className="text-light-gray text-sm">
            <p>Analyzing secondary content against primary file...</p>
            <div className="w-full bg-dark-secondary/30 rounded-full h-2 mt-2">
              <div className="bg-blue-500 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
            </div>
          </div>
        </div>
      )}
    </GlassCard>
  )
}
