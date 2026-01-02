import os
import subprocess
import tempfile
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from gtts import gTTS
from loguru import logger
from app.config import settings
from app.audio.utils import convert_audio_array_to_bytes
import numpy as np

class TTSProvider(ABC):
    """
    Abstract base class for Text-to-Speech providers
    """
    
    @abstractmethod
    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
        
        Returns:
            Audio bytes (WAV format)
        """
        pass

class GTTSProvider(TTSProvider):
    """
    Google Text-to-Speech provider
    Free, good quality, natural-sounding voices
    """
    
    def __init__(self):
        """Initialize gTTS provider"""
        logger.info("Initializing gTTS provider")
    
    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize text using Google TTS
        
        Args:
            text: Text to synthesize
            language: Language code
        
        Returns:
            Audio bytes in WAV format
        """
        try:
            logger.info(f"Synthesizing text with gTTS (language={language}, length={len(text)})")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
                tts.save(temp_mp3.name)
                temp_mp3_path = temp_mp3.name
            
            # Convert MP3 to WAV using ffmpeg
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            # Use ffmpeg for conversion
            cmd = [
                'ffmpeg',
                '-i', temp_mp3_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                temp_wav_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg conversion failed: {result.stderr}")
                raise RuntimeError(f"FFmpeg conversion error: {result.stderr}")
            
            # Read WAV file
            with open(temp_wav_path, 'rb') as wav_file:
                audio_bytes = wav_file.read()
            
            # Clean up temp files
            os.unlink(temp_mp3_path)
            os.unlink(temp_wav_path)
            
            logger.info(f"TTS synthesis complete (audio size: {len(audio_bytes)} bytes)")
            return audio_bytes
        
        except Exception as e:
            logger.error(f"gTTS synthesis error: {e}")
            raise

class ElevenLabsProvider(TTSProvider):
    """
    ElevenLabs Text-to-Speech provider
    Premium quality, natural-sounding voices
    Requires API key
    """
    
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Initialize ElevenLabs provider
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        logger.info(f"Initializing ElevenLabs provider (voice_id={voice_id})")
    
    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize text using ElevenLabs
        
        Args:
            text: Text to synthesize
            language: Language code (used for model selection)
        
        Returns:
            Audio bytes in WAV format
        """
        try:
            import requests
            
            logger.info(f"Synthesizing with ElevenLabs (length={len(text)})")
            
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                raise RuntimeError(f"ElevenLabs API error: {response.status_code}")
            
            audio_bytes = response.content
            logger.info(f"ElevenLabs synthesis complete (audio size: {len(audio_bytes)} bytes)")
            return audio_bytes
        
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {e}")
            raise

class CoquiProvider(TTSProvider):
    """
    Coqui TTS provider
    Open-source, offline, natural-sounding
    """
    
    def __init__(self, model_name: str = "glow-tts"):
        """
        Initialize Coqui provider
        
        Args:
            model_name: Coqui model to use
        """
        try:
            from TTS.api import TTS
            self.tts = TTS(model_name=model_name, gpu=False)
            logger.info(f"Coqui TTS initialized with model: {model_name}")
        except ImportError:
            logger.error("Coqui TTS not installed. Install with: pip install TTS")
            raise
    
    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize text using Coqui
        
        Args:
            text: Text to synthesize
            language: Language code
        
        Returns:
            Audio bytes in WAV format
        """
        try:
            logger.info(f"Synthesizing with Coqui (language={language}, length={len(text)})")
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Synthesize
            self.tts.tts_to_file(text=text, file_path=output_path, language=language)
            
            # Read audio file
            with open(output_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Clean up
            os.unlink(output_path)
            
            logger.info(f"Coqui synthesis complete (audio size: {len(audio_bytes)} bytes)")
            return audio_bytes
        
        except Exception as e:
            logger.error(f"Coqui synthesis error: {e}")
            raise

class TextToSpeechEngine:
    """
    Text-to-Speech engine with multiple provider support
    """
    
    def __init__(self, provider: str = "gtts"):
        """
        Initialize TTS engine
        
        Args:
            provider: TTS provider to use (gtts, elevenlabs, coqui)
        """
        self.provider_name = provider
        self.provider = self._init_provider(provider)
        logger.info(f"TTS engine initialized with provider: {provider}")
    
    def _init_provider(self, provider: str) -> TTSProvider:
        """
        Initialize TTS provider
        
        Args:
            provider: Provider name
        
        Returns:
            Initialized provider instance
        """
        if provider.lower() == "gtts":
            return GTTSProvider()
        elif provider.lower() == "elevenlabs":
            if not settings.ELEVENLABS_API_KEY:
                logger.warning("ElevenLabs API key not set, falling back to gTTS")
                return GTTSProvider()
            return ElevenLabsProvider(
                api_key=settings.ELEVENLABS_API_KEY,
                voice_id=settings.ELEVENLABS_VOICE_ID
            )
        elif provider.lower() == "coqui":
            return CoquiProvider()
        else:
            logger.warning(f"Unknown provider {provider}, using gTTS")
            return GTTSProvider()
    
    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
        
        Returns:
            Audio bytes in WAV format
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return b''
        
        try:
            return self.provider.synthesize(text, language)
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            # Return empty audio on error
            return b''
    
    def synthesize_with_pauses(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize text with natural pauses
        
        Args:
            text: Text to synthesize
            language: Language code
        
        Returns:
            Audio bytes with pauses
        """
        # Split by sentence endings and add pauses
        sentences = text.split('. ')
        audio_chunks = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Add period back if removed
                if i < len(sentences) - 1:
                    sentence = sentence + '.'
                
                audio = self.synthesize(sentence, language)
                if audio:
                    audio_chunks.append(audio)
                    # Add short pause between sentences
                    if i < len(sentences) - 1:
                        from app.audio.utils import add_silence
                        pause = add_silence(duration_ms=300, sample_rate=16000)
                        audio_chunks.append(pause)
        
        if audio_chunks:
            # Concatenate all chunks
            combined = b''.join(audio_chunks)
            return combined
        
        return b''

# Global TTS engine instance
_tts_engine = None

def get_tts_engine() -> TextToSpeechEngine:
    """
    Get or create global TTS engine
    
    Returns:
        TextToSpeechEngine instance
    """
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TextToSpeechEngine(settings.TTS_PROVIDER)
    return _tts_engine
