import numpy as np
import webrtcvad
import collections
from typing import Iterator, Tuple
from app.config import settings

class VoiceActivityDetector:
    """
    Voice Activity Detection using WebRTC VAD algorithm
    Detects when user stops speaking based on silence threshold
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        silence_threshold: float = 1.5,
        min_speech_length: float = 0.5
    ):
        """
        Initialize VAD
        
        Args:
            sample_rate: Audio sample rate (8000, 16000, 32000, 48000)
            silence_threshold: Silence duration before considering speech ended (seconds)
            min_speech_length: Minimum speech duration to consider valid (seconds)
        """
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.min_speech_length = min_speech_length
        
        # Initialize WebRTC VAD
        self.vad = webrtcvad.VAD()
        self.vad.set_aggressiveness(2)  # 0-3, higher = more aggressive
        
        # Frame size in samples (20ms frames for WebRTC)
        self.frame_size = int(self.sample_rate * 0.02)
        
        # Silence detection state
        self.silence_frames = 0
        self.speech_frames = 0
        self.in_speech = False
        self.speech_started = False
        
        # Streaming buffer
        self.ring_buffer = collections.deque(maxlen=self.get_frames_for_duration(silence_threshold))
    
    def get_frames_for_duration(self, duration_seconds: float) -> int:
        """
        Calculate number of frames for given duration
        
        Args:
            duration_seconds: Duration in seconds
        
        Returns:
            Number of frames
        """
        return int((duration_seconds * self.sample_rate) / self.frame_size)
    
    def is_speech(self, frame: bytes) -> bool:
        """
        Detect if frame contains speech
        
        Args:
            frame: Audio frame as bytes
        
        Returns:
            True if speech detected, False otherwise
        """
        try:
            return self.vad.is_speech(frame, self.sample_rate)
        except Exception as e:
            print(f"VAD detection error: {e}")
            return False
    
    def process_frame(self, frame: bytes) -> bool:
        """
        Process single audio frame and detect speech
        
        Args:
            frame: Audio frame as bytes
        
        Returns:
            True if speech detected in this frame
        """
        speech_detected = self.is_speech(frame)
        self.ring_buffer.append(speech_detected)
        
        # Track speech and silence
        if speech_detected:
            self.silence_frames = 0
            self.speech_frames += 1
            if not self.in_speech and self.speech_frames > 3:  # Debounce
                self.in_speech = True
                self.speech_started = True
        else:
            self.silence_frames += 1
            self.speech_frames = 0
        
        return speech_detected
    
    def has_speech_ended(self) -> bool:
        """
        Detect if user has finished speaking (silence threshold exceeded)
        
        Returns:
            True if speech has ended (silence detected)
        """
        silence_duration_frames = self.get_frames_for_duration(self.silence_threshold)
        
        # Check if enough silence has been detected
        if self.in_speech and self.silence_frames > silence_duration_frames:
            # Also check minimum speech length was met
            min_speech_frames = self.get_frames_for_duration(self.min_speech_length)
            if self.speech_frames > min_speech_frames or self.speech_started:
                return True
        
        return False
    
    def reset(self):
        """
        Reset VAD state for next speech segment
        """
        self.silence_frames = 0
        self.speech_frames = 0
        self.in_speech = False
        self.speech_started = False
        self.ring_buffer.clear()
    
    def get_speech_probability(self) -> float:
        """
        Get probability that current buffer contains speech
        
        Returns:
            Probability between 0.0 and 1.0
        """
        if not self.ring_buffer:
            return 0.0
        
        speech_count = sum(self.ring_buffer)
        return speech_count / len(self.ring_buffer)

class AudioFrameProcessor:
    """
    Process audio stream and yield frames
    Handles VAD-based chunking
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration_ms: int = 20
    ):
        """
        Initialize audio frame processor
        
        Args:
            sample_rate: Sample rate in Hz
            chunk_duration_ms: Duration of each frame in milliseconds
        """
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.chunk_size = int((chunk_duration_ms / 1000) * sample_rate * 2)  # 2 bytes per sample
        self.vad = VoiceActivityDetector(
            sample_rate=sample_rate,
            silence_threshold=settings.VAD_SILENCE_THRESHOLD,
            min_speech_length=settings.VAD_MIN_SPEECH_LENGTH
        )
    
    def process_audio_stream(self, audio_stream: Iterator[bytes]) -> Iterator[Tuple[bytes, bool]]:
        """
        Process audio stream with VAD
        
        Args:
            audio_stream: Iterator of audio frames
        
        Yields:
            Tuples of (frame, speech_detected)
        """
        for frame in audio_stream:
            if len(frame) < self.chunk_size:
                continue
            
            speech_detected = self.vad.process_frame(frame)
            yield frame, speech_detected
            
            if self.vad.has_speech_ended():
                break
    
    def extract_speech_frames(self, audio_stream: Iterator[bytes]) -> bytes:
        """
        Extract and concatenate frames containing speech
        
        Args:
            audio_stream: Iterator of audio frames
        
        Yields:
            Concatenated speech audio
        """
        self.vad.reset()
        speech_frames = []
        
        for frame, speech_detected in self.process_audio_stream(audio_stream):
            if speech_detected or self.vad.in_speech:
                speech_frames.append(frame)
        
        if speech_frames:
            return b''.join(speech_frames)
        return b''

def numpy_to_vad_frame(audio_array: np.ndarray, sample_rate: int = 16000) -> bytes:
    """
    Convert numpy array to VAD frame format
    
    Args:
        audio_array: Numpy audio array
        sample_rate: Sample rate in Hz
    
    Returns:
        Audio as bytes (16-bit PCM)
    """
    if audio_array.dtype != np.int16:
        audio_array = (audio_array * 32767).astype(np.int16)
    return audio_array.tobytes()
