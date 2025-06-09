#!/usr/bin/env python3
"""
Python Notification Sounds für CORTEX Research
==============================================

Verschiedene Optionen für Audio-Notifications nach langen API-Research-Runs.
"""

import os
import sys
import time
import math
import threading
from typing import Optional

# Option 1: System Bell (simplest - works everywhere)
def simple_bell():
    """Einfachster System-Bell - funktioniert überall"""
    print('\a\a\a\a\a \n- Fertig!')  # ASCII Bell character

# Option 2: playsound (external library, aber sehr einfach)
def play_notification_file(filename: str = "notification.wav"):
    """Spielt eine Audio-Datei ab (benötigt playsound: pip install playsound)"""
    try:
        from playsound import playsound
        playsound(filename)
    except ImportError:
        print("INFO: playsound not installed. Use: pip install playsound")
        simple_bell()
    except Exception as e:
        print(f"Audio playback failed: {e}")
        simple_bell()

# Option 3: Synthesized Tone (pure Python with wave module)
def generate_tone_wave(frequency: int = 800, duration: float = 0.5, volume: float = 0.3):
    """Generiert einen Ton als WAV-Datei (pure Python)"""
    import wave
    import struct
    
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    # Generate sine wave
    audio_data = []
    for i in range(frames):
        # Sine wave formula
        value = int(32767 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
        audio_data.append(struct.pack('<h', value))
    
    # Write to WAV file
    with wave.open('temp_notification.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(audio_data))
    
    return 'temp_notification.wav'

# Option 4: Cross-platform notification (mit pygame)
def pygame_notification_tone(frequency: int = 800, duration: float = 0.5):
    """Spielt Ton mit pygame ab (pip install pygame)"""
    try:
        import pygame
        import numpy as np
        
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Generate tone
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave_value = 0.3 * np.sin(2 * np.pi * frequency * i / sample_rate)
            arr[i] = [wave_value, wave_value]
        
        sound = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
        sound.play()
        time.sleep(duration)
        pygame.mixer.quit()
        
    except ImportError:
        print("INFO: pygame not installed. Use: pip install pygame numpy")
        simple_bell()
    except Exception as e:
        print(f"Pygame audio failed: {e}")
        simple_bell()

# Option 5: Platform-specific system sounds
def system_notification():
    """Platform-spezifische System-Notification"""
    system = os.name
    
    if system == 'nt':  # Windows
        try:
            import winsound
            # Windows system sound
            winsound.MessageBeep(winsound.MB_ICONINFORMATION)
        except ImportError:
            simple_bell()
    elif system == 'posix':  # Linux/macOS
        if sys.platform == 'darwin':  # macOS
            os.system('afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || echo "\\a"')
        else:  # Linux
            # Try various Linux audio systems
            audio_commands = [
                'paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null',
                'aplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null', 
                'speaker-test -t sine -f 800 -l 1 2>/dev/null',
                'echo "\\a"'
            ]
            for cmd in audio_commands:
                if os.system(cmd) == 0:
                    break
    else:
        simple_bell()

# Option 6: "Tideliiing" Melody (multiple tones)
def tideliiing_melody():
    """Klassisches 'Tideliiing' mit mehreren Tönen"""
    try:
        import pygame
        import numpy as np
        
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Tideliiing melody: C-E-G ascending
        frequencies = [523, 659, 784]  # C5, E5, G5
        durations = [0.2, 0.2, 0.4]
        
        for freq, dur in zip(frequencies, durations):
            sample_rate = 22050
            frames = int(dur * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                # Fade out for nice sound
                fade = 1.0 - (i / frames) * 0.7
                wave_value = 0.3 * fade * np.sin(2 * np.pi * freq * i / sample_rate)
                arr[i] = [wave_value, wave_value]
            
            sound = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
            sound.play()
            time.sleep(dur)
        
        pygame.mixer.quit()
        
    except ImportError:
        # Fallback: ASCII sequence that sounds like melody
        print("♪ Ti-de-lii-ing! ♪")
        for _ in range(3):
            simple_bell()
            time.sleep(0.2)

# Integration für dein CORTEX Script
class NotificationManager:
    """Notification Manager für CORTEX Research"""
    
    def __init__(self, method: str = "auto"):
        self.method = method
        self.available_methods = self._detect_available_methods()
        
        if method == "auto":
            self.method = self._select_best_method()
    
    def _detect_available_methods(self) -> list:
        """Erkennt verfügbare Audio-Methoden"""
        available = ["bell"]  # Always available
        
        try:
            import pygame
            available.append("pygame")
        except ImportError:
            pass
            
        try:
            from playsound import playsound
            available.append("playsound")
        except ImportError:
            pass
            
        if os.name == 'nt':
            try:
                import winsound
                available.append("winsound")
            except ImportError:
                pass
        
        return available
    
    def _select_best_method(self) -> str:
        """Wählt beste verfügbare Methode"""
        if "pygame" in self.available_methods:
            return "pygame"
        elif "winsound" in self.available_methods:
            return "winsound"
        elif "playsound" in self.available_methods:
            return "playsound"
        else:
            return "bell"
    
    def notify(self, message: str = "Analysis complete!"):
        """Spielt Notification ab"""
        print(f"\n🔔 {message}")
        
        if self.method == "pygame":
            tideliiing_melody()
        elif self.method == "winsound":
            system_notification()
        elif self.method == "playsound":
            # First generate a tone file, then play it
            tone_file = generate_tone_wave(800, 0.5, 0.3)
            play_notification_file(tone_file)
            os.remove(tone_file)  # Cleanup
        else:
            # Fallback
            for _ in range(3):
                simple_bell()
                time.sleep(0.1)

# Einfache Integration in dein bestehendes Script
def research_complete_notification():
    """Call this at the end of your API research"""
    notifier = NotificationManager()
    notifier.notify("🧠 CORTEX API Research Complete! 🎯")

# Async version für non-blocking notification
def async_notification(message: str = "Research complete!"):
    """Non-blocking notification in separatem Thread"""
    def play_sound():
        notifier = NotificationManager()
        notifier.notify(message)
    
    thread = threading.Thread(target=play_sound, daemon=True)
    thread.start()

# === INTEGRATION EXAMPLE ===
if __name__ == "__main__":
    print("Testing notification methods...")
    
    print("\n1. Simple bell:")
    simple_bell()
    time.sleep(1)
    
    print("\n2. System notification:")
    system_notification()
    time.sleep(1)
    
    print("\n3. Tideliiing melody:")
    tideliiing_melody()
    time.sleep(1)
    
    print("\n4. Full notification manager:")
    research_complete_notification()
    
    print("\nAdd this to your CORTEX script:")
    print("# At the end of your API research loop:")
    print("from notification_sounds import research_complete_notification")
    print("research_complete_notification()")

"""
INSTALLATION GUIDE:
==================

Minimal (nur System Bell):
- Keine zusätzlichen Dependencies

Optimal (schöne Töne):
pip install pygame numpy

Alternative:
pip install playsound

INTEGRATION IN DEIN SCRIPT:
==========================

# Import am Anfang deines Scripts
from notification_sounds import NotificationManager

# Am Ende der Analyse
notifier = NotificationManager()
notifier.notify("🧠 API Parameter Research Complete! 🎯")

# Oder ganz einfach:
research_complete_notification()
"""