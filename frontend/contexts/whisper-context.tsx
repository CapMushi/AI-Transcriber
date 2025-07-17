"use client"

import React, { createContext, useContext, ReactNode } from 'react'
import { useWhisperAPI } from '@/hooks/use-whisper-api'

// Create the context
const WhisperContext = createContext<ReturnType<typeof useWhisperAPI> | null>(null)

// Provider component
export function WhisperProvider({ children }: { children: ReactNode }) {
  const whisperState = useWhisperAPI()
  
  return (
    <WhisperContext.Provider value={whisperState}>
      {children}
    </WhisperContext.Provider>
  )
}

// Custom hook to use the context
export function useWhisperContext() {
  const context = useContext(WhisperContext)
  if (!context) {
    throw new Error('useWhisperContext must be used within a WhisperProvider')
  }
  return context
} 