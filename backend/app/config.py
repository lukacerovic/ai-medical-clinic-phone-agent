from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Model & API
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    
    # Audio Processing
    VAD_SILENCE_THRESHOLD: float = 1.5
    VAD_MIN_SPEECH_LENGTH: float = 0.5
    SAMPLE_RATE: int = 16000
    CHUNK_SIZE: int = 1024
    AUDIO_FORMAT: str = "PCM_16"
    
    # Server
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000"
    ]
    
    # Database
    SERVICES_JSON_PATH: str = "./app/data/services.json"
    RESERVATIONS_JSON_PATH: str = "./app/data/reservations.json"
    
    # TTS Provider
    TTS_PROVIDER: str = "gtts"  # gtts, elevenlabs, coqui
    
    # Medical Settings
    START_GREETING: str = "Good afternoon, welcome to Central Medical Clinic. How can I help you today?"
    CLINIC_NAME: str = "Central Medical Clinic"
    CLINIC_PHONE: str = "+1-800-CLINIC"
    CLINIC_EMAIL: str = "reception@clinic.example.com"
    
    # Session Settings
    SESSION_TIMEOUT: int = 600  # seconds
    MAX_CONCURRENT_CALLS: int = 10
    CONVERSATION_HISTORY_SIZE: int = 20
    
    # Whisper Settings
    WHISPER_MODEL: str = "base"
    WHISPER_LANGUAGE: str = "en"
    
    # Emergency Keywords
    EMERGENCY_KEYWORDS: List[str] = [
        "chest pain",
        "difficulty breathing",
        "severe bleeding",
        "loss of consciousness",
        "allergic reaction",
        "emergency",
        "911",
        "ambulance"
    ]
    
    # Logging
    LOG_FILE: str = "logs/clinic_agent.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Ensure required directories exist
Path("logs").mkdir(exist_ok=True)
Path("./app/data").mkdir(exist_ok=True)
Path("./uploads").mkdir(exist_ok=True)
