import { cn } from "@/lib/utils"
import type React from "react"

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  opacity?: "low" | "medium" | "high"
  blur?: "sm" | "md" | "lg" | "xl"
  className?: string
}

export function GlassCard({ children, opacity = "medium", blur = "lg", className, ...props }: GlassCardProps) {
  const opacityClass = {
    low: "bg-light-gray/[0.15]",
    medium: "bg-light-gray/[0.25]",
    high: "bg-light-gray/[0.35]",
  }[opacity]

  const blurClass = {
    sm: "backdrop-blur-sm",
    md: "backdrop-blur-md",
    lg: "backdrop-blur-lg",
    xl: "backdrop-blur-xl",
  }[blur]

  return (
    <div
      className={cn("rounded-xl border border-light-gray/[0.2] shadow-xl", opacityClass, blurClass, className)}
      {...props}
    >
      {children}
    </div>
  )
}
