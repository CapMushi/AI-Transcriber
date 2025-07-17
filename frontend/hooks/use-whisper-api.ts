/**
 * Custom Hook for Whisper AI API Operations
 * Manages state, API calls, and error handling
 */

import { useState, useCallback, useEffect } from 'react'
import { 
  apiService, 
  UploadResponse, 
  TranscriptionResponse, 
  FileInfo,
  APIError,
  SupportedFormats,
  AvailableModels,
  DownloadFormats
} from '@/lib/api'

export interface UseWhisperAPIState {
  // File state
  uploadedFile: FileInfo | null
  isUploading: boolean
  uploadProgress: number
  
  // Transcription state
  transcription: TranscriptionResponse | null
  isTranscribing: boolean
  transcriptionProgress: number
  
  // API info state
  supportedFormats: SupportedFormats | null
  availableModels: AvailableModels | null
  downloadFormats: DownloadFormats | null
  
  // Error state
  error: string | null
  
  // Loading states
  isLoadingFormats: boolean
  isLoadingModels: boolean
}

export interface UseWhisperAPIActions {
  // File operations
  uploadFile: (file: File) => Promise<boolean>
  clearFile: () => void
  
  // Transcription operations
  transcribeFile: (model?: string, language?: string) => Promise<boolean>
  detectLanguage: () => Promise<boolean>
  
  // Download operations
  downloadTranscription: (format?: string, filename?: string) => Promise<boolean>
  
  // API info operations
  loadSupportedFormats: () => Promise<void>
  loadAvailableModels: () => Promise<void>
  loadDownloadFormats: () => Promise<void>
  
  // Error handling
  clearError: () => void
}

