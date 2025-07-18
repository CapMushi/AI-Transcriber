"use client"

import { useState, useEffect, useCallback } from "react"
import { GlassButton } from "@/components/glass-button"
import { Zap } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"

export function ActionButtons() {
  const {
    uploadedFile,
    transcription,
    isTranscribing,
    transcribeFile
  } = useWhisperContext()

  // Debug loggingF
  console.log('🔍 ActionButtons - Current state:', {
    uploadedFile: uploadedFile ? 'File uploaded' : 'No file',
    transcription: transcription ? 'Has transcription' : 'No transcription',
    isTranscribing
  })
  
  // Force re-render when uploadedFile changes
  useEffect(() => {
    console.log('🔄 ActionButtons: uploadedFile changed to:', uploadedFile)
  }, [uploadedFile])

  // Debug button state
  console.log('🔍 Button disabled check:', { isTranscribing, uploadedFile: !!uploadedFile, disabled: isTranscribing })

  const handleTranscribe = useCallback(async () => {
    console.log('🎯 Transcribe button clicked')
    console.log('📁 Uploaded file state:', uploadedFile)
    
    if (!uploadedFile) {
      console.error('❌ No file uploaded, cannot transcribe')
      return
    }
    
    console.log('🔄 Starting transcription with default model (base)...')
    // Use default model 'base' - model selection is now handled in transcription component
    const result = await transcribeFile('base', 'auto')
    console.log('📝 Transcription result:', result)
  }, [uploadedFile, transcribeFile])

  return (
    <div className="flex flex-col gap-4">
      {/* Main Action Button */}
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
      </div>
    </div>
  )
}
