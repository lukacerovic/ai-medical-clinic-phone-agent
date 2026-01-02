import React, { useState, useEffect } from 'react'
import CallButton from './components/CallButton'
import CallStatus from './components/CallStatus'
import AudioVisualizer from './components/AudioVisualizer'
import './styles/App.css'

const DEBUG = import.meta.env.REACT_APP_DEBUG === 'true'
const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000'
const WS_URL = import.meta.env.REACT_APP_WS_URL || 'ws://localhost:8000'

function App() {
  const [callActive, setCallActive] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [callStatus, setCallStatus] = useState('idle')
  const [audioLevel, setAudioLevel] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState(null)

  // Request microphone access on mount
  useEffect(() => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          DEBUG && console.log('Microphone access granted')
          // Store stream for later use
          window.audioStream = stream
        })
        .catch(err => {
          console.error('Microphone access denied:', err)
          setError('Microphone access is required for this application')
        })
    } else {
      setError('Your browser does not support audio input')
    }
  }, [])

  const handleStartCall = async () => {
    try {
      setError(null)
      setCallStatus('connecting')
      DEBUG && console.log('Starting call...')

      // Initialize call session
      const response = await fetch(`${API_URL}/api/call/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to start call')
      }

      const data = await response.json()
      const newSessionId = data.sessionId
      setSessionId(newSessionId)

      DEBUG && console.log('Call session started:', newSessionId)
      DEBUG && console.log('Greeting:', data.greeting)

      // Play greeting audio
      setCallActive(true)
      setCallStatus('speaking')
      
      // Simulate playing greeting
      setTimeout(() => {
        setCallStatus('listening')
        startAudioCapture(newSessionId)
      }, 3000)

    } catch (err) {
      console.error('Error starting call:', err)
      setError(err.message)
      setCallStatus('idle')
    }
  }

  const handleEndCall = async () => {
    try {
      setCallStatus('ending')
      DEBUG && console.log('Ending call...')

      if (sessionId) {
        await fetch(`${API_URL}/api/call/end`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ session_id: sessionId }),
        })
      }

      setCallActive(false)
      setCallStatus('idle')
      setSessionId(null)
      setTranscript('')
      setAudioLevel(0)
      
      DEBUG && console.log('Call ended')
    } catch (err) {
      console.error('Error ending call:', err)
      setError(err.message)
    }
  }

  const startAudioCapture = (sid) => {
    if (!window.audioStream) {
      console.error('Audio stream not available')
      return
    }

    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(window.audioStream)
      source.connect(analyser)

      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      
      const checkAudioLevel = () => {
        if (!callActive) return
        
        analyser.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        setAudioLevel(average / 255) // Normalize to 0-1
        
        requestAnimationFrame(checkAudioLevel)
      }
      
      checkAudioLevel()
      DEBUG && console.log('Audio capture started')
    } catch (err) {
      console.error('Error starting audio capture:', err)
    }
  }

  return (
    <div className="app">
      <div className="clinic-header">
        <div className="clinic-logo">🏥</div>
        <h1>Central Medical Clinic</h1>
        <p>AI Phone Reception</p>
      </div>

      <div className="phone-interface">
        <div className="call-container">
          {error && (
            <div className="error-banner">
              ⚠️ {error}
            </div>
          )}

          <CallStatus 
            status={callStatus} 
            transcript={transcript}
            isActive={callActive}
          />

          {callActive && (
            <AudioVisualizer level={audioLevel} />
          )}

          <CallButton 
            active={callActive}
            status={callStatus}
            onStartCall={handleStartCall}
            onEndCall={handleEndCall}
          />
        </div>
      </div>

      <div className="clinic-footer">
        <p>📞 For emergencies, please call 911</p>
        <p className="disclaimer">
          This is an AI-powered virtual assistant. For medical emergencies, 
          please contact emergency services immediately.
        </p>
      </div>
    </div>
  )
}

export default App
