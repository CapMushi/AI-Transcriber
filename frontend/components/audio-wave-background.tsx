"use client"

import { useEffect, useRef } from "react"

export function AudioWaveBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    let animationId: number
    let time = 0

    const drawWaves = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Set up gradient for wave lines
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0)
      gradient.addColorStop(0, "rgba(45, 64, 89, 0.3)")
      gradient.addColorStop(0.5, "rgba(255, 87, 34, 0.4)")
      gradient.addColorStop(1, "rgba(45, 64, 89, 0.3)")

      ctx.strokeStyle = gradient
      ctx.lineWidth = 2
      ctx.lineCap = "round"

      // Draw multiple wave lines
      const waves = [
        { amplitude: 30, frequency: 0.02, phase: 0, yOffset: canvas.height * 0.2 },
        { amplitude: 40, frequency: 0.015, phase: Math.PI / 3, yOffset: canvas.height * 0.4 },
        { amplitude: 25, frequency: 0.025, phase: Math.PI / 2, yOffset: canvas.height * 0.6 },
        { amplitude: 35, frequency: 0.018, phase: Math.PI, yOffset: canvas.height * 0.8 },
      ]

      waves.forEach((wave, index) => {
        ctx.beginPath()
        ctx.globalAlpha = 0.6 - index * 0.1

        for (let x = 0; x < canvas.width; x += 2) {
          const y = wave.yOffset + Math.sin(x * wave.frequency + time + wave.phase) * wave.amplitude
          if (x === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        }
        ctx.stroke()
      })

      // Draw additional subtle vertical lines
      ctx.globalAlpha = 0.1
      ctx.strokeStyle = "rgba(255, 87, 34, 0.3)"
      ctx.lineWidth = 1

      for (let i = 0; i < 20; i++) {
        const x = (canvas.width / 20) * i + Math.sin(time * 0.01 + i) * 10
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }

      time += 0.02
      animationId = requestAnimationFrame(drawWaves)
    }

    drawWaves()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 z-0 pointer-events-none"
      style={{ background: "transparent" }}
    />
  )
}
