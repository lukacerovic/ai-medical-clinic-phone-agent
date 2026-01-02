from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class ServiceBase(BaseModel):
    """Base service model"""
    id: str
    name: str
    durationMinutes: int
    price: float
    description: str
    whatIsIncluded: str
    howItsDone: str
    specialPreparation: Optional[str] = None

class Service(ServiceBase):
    """Complete service model"""
    pass

class ServiceResponse(BaseModel):
    """Service response model"""
    services: List[Service]

class PatientInfo(BaseModel):
    """Patient information model"""
    name: str = Field(..., min_length=2, max_length=100)
    dateOfBirth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    medicalHistory: Optional[str] = None

class ReservationBase(BaseModel):
    """Base reservation model"""
    serviceId: str
    date: date
    time: str  # HH:MM format
    patientName: str
    patientDOB: date

class Reservation(ReservationBase):
    """Complete reservation model"""
    id: str
    status: str = "confirmed"  # confirmed, cancelled, completed
    createdAt: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

class ReservationResponse(BaseModel):
    """Reservation response model"""
    reservations: List[Reservation]

class AvailabilitySlot(BaseModel):
    """Available appointment slot"""
    date: date
    time: str  # HH:MM format
    serviceId: str
    available: bool

class AvailabilityResponse(BaseModel):
    """Availability response model"""
    slots: List[AvailabilitySlot]

class CallSessionStatus(str, Enum):
    """Call session status enum"""
    INITIATED = "initiated"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ENDED = "ended"
    ERROR = "error"

class CallSession(BaseModel):
    """Call session model"""
    sessionId: str
    status: CallSessionStatus
    startTime: datetime
    endTime: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    messageCount: int = 0
    conversationHistory: List[dict] = []

class AudioChunk(BaseModel):
    """Audio chunk model"""
    sessionId: str
    audio: bytes
    format: str = "wav"
    sampleRate: int = 16000

class TranscriptionResult(BaseModel):
    """Transcription result model"""
    text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    language: str = "en"
    duration: float  # seconds

class AIResponse(BaseModel):
    """AI agent response model"""
    text: str
    audio: bytes
    format: str = "wav"
    actionType: str = "respond"  # respond, book, lookup, escalate
    extractedInfo: Optional[dict] = None

class MessageLog(BaseModel):
    """Message log for conversation history"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    audioUrl: Optional[str] = None

class ConversationHistory(BaseModel):
    """Conversation history model"""
    sessionId: str
    messages: List[MessageLog]
    startTime: datetime
    endTime: Optional[datetime] = None

class EmergencyAlert(BaseModel):
    """Emergency alert model"""
    sessionId: str
    trigger: str  # keyword that triggered alert
    userText: str
    timestamp: datetime = Field(default_factory=datetime.now)
    escalated: bool = False

class CallStartRequest(BaseModel):
    """Request to start a call"""
    patientId: Optional[str] = None
    clinicId: Optional[str] = None

class CallStartResponse(BaseModel):
    """Response when starting a call"""
    sessionId: str
    status: str = "initialized"
    greeting: str

class CallEndRequest(BaseModel):
    """Request to end a call"""
    sessionId: str
    reason: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: int = 400

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