export function useWhisperAPI(): UseWhisperAPIState & UseWhisperAPIActions {
  // State
  const [uploadedFile, setUploadedFile] = useState<FileInfo | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  
  const [transcription, setTranscription] = useState<TranscriptionResponse | null>(null)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [transcriptionProgress, setTranscriptionProgress] = useState(0)
  
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats | null>(null)
  const [availableModels, setAvailableModels] = useState<AvailableModels | null>(null)
  const [downloadFormats, setDownloadFormats] = useState<DownloadFormats | null>(null)
  
  const [error, setError] = useState<string | null>(null)
  const [isLoadingFormats, setIsLoadingFormats] = useState(false)
  const [isLoadingModels, setIsLoadingModels] = useState(false)

  // Clear error
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // Upload file
  const uploadFile = useCallback(async (file: File): Promise<boolean> => {
    console.log('🚀 Starting file upload:', file.name, file.size, 'bytes')
    try {
      setIsUploading(true)
      setUploadProgress(0)
      setError(null)
      
      console.log('📤 Uploading file to API...')
      
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 100)

      const response = await apiService.uploadFile(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      console.log('📥 Upload response:', response)
      
      if (response.success && response.file_info) {
        console.log('✅ Upload successful, file info:', response.file_info)
        console.log('🔄 Setting uploadedFile state...')
        setUploadedFile(response.file_info)
        console.log('✅ uploadedFile state set to:', response.file_info)
        return true
      } else {
        console.error('❌ Upload failed:', response.error)
        setError(response.error || 'Upload failed')
        return false
      }
    } catch (err) {
      console.error('💥 Upload error:', err)
      const apiError = err as APIError
      setError(apiError.message || 'Upload failed')
      return false
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }, [])

  // Clear uploaded file
  const clearFile = useCallback(() => {
    setUploadedFile(null)
    setTranscription(null)
    setError(null)
  }, [])

  // Transcribe file
  const transcribeFile = useCallback(async (
    model: string = 'base',
    language: string = 'auto'
  ): Promise<boolean> => {
    console.log('🎯 Starting transcription with model:', model, 'language:', language)
    console.log('📁 Uploaded file:', uploadedFile)
    
    if (!uploadedFile) {
      console.error('❌ No file uploaded for transcription')
      setError('No file uploaded')
      return false
    }
    
    // Allow transcription even with duration 0 (might be a short file)
    console.log('📊 File duration:', uploadedFile.duration, 'seconds')
    if (uploadedFile.duration === 0) {
      console.log('⚠️ File duration is 0, but proceeding with transcription...')
    }

    try {
      setIsTranscribing(true)
      setTranscriptionProgress(0)
      setError(null)
      
      console.log('🔄 Calling transcription API...')
      
      // Simulate transcription progress
      const progressInterval = setInterval(() => {
        setTranscriptionProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 5
        })
      }, 200)

      const response = await apiService.transcribeFile(
        uploadedFile.file_path,
        model,
        language
      )
      
      clearInterval(progressInterval)
      setTranscriptionProgress(100)
      
      console.log('📝 Transcription response:', response)
      
      if (response.success) {
        console.log('✅ Transcription successful:', response)
        setTranscription(response)
        return true
      } else {
        console.error('❌ Transcription failed:', response.error)
        setError(response.error || 'Transcription failed')
        return false
      }
    } catch (err) {
      console.error('💥 Transcription error:', err)
      const apiError = err as APIError
      setError(apiError.message || 'Transcription failed')
      return false
    } finally {
      setIsTranscribing(false)
      setTimeout(() => setTranscriptionProgress(0), 1000)
    }
  }, [uploadedFile])

  // Detect language
  const detectLanguage = useCallback(async (): Promise<boolean> => {
    if (!uploadedFile) {
      setError('No file uploaded')
      return false
    }

    try {
      setError(null)
      const response = await apiService.detectLanguage(uploadedFile.file_path)
      
      if (response.success) {
        // Update transcription with detected language
        if (transcription) {
          setTranscription({
            ...transcription,
            language: response.language || transcription.language
          })
        }
        return true
      } else {
        setError(response.error || 'Language detection failed')
        return false
      }
    } catch (err) {
      const apiError = err as APIError
      setError(apiError.message || 'Language detection failed')
      return false
    }
  }, [uploadedFile, transcription])

  // Download transcription
  const downloadTranscription = useCallback(async (
    format: string = 'txt',
    filename: string = 'transcription'
  ): Promise<boolean> => {
    if (!transcription) {
      setError('No transcription available')
      return false
    }

    try {
      setError(null)
      const blob = await apiService.downloadTranscription(
        transcription,
        format,
        filename
      )
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      return true
    } catch (err) {
      const apiError = err as APIError
      setError(apiError.message || 'Download failed')
      return false
    }
  }, [transcription])

  // Load supported formats
  const loadSupportedFormats = useCallback(async () => {
    try {
      setIsLoadingFormats(true)
      setError(null)
      const formats = await apiService.getSupportedFormats()
      setSupportedFormats(formats)
    } catch (err) {
      const apiError = err as APIError
      setError(apiError.message || 'Failed to load supported formats')
    } finally {
      setIsLoadingFormats(false)
    }
  }, [])

  // Load available models
  const loadAvailableModels = useCallback(async () => {
    try {
      setIsLoadingModels(true)
      setError(null)
      const models = await apiService.getAvailableModels()
      setAvailableModels(models)
    } catch (err) {
      const apiError = err as APIError
      setError(apiError.message || 'Failed to load available models')
    } finally {
      setIsLoadingModels(false)
    }
  }, [])

  // Load download formats
  const loadDownloadFormats = useCallback(async () => {
    try {
      setError(null)
      const formats = await apiService.getDownloadFormats()
      setDownloadFormats(formats)
    } catch (err) {
      const apiError = err as APIError
      setError(apiError.message || 'Failed to load download formats')
    }
  }, [])

  // Debug: Monitor uploadedFile state changes
  useEffect(() => {
    console.log('🔄 uploadedFile state changed:', uploadedFile)
  }, [uploadedFile])

  return {
    // State
    uploadedFile,
    isUploading,
    uploadProgress,
    transcription,
    isTranscribing,
    transcriptionProgress,
    supportedFormats,
    availableModels,
    downloadFormats,
    error,
    isLoadingFormats,
    isLoadingModels,
    
    // Actions
    uploadFile,
    clearFile,
    transcribeFile,
    detectLanguage,
    downloadTranscription,
    loadSupportedFormats,
    loadAvailableModels,
    loadDownloadFormats,
    clearError,
  }
} 