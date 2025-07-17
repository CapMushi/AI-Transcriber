"use client"

import { useState } from "react"
import { GlassCard } from "@/components/glass-card"
import { GlassButton } from "@/components/glass-button"
import { Play, Pause, RotateCcw, RotateCw, Volume2, VolumeX, Music } from "lucide-react"
import { Slider } from "@/components/ui/slider"

type PlaybackControlsProps = {}

export function PlaybackControls({}: PlaybackControlsProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(30) // Example progress 0-100
  const [volume, setVolume] = useState(70) // Example volume 0-100

  return (
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
          onClick={() => console.log("Rewind")}
          className="p-2 border-dark-secondary/30 hover:border-accent-orange/30"
        >
          <RotateCcw className="h-4 w-4 text-light-gray" />
        </GlassButton>
        <GlassButton
          size="lg"
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-3 border-accent-orange/30 hover:bg-accent-orange/20"
        >
          {isPlaying ? <Pause className="h-6 w-6 text-light-gray" /> : <Play className="h-6 w-6 text-light-gray" />}
        </GlassButton>
        <GlassButton
          size="icon"
          onClick={() => console.log("Fast-forward")}
          className="p-2 border-dark-secondary/30 hover:border-accent-orange/30"
        >
          <RotateCw className="h-4 w-4 text-light-gray" />
        </GlassButton>
      </div>

      <div className="flex items-center gap-3 w-full">
        <span className="text-light-gray text-xs min-w-[35px] font-mono">0:30</span>
        <Slider
          value={[progress]}
          max={100}
          step={1}
          onValueChange={(val) => setProgress(val[0])}
          className="w-full [&>span:first-child]:bg-dark-secondary/[0.5] [&>span>span]:bg-accent-orange [&>span>span]:shadow-lg [&>span>span]:border [&>span>span]:border-accent-orange/[0.3]"
        />
        <span className="text-light-gray text-xs min-w-[35px] font-mono">1:45</span>
      </div>

      <div className="flex items-center gap-2 w-full">
        {volume === 0 ? (
          <VolumeX className="h-4 w-4 text-light-gray" />
        ) : (
          <Volume2 className="h-4 w-4 text-light-gray" />
        )}
        <Slider
          value={[volume]}
          max={100}
          step={1}
          onValueChange={(val) => setVolume(val[0])}
          className="w-full max-w-[150px] [&>span:first-child]:bg-dark-secondary/[0.5] [&>span>span]:bg-accent-orange [&>span>span]:shadow-lg [&>span>span]:border [&>span>span]:border-accent-orange/[0.3]"
        />
        <span className="text-light-gray text-xs min-w-[30px] font-mono">{volume}%</span>
      </div>
    </GlassCard>
  )
}
