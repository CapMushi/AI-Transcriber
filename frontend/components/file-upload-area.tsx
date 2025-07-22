"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { GlassCard } from "@/components/glass-card"
import { GlassButton } from "@/components/glass-button"
import { Upload, FileAudio, FileVideo, X, CheckCircle, AlertCircle, Database, Search } from "lucide-react"
import { useWhisperContext } from "@/contexts/whisper-context"

export function FileUploadArea() {
  const [isDragOverPrimary, setIsDragOverPrimary] = useState(false)
  const [isDragOverSecondary, setIsDragOverSecondary] = useState(false)
  const {
    uploadedFile,
    primaryFile,
    secondaryFile,
    isUploading,
    uploadProgress,
    error,
    supportedFormats,
    uploadFile,
    uploadPrimaryFile,
    uploadSecondaryFile,
    clearFile,
    clearPrimaryFile,
    clearSecondaryFile,
    loadSupportedFormats,
    clearError
  } = useWhisperContext()

  // Load supported formats on component mount
  useEffect(() => {
    loadSupportedFormats()
  }, [loadSupportedFormats])

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, isPrimary: boolean) => {
    e.preventDefault()
    if (isPrimary) {
      setIsDragOverPrimary(true)
    } else {
      setIsDragOverSecondary(true)
    }
  }

  const handleDragLeave = (isPrimary: boolean) => {
    if (isPrimary) {
      setIsDragOverPrimary(false)
    } else {
      setIsDragOverSecondary(false)
    }
  }

  const handleFileUpload = async (files: FileList, isPrimary: boolean) => {
    console.log('📂 File upload handler called with files:', files.length, 'files for', isPrimary ? 'primary' : 'secondary')
    if (files.length === 0) {
      console.log('⚠️ No files selected')
      return
    }
    
    const file = files[0]
    console.log('📁 Selected file:', { name: file.name, size: file.size, type: file.type, isPrimary })
    console.log('🔄 Calling upload function...')
    
    // Use appropriate upload function based on file type
    if (isPrimary) {
      const result = await uploadPrimaryFile(file)
      console.log('📤 Primary upload result:', result)
    } else {
      const result = await uploadSecondaryFile(file)
      console.log('📤 Secondary upload result:', result)
    }
  }

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>, isPrimary: boolean) => {
    e.preventDefault()
    if (isPrimary) {
      setIsDragOverPrimary(false)
    } else {
      setIsDragOverSecondary(false)
    }
    await handleFileUpload(e.dataTransfer.files, isPrimary)
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>, isPrimary: boolean) => {
    const files = e.target.files
    if (files) {
      await handleFileUpload(files, isPrimary)
    }
  }

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-2">
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
        <div className="w-full">
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

      {/* Side by Side Upload Areas with File Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1">
        {/* Primary Column */}
        <div className="flex flex-col gap-4">
          {/* Primary File Info */}
          {primaryFile && !isUploading && (
            <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <span className="text-green-300 font-semibold">Primary File Uploaded</span>
              </div>
              <div className="text-sm text-light-gray space-y-1">
                <p><span className="text-accent-orange">Name:</span> {primaryFile.original_name}</p>
                <p><span className="text-accent-orange">Size:</span> {primaryFile.size_mb.toFixed(2)} MB</p>
                <p><span className="text-accent-orange">Duration:</span> {primaryFile.duration.toFixed(1)}s</p>
                <p><span className="text-accent-orange">Type:</span> {primaryFile.is_audio ? 'Audio' : 'Video'} ({primaryFile.format})</p>
              </div>
              <button
                onClick={clearPrimaryFile}
                className="mt-2 text-red-400 hover:text-red-300 text-sm flex items-center gap-1"
              >
                <X className="h-4 w-4" />
                Remove Primary File
              </button>
            </div>
          )}

          {/* Primary Upload Area */}
          <GlassCard
            opacity="medium"
            blur="lg"
            className="p-4 text-center flex flex-col items-center justify-center h-full w-full transition-all duration-300 ease-in-out border-dark-secondary/30"
          >
            <div className="flex items-center gap-2 mb-4">
              <Database className="h-5 w-5 text-accent-orange" />
              <h3 className="text-lg font-semibold text-light-gray">Primary Video/Audio</h3>
            </div>
            <p className="text-sm text-light-gray/70 mb-4">Knowledge Base</p>
            
            <div
              className={`w-full p-4 border-2 border-dashed rounded-lg transition-colors duration-300 ease-in-out flex-1 flex flex-col items-center justify-center ${
                isDragOverPrimary
                  ? "border-accent-orange bg-accent-orange/[0.1] shadow-inner-lg"
                  : "border-light-gray/[0.3] hover:border-accent-orange/50"
              }`}
              onDragOver={(e) => handleDragOver(e, true)}
              onDragLeave={() => handleDragLeave(true)}
              onDrop={(e) => handleDrop(e, true)}
            >
              <div className="flex justify-center items-center gap-3 mb-4">
                <FileAudio className="h-6 w-6 text-dark-secondary" />
                <Upload className="h-8 w-8 text-accent-orange" />
                <FileVideo className="h-6 w-6 text-dark-secondary" />
              </div>
              <p className="text-light-gray text-sm mb-4">
                <label htmlFor="primary-file-upload" className="cursor-pointer text-accent-orange font-semibold hover:underline">
                  Upload Primary File
                </label>{" "}
                or drag and drop here.
              </p>
              
              <input 
                id="primary-file-upload" 
                type="file" 
                className="hidden" 
                onChange={(e) => handleFileSelect(e, true)} 
                accept="audio/*,video/*" 
              />
              <GlassButton asChild className="mt-2 px-4 py-2 border-accent-orange/30 hover:bg-accent-orange/20 text-sm">
                <label htmlFor="primary-file-upload" className="cursor-pointer">
                  Select Primary File
                </label>
              </GlassButton>
            </div>
          </GlassCard>
        </div>

        {/* Secondary Column */}
        <div className="flex flex-col gap-4">
          {/* Secondary File Info */}
          {secondaryFile && !isUploading && (
            <div className="p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-blue-400" />
                <span className="text-blue-300 font-semibold">Secondary File Uploaded</span>
              </div>
              <div className="text-sm text-light-gray space-y-1">
                <p><span className="text-accent-orange">Name:</span> {secondaryFile.original_name}</p>
                <p><span className="text-accent-orange">Size:</span> {secondaryFile.size_mb.toFixed(2)} MB</p>
                <p><span className="text-accent-orange">Duration:</span> {secondaryFile.duration.toFixed(1)}s</p>
                <p><span className="text-accent-orange">Type:</span> {secondaryFile.is_audio ? 'Audio' : 'Video'} ({secondaryFile.format})</p>
              </div>
              <button
                onClick={clearSecondaryFile}
                className="mt-2 text-red-400 hover:text-red-300 text-sm flex items-center gap-1"
              >
                <X className="h-4 w-4" />
                Remove Secondary File
              </button>
            </div>
          )}

          {/* Secondary Upload Area */}
          <GlassCard
            opacity="medium"
            blur="lg"
            className="p-4 text-center flex flex-col items-center justify-center h-full w-full transition-all duration-300 ease-in-out border-dark-secondary/30"
          >
            <div className="flex items-center gap-2 mb-4">
              <Search className="h-5 w-5 text-accent-orange" />
              <h3 className="text-lg font-semibold text-light-gray">Secondary Video/Audio</h3>
            </div>
            <p className="text-sm text-light-gray/70 mb-4">Query Content</p>
            
            <div
              className={`w-full p-4 border-2 border-dashed rounded-lg transition-colors duration-300 ease-in-out flex-1 flex flex-col items-center justify-center ${
                isDragOverSecondary
                  ? "border-accent-orange bg-accent-orange/[0.1] shadow-inner-lg"
                  : "border-light-gray/[0.3] hover:border-accent-orange/50"
              }`}
              onDragOver={(e) => handleDragOver(e, false)}
              onDragLeave={() => handleDragLeave(false)}
              onDrop={(e) => handleDrop(e, false)}
            >
              <div className="flex justify-center items-center gap-3 mb-4">
                <FileAudio className="h-6 w-6 text-dark-secondary" />
                <Upload className="h-8 w-8 text-accent-orange" />
                <FileVideo className="h-6 w-6 text-dark-secondary" />
              </div>
              <p className="text-light-gray text-sm mb-4">
                <label htmlFor="secondary-file-upload" className="cursor-pointer text-accent-orange font-semibold hover:underline">
                  Upload Secondary File
                </label>{" "}
                or drag and drop here.
              </p>
              
              <input 
                id="secondary-file-upload" 
                type="file" 
                className="hidden" 
                onChange={(e) => handleFileSelect(e, false)} 
                accept="audio/*,video/*" 
              />
              <GlassButton asChild className="mt-2 px-4 py-2 border-accent-orange/30 hover:bg-accent-orange/20 text-sm">
                <label htmlFor="secondary-file-upload" className="cursor-pointer">
                  Select Secondary File
                </label>
              </GlassButton>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Supported Formats Info */}
      {supportedFormats && (
        <div className="text-xs text-light-gray/70 text-center">
          <p>Supported: {supportedFormats.audio_formats.join(', ')}</p>
          <p>Max size: {supportedFormats.max_file_size_mb}MB</p>
        </div>
      )}
    </div>
  )
}
