"use client"

import { useState, useEffect, useCallback } from "react"
import { GlassButton } from "@/components/glass-button"
import { Zap, Search, Trash2 } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"
import { TranscriptionResponse } from "@/lib/api"

export function ActionButtons() {
  const {
    uploadedFile,
    primaryFiles,
    secondaryFile,
    transcription,
    isTranscribing,
    isComparing,
    isClearing,
    transcribeFile,
    storePrimaryContent,
    storeMultiplePrimaryContent,
    clearEmbeddings,
    compareContent,
    selectedModel
  } = useWhisperContext()

  // Debug logging
  console.log('🔍 ActionButtons - Current state:', {
    uploadedFile: uploadedFile ? 'File uploaded' : 'No file',
    primaryFiles: primaryFiles && primaryFiles.length > 0 ? `${primaryFiles.length} files uploaded` : 'No primary files',
    secondaryFile: secondaryFile ? 'Secondary file uploaded' : 'No secondary file',
    transcription: transcription ? 'Has transcription' : 'No transcription',
    isTranscribing,
    isComparing
  })
  
  // Force re-render when files change
  useEffect(() => {
    console.log('🔄 ActionButtons: files changed to:', { primaryFiles, secondaryFile })
  }, [primaryFiles, secondaryFile])

  const handleTranscribe = useCallback(async () => {
    console.log('🎯 Transcribe button clicked')
    console.log('📁 Primary files state:', primaryFiles)
    
    if (!primaryFiles || primaryFiles.length === 0) {
      console.error('❌ No primary files uploaded, cannot transcribe')
      return
    }
    
    console.log('🔄 Starting transcription with default model (base)...')
    // Use default model 'base' - model selection is now handled in transcription component
    const result = await transcribeFile('base', 'auto')
    console.log('📝 Transcription result:', result)
  }, [primaryFiles, transcribeFile])

  const handleCompare = useCallback(async () => {
    console.log('🔍 Compare button clicked')
    console.log('📁 Primary files state:', primaryFiles)
    console.log('📁 Secondary file state:', secondaryFile)
    
    if (!primaryFiles || primaryFiles.length === 0 || !secondaryFile) {
      console.error('❌ Both primary files and secondary file are required for comparison')
      return
    }
    
    console.log('🔄 Starting content comparison workflow...')
    
    // Step 1: Store multiple primary content first
    console.log('💾 Step 1: Storing multiple primary content...')
    console.log('🔍 DEBUG: About to call storeMultiplePrimaryContent...')
    try {
      const storeResult = await storeMultiplePrimaryContent(selectedModel, 'auto')
      console.log('🔍 DEBUG: storeMultiplePrimaryContent result:', storeResult)
      if (!storeResult) {
        console.error('❌ Failed to store multiple primary content')
        return
      }
      
      // Wait for storage to complete before proceeding
      console.log('⏳ Waiting for storage to complete...')
      await new Promise(resolve => setTimeout(resolve, 6000)) // Wait 6 seconds for storage
      console.log('✅ Storage wait completed')
      
    } catch (error) {
      console.error('💥 storeMultiplePrimaryContent failed with error:', error)
      return
    }
    
    // Step 2: Compare content
    console.log('🔍 Step 2: Comparing content...')
    const compareResult = await compareContent()
    console.log('🔍 Comparison result:', compareResult)
  }, [primaryFiles, secondaryFile, storeMultiplePrimaryContent, compareContent, selectedModel])

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
          disabled={isTranscribing || !primaryFiles || primaryFiles.length === 0}
          className="px-6 py-2 text-sm font-semibold bg-accent-orange/70 hover:bg-accent-orange/90 border-accent-orange/80 flex items-center gap-2 text-light-gray disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Zap className="h-4 w-4" />
          {isTranscribing ? "Transcribing..." : "Transcribe Primary"}
          {/* Show button state */}
          <span className="text-xs opacity-50">
            ({primaryFiles && primaryFiles.length > 0 ? `${primaryFiles.length} Primary Files Ready` : 'No Primary Files'})
          </span>
        </GlassButton>

        <GlassButton
          onClick={handleCompare}
          disabled={isComparing || !primaryFiles || primaryFiles.length === 0 || !secondaryFile}
          className="px-6 py-2 text-sm font-semibold bg-blue-500/70 hover:bg-blue-500/90 border-blue-500/80 flex items-center gap-2 text-light-gray disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Search className="h-4 w-4" />
          {isComparing ? "Comparing..." : "Compare Content"}
          {/* Show button state */}
          <span className="text-xs opacity-50">
            ({primaryFiles && primaryFiles.length > 0 && secondaryFile ? 'Both Ready' : 'Need Both Files'})
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
