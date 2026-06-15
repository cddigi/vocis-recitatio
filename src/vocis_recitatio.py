"""
VŌCIS RECITĀTIŌ Main Application
=================================
Voice recorder inspired by the Talkboy from Home Alone 2,
with a Hackers (1995) aesthetic and Classical Latin interface.

"Hack the Planet!"

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.
"""

import time
from config import DEBUG, Timing
from audio_engine import AudioEngine, AudioState
from file_manager import FileManager
from ui import VocisRecitatioUI


class VocisRecitatioApp:
    """
    Main Vōcis Recitātiō application controller.

    Coordinates audio engine, file management, and UI.
    """

    def __init__(self):
        self._running = False

        # Initialize file manager first (creates directories)
        self.files = FileManager()

        # Initialize audio engine with callbacks
        self.audio = AudioEngine(
            on_state_change=self._on_audio_state_change,
            on_level_update=self._on_audio_level
        )

        # Initialize UI (EXĪ button calls back into stop() to leave the app)
        self.ui = VocisRecitatioUI(self.audio, self.files, on_exit=self.stop)

        if DEBUG:
            print(">>> Vōcis Recitātiō initialized")

    def _on_audio_state_change(self, state):
        """Callback when audio state changes."""
        if DEBUG:
            print(f">>> Audio state: {state}")

    def _on_audio_level(self, level):
        """Callback for audio level updates during recording."""
        pass

    def start(self):
        """Start the application."""
        if DEBUG:
            print(">>> Starting Vōcis Recitātiō...")
            print(">>> ===========================")
            print(">>>    HACK THE PLANET!")
            print(">>> ===========================")

        # Initialize UI
        self.ui.init()

        # Start main loop
        self._running = True
        self._main_loop()

    def stop(self):
        """Stop the application."""
        self._running = False

        # Tear down any active audio path (recording, playing, or paused) so
        # the mic/speaker are released before we leave.
        if not self.audio.is_idle:
            self.audio.stop()

        if DEBUG:
            print(">>> Vōcis Recitātiō dēsiit")  # "has stopped"

    def _main_loop(self):
        """Main application loop."""
        last_update = self._get_time_ms()

        while self._running:
            now = self._get_time_ms()

            # Update UI and audio at target rate
            if now - last_update >= Timing.WAVE_UPDATE_MS:
                self.ui.update()
                last_update = now

            # Small sleep to prevent CPU hogging
            time.sleep(0.01)

    def _get_time_ms(self):
        """Get current time in milliseconds."""
        if hasattr(time, 'ticks_ms'):
            return time.ticks_ms()
        return int(time.time() * 1000)


def main():
    """Entry point for Vōcis Recitātiō application."""
    app = VocisRecitatioApp()

    try:
        app.start()
    except KeyboardInterrupt:
        if DEBUG:
            print("\n>>> Interruptum ab ūsōre")  # Interrupted by user
    except Exception as e:
        if DEBUG:
            print(f">>> ERROR FĀTĀLIS: {e}")
    finally:
        app.stop()


# Run if executed directly
if __name__ == "__main__":
    main()
