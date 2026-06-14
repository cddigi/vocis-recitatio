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

        # Playback progress (wall-clock). Sample-rate playback is non-blocking,
        # so we time it ourselves to detect the end and drive the progress bar.
        self._playback_start_ms = 0
        self._playback_accum_s = 0.0
        self._playback_total_s = 0.0

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

    def _now_ms(self):
        """Millisecond clock (MicroPython ticks_ms, CPython fallback)."""
        return time.ticks_ms() if hasattr(time, "ticks_ms") else int(time.time() * 1000)

    def _pcm_duration_s(self, num_bytes):
        """Seconds of audio represented by num_bytes of PCM at the rec format."""
        channels = 2 if Audio.STEREO else 1
        bytes_per_sec = Audio.SAMPLE_RATE * channels * (Audio.BIT_DEPTH // 8)
        if bytes_per_sec <= 0:
            return 0.0
        return num_bytes / bytes_per_sec

    def _start_playback_timer(self, total_s):
        """Begin timing a playback of total_s wall-clock seconds."""
        self._playback_total_s = total_s
        self._playback_accum_s = 0.0
        self._playback_start_ms = self._now_ms()

    def _reset_playback_timer(self):
        self._playback_total_s = 0.0
        self._playback_accum_s = 0.0
        self._playback_start_ms = 0

    @property
    def playback_elapsed_s(self):
        """Wall-clock seconds elapsed in the current playback."""
        if self.is_playing:
            return self._playback_accum_s + (self._now_ms() - self._playback_start_ms) / 1000
        if self.is_paused:
            return self._playback_accum_s
        return 0.0

    @property
    def playback_total_s(self):
        """Total wall-clock seconds of the current playback (0 if unknown)."""
        return self._playback_total_s

    @property
    def playback_fraction(self):
        """Playback progress 0.0-1.0 (0 if total unknown)."""
        if self._playback_total_s <= 0:
            return 0.0
        frac = self.playback_elapsed_s / self._playback_total_s
        if frac < 0:
            return 0.0
        return 1.0 if frac > 1 else frac

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
            try:
                import os
                size = os.stat(filepath)[6]
                self._start_playback_timer(
                    self._pcm_duration_s(max(0, size - 44)) / self._speed
                )
            except OSError:
                self._start_playback_timer(0.0)
            self._set_state(AudioState.PLAYING)
            if DEBUG:
                print(f">>> Playing (simulation): {filepath} @ {self._speed}x")
            return True

        try:
            # Calculate effective sample rate for speed.
            # Variable speed = changing the PLAYBACK sample rate (no DSP/pitch
            # shift), exactly like play_buffer(). The WAV header stores 16 kHz,
            # so playing via play(file://...) would ignore speed entirely; we
            # read the raw PCM instead and feed it at effective_rate.
            effective_rate = int(Audio.SAMPLE_RATE * self._speed)

            # Skip the fixed 44-byte RIFF/fmt /data header written by
            # _write_wav_header, leaving just the PCM samples.
            WAV_HEADER_SIZE = 44

            # Read the whole clip into RAM. Like play_buffer (which already
            # holds the full PCM buffer), this trades memory for simplicity;
            # a 5-min 16 kHz mono 16-bit clip is ~9.6 MB, fine on PSRAM.
            with open(filepath, 'rb') as f:
                f.read(WAV_HEADER_SIZE)
                pcm = f.read()

            self._player.play_raw(
                pcm,
                sample=effective_rate,
                stereo=Audio.STEREO,
                bits=Audio.BIT_DEPTH,
                volume=self._volume,
                sync=False  # Non-blocking
            )

            self._start_playback_timer(self._pcm_duration_s(len(pcm)) / self._speed)
            self._set_state(AudioState.PLAYING)

            if DEBUG:
                print(f">>> Playing: {filepath} @ {self._speed}x (rate={effective_rate})")
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
            self._start_playback_timer(
                self._pcm_duration_s(len(self._temp_buffer)) / self._speed
            )
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

            self._start_playback_timer(
                self._pcm_duration_s(len(self._temp_buffer)) / self._speed
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

        # Bank the elapsed time so the progress timer freezes while paused.
        self._playback_accum_s += (self._now_ms() - self._playback_start_ms) / 1000
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

        # Restart the segment clock; banked time is preserved in accum.
        self._playback_start_ms = self._now_ms()
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

            self._reset_playback_timer()
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

        Also detects the end of a non-blocking playback and returns the
        engine to IDLE so the UI can reset its transport controls.

        Returns audio level (0-100) if recording, else 0.
        """
        # Auto-stop recording at the configured cap (buffer was sized for it).
        if self.is_recording and self.recording_duration >= Audio.MAX_RECORDING_TIME:
            self.stop_recording()

        # End-of-playback detection (sample-rate playback is non-blocking).
        if self.is_playing and self._playback_total_s > 0:
            if self.playback_elapsed_s >= self._playback_total_s:
                self.stop()

        if self.is_recording and self._on_level_update:
            level = self.audio_level
            self._on_level_update(level)
            return level
        return 0
