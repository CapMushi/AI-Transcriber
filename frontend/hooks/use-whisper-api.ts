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
  primaryFile: FileInfo | null
  secondaryFile: FileInfo | null
  isUploading: boolean
  uploadProgress: number
  
  // Audio playback state
  audioUrl: string | null
  
  // Transcription state
  transcription: TranscriptionResponse | null
  isTranscribing: boolean
  transcriptionProgress: number
  
  // Storage state
  isStoring: boolean  // NEW: Track storage progress
  storageProgress: number  // NEW: Storage progress percentage
  
  // Clear embeddings state
  isClearing: boolean
  
  // Comparison state
  comparisonResult: any | null
  isComparing: boolean
  
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
  uploadPrimaryFile: (file: File) => Promise<boolean>
  uploadSecondaryFile: (file: File) => Promise<boolean>
  clearFile: () => void
  clearPrimaryFile: () => void
  clearSecondaryFile: () => void
  
  // Transcription operations
  transcribeFile: (model?: string, language?: string) => Promise<boolean>
  detectLanguage: () => Promise<boolean>
  
  // Storage operations
  storePrimaryContent: (model?: string, language?: string) => Promise<boolean>
  
  // Clear embeddings operations
  clearEmbeddings: () => Promise<boolean>
  
  // Comparison operations
  compareContent: () => Promise<boolean>
  
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
  const [primaryFile, setPrimaryFile] = useState<FileInfo | null>(null)
  const [secondaryFile, setSecondaryFile] = useState<FileInfo | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  
  // Audio playback state
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  
  const [transcription, setTranscription] = useState<TranscriptionResponse | null>(null)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [transcriptionProgress, setTranscriptionProgress] = useState(0)
  
  const [isStoring, setIsStoring] = useState(false) // NEW: Track storage progress
  const [storageProgress, setStorageProgress] = useState(0) // NEW: Storage progress percentage
  
  const [isClearing, setIsClearing] = useState(false)
  
  const [comparisonResult, setComparisonResult] = useState<any | null>(null)
  const [isComparing, setIsComparing] = useState(false)
  
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
        
        // Create audio URL for playback
        const audioUrl = URL.createObjectURL(file)
        setAudioUrl(audioUrl)
        console.log('✅ Audio URL created for playback')
        
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

  // Upload primary file
  const uploadPrimaryFile = useCallback(async (file: File): Promise<boolean> => {
    console.log('🚀 Starting primary file upload:', file.name, file.size, 'bytes')
    try {
      setIsUploading(true)
      setUploadProgress(0)
      setError(null)
      
      console.log('📤 Uploading primary file to API...')
      
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
      
      console.log('📥 Primary upload response:', response)
      
      if (response.success && response.file_info) {
        console.log('✅ Primary file uploaded successfully:', response.file_info)
        setPrimaryFile(response.file_info)
        
        // Create audio URL for playback
        const audioUrl = URL.createObjectURL(file)
        setAudioUrl(audioUrl)
        console.log('✅ Audio URL created for primary file playback')
        
        return true
      } else {
        console.error('❌ Primary file upload failed:', response.error)
        setError(response.error || 'Primary file upload failed')
        return false
      }
    } catch (err) {
      console.error('💥 Primary file upload error:', err)
      const apiError = err as APIError
      setError(apiError.message || 'Primary file upload failed')
      return false
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }, [])

  // Upload secondary file
  const uploadSecondaryFile = useCallback(async (file: File): Promise<boolean> => {
    console.log('🚀 Starting secondary file upload:', file.name, file.size, 'bytes')
    try {
      setIsUploading(true)
      setUploadProgress(0)
      setError(null)
      
      console.log('📤 Uploading secondary file to API...')
      
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
      
      console.log('📥 Secondary upload response:', response)
      
      if (response.success && response.file_info) {
        console.log('✅ Secondary file uploaded successfully:', response.file_info)
        setSecondaryFile(response.file_info)
        return true
      } else {
        console.error('❌ Secondary file upload failed:', response.error)
        setError(response.error || 'Secondary file upload failed')
        return false
      }
    } catch (err) {
      console.error('💥 Secondary file upload error:', err)
      const apiError = err as APIError
      setError(apiError.message || 'Secondary file upload failed')
      return false
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }, [])

  // Clear primary file
  const clearPrimaryFile = useCallback(() => {
    setPrimaryFile(null)
    setError(null)
    // Cleanup audio URL
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl(null)
    }
  }, [audioUrl])

  // Clear secondary file
  const clearSecondaryFile = useCallback(() => {
    setSecondaryFile(null)
    setError(null)
  }, [])

  // Store primary content
  const storePrimaryContent = useCallback(async (
    model: string = 'base',
    language: string = 'auto'
  ): Promise<boolean> => {
    console.log('💾 Starting primary content storage...')
    console.log('📁 Primary file:', primaryFile)
    
    if (!primaryFile) {
      console.error('❌ No primary file uploaded for storage')
      setError('No primary file uploaded')
      return false
    }
    
    try {
      setIsTranscribing(true)  // Start transcription state
      setError(null)
      
      console.log('🔄 Calling store primary API...')
      
      const response = await apiService.storePrimaryContent(
        primaryFile.file_path,
        model,
        language
      )
      
      console.log('📥 Store primary response:', response)
      
      if (response.success) {
        console.log('✅ Transcription completed successfully:', response)
        
        // Set the transcription from storage response immediately
        const transcriptionData = {
          success: true,
          message: response.message || "Transcription completed",
          text: response.text,
          segments: response.segments,
          language: "auto",
          confidence: 0.0,
          processing_time: 0.0,
          model_used: model,
          file_path: primaryFile?.file_path || "",
          error: undefined
        }
        console.log('📝 Transcription data to set:', transcriptionData)
        setTranscription(transcriptionData)
        
        // Check if storage is happening in background
        if (response.storage_in_progress) {
          console.log('🔄 Storage is happening in background, showing progress...')
          setIsStoring(true)
          setStorageProgress(0)
          
          // Simulate storage progress (since we can't track real progress)
          const progressInterval = setInterval(() => {
            setStorageProgress(prev => {
              if (prev >= 90) {
                clearInterval(progressInterval)
                return 90
              }
              return prev + 10
            })
          }, 500)
          
          // Stop storage progress after a reasonable time
          setTimeout(() => {
            clearInterval(progressInterval)
            setStorageProgress(100)
            setTimeout(() => {
              setIsStoring(false)
              setStorageProgress(0)
            }, 1000)
          }, 5000) // Assume storage takes ~5 seconds
        }
        
        return true
      } else {
        console.error('❌ Store primary failed:', response.error)
        setError(response.error || 'Store primary failed')
        return false
      }
    } catch (err) {
      console.error('💥 Store primary error:', err)
      const apiError = err as APIError
      setError(apiError.message || 'Store primary failed')
      return false
    } finally {
      setIsTranscribing(false)
    }
  }, [primaryFile])

  // Compare content
  const compareContent = useCallback(async (): Promise<boolean> => {
    console.log('🔍 Starting content comparison...')
    console.log('📁 Primary file:', primaryFile)
    console.log('📁 Secondary file:', secondaryFile)
    
    if (!primaryFile || !secondaryFile) {
      console.error('❌ Both primary and secondary files are required for comparison')
      setError('Both primary and secondary files are required for comparison')
      return false
    }
    
    try {
      setIsComparing(true)
      setError(null)
      
      console.log('🔄 Calling comparison API...')
      
      // Call the actual comparison API (now only searches against stored primary)
      const response = await apiService.compareContent(
        primaryFile.file_path,  // This is now just for reference, not used in storage
        secondaryFile.file_path
      )
      
      console.log('📥 Comparison response:', response)
      
      if (response.success) {
        console.log('✅ Comparison successful:', response)
        setComparisonResult(response)
        
        // Debug: Print transcriptions of both files
        console.log('🔍 SECONDARY TRANSCRIPTION:', response.secondary_text)
        console.log('🔍 COMPARISON RESULT:', {
          found: response.found,
          confidence: response.confidence,
          timestamps: response.timestamps,
          message: response.message
        })
        
        return true
      } else {
        console.error('❌ Comparison failed:', response.error)
        setError(response.error || 'Comparison failed')
        return false
      }
    } catch (err) {
      console.error('💥 Comparison error:', err)
      const apiError = err as APIError
      setError(apiError.message || 'Comparison failed')
      return false
    } finally {
      setIsComparing(false)
    }
  }, [primaryFile, secondaryFile])

  // Clear uploaded file (for backward compatibility)
  const clearFile = useCallback(() => {
    setUploadedFile(null)
    setTranscription(null)
    setError(null)
    // Cleanup audio URL
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl(null)
    }
  }, [audioUrl])

  // Transcribe file
  const transcribeFile = useCallback(async (
    model: string = 'base',
    language: string = 'auto'
  ): Promise<boolean> => {
    console.log('🎯 Starting transcription with model:', model, 'language:', language)
    console.log('📁 Primary file:', primaryFile)
    
    if (!primaryFile) {
      console.error('❌ No primary file uploaded for transcription')
      setError('No primary file uploaded')
      return false
    }
    
    // Allow transcription even with duration 0 (might be a short file)
    console.log('📊 File duration:', primaryFile.duration, 'seconds')
    if (primaryFile.duration === 0) {
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
        primaryFile.file_path,
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
  }, [primaryFile])

  // Detect language
  const detectLanguage = useCallback(async (): Promise<boolean> => {
    if (!primaryFile) {
      setError('No primary file uploaded')
      return false
    }

    try {
      setError(null)
      const response = await apiService.detectLanguage(primaryFile.file_path)
      
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
  }, [primaryFile, transcription])

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

  // Clear embeddings
  const clearEmbeddings = useCallback(async (): Promise<boolean> => {
    try {
      setIsClearing(true)
      setError(null)
      
      const response = await apiService.clearEmbeddings()
      
      if (response.success) {
        console.log('✅ Embeddings cleared successfully')
        return true
      } else {
        setError(response.error || 'Failed to clear embeddings')
        return false
      }
    } catch (error) {
      setError('Clear embeddings failed')
      return false
    } finally {
      setIsClearing(false)
    }
  }, [])

  // Debug: Monitor uploadedFile state changes
  useEffect(() => {
    console.log('🔄 uploadedFile state changed:', uploadedFile)
  }, [uploadedFile])

  return {
    // State
    uploadedFile,
    primaryFile,
    secondaryFile,
    isUploading,
    uploadProgress,
    audioUrl,
    transcription,
    isTranscribing,
    transcriptionProgress,
    isStoring, // NEW: Expose storage progress state
    storageProgress, // NEW: Expose storage progress state
    isClearing,
    comparisonResult,
    isComparing,
    supportedFormats,
    availableModels,
    downloadFormats,
    error,
    isLoadingFormats,
    isLoadingModels,
    
    // Actions
    uploadFile,
    uploadPrimaryFile,
    uploadSecondaryFile,
    clearFile,
    clearPrimaryFile,
    clearSecondaryFile,
    transcribeFile,
    detectLanguage,
    storePrimaryContent,
    clearEmbeddings,
    compareContent,
    downloadTranscription,
    loadSupportedFormats,
    loadAvailableModels,
    loadDownloadFormats,
    clearError,
  }
} 