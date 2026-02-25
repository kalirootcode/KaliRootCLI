"""
Audio Module for KaliRoot CLI — DOMINION Edition
Handles Speech-to-Text. Groq Whisper removed; future Gemini Speech integration pending.
"""

import os
import time
import logging

# Optional audio dependencies (may not be available on Termux)
try:
    import numpy as np
    import scipy.io.wavfile as wav
    SCIPY_AVAILABLE = True
except ImportError:
    np = None
    wav = None
    SCIPY_AVAILABLE = False
    
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except (OSError, ImportError):
    sd = None
    AUDIO_AVAILABLE = False
    
from .ui.display import console, show_loading, print_error, print_success, print_info

logger = logging.getLogger(__name__)

class AudioHandler:
    """Handles audio recording and transcription."""
    
    def __init__(self):
        self.samplerate = 44100
        self.channels = 1
        
    def record_audio(self, duration: int = 5, filename: str = "command.wav") -> str:
        """
        Record audio from microphone.
        
        Args:
            duration: Seconds to record
            filename: Output filename
            
        Returns:
            Path to recorded file or None
        """
        if not AUDIO_AVAILABLE or sd is None:
            print_error("🔊 Driver de audio no encontrado (PortAudio/sounddevice missing).")
            print_error("Instala: pip install kr-cli-dominion[audio] (requiere PC/Linux)")
            return None
        
        if not SCIPY_AVAILABLE or wav is None:
            print_error("🔊 Módulos de audio no disponibles.")
            print_error("Instala: pip install kr-cli-dominion[audio]")
            return None
            
        try:
            print(f"🎙️ Escuchando... ({duration}s)")
            
            # Record
            recording = sd.rec(
                int(duration * self.samplerate), 
                samplerate=self.samplerate, 
                channels=self.channels,
                dtype='int16'
            )
            sd.wait()
            
            # Save
            filepath = os.path.join(os.getcwd(), filename)
            wav.write(filepath, self.samplerate, recording)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Recording error: {e}")
            print_error(f"Error grabando audio: {e}")
            return None

    def transcribe(self, filepath: str) -> str:
        """
        Transcribe audio file to text.
        NOTE: Groq Whisper removed in DOMINION refactoring.
        Future integration: Gemini Speech-to-Text API.
        """
        print_info("[dim]STT: Transcripción por voz en desarrollo para DOMINION. Por ahora ingresa tu comando manualmente.[/dim]")
        return None
            
def listen_and_execute():
    """Main voice functionality."""
    handler = AudioHandler()
    
    # 1. Record
    filepath = handler.record_audio(duration=5)
    if not filepath:
        return
        
    # 2. Transcribe
    with show_loading("🧠 Transcribiendo voz..."):
        text = handler.transcribe(filepath)
        
    console.print(f"\n[bold cyan]🗣️ Dijiste:[/bold cyan] '{text}'\n")
    
    # Clean up
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
            
    # 3. Execute
    if text and "Error" not in text:
        # We pass this text to execute_and_analyze logic
        # But since we are in a standalone function, we import it or return
        return text
    return None
