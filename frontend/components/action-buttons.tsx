"use client"

import { useState, useEffect, useCallback } from "react"
import { GlassButton } from "@/components/glass-button"
import { Zap, Download, Settings } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"

export function ActionButtons() {
  const {
    uploadedFile,
    transcription,
    isTranscribing,
    transcribeFile,
    downloadTranscription,
    availableModels,
    loadAvailableModels
  } = useWhisperContext()

  // Debug logging
  console.log('🔍 ActionButtons - Current state:', {
    uploadedFile: uploadedFile ? 'File uploaded' : 'No file',
    transcription: transcription ? 'Has transcription' : 'No transcription',
    isTranscribing,
    availableModels: availableModels ? 'Models loaded' : 'No models'
  })
  
  // Force re-render when uploadedFile changes
  useEffect(() => {
    console.log('🔄 ActionButtons: uploadedFile changed to:', uploadedFile)
  }, [uploadedFile])

  // Debug button state
  console.log('🔍 Button disabled check:', { isTranscribing, uploadedFile: !!uploadedFile, disabled: isTranscribing })

  const [showSettings, setShowSettings] = useState(false)
  const [selectedModel, setSelectedModel] = useState('base')

  const handleTranscribe = useCallback(async () => {
    console.log('🎯 Transcribe button clicked')
    console.log('📁 Uploaded file state:', uploadedFile)
    console.log('⚙️ Selected model:', selectedModel)
    
    if (!uploadedFile) {
      console.error('❌ No file uploaded, cannot transcribe')
      return
    }
    
    console.log('🔄 Starting transcription...')
    const result = await transcribeFile(selectedModel, 'auto')
    console.log('📝 Transcription result:', result)
  }, [uploadedFile, transcribeFile, selectedModel])

  const handleDownload = async () => {
    if (!transcription) return
    await downloadTranscription('txt', 'transcription')
  }

  const handleDownloadJSON = async () => {
    if (!transcription) return
    await downloadTranscription('json', 'transcription')
  }

  const handleDownloadSRT = async () => {
    if (!transcription) return
    await downloadTranscription('srt', 'transcription')
  }

  // Load available models on component mount
  useEffect(() => {
    loadAvailableModels()
  }, [loadAvailableModels])

  return (
    <div className="flex flex-col gap-4">
      {/* Main Action Buttons */}
      <div className="flex gap-4 justify-center">
        <GlassButton
          onClick={handleTranscribe}
          disabled={isTranscribing}
          className="px-6 py-2 text-sm font-semibold bg-accent-orange/70 hover:bg-accent-orange/90 border-accent-orange/80 flex items-center gap-2 text-light-gray disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Zap className="h-4 w-4" />
          {isTranscribing ? "Transcribing..." : "Transcribe"}
          {/* Show button state */}
          <span className="text-xs opacity-50">
            ({uploadedFile ? 'File Ready' : 'No File'})
          </span>
        </GlassButton>
        
        <GlassButton
          onClick={() => setShowSettings(!showSettings)}
          disabled={isTranscribing}
          className="px-6 py-2 text-sm font-semibold flex items-center gap-2 border-dark-secondary/30 hover:border-accent-orange/30"
        >
          <Settings className="h-4 w-4" />
          Settings
        </GlassButton>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-dark-secondary/20 border border-dark-secondary/30 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-light-gray mb-3">Transcription Settings</h3>
          
          <div className="space-y-3">
            <div>
              <label className="text-xs text-light-gray/70 block mb-1">Whisper Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full bg-dark-secondary/30 border border-dark-secondary/50 rounded px-3 py-2 text-sm text-light-gray focus:border-accent-orange/50 focus:outline-none"
              >
                {availableModels?.available_models.map((model) => (
                  <option key={model} value={model}>
                    {model.charAt(0).toUpperCase() + model.slice(1)} Model
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Download Buttons */}
      {transcription && (
        <div className="flex gap-2 justify-center flex-wrap">
          <GlassButton
            onClick={handleDownload}
            disabled={isTranscribing}
            className="px-4 py-2 text-xs font-semibold flex items-center gap-2 border-dark-secondary/30 hover:border-accent-orange/30"
          >
            <Download className="h-3 w-3" />
            Download TXT
          </GlassButton>
          
          <GlassButton
            onClick={handleDownloadJSON}
            disabled={isTranscribing}
            className="px-4 py-2 text-xs font-semibold flex items-center gap-2 border-dark-secondary/30 hover:border-accent-orange/30"
          >
            <Download className="h-3 w-3" />
            Download JSON
          </GlassButton>
          
          <GlassButton
            onClick={handleDownloadSRT}
            disabled={isTranscribing}
            className="px-4 py-2 text-xs font-semibold flex items-center gap-2 border-dark-secondary/30 hover:border-accent-orange/30"
          >
            <Download className="h-3 w-3" />
            Download SRT
          </GlassButton>
        </div>
      )}
    </div>
  )
}
