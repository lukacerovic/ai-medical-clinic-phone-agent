import React from 'react'
import '../styles/CallStatus.css'

function CallStatus({ status, transcript, isActive }) {
  const getStatusMessage = () => {
    switch (status) {
      case 'connecting':
        return '📞 Connecting to clinic...'
      case 'listening':
        return '🎤 Listening... Speak naturally'
      case 'speaking':
        return '🔊 Speaking...'
      case 'processing':
        return '⏳ Processing your request...'
      case 'ending':
        return '👋 Thank you for calling. Goodbye!'
      default:
        return '☎️ Press "Call Clinic" to start'
    }
  }

  return (
    <div className={`call-status ${status}`}>
      <div className="status-message">
        {getStatusMessage()}
      </div>
      
      {isActive && status === 'listening' && (
        <div className="listening-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      )}
      
      {transcript && (
        <div className="transcript">
          <div className="transcript-label">You said:</div>
          <div className="transcript-text">{transcript}</div>
        </div>
      )}
    </div>
  )
}

export default CallStatus
