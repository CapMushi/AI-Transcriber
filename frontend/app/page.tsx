"use client"

import { Header } from "@/components/header"
import { FileUploadArea } from "@/components/file-upload-area"
import { TranscriptionOutput } from "@/components/transcription-output"
import { PlaybackControls } from "@/components/playback-controls"
import { ActionButtons } from "@/components/action-buttons"
import { LoadingIndicator } from "@/components/loading-indicator"
import { AudioWaveBackground } from "@/components/audio-wave-background"
import { ErrorDisplay } from "@/components/error-display"
import { DebugPanel } from "@/components/debug-panel"
import { WhisperProvider, useWhisperContext } from "@/contexts/whisper-context"

function HomeContent() {
  const {
    transcription,
    isTranscribing,
    error,
    clearError
  } = useWhisperContext()

  return (
    <div className="h-screen bg-dark-primary overflow-hidden flex flex-col relative">
      {/* Audio Wave Background */}
      <AudioWaveBackground />

      {/* Error Display */}
      <ErrorDisplay error={error} onClear={clearError} />

      {/* Header */}
      <Header />

      {/* Main content area - flex-1 to take remaining space */}
      <main className="flex-1 flex flex-col px-4 py-4 max-w-7xl mx-auto w-full min-h-0 relative z-10">
        {/* Two-panel layout - flex-1 to take available space */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1 mb-4 min-h-0">
          {/* Left Panel - Upload Area */}
          <div className="flex flex-col min-h-0">
            <FileUploadArea />
          </div>

          {/* Right Panel - Transcription */}
          <div className="flex flex-col min-h-0">
            <TranscriptionOutput transcription={transcription} />
          </div>
        </div>

        {/* Bottom section - Playback controls and action buttons */}
        <div className="flex-shrink-0 space-y-4">
          <PlaybackControls />
          <ActionButtons />
        </div>
      </main>

      <LoadingIndicator isLoading={isTranscribing} />
      
      {/* Debug Panel - Remove this in production */}
      <DebugPanel />
    </div>
  )
}

export default function Home() {
  return (
    <WhisperProvider>
      <HomeContent />
    </WhisperProvider>
  )
}
