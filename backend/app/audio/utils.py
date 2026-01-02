import io
import wave
import numpy as np
from typing import Tuple
import subprocess
import os
from app.config import settings

def convert_bytes_to_audio_array(
    audio_bytes: bytes,
    sample_rate: int = 16000,
    format: str = "wav"
) -> Tuple[np.ndarray, int]:
    """
    Convert bytes to numpy audio array
    
    Args:
        audio_bytes: Audio data as bytes
        sample_rate: Sample rate in Hz
        format: Audio format (wav, pcm, etc)
    
    Returns:
        Tuple of (audio_array, sample_rate)
    """
    try:
        if format == "wav":
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
                sample_rate = wav_file.getframerate()
                return audio_array, sample_rate
        elif format == "pcm":
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            return audio_array, sample_rate
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        print(f"Error converting audio: {e}")
        raise

def convert_audio_array_to_bytes(
    audio_array: np.ndarray,
    sample_rate: int = 16000,
    format: str = "wav"
) -> bytes:
    """
    Convert numpy audio array to bytes
    
    Args:
        audio_array: Numpy audio array
        sample_rate: Sample rate in Hz
        format: Output format (wav, pcm, etc)
    
    Returns:
        Audio data as bytes
    """
    try:
        if format == "wav":
            output = io.BytesIO()
            with wave.open(output, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_array.astype(np.int16).tobytes())
            return output.getvalue()
        elif format == "pcm":
            return audio_array.astype(np.int16).tobytes()
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        print(f"Error converting audio array: {e}")
        raise

def normalize_audio(audio_array: np.ndarray, target_level: float = -20.0) -> np.ndarray:
    """
    Normalize audio to target level in dB
    
    Args:
        audio_array: Input audio array
        target_level: Target level in dB
    
    Returns:
        Normalized audio array
    """
    # Calculate RMS
    rms = np.sqrt(np.mean(audio_array**2))
    
    if rms == 0:
        return audio_array
    
    # Convert target level from dB to linear
    target_linear = 10 ** (target_level / 20.0)
    
    # Calculate scaling factor
    scale = target_linear / rms
    
    # Apply with clipping
    normalized = np.clip(audio_array * scale, -32768, 32767)
    
    return normalized

def resample_audio(
    audio_array: np.ndarray,
    orig_sr: int,
    target_sr: int
) -> np.ndarray:
    """
    Resample audio to target sample rate using ffmpeg
    
    Args:
        audio_array: Input audio array
        orig_sr: Original sample rate
        target_sr: Target sample rate
    
    Returns:
        Resampled audio array
    """
    if orig_sr == target_sr:
        return audio_array
    
    try:
        import librosa
        return librosa.resample(audio_array, orig_sr=orig_sr, target_sr=target_sr)
    except ImportError:
        # Fallback: simple nearest-neighbor resampling
        ratio = target_sr / orig_sr
        indices = np.arange(0, len(audio_array), 1/ratio).astype(int)
        indices = np.clip(indices, 0, len(audio_array) - 1)
        return audio_array[indices]

def apply_ffmpeg_processing(
    input_path: str,
    output_path: str,
    filters: str = None
) -> bool:
    """
    Apply ffmpeg audio processing
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        filters: FFmpeg filter string
    
    Returns:
        Success status
    """
    try:
        cmd = ['ffmpeg', '-i', input_path, '-y']
        
        if filters:
            cmd.extend(['-af', filters])
        
        cmd.extend(['-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', output_path])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"FFmpeg processing error: {e}")
        return False

def add_silence(duration_ms: float = 500, sample_rate: int = 16000) -> np.ndarray:
    """
    Generate silence audio
    
    Args:
        duration_ms: Duration in milliseconds
        sample_rate: Sample rate in Hz
    
    Returns:
        Silence audio array
    """
    samples = int((duration_ms / 1000) * sample_rate)
    return np.zeros(samples, dtype=np.int16)

def concatenate_audio(*audio_arrays: np.ndarray) -> np.ndarray:
    """
    Concatenate multiple audio arrays
    
    Args:
        *audio_arrays: Variable number of audio arrays
    
    Returns:
        Concatenated audio array
    """
    return np.concatenate(audio_arrays)

def get_audio_duration(audio_array: np.ndarray, sample_rate: int = 16000) -> float:
    """
    Get duration of audio array in seconds
    
    Args:
        audio_array: Input audio array
        sample_rate: Sample rate in Hz
    
    Returns:
        Duration in seconds
    """
    return len(audio_array) / sample_rate

def detect_clipping(audio_array: np.ndarray, threshold: float = 0.95) -> bool:
    """
    Detect if audio is clipping (distortion)
    
    Args:
        audio_array: Input audio array (normalized -1 to 1)
        threshold: Clipping threshold (0.0 to 1.0)
    
    Returns:
        True if clipping detected
    """
    max_val = np.max(np.abs(audio_array))
    return max_val > threshold
