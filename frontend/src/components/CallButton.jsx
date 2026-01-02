import React from 'react'
import '../styles/CallButton.css'

function CallButton({ active, status, onStartCall, onEndCall }) {
  const getButtonText = () => {
    switch (status) {
      case 'connecting':
        return 'Connecting...'
      case 'listening':
        return 'Listening...'
      case 'speaking':
        return 'Speaking...'
      case 'processing':
        return 'Processing...'
      case 'ending':
        return 'Ending Call...'
      default:
        return 'Call Clinic'
    }
  }

  if (active) {
    return (
      <button 
        className="call-button end-call" 
        onClick={onEndCall}
        disabled={status === 'ending'}
      >
        <span className="call-icon">📞</span>
        <span className="call-text">End Call</span>
      </button>
    )
  }

  return (
    <button 
      className="call-button start-call" 
      onClick={onStartCall}
      disabled={status !== 'idle'}
    >
      <span className="call-icon">📞</span>
      <span className="call-text">{getButtonText()}</span>
    </button>
  )
}

export default CallButton
