import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import type React from "react"

interface GlassButtonProps extends React.ComponentPropsWithoutRef<typeof Button> {
  children: React.ReactNode
  className?: string
}

export function GlassButton({ children, className, ...props }: GlassButtonProps) {
  return (
    <Button
      className={cn(
        "relative overflow-hidden rounded-lg border border-light-gray/[0.3] bg-light-gray/[0.2] text-light-gray shadow-lg backdrop-blur-md transition-all duration-300",
        "hover:bg-light-gray/[0.3] hover:border-light-gray/[0.4] hover:shadow-2xl",
        "active:bg-light-gray/[0.15] active:border-light-gray/[0.2] active:shadow-inner",
        "focus-visible:ring-2 focus-visible:ring-accent-orange focus-visible:ring-offset-2 focus-visible:ring-offset-transparent",
        className,
      )}
      {...props}
    >
      {children}
    </Button>
  )
}
