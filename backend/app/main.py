from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import json
import uuid
from datetime import datetime
from loguru import logger

from app.config import settings
from app.models.schemas import (
    CallStartResponse, HealthCheckResponse, ErrorResponse,
    CallSession, CallSessionStatus
)
from app.audio.speech_to_text import get_stt_engine
from app.audio.text_to_speech import get_tts_engine
from app.audio.vad import VoiceActivityDetector

# Configure logging
logger.add(
    settings.LOG_FILE,
    rotation=f"{settings.LOG_MAX_BYTES} bytes",
    retention=settings.LOG_BACKUP_COUNT,
    level=settings.LOG_LEVEL
)

# Session management
active_sessions = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager
    Runs on startup and shutdown
    """
    # Startup
    logger.info("="*50)
    logger.info("🏥 Medical Clinic Phone Agent - Starting Up")
    logger.info(f"Configuration: {settings.DEBUG=}, {settings.LOG_LEVEL=}")
    logger.info(f"TTS Provider: {settings.TTS_PROVIDER}")
    logger.info(f"STT Model: {settings.WHISPER_MODEL}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    logger.info("="*50)
    
    # Pre-load engines
    try:
        logger.info("Pre-loading TTS engine...")
        get_tts_engine()
        logger.info("✓ TTS engine loaded")
    except Exception as e:
        logger.warning(f"TTS pre-load failed: {e}")
    
    try:
        logger.info("Pre-loading STT engine...")
        get_stt_engine()
        logger.info("✓ STT engine loaded")
    except Exception as e:
        logger.warning(f"STT pre-load failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    logger.info(f"Active sessions: {len(active_sessions)}")
    # Clean up sessions
    for session_id in list(active_sessions.keys()):
        await cleanup_session(session_id)
    logger.info("✓ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Medical Clinic Phone Agent API",
    description="AI-powered phone call agent for medical clinic reception",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= REST ENDPOINTS =============

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

@app.post("/api/call/start", response_model=CallStartResponse)
async def start_call():
    """
    Initialize a new call session
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Create new session
        session = CallSession(
            sessionId=session_id,
            status=CallSessionStatus.INITIATED,
            startTime=datetime.utcnow(),
            messageCount=0,
            conversationHistory=[]
        )
        
        active_sessions[session_id] = {
            "session": session,
            "vad": VoiceActivityDetector(
                sample_rate=settings.SAMPLE_RATE,
                silence_threshold=settings.VAD_SILENCE_THRESHOLD,
                min_speech_length=settings.VAD_MIN_SPEECH_LENGTH
            )
        }
        
        logger.info(f"✓ Call session started: {session_id}")
        
        # Generate greeting audio
        tts = get_tts_engine()
        greeting_audio = tts.synthesize(settings.START_GREETING)
        
        return CallStartResponse(
            sessionId=session_id,
            status="initialized",
            greeting=settings.START_GREETING
        )
    
    except Exception as e:
        logger.error(f"Error starting call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/call/end")
async def end_call(session_id: str):
    """
    End a call session
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await cleanup_session(session_id)
        logger.info(f"✓ Call session ended: {session_id}")
        
        return {"status": "ended", "sessionId": session_id}
    
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/services")
async def get_services():
    """
    Get list of available services
    """
    try:
        import json
        with open(settings.SERVICES_JSON_PATH, 'r') as f:
            services = json.load(f)
        return {"services": services}
    except Exception as e:
        logger.error(f"Error loading services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations")
async def get_reservations(session_id: str = None):
    """
    Get list of reservations
    """
    try:
        import json
        with open(settings.RESERVATIONS_JSON_PATH, 'r') as f:
            reservations = json.load(f)
        return {"reservations": reservations}
    except Exception as e:
        logger.error(f"Error loading reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= WEBSOCKET ENDPOINT =============

@app.websocket("/ws/call/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for voice call communication
    Handles real-time audio streaming and conversation
    """
    try:
        # Validate session
        if session_id not in active_sessions:
            await websocket.close(code=4000, reason="Session not found")
            return
        
        await websocket.accept()
        logger.info(f"📞 WebSocket connected: {session_id}")
        
        session_data = active_sessions[session_id]
        vad = session_data["vad"]
        stt = get_stt_engine()
        tts = get_tts_engine()
        
        # Main conversation loop
        while True:
            try:
                # Receive audio chunk from client
                data = await websocket.receive_bytes()
                
                if not data:
                    continue
                
                # Process audio with VAD
                vad.process_frame(data)
                
                # Check if speech has ended
                if vad.has_speech_ended():
                    logger.debug("Speech ended, processing...")
                    
                    # Transcribe audio
                    transcription = stt.transcribe(data)
                    user_text = transcription.get("text", "").strip()
                    
                    if not user_text:
                        logger.warning("No transcription result")
                        continue
                    
                    logger.info(f"User: {user_text}")
                    
                    # TODO: Send to CrewAI for processing
                    # For now, send a simple echo response
                    response_text = f"You said: {user_text}. How can I help further?"
                    
                    # Synthesize response
                    response_audio = tts.synthesize(response_text)
                    
                    # Send response audio to client
                    await websocket.send_bytes(response_audio)
                    logger.info(f"Assistant: {response_text}")
                    
                    # Reset VAD for next utterance
                    vad.reset()
            
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {session_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({"error": str(e)})
                break
    
    finally:
        await cleanup_session(session_id)

# ============= UTILITY FUNCTIONS =============

async def cleanup_session(session_id: str):
    """
    Clean up session resources
    """
    if session_id in active_sessions:
        session_data = active_sessions[session_id]
        session = session_data["session"]
        
        # Update session end time
        session.endTime = datetime.utcnow()
        session.status = CallSessionStatus.ENDED
        
        logger.info(
            f"Session {session_id} ended. "
            f"Duration: {(session.endTime - session.startTime).total_seconds():.2f}s, "
            f"Messages: {session.messageCount}"
        )
        
        del active_sessions[session_id]

# ============= ERROR HANDLERS =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

# ============= STARTUP/SHUTDOWN =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
