import whisper
import numpy as np
from typing import Optional, Dict, Any
from app.audio.utils import convert_bytes_to_audio_array, get_audio_duration
from app.config import settings
from loguru import logger

class SpeechToTextEngine:
    """
    Speech-to-Text engine using OpenAI Whisper
    Transcribes audio to text with confidence scores
    """
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper STT engine
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        logger.info(f"Loading Whisper model: {model_name}")
        try:
            self.model = whisper.load_model(model_name)
            logger.info(f"Whisper model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio bytes
            language: Language code (e.g., 'en', 'es', 'fr')
            format: Audio format (wav, pcm, mp3)
        
        Returns:
            Dictionary with transcription results
        """
        try:
            # Convert bytes to audio array
            audio_array, sample_rate = convert_bytes_to_audio_array(
                audio_data,
                format=format
            )
            
            # Normalize audio
            if np.max(np.abs(audio_array)) > 0:
                audio_array = audio_array.astype(np.float32) / 32768.0
            
            logger.info(f"Transcribing audio (sample_rate={sample_rate}, duration={get_audio_duration(audio_array, sample_rate):.2f}s)")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_array,
                language=language,
                fp16=False  # Use fp32 for CPU
            )
            
            # Extract results
            text = result["text"].strip()
            confidence = self._calculate_confidence(result)
            detected_language = result.get("language", language)
            
            logger.info(f"Transcription: '{text}' (confidence: {confidence:.2f}, language: {detected_language})")
            
            return {
                "text": text,
                "confidence": confidence,
                "language": detected_language,
                "duration": get_audio_duration(audio_array, sample_rate),
                "segments": result.get("segments", [])
            }
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "duration": 0.0,
                "error": str(e)
            }
    
    def transcribe_stream(
        self,
        audio_stream,
        language: str = "en",
        format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio stream
        
        Args:
            audio_stream: Audio stream or file path
            language: Language code
            format: Audio format
        
        Returns:
            Transcription results
        """
        try:
            logger.info(f"Transcribing audio stream (language={language})")
            
            result = self.model.transcribe(
                audio_stream,
                language=language,
                fp16=False
            )
            
            text = result["text"].strip()
            confidence = self._calculate_confidence(result)
            
            return {
                "text": text,
                "confidence": confidence,
                "language": result.get("language", language),
                "segments": result.get("segments", [])
            }
        
        except Exception as e:
            logger.error(f"Stream transcription error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate overall confidence from transcription result
        
        Args:
            result: Whisper transcription result
        
        Returns:
            Confidence score between 0 and 1
        """
        segments = result.get("segments", [])
        
        if not segments:
            return 0.0
        
        # Average confidence from segment probabilities
        confidences = []
        for segment in segments:
            if "confidence" in segment:
                confidences.append(segment["confidence"])
            elif "no_speech_prob" in segment:
                # Calculate from no_speech probability
                no_speech_prob = segment["no_speech_prob"]
                confidences.append(1.0 - no_speech_prob)
        
        if confidences:
            return np.mean(confidences)
        
        return 0.8  # Default confidence
    
    def detect_language(self, audio_data: bytes) -> str:
        """
        Detect language of audio
        
        Args:
            audio_data: Audio bytes
        
        Returns:
            Language code
        """
        try:
            audio_array, sample_rate = convert_bytes_to_audio_array(audio_data)
            
            if np.max(np.abs(audio_array)) > 0:
                audio_array = audio_array.astype(np.float32) / 32768.0
            
            # Get language from first few seconds
            result = self.model.transcribe(audio_array[:sample_rate * 5])
            language = result.get("language", "en")
            
            logger.info(f"Detected language: {language}")
            return language
        
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en"  # Default to English

class SpeechSegment:
    """
    Represents a speech segment with metadata
    """
    
    def __init__(
        self,
        text: str,
        confidence: float,
        start_time: float,
        end_time: float,
        speaker_id: Optional[int] = None
    ):
        self.text = text
        self.confidence = confidence
        self.start_time = start_time
        self.end_time = end_time
        self.speaker_id = speaker_id
        self.duration = end_time - start_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "speaker_id": self.speaker_id
        }

# Global STT engine instance
_stt_engine = None

def get_stt_engine() -> SpeechToTextEngine:
    """
    Get or create global STT engine
    
    Returns:
        SpeechToTextEngine instance
    """
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = SpeechToTextEngine(settings.WHISPER_MODEL)
    return _stt_engine
