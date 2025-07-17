"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { GlassCard } from "@/components/glass-card"
import { GlassButton } from "@/components/glass-button"
import { Upload, FileAudio, FileVideo, X, CheckCircle, AlertCircle } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"

export function FileUploadArea() {
  const [isDragOver, setIsDragOver] = useState(false)
  const {
    uploadedFile,
    isUploading,
    uploadProgress,
    error,
    supportedFormats,
    uploadFile,
    clearFile,
    loadSupportedFormats,
    clearError
  } = useWhisperContext()

  // Load supported formats on component mount
  useEffect(() => {
    loadSupportedFormats()
  }, [loadSupportedFormats])

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleFileUpload = async (files: FileList) => {
    console.log('📂 File upload handler called with files:', files.length, 'files')
    if (files.length === 0) {
      console.log('⚠️ No files selected')
      return
    }
    
    const file = files[0]
    console.log('📁 Selected file:', { name: file.name, size: file.size, type: file.type })
    console.log('🔄 Calling uploadFile function...')
    
    const result = await uploadFile(file)
    console.log('📤 Upload result:', result)
  }

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(false)
    await handleFileUpload(e.dataTransfer.files)
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      await handleFileUpload(files)
    }
  }

  return (
    <GlassCard
      opacity="medium"
      blur="lg"
      className="p-4 text-center flex flex-col items-center justify-center h-full w-full transition-all duration-300 ease-in-out border-dark-secondary/30"
    >
      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <span className="text-red-300 text-sm">{error}</span>
          <button
            onClick={clearError}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Upload Progress */}
      {isUploading && (
        <div className="mb-4 w-full">
          <div className="flex items-center justify-between text-sm text-light-gray mb-2">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-dark-secondary/30 rounded-full h-2">
            <div
              className="bg-accent-orange h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Uploaded File Info */}
      {uploadedFile && !isUploading && (
        <div className="mb-4 p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <span className="text-green-300 font-semibold">File Uploaded Successfully</span>
          </div>
          <div className="text-sm text-light-gray space-y-1">
            <p><span className="text-accent-orange">Name:</span> {uploadedFile.original_name}</p>
            <p><span className="text-accent-orange">Size:</span> {uploadedFile.size_mb.toFixed(2)} MB</p>
            <p><span className="text-accent-orange">Duration:</span> {uploadedFile.duration.toFixed(1)}s</p>
            <p><span className="text-accent-orange">Type:</span> {uploadedFile.is_audio ? 'Audio' : 'Video'} ({uploadedFile.format})</p>
          </div>
          <button
            onClick={clearFile}
            className="mt-2 text-red-400 hover:text-red-300 text-sm flex items-center gap-1"
          >
            <X className="h-4 w-4" />
            Remove File
          </button>
        </div>
      )}

      {/* Upload Area */}
      {!uploadedFile && (
        <div
          className={`w-full p-6 border-2 border-dashed rounded-lg transition-colors duration-300 ease-in-out flex-1 flex flex-col items-center justify-center ${
            isDragOver
              ? "border-accent-orange bg-accent-orange/[0.1] shadow-inner-lg"
              : "border-light-gray/[0.3] hover:border-accent-orange/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex justify-center items-center gap-3 mb-4">
            <FileAudio className="h-8 w-8 text-dark-secondary" />
            <Upload className="h-12 w-12 text-accent-orange" />
            <FileVideo className="h-8 w-8 text-dark-secondary" />
          </div>
          <p className="text-light-gray text-base mb-4">
            <label htmlFor="file-upload" className="cursor-pointer text-accent-orange font-semibold hover:underline">
              Upload Audio/Video
            </label>{" "}
            or drag and drop your file here.
          </p>
          
          {/* Supported Formats Info */}
          {supportedFormats && (
            <div className="text-xs text-light-gray/70 mb-4">
              <p>Supported: {supportedFormats.audio_formats.join(', ')}</p>
              <p>Max size: {supportedFormats.max_file_size_mb}MB</p>
            </div>
          )}
          
          <input 
            id="file-upload" 
            type="file" 
            className="hidden" 
            onChange={handleFileSelect} 
            accept="audio/*,video/*" 
          />
          <GlassButton asChild className="mt-2 px-6 py-2 border-accent-orange/30 hover:bg-accent-orange/20">
            <label htmlFor="file-upload" className="cursor-pointer">
              Select File
            </label>
          </GlassButton>
        </div>
      )}
    </GlassCard>
  )
}
