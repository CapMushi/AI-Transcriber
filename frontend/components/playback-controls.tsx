"use client"

import { useState, useRef } from "react"
import { GlassCard } from "@/components/glass-card"
import { GlassButton } from "@/components/glass-button"
import { Play, Pause, RotateCcw, RotateCw, Volume2, VolumeX, Music } from "lucide-react"
import { Slider } from "@/components/ui/slider"
import { useWhisperContext } from "@/contexts/whisper-context"
import { useAudioPlayer } from "@/hooks/use-audio-player"

type PlaybackControlsProps = {}

// Helper function to format time
function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds === 0) return "0:00"
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function PlaybackControls({}: PlaybackControlsProps) {
  const { audioUrl } = useWhisperContext()
  const {
    audioRef,
    isPlaying,
    currentTime,
    duration,
    volume,
    play,
    pause,
    seek,
    setVolume
  } = useAudioPlayer(audioUrl)

  return (
    <>
      {/* Hidden audio element */}
      <audio ref={audioRef} />
      
      <GlassCard opacity="medium" blur="lg" className="p-4 w-full flex flex-col gap-3 border-dark-secondary/30">
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1 rounded-full bg-accent-orange/20 border border-accent-orange/30">
          <Music className="h-4 w-4 text-accent-orange" />
        </div>
        <h3 className="text-base font-semibold text-light-gray">Playback Controls</h3>
      </div>

      <div className="flex items-center justify-center gap-4">
        <GlassButton
          size="icon"
          onClick={() => seek(Math.max(0, currentTime - 10))}
          className="p-2 border-dark-secondary/30 hover:border-accent-orange/30"
          disabled={!audioUrl}
        >
          <RotateCcw className="h-4 w-4 text-light-gray" />
        </GlassButton>
        <GlassButton
          size="lg"
          onClick={isPlaying ? pause : play}
          className="p-3 border-accent-orange/30 hover:bg-accent-orange/20"
          disabled={!audioUrl}
        >
          {isPlaying ? <Pause className="h-6 w-6 text-light-gray" /> : <Play className="h-6 w-6 text-light-gray" />}
        </GlassButton>
        <GlassButton
          size="icon"
          onClick={() => seek(Math.min(duration, currentTime + 10))}
          className="p-2 border-dark-secondary/30 hover:border-accent-orange/30"
          disabled={!audioUrl}
        >
          <RotateCw className="h-4 w-4 text-light-gray" />
        </GlassButton>
      </div>

      <div className="flex items-center gap-3 w-full">
        <span className="text-light-gray text-xs min-w-[35px] font-mono">
          {audioUrl ? formatTime(currentTime) : "0:00"}
        </span>
        <Slider
          value={[audioUrl ? (currentTime / duration) * 100 : 0]}
          max={100}
          step={1}
          onValueChange={(val) => {
            if (audioUrl && duration > 0) {
              const newTime = (val[0] / 100) * duration
              seek(newTime)
            }
          }}
          disabled={!audioUrl}
          className="w-full [&>span:first-child]:bg-dark-secondary/[0.5] [&>span>span]:bg-accent-orange [&>span>span]:shadow-lg [&>span>span]:border [&>span>span]:border-accent-orange/[0.3]"
        />
        <span className="text-light-gray text-xs min-w-[35px] font-mono">
          {audioUrl ? formatTime(duration) : "0:00"}
        </span>
      </div>

      <div className="flex items-center gap-2 w-full">
        {volume === 0 ? (
          <VolumeX className="h-4 w-4 text-light-gray" />
        ) : (
          <Volume2 className="h-4 w-4 text-light-gray" />
        )}
        <Slider
          value={[volume * 100]}
          max={100}
          step={1}
          onValueChange={(val) => setVolume(val[0] / 100)}
          disabled={!audioUrl}
          className="w-full max-w-[150px] [&>span:first-child]:bg-dark-secondary/[0.5] [&>span>span]:bg-accent-orange [&>span>span]:shadow-lg [&>span>span]:border [&>span>span]:border-accent-orange/[0.3]"
        />
        <span className="text-light-gray text-xs min-w-[30px] font-mono">
          {audioUrl ? Math.round(volume * 100) : 0}%
        </span>
      </div>
    </GlassCard>
    </>
  )
}
