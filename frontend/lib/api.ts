/**
 * API Service Layer for Whisper AI Frontend
 * Handles all communication with the backend API
 */

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// TypeScript Interfaces
export interface FileInfo {
  file_path: string
  original_name: string
  size_mb: number
  duration: number
  format: string
  is_audio: boolean
  is_video: boolean
}

export interface UploadResponse {
  success: boolean
  message: string
  file_info?: FileInfo
  error?: string
}

export interface TranscriptionSegment {
  start: number
  end: number
  text: string
}

export interface TranscriptionResponse {
  success: boolean
  message: string
  text: string
  segments: TranscriptionSegment[]
  language: string
  confidence: number
  processing_time: number
  model_used: string
  file_path: string
  error?: string
}

export interface SupportedFormats {
  audio_formats: string[]
  video_formats: string[]
  max_file_size_mb: number
}

export interface AvailableModels {
  available_models: string[]
  default_model: string
}

export interface DownloadFormats {
  available_formats: string[]
  default_format: string
}

export interface ComparisonResponse {
  success: boolean
  message: string
  found: boolean
  timestamps: Array<{ start_time: number; end_time: number }>
  confidence: number
  primary_text: string
  secondary_text: string
  error?: string
}

export interface StorePrimaryResponse {
  success: boolean
  message: string
  file_id: string
  chunks_stored: number
  text: string
  segments: TranscriptionSegment[]
  error?: string
}

// API Error Class
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

// API Service Class
class APIService {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, defaultOptions)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new APIError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Network error',
        0,
        error
      )
    }
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health')
  }

  // Get API Info
  async getAPIInfo(): Promise<any> {
    return this.request<any>('/')
  }

  // Get Supported Formats
  async getSupportedFormats(): Promise<SupportedFormats> {
    return this.request<SupportedFormats>('/api/supported-formats')
  }

  // Get Available Models
  async getAvailableModels(): Promise<AvailableModels> {
    return this.request<AvailableModels>('/api/models')
  }

  // Get Download Formats
  async getDownloadFormats(): Promise<DownloadFormats> {
    return this.request<DownloadFormats>('/api/formats')
  }

  // Upload File
  async uploadFile(file: File): Promise<UploadResponse> {
    console.log('🌐 API: Starting file upload to:', `${this.baseURL}/api/upload`)
    console.log('📁 API: File details:', { name: file.name, size: file.size, type: file.type })
    
    const formData = new FormData()
    formData.append('file', file)

    const url = `${this.baseURL}/api/upload`
    
    try {
      console.log('📤 API: Sending POST request to:', url)
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      })

      console.log('📥 API: Response status:', response.status, response.statusText)
      console.log('📋 API: Response headers:', Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('❌ API: Upload failed with status:', response.status, errorData)
        throw new APIError(
          errorData.detail || `Upload failed: ${response.statusText}`,
          response.status,
          errorData
        )
      }

      const result = await response.json()
      console.log('✅ API: Upload successful:', result)
      return result
    } catch (error) {
      console.error('💥 API: Upload error:', error)
      if (error instanceof APIError) {
        throw error
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Upload failed',
        0,
        error
      )
    }
  }

  // Transcribe File
  async transcribeFile(
    filePath: string,
    model: string = 'base',
    language: string = 'auto',
    task: string = 'transcribe'
  ): Promise<TranscriptionResponse> {
    return this.request<TranscriptionResponse>('/api/transcribe', {
      method: 'POST',
      body: JSON.stringify({
        file_path: filePath,
        model,
        language,
        task,
      }),
    })
  }

  // Detect Language
  async detectLanguage(filePath: string): Promise<any> {
    return this.request<any>('/api/detect-language', {
      method: 'POST',
      body: JSON.stringify({
        file_path: filePath,
      }),
    })
  }

  // Download Transcription
  async downloadTranscription(
    transcriptionData: any,
    format: string = 'txt',
    filename: string = 'transcription'
  ): Promise<Blob> {
    const url = `${this.baseURL}/api/download`
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcription_data: transcriptionData,
          format,
          filename,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new APIError(
          errorData.detail || `Download failed: ${response.statusText}`,
          response.status,
          errorData
        )
      }

      return await response.blob()
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Download failed',
        0,
        error
      )
    }
  }

  // Compare Content
  async compareContent(
    primaryFilePath: string,
    secondaryFilePath: string,
    threshold: number = 0.95
  ): Promise<ComparisonResponse> {
    console.log('🔍 API: Starting content comparison...')
    console.log('📁 Primary file path:', primaryFilePath)
    console.log('📁 Secondary file path:', secondaryFilePath)
    
    try {
      const result = await this.request<ComparisonResponse>('/api/compare-content', {
        method: 'POST',
        body: JSON.stringify({
          primary_file_path: primaryFilePath,
          secondary_file_path: secondaryFilePath,
          threshold,
        }),
      })
      
      console.log('✅ API: Comparison successful:', result)
      return result
    } catch (error) {
      console.error('💥 API: Comparison error:', error)
      if (error instanceof APIError) {
        throw error
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Comparison failed',
        0,
        error
      )
    }
  }

  // Store Primary Content
  async storePrimaryContent(
    filePath: string,
    model: string = 'base',
    language: string = 'auto'
  ): Promise<StorePrimaryResponse> {
    console.log('💾 API: Storing primary content...')
    console.log('📁 File path:', filePath)
    console.log('🤖 Model:', model)
    console.log('🌍 Language:', language)

    try {
      const result = await this.request<StorePrimaryResponse>('/api/store-primary', {
        method: 'POST',
        body: JSON.stringify({
          file_path: filePath,
          model,
          language,
        }),
      })

      console.log('✅ API: Primary content stored:', result)
      return result
    } catch (error) {
      console.error('💥 API: Store primary content error:', error)
      if (error instanceof APIError) {
        throw error
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Store primary content failed',
        0,
        error
      )
    }
  }
}

// Export singleton instance
export const apiService = new APIService()

// Export types for use in components
export type {
  FileInfo,
  UploadResponse,
  TranscriptionResponse,
  TranscriptionSegment,
  SupportedFormats,
  AvailableModels,
  DownloadFormats,
  ComparisonResponse,
  StorePrimaryResponse,
} 