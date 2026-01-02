import React, { useEffect, useRef } from 'react'
import '../styles/AudioVisualizer.css'

function AudioVisualizer({ level }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height

    // Clear canvas
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, width, height)

    // Draw waveform visualization
    ctx.fillStyle = '#2196F3'
    const barHeight = level * height
    ctx.fillRect(0, height - barHeight, width, barHeight)

    // Draw border
    ctx.strokeStyle = '#e0e0e0'
    ctx.lineWidth = 1
    ctx.strokeRect(0, 0, width, height)
  }, [level])

  return (
    <div className="audio-visualizer">
      <canvas 
        ref={canvasRef} 
        width={300} 
        height={80}
        className="visualizer-canvas"
      />
      <div className="visualizer-label">Audio Level</div>
    </div>
  )
}

export default AudioVisualizer
