"use client"

import { useWhisperContext } from "@/contexts/whisper-context"

export function DebugPanel() {
  const {
    uploadedFile,
    primaryFile,
    secondaryFile,
    isUploading,
    uploadProgress,
    transcription,
    isTranscribing,
    transcriptionProgress,
    error,
    supportedFormats,
    availableModels
  } = useWhisperContext()

  return (
    <div className="fixed bottom-4 left-4 bg-black/80 text-white p-4 rounded-lg text-xs max-w-sm z-50">
      <h3 className="font-bold mb-2">Debug Info</h3>
      <div className="space-y-1">
        <div>📁 Primary File: {primaryFile ? primaryFile.original_name : 'None'}</div>
        <div>🔍 Secondary File: {secondaryFile ? secondaryFile.original_name : 'None'}</div>
        <div>📤 Uploading: {isUploading ? `${uploadProgress}%` : 'No'}</div>
        <div>🎯 Transcribing: {isTranscribing ? `${transcriptionProgress}%` : 'No'}</div>
        <div>📝 Has Transcription: {transcription ? 'Yes' : 'No'}</div>
        <div>❌ Error: {error || 'None'}</div>
        <div>📋 Formats: {supportedFormats ? 'Loaded' : 'Not loaded'}</div>
        <div>⚙️ Models: {availableModels ? 'Loaded' : 'Not loaded'}</div>
      </div>
    </div>
  )
} 