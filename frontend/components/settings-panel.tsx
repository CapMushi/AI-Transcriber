"use client"

import { useState } from "react"
import { GlassCard } from "@/components/glass-card"
import { ChevronLeft, ChevronRight, Settings, Brain, Target, Globe } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

export function SettingsPanel() {
  const [isOpen, setIsOpen] = useState(false)
  const [confidenceThreshold, setConfidenceThreshold] = useState(75)
  const [translationEnabled, setTranslationEnabled] = useState(false)
  const [selectedModel, setSelectedModel] = useState("tiny")

  return (
    <div
      className={cn(
        "fixed right-0 top-0 h-full z-40 transition-all duration-300 ease-in-out",
        isOpen ? "w-96" : "w-20",
      )}
    >
      <GlassCard
        opacity="medium"
        blur="lg"
        className={cn(
          "h-full p-6 flex flex-col gap-8 transition-all duration-300 ease-in-out",
          isOpen ? "rounded-l-xl rounded-r-none" : "rounded-xl items-center justify-center",
        )}
      >
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="absolute top-1/2 -left-5 -translate-y-1/2 p-3 rounded-full bg-gray-light/[0.2] border border-gray-light/[0.3] shadow-lg text-gray-light hover:bg-gray-light/[0.3] transition-all duration-200 z-50 group"
          aria-label={isOpen ? "Collapse settings" : "Expand settings"}
        >
          {isOpen ? (
            <ChevronRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          ) : (
            <ChevronLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
          )}
        </button>

        {!isOpen && (
          <div className="flex flex-col items-center gap-4">
            xt-sm font-medium transform -rotate-90 whitespace-nowrap">Set items-center gap-3 mb-4">
              <div className="p-2 rounded-full bg-red-bright/20">
                <Settings className="h-5 w-5 text-red-bright" />
              </div>
              <h2 className="text-xl font-semibold text-gray-light">Settings</h2>
            </div>

            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-red-bright" />
                <Label htmlFor="model-select" className="text-gray-light font-medium">
                  AI Model
                </Label>
              </div>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger
                  id="model-select"
                  className="bg-gray-light/[0.15] border-gray-light/[0.3] text-gray-light placeholder:text-gray-light/[0.7] focus:ring-red-bright focus:ring-offset-transparent"
                >
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent className="bg-dark-brown/[0.95] backdrop-blur-md border-gray-light/[0.3] text-gray-light">
                  <SelectItem value="tiny" className="hover:bg-gray-light/[0.15] focus:bg-gray-light/[0.15]">
                    Tiny
                  </SelectItem>
                  <SelectItem value="base" className="hover:bg-gray-light/[0.15] focus:bg-gray-light/[0.15]">
                    Base
                  </SelectItem>
                  <SelectItem value="small" className="hover:bg-gray-light/[0.15] focus:bg-gray-light/[0.15]">
                    Small
                  </SelectItem>
                  <SelectItem value="medium" className="hover:bg-gray-light/[0.15] focus:bg-gray-light/[0.15]">
                    Medium
                  </SelectItem>
                  <SelectItem value="large" className="hover:bg-gray-light/[0.15] focus:bg-gray-light/[0.15]">
                    Large
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-4 w-4 text-red-bright" />
                <Label htmlFor="confidence-slider" className="text-gray-light font-medium">
                  Confidence Threshold: {confidenceThreshold}%
                </Label>
              </div>
              <Slider
                id="confidence-slider"
                value={[confidenceThreshold]}
                max={100}
                step={1}
                onValueChange={(val) => setConfidenceThreshold(val[0])}
                className="w-full [&>span:first-child]:bg-gray-light/[0.2] [&>span>span]:bg-red-bright [&>span>span]:shadow-lg [&>span>span]:border [&>span>span]:border-gray-light/[0.3]"
              />
            </div>

            <div className="flex items-center justify-between gap-3 p-4 rounded-lg bg-gray-light/[0.05] border border-gray-light/[0.1]">
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-red-bright" />
                <Label htmlFor="translation-switch" className="text-gray-light font-medium">
                  Enable Translation
                </Label>
              </div>
              <Switch
                id="translation-switch"
                checked={translationEnabled}
                onCheckedChange={setTranslationEnabled}
                className="data-[state=checked]:bg-red-bright data-[state=unchecked]:bg-gray-light/[0.2] [&>span]:bg-gray-light/[0.8] [&>span]:data-[state=checked]:bg-gray-light"
              />
            </div>
          </>
        )}
      </GlassCard>
    </div>
  )
}
