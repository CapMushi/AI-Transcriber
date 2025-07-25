"use client"

import { useState, useEffect, useCallback } from "react"
import { GlassButton } from "@/components/glass-button"
import { Zap, Search, Trash2 } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"

export function ActionButtons() {
  const {
    uploadedFile,
    primaryFile,
    secondaryFile,
    transcription,
    isTranscribing,
    isComparing,
    isClearing,
    transcribeFile,
    storePrimaryContent,
    clearEmbeddings,
    compareContent
  } = useWhisperContext()

  // Debug logging
  console.log('🔍 ActionButtons - Current state:', {
    uploadedFile: uploadedFile ? 'File uploaded' : 'No file',
    primaryFile: primaryFile ? 'Primary file uploaded' : 'No primary file',
    secondaryFile: secondaryFile ? 'Secondary file uploaded' : 'No secondary file',
    transcription: transcription ? 'Has transcription' : 'No transcription',
    isTranscribing,
    isComparing
  })
  
  // Force re-render when files change
  useEffect(() => {
    console.log('🔄 ActionButtons: files changed to:', { primaryFile, secondaryFile })
  }, [primaryFile, secondaryFile])

  const handleTranscribe = useCallback(async () => {
    console.log('🎯 Transcribe button clicked')
    console.log('📁 Primary file state:', primaryFile)
    
    if (!primaryFile) {
      console.error('❌ No primary file uploaded, cannot transcribe')
      return
    }
    
    console.log('🔄 Starting transcription with default model (base)...')
    // Use default model 'base' - model selection is now handled in transcription component
    const result = await transcribeFile('base', 'auto')
    console.log('📝 Transcription result:', result)
  }, [primaryFile, transcribeFile])

  const handleCompare = useCallback(async () => {
    console.log('🔍 Compare button clicked')
    console.log('📁 Primary file state:', primaryFile)
    console.log('📁 Secondary file state:', secondaryFile)
    
    if (!primaryFile || !secondaryFile) {
      console.error('❌ Both primary and secondary files are required for comparison')
      return
    }
    
    console.log('🔄 Starting content comparison workflow...')
    
    // Step 1: Store primary content first
    console.log('💾 Step 1: Storing primary content...')
    const storeResult = await storePrimaryContent('base', 'auto')
    if (!storeResult) {
      console.error('❌ Failed to store primary content')
      return
    }
    
    // Step 2: Compare content
    console.log('🔍 Step 2: Comparing content...')
    const compareResult = await compareContent()
    console.log('🔍 Comparison result:', compareResult)
  }, [primaryFile, secondaryFile, storePrimaryContent, compareContent])

  const handleClearEmbeddings = useCallback(async () => {
    console.log('🧹 Clear embeddings button clicked')
    
    console.log('🔄 Starting clear embeddings...')
    const result = await clearEmbeddings()
    console.log('🧹 Clear embeddings result:', result)
  }, [clearEmbeddings])

  return (
    <div className="flex flex-col gap-4">
      {/* Main Action Buttons */}
      <div className="flex gap-4 justify-center">
        <GlassButton
          onClick={handleTranscribe}
          disabled={isTranscribing || !primaryFile}
          className="px-6 py-2 text-sm font-semibold bg-accent-orange/70 hover:bg-accent-orange/90 border-accent-orange/80 flex items-center gap-2 text-light-gray disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Zap className="h-4 w-4" />
          {isTranscribing ? "Transcribing..." : "Transcribe Primary"}
          {/* Show button state */}
          <span className="text-xs opacity-50">
            ({primaryFile ? 'Primary Ready' : 'No Primary File'})
          </span>
        </GlassButton>

        <GlassButton
          onClick={handleCompare}
          disabled={isComparing || !primaryFile || !secondaryFile}
          className="px-6 py-2 text-sm font-semibold bg-blue-500/70 hover:bg-blue-500/90 border-blue-500/80 flex items-center gap-2 text-light-gray disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Search className="h-4 w-4" />
          {isComparing ? "Comparing..." : "Compare Content"}
          {/* Show button state */}
          <span className="text-xs opacity-50">
            ({primaryFile && secondaryFile ? 'Both Ready' : 'Need Both Files'})
          </span>
        </GlassButton>

        <GlassButton
          onClick={handleClearEmbeddings}
          disabled={isClearing}
          className="px-6 py-2 text-sm font-semibold bg-red-500/70 hover:bg-red-500/90 border-red-500/80 flex items-center gap-2 text-light-gray disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Trash2 className="h-4 w-4" />
          {isClearing ? "Clearing..." : "Clear Embeddings"}
        </GlassButton>
      </div>
    </div>
  )
}
