"""
VŌCIS RECITĀTIŌ Audio Engine
=============================
Recording, playback, and speed control for voice recordings.

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.
"""

import time
from config import Audio, Files, DEBUG

try:
    from system import audio
    from hardware import Speaker, Mic
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    if DEBUG:
        print(">>> WARNING: Audio hardware not available (simulation mode)")


class AudioState:
    """Enumeration of audio engine states."""
    IDLE = "idle"
    RECORDING = "recording"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioEngine:
    """
    Core audio engine for recording and playback.

    Handles:
    - Voice recording to WAV files
    - Playback with speed control (tardē/celer modes)
    - Volume management
    - Recording level monitoring (RMS)
    """

    def __init__(self, on_state_change=None, on_level_update=None):
        """
        Initialize the audio engine.

        Args:
            on_state_change: Callback(state) when state changes
            on_level_update: Callback(level) for audio level updates (0-100)
        """
        self._state = AudioState.IDLE
        self._on_state_change = on_state_change
        self._on_level_update = on_level_update

        # Audio components
        self._recorder = None
        self._player = None

        # Current recording/playback info
        self._current_file = None
        self._recording_start_time = None
        self._recording_duration = 0

        # Playback settings
        self._volume = Audio.VOLUME_DEFAULT
        self._speed = Audio.SPEED_NORMAL
        self._current_sample_rate = Audio.SAMPLE_RATE

        # Temporary buffer for unsaved recording
        self._temp_buffer = None

        # Initialize hardware if available
        self._init_hardware()

    def _init_hardware(self):
        """Initialize audio hardware components."""
        if not HARDWARE_AVAILABLE:
            if DEBUG:
                print(">>> Audio engine running in simulation mode")
            return

        try:
            self._recorder = audio.Recorder(
                sample=Audio.SAMPLE_RATE,
                bits=Audio.BIT_DEPTH,
                stereo=Audio.STEREO
            )
            self._player = audio.Player()
            if DEBUG:
                print(">>> Audio hardware initialized")
        except Exception as e:
            if DEBUG:
                print(f">>> ERROR initializing audio: {e}")

    def _set_state(self, new_state):
        """Update state and notify callback."""
        if self._state != new_state:
            self._state = new_state
            if self._on_state_change:
                self._on_state_change(new_state)

    @property
    def state(self):
        """Current audio engine state."""
        return self._state

    @property
    def is_recording(self):
        """True if currently recording."""
        return self._state == AudioState.RECORDING

    @property
    def is_playing(self):
        """True if currently playing."""
        return self._state == AudioState.PLAYING

    @property
    def is_paused(self):
        """True if playback is paused."""
        return self._state == AudioState.PAUSED

    @property
    def is_idle(self):
        """True if idle (not recording or playing)."""
        return self._state == AudioState.IDLE

    @property
    def volume(self):
        """Current volume level (0-100)."""
        return self._volume

    @volume.setter
    def volume(self, value):
        """Set volume level (0-100)."""
        self._volume = max(Audio.VOLUME_MIN, min(Audio.VOLUME_MAX, value))
        if self._player and HARDWARE_AVAILABLE:
            try:
                self._player.set_vol(self._volume)
            except Exception:
                pass

    @property
    def speed(self):
        """Current playback speed multiplier."""
        return self._speed

    @speed.setter
    def speed(self, value):
        """Set playback speed multiplier."""
        self._speed = value
        # Calculate sample rate for speed effect
        self._current_sample_rate = int(Audio.SAMPLE_RATE * value)

    @property
    def recording_duration(self):
        """Current recording duration in seconds."""
        if self.is_recording and self._recording_start_time:
            return time.time() - self._recording_start_time
        return self._recording_duration

    @property
    def audio_level(self):
        """Current audio input level (0-100)."""
        if not self.is_recording or not self._recorder:
            return 0
        try:
            # RMS returns dB, convert to 0-100 scale
            rms = self._recorder.rms()
            # Typical range: -60dB (silence) to 0dB (max)
            # Map to 0-100
            level = max(0, min(100, (rms + 60) * 100 / 60))
            return int(level)
        except Exception:
            return 0

    def start_recording(self, max_duration=None):
        """
        Start recording audio to temporary buffer.

        Args:
            max_duration: Maximum recording time in seconds (default: from config)

        Returns:
            True if recording started successfully
        """
        if not self.is_idle:
            if DEBUG:
                print(">>> Cannot start recording: not idle")
            return False

        if not HARDWARE_AVAILABLE:
            self._set_state(AudioState.RECORDING)
            self._recording_start_time = time.time()
            if DEBUG:
                print(">>> Recording started (simulation)")
            return True

        try:
            duration = max_duration or Audio.MAX_RECORDING_TIME

            # Create buffer for recording
            self._temp_buffer = self._recorder.create_pcm_buf(time=duration)

            # Start recording into buffer (async)
            self._recorder.record_into(
                self._temp_buffer,
                sample=Audio.SAMPLE_RATE,
                bits=Audio.BIT_DEPTH,
                stereo=Audio.STEREO,
                sync=False  # Non-blocking
            )

            self._recording_start_time = time.time()
            self._set_state(AudioState.RECORDING)

            if DEBUG:
                print(f">>> Recording started (max {duration}s)")
            return True

        except Exception as e:
            if DEBUG:
                print(f">>> ERROR starting recording: {e}")
            return False

    def stop_recording(self):
        """
        Stop recording and return duration.

        Returns:
            Recording duration in seconds, or 0 on error
        """
        if not self.is_recording:
            return 0

        duration = 0

        if self._recording_start_time:
            duration = time.time() - self._recording_start_time
            self._recording_duration = duration

        if HARDWARE_AVAILABLE and self._recorder:
            try:
                self._recorder.stop()
            except Exception as e:
                if DEBUG:
                    print(f">>> ERROR stopping recording: {e}")

        self._set_state(AudioState.IDLE)

        if DEBUG:
            print(f">>> Recording stopped ({duration:.1f}s)")

        return duration

    def save_recording(self, filename):
        """
        Save the current recording to a file.

        Args:
            filename: Name for the recording (without path/extension)

        Returns:
            Full path to saved file, or None on error
        """
        if self._temp_buffer is None and not DEBUG:
            if DEBUG:
                print(">>> No recording to save")
            return None

        # Ensure directory exists
        try:
            import os
            if not Files.RECORDINGS_FOLDER in os.listdir(Files.SD_ROOT):
                os.makedirs(Files.RECORDINGS_FOLDER)
        except Exception:
            pass

        # Build full path
        if not filename.endswith(f".{Audio.FILE_FORMAT}"):
            filename = f"{filename}.{Audio.FILE_FORMAT}"
        filepath = f"{Files.RECORDINGS_FOLDER}/{filename}"

        if not HARDWARE_AVAILABLE:
            if DEBUG:
                print(f">>> Saved (simulation): {filepath}")
            return filepath

        try:
            # Save buffer to file
            with open(filepath, 'wb') as f:
                # Write WAV header
                self._write_wav_header(f, len(self._temp_buffer))
                # Write audio data
                f.write(self._temp_buffer)

            if DEBUG:
                print(f">>> Saved: {filepath}")

            # Clear temp buffer
            self._temp_buffer = None

            return filepath

        except Exception as e:
            if DEBUG:
                print(f">>> ERROR saving: {e}")
            return None

    def _write_wav_header(self, file, data_size):
        """Write WAV file header."""
        import struct

        channels = 2 if Audio.STEREO else 1
        sample_rate = Audio.SAMPLE_RATE
        bits_per_sample = Audio.BIT_DEPTH
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8

        # RIFF header
        file.write(b'RIFF')
        file.write(struct.pack('<I', 36 + data_size))
        file.write(b'WAVE')

        # fmt chunk
        file.write(b'fmt ')
        file.write(struct.pack('<I', 16))  # Chunk size
        file.write(struct.pack('<H', 1))   # Audio format (PCM)
        file.write(struct.pack('<H', channels))
        file.write(struct.pack('<I', sample_rate))
        file.write(struct.pack('<I', byte_rate))
        file.write(struct.pack('<H', block_align))
        file.write(struct.pack('<H', bits_per_sample))

        # data chunk
        file.write(b'data')
        file.write(struct.pack('<I', data_size))

    def play_file(self, filepath, speed=None):
        """
        Start playback of a recording.

        Args:
            filepath: Path to audio file
            speed: Playback speed multiplier (default: current speed)

        Returns:
            True if playback started successfully
        """
        if not self.is_idle and not self.is_paused:
            if DEBUG:
                print(">>> Cannot start playback: busy")
            return False

        if speed is not None:
            self.speed = speed

        self._current_file = filepath

        if not HARDWARE_AVAILABLE:
            self._set_state(AudioState.PLAYING)
            if DEBUG:
                print(f">>> Playing (simulation): {filepath} @ {self._speed}x")
            return True

        try:
            # Calculate effective sample rate for speed
            effective_rate = int(Audio.SAMPLE_RATE * self._speed)

            self._player.play(
                f"file://{filepath}",
                volume=self._volume,
                sync=False  # Non-blocking
            )

            self._set_state(AudioState.PLAYING)

            if DEBUG:
                print(f">>> Playing: {filepath} @ {self._speed}x")
            return True

        except Exception as e:
            if DEBUG:
                print(f">>> ERROR playing: {e}")
            return False

    def play_buffer(self, speed=None):
        """
        Play the current recording buffer (before saving).

        Args:
            speed: Playback speed multiplier

        Returns:
            True if playback started successfully
        """
        if self._temp_buffer is None:
            if DEBUG:
                print(">>> No buffer to play")
            return False

        if not self.is_idle:
            if DEBUG:
                print(">>> Cannot play buffer: busy")
            return False

        if speed is not None:
            self.speed = speed

        if not HARDWARE_AVAILABLE:
            self._set_state(AudioState.PLAYING)
            if DEBUG:
                print(f">>> Playing buffer (simulation) @ {self._speed}x")
            return True

        try:
            # Calculate effective sample rate for speed
            effective_rate = int(Audio.SAMPLE_RATE * self._speed)

            self._player.play_raw(
                self._temp_buffer,
                sample=effective_rate,
                stereo=Audio.STEREO,
                bits=Audio.BIT_DEPTH,
                volume=self._volume,
                sync=False
            )

            self._set_state(AudioState.PLAYING)

            if DEBUG:
                print(f">>> Playing buffer @ {self._speed}x (rate={effective_rate})")
            return True

        except Exception as e:
            if DEBUG:
                print(f">>> ERROR playing buffer: {e}")
            return False

    def pause(self):
        """Pause current playback."""
        if not self.is_playing:
            return False

        if HARDWARE_AVAILABLE and self._player:
            try:
                self._player.pause()
            except Exception as e:
                if DEBUG:
                    print(f">>> ERROR pausing: {e}")
                return False

        self._set_state(AudioState.PAUSED)
        if DEBUG:
            print(">>> Paused")
        return True

    def resume(self):
        """Resume paused playback."""
        if not self.is_paused:
            return False

        if HARDWARE_AVAILABLE and self._player:
            try:
                self._player.resume()
            except Exception as e:
                if DEBUG:
                    print(f">>> ERROR resuming: {e}")
                return False

        self._set_state(AudioState.PLAYING)
        if DEBUG:
            print(">>> Resumed")
        return True

    def stop(self):
        """Stop current recording or playback."""
        if self.is_recording:
            return self.stop_recording()

        if self.is_playing or self.is_paused:
            if HARDWARE_AVAILABLE and self._player:
                try:
                    self._player.stop()
                except Exception:
                    pass

            self._set_state(AudioState.IDLE)
            if DEBUG:
                print(">>> Stopped")
            return True

        return False

    def set_speed_slow(self):
        """Set playback speed to slow (vōx gravis - deep voice effect)."""
        self.speed = Audio.SPEED_SLOW
        if DEBUG:
            print(f">>> Speed: TARDĒ ({self.speed}x)")

    def set_speed_normal(self):
        """Set playback speed to normal."""
        self.speed = Audio.SPEED_NORMAL
        if DEBUG:
            print(f">>> Speed: NORMAL ({self.speed}x)")

    def set_speed_fast(self):
        """Set playback speed to fast (vōx acūta - high voice effect)."""
        self.speed = Audio.SPEED_FAST
        if DEBUG:
            print(f">>> Speed: CELER ({self.speed}x)")

    def clear_buffer(self):
        """Clear the temporary recording buffer."""
        self._temp_buffer = None
        self._recording_duration = 0
        if DEBUG:
            print(">>> Buffer cleared")

    def has_unsaved_recording(self):
        """Check if there's an unsaved recording in the buffer."""
        return self._temp_buffer is not None

    def update(self):
        """
        Update loop - call periodically to update audio levels.

        Returns audio level (0-100) if recording, else 0.
        """
        if self.is_recording and self._on_level_update:
            level = self.audio_level
            self._on_level_update(level)
            return level
        return 0
