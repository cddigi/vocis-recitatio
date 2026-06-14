"""
VŌCIS RECITĀTIŌ User Interface
===============================
Hackers (1995) aesthetic - green phosphor, neon accents, terminal vibes.
"Mess with the best, die like the rest."

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.
"""

import time
import math
from config import Colors, Layout, Text, Timing, SCREEN_WIDTH, SCREEN_HEIGHT, DEBUG

try:
    import M5
    from m5ui import Widgets
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    if DEBUG:
        print(">>> WARNING: Display hardware not available")


def _now_ms():
    """Millisecond clock (MicroPython ticks_ms, CPython fallback)."""
    return time.ticks_ms() if hasattr(time, "ticks_ms") else int(time.time() * 1000)


class HackerButton:
    """
    Custom button with Hackers (1995) terminal aesthetic.

    Green phosphor text, glowing borders, pulsing effects.
    """

    def __init__(self, x, y, width, height, label, on_press=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.on_press = on_press

        self._pressed = False
        self._enabled = True
        self._active = False  # For toggle states like REC

        # UI elements (created on draw)
        self._bg = None
        self._border = None
        self._text = None

    def draw(self):
        """Draw the button."""
        if not HARDWARE_AVAILABLE:
            return

        # Background rectangle
        bg_color = Colors.BUTTON_ACTIVE if self._pressed else Colors.BUTTON_BG
        if self._active:
            bg_color = Colors.REC_ACTIVE if self.label == Text.BTN_REC else Colors.PLAY_ACTIVE

        Widgets.fillRoundRect(
            self.x, self.y, self.width, self.height,
            5, bg_color
        )

        # Border (green phosphor glow)
        border_color = Colors.NEON_CYAN if self._active else Colors.BUTTON_BORDER
        if not self._enabled:
            border_color = Colors.PHOSPHOR_DIM

        Widgets.drawRoundRect(
            self.x, self.y, self.width, self.height,
            5, border_color
        )

        # Second border for glow effect
        if self._active or self._pressed:
            Widgets.drawRoundRect(
                self.x + 1, self.y + 1, self.width - 2, self.height - 2,
                4, border_color
            )

        # Label
        text_color = Colors.BUTTON_TEXT if self._enabled else Colors.PHOSPHOR_DIM
        if self._active:
            text_color = Colors.BG_PRIMARY

        # Center text
        text_x = self.x + (self.width // 2) - (len(self.label) * 6)
        text_y = self.y + (self.height // 2) - 8

        Widgets.Label(
            self.label, text_x, text_y, 1.0,
            text_color=text_color, bg_color=bg_color
        )

    def check_touch(self, touch_x, touch_y):
        """Check if touch is within button bounds."""
        if not self._enabled:
            return False

        in_bounds = (
            self.x <= touch_x <= self.x + self.width and
            self.y <= touch_y <= self.y + self.height
        )

        if in_bounds and self.on_press:
            self._pressed = True
            self.draw()
            self.on_press()
            return True

        return False

    def release(self):
        """Release button (call after touch up)."""
        if self._pressed:
            self._pressed = False
            self.draw()

    def set_active(self, active):
        """Set active state (for toggles like REC)."""
        self._active = active
        self.draw()

    @property
    def is_active(self):
        """Whether the button is in its active/toggled state."""
        return self._active

    def set_enabled(self, enabled):
        """Enable/disable button."""
        self._enabled = enabled
        self.draw()

    def set_label(self, label):
        """Update button label."""
        self.label = label
        self.draw()


class WaveformDisplay:
    """
    Real-time audio waveform visualizer.

    Matrix-style cascading effect with green phosphor aesthetic.
    """

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Waveform data (circular buffer)
        self._buffer_size = width
        self._buffer = [0] * self._buffer_size
        self._buffer_pos = 0

        # Visual settings
        self._bar_width = 3
        self._bar_gap = 1
        self._num_bars = width // (self._bar_width + self._bar_gap)

        # Grid lines for that hacker aesthetic
        self._show_grid = True
        self._grid_spacing = 40

    def draw_background(self):
        """Draw the waveform background with grid."""
        if not HARDWARE_AVAILABLE:
            return

        # Dark background
        Widgets.fillRect(
            self.x, self.y, self.width, self.height,
            Colors.BG_TERMINAL
        )

        # Border
        Widgets.drawRect(
            self.x, self.y, self.width, self.height,
            Colors.PHOSPHOR_DIM
        )

        if self._show_grid:
            # Horizontal grid lines
            for i in range(0, self.height, self._grid_spacing):
                y = self.y + i
                Widgets.drawLine(
                    self.x, y, self.x + self.width, y,
                    Colors.BG_SECONDARY
                )

            # Vertical grid lines
            for i in range(0, self.width, self._grid_spacing):
                x = self.x + i
                Widgets.drawLine(
                    x, self.y, x, self.y + self.height,
                    Colors.BG_SECONDARY
                )

            # Center line (brighter)
            center_y = self.y + self.height // 2
            Widgets.drawLine(
                self.x, center_y, self.x + self.width, center_y,
                Colors.PHOSPHOR_DIM
            )

    def update(self, level):
        """
        Update waveform with new audio level.

        Args:
            level: Audio level 0-100
        """
        # Add to circular buffer
        self._buffer[self._buffer_pos] = level
        self._buffer_pos = (self._buffer_pos + 1) % self._buffer_size

        self._draw_waveform()

    def _draw_waveform(self):
        """Draw the waveform bars."""
        if not HARDWARE_AVAILABLE:
            return

        # Clear waveform area (preserve grid)
        self.draw_background()

        center_y = self.y + self.height // 2
        max_amplitude = self.height // 2 - 5

        # Draw bars
        for i in range(self._num_bars):
            # Get level from buffer
            buffer_idx = (self._buffer_pos - self._num_bars + i) % self._buffer_size
            level = self._buffer[buffer_idx]

            # Calculate bar height
            bar_height = int((level / 100) * max_amplitude)

            if bar_height < 2:
                bar_height = 2  # Minimum visibility

            # Bar position
            bar_x = self.x + 5 + i * (self._bar_width + self._bar_gap)
            bar_top = center_y - bar_height
            bar_bottom = center_y + bar_height

            # Color based on level
            if level > 90:
                color = Colors.NEON_RED
            elif level > 70:
                color = Colors.NEON_YELLOW
            else:
                color = Colors.WAVE_PRIMARY

            # Draw symmetric bar
            Widgets.fillRect(
                bar_x, bar_top,
                self._bar_width, bar_height * 2,
                color
            )

            # Glow effect for high levels
            if level > 80:
                Widgets.drawRect(
                    bar_x - 1, bar_top - 1,
                    self._bar_width + 2, bar_height * 2 + 2,
                    Colors.WAVE_PEAK
                )

    def clear(self):
        """Clear the waveform display."""
        self._buffer = [0] * self._buffer_size
        self._buffer_pos = 0
        self.draw_background()


class FileListView:
    """
    Scrollable file list with Hackers terminal aesthetic.

    Green text on black, selection highlighting, scroll indicators.
    """

    def __init__(self, x, y, width, height, on_select=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_select = on_select

        self._items = []  # List of RecordingInfo
        self._selected_index = -1
        self._scroll_offset = 0
        self._item_height = Layout.LIST_ITEM_HEIGHT
        self._visible_count = height // self._item_height

    def set_items(self, items):
        """Set the list items."""
        self._items = items
        self._selected_index = 0 if items else -1
        self._scroll_offset = 0
        self.draw()

    def draw(self):
        """Draw the file list."""
        if not HARDWARE_AVAILABLE:
            return

        # Background
        Widgets.fillRect(
            self.x, self.y, self.width, self.height,
            Colors.BG_PRIMARY
        )

        # Border
        Widgets.drawRect(
            self.x, self.y, self.width, self.height,
            Colors.PHOSPHOR_DIM
        )

        # Header
        Widgets.fillRect(
            self.x, self.y, self.width, 30,
            Colors.BG_SECONDARY
        )
        Widgets.Label(
            "[ RECITĀTIŌNĒS ]",
            self.x + 10, self.y + 8, 0.8,
            text_color=Colors.NEON_CYAN, bg_color=Colors.BG_SECONDARY
        )

        if not self._items:
            # No files message
            Widgets.Label(
                Text.NO_FILES,
                self.x + 20, self.y + self.height // 2, 0.7,
                text_color=Colors.PHOSPHOR_DIM, bg_color=Colors.BG_PRIMARY
            )
            return

        # Draw visible items
        list_start_y = self.y + 35
        for i in range(self._visible_count):
            item_index = self._scroll_offset + i
            if item_index >= len(self._items):
                break

            item = self._items[item_index]
            item_y = list_start_y + i * self._item_height

            # Selection highlight
            is_selected = item_index == self._selected_index
            if is_selected:
                Widgets.fillRect(
                    self.x + 2, item_y, self.width - 4, self._item_height - 2,
                    Colors.BG_SECONDARY
                )
                Widgets.drawRect(
                    self.x + 2, item_y, self.width - 4, self._item_height - 2,
                    Colors.NEON_CYAN
                )

            # File name
            text_color = Colors.FILE_SELECTED if is_selected else Colors.FILE_NORMAL
            bg_color = Colors.BG_SECONDARY if is_selected else Colors.BG_PRIMARY

            # Truncate long names
            display_name = item.name
            if len(display_name) > 20:
                display_name = display_name[:17] + "..."

            Widgets.Label(
                f"> {display_name}",
                self.x + 10, item_y + 5, 0.7,
                text_color=text_color, bg_color=bg_color
            )

            # Duration and size
            info_text = f"{item.duration_str} | {item.size_str}"
            Widgets.Label(
                info_text,
                self.x + 10, item_y + 25, 0.6,
                text_color=Colors.FILE_SIZE, bg_color=bg_color
            )

        # Scroll indicators
        if self._scroll_offset > 0:
            Widgets.Label(
                "↑", self.x + self.width - 20, list_start_y, 0.8,
                text_color=Colors.NEON_CYAN, bg_color=Colors.BG_PRIMARY
            )

        if self._scroll_offset + self._visible_count < len(self._items):
            Widgets.Label(
                "↓", self.x + self.width - 20, self.y + self.height - 25, 0.8,
                text_color=Colors.NEON_CYAN, bg_color=Colors.BG_PRIMARY
            )

    def select_next(self):
        """Select next item in list."""
        if not self._items:
            return

        self._selected_index = (self._selected_index + 1) % len(self._items)

        # Scroll if needed
        if self._selected_index >= self._scroll_offset + self._visible_count:
            self._scroll_offset = self._selected_index - self._visible_count + 1
        elif self._selected_index < self._scroll_offset:
            self._scroll_offset = self._selected_index

        self.draw()

    def select_prev(self):
        """Select previous item in list."""
        if not self._items:
            return

        self._selected_index = (self._selected_index - 1) % len(self._items)

        # Scroll if needed
        if self._selected_index < self._scroll_offset:
            self._scroll_offset = self._selected_index
        elif self._selected_index >= self._scroll_offset + self._visible_count:
            self._scroll_offset = self._selected_index - self._visible_count + 1

        self.draw()

    def get_selected(self):
        """Get currently selected item."""
        if 0 <= self._selected_index < len(self._items):
            return self._items[self._selected_index]
        return None

    def check_touch(self, touch_x, touch_y):
        """Handle touch on list item."""
        if not (self.x <= touch_x <= self.x + self.width and
                self.y <= touch_y <= self.y + self.height):
            return False

        # Check which item was touched
        list_start_y = self.y + 35
        rel_y = touch_y - list_start_y
        if rel_y < 0:
            return False

        item_index = self._scroll_offset + int(rel_y / self._item_height)
        if 0 <= item_index < len(self._items):
            self._selected_index = item_index
            self.draw()
            if self.on_select:
                self.on_select(self._items[item_index])
            return True

        return False


class StatusBar:
    """
    Status bar with system info and recording status.

    Matrix-style scrolling text effect.
    """

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self._status_text = Text.STATUS_READY
        self._recording_time = 0
        self._blink_state = False
        self._last_blink = 0

    def draw(self):
        """Draw the status bar."""
        if not HARDWARE_AVAILABLE:
            return

        # Background
        Widgets.fillRect(
            self.x, self.y, self.width, self.height,
            Colors.BG_SECONDARY
        )

        # Top border (scanline effect)
        Widgets.drawLine(
            self.x, self.y, self.x + self.width, self.y,
            Colors.PHOSPHOR_DIM
        )

        # Status text with cursor blink
        display_text = self._status_text
        if self._blink_state:
            display_text += "_"

        Widgets.Label(
            display_text,
            self.x + 10, self.y + 10, 1.0,
            text_color=Colors.PHOSPHOR_BRIGHT, bg_color=Colors.BG_SECONDARY
        )

        # Recording time (if recording)
        if self._recording_time > 0:
            mins = int(self._recording_time) // 60
            secs = int(self._recording_time) % 60
            time_text = f"SCRĪBŌ: {mins:02d}:{secs:02d}"

            Widgets.Label(
                time_text,
                self.x + self.width - 180, self.y + 10, 1.0,
                text_color=Colors.REC_ACTIVE, bg_color=Colors.BG_SECONDARY
            )

    def set_status(self, text):
        """Set status message."""
        self._status_text = text
        self.draw()

    def set_recording_time(self, seconds):
        """Set recording time display."""
        self._recording_time = seconds
        self.draw()

    def update_blink(self):
        """Update cursor blink state."""
        now = _now_ms()
        if now - self._last_blink > Timing.STATUS_BLINK_MS:
            self._blink_state = not self._blink_state
            self._last_blink = now
            self.draw()


class VocisRecitatioUI:
    """
    Main UI controller for Vōcis Recitātiō application.

    Orchestrates all UI components with Hackers (1995) aesthetic.
    """

    def __init__(self, audio_engine, file_manager, on_exit=None):
        self.audio = audio_engine
        self.files = file_manager
        self._on_exit = on_exit  # called by the EXĪ button to leave the app

        # UI Components
        self.waveform = None
        self.file_list = None
        self.status_bar = None
        self.buttons = {}

        self._initialized = False

        # Touch edge-detection + debounce state (fire on_press once per tap)
        self._touch_active = False
        self._last_touch_ms = 0

        # Transport reconciliation state
        self._prev_idle = True       # was the engine idle last frame?
        self._stop_was_manual = False  # keep DĒSIĪ vs PARĀTUS on next idle

    def init(self):
        """Initialize the UI."""
        if not HARDWARE_AVAILABLE:
            if DEBUG:
                print(">>> UI running in simulation mode")
            self._initialized = True
            return

        try:
            M5.begin()
            Widgets.fillScreen(Colors.BG_PRIMARY)
            Widgets.setBrightness(100)

            self._draw_header()
            self._create_waveform()
            self._create_file_list()
            self._create_status_bar()
            self._create_buttons()

            self._initialized = True
            if DEBUG:
                print(">>> UI initialized")

        except Exception as e:
            if DEBUG:
                print(f">>> ERROR initializing UI: {e}")

    def _draw_header(self):
        """Draw the app header with ASCII art title."""
        # Title background
        Widgets.fillRect(
            0, 0, SCREEN_WIDTH, Layout.HEADER_HEIGHT,
            Colors.BG_SECONDARY
        )

        # Title
        Widgets.Label(
            Text.TITLE,
            20, 15, 1.5,
            text_color=Colors.NEON_CYAN, bg_color=Colors.BG_SECONDARY
        )

        # Subtitle
        Widgets.Label(
            Text.SUBTITLE,
            400, 25, 0.8,
            text_color=Colors.PHOSPHOR_DIM, bg_color=Colors.BG_SECONDARY
        )

        # Decorative border
        Widgets.drawLine(
            0, Layout.HEADER_HEIGHT - 2, SCREEN_WIDTH, Layout.HEADER_HEIGHT - 2,
            Colors.NEON_CYAN
        )
        Widgets.drawLine(
            0, Layout.HEADER_HEIGHT - 1, SCREEN_WIDTH, Layout.HEADER_HEIGHT - 1,
            Colors.PHOSPHOR_DIM
        )

    def _create_waveform(self):
        """Create waveform display."""
        self.waveform = WaveformDisplay(
            Layout.WAVE_X,
            Layout.WAVE_Y,
            Layout.WAVE_WIDTH,
            Layout.WAVE_HEIGHT
        )
        self.waveform.draw_background()

    def _create_file_list(self):
        """Create file list view."""
        self.file_list = FileListView(
            Layout.LIST_X,
            Layout.LIST_Y,
            Layout.LIST_WIDTH,
            Layout.LIST_HEIGHT,
            on_select=self._on_file_select
        )
        self.refresh_file_list()

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = StatusBar(
            Layout.STATUS_X,
            Layout.STATUS_Y,
            Layout.STATUS_WIDTH,
            50
        )
        self.status_bar.draw()

    def _create_buttons(self):
        """Create control buttons with Latin labels."""
        button_y = Layout.BUTTON_Y
        button_spacing = Layout.BUTTON_WIDTH + Layout.BUTTON_MARGIN

        # Main transport controls (Latin imperatives)
        self.buttons['rec'] = HackerButton(
            40, button_y, Layout.BUTTON_WIDTH, Layout.BUTTON_HEIGHT,
            Text.BTN_REC, on_press=self._on_rec
        )

        self.buttons['stop'] = HackerButton(
            40 + button_spacing, button_y, Layout.BUTTON_WIDTH, Layout.BUTTON_HEIGHT,
            Text.BTN_STOP, on_press=self._on_stop
        )

        self.buttons['play'] = HackerButton(
            40 + button_spacing * 2, button_y, Layout.BUTTON_WIDTH, Layout.BUTTON_HEIGHT,
            Text.BTN_PLAY, on_press=self._on_play
        )

        self.buttons['save'] = HackerButton(
            40 + button_spacing * 3, button_y, Layout.BUTTON_WIDTH, Layout.BUTTON_HEIGHT,
            Text.BTN_SAVE, on_press=self._on_save
        )

        # Speed controls (Latin adverbs)
        speed_btn_width = 100
        speed_btn_height = 60

        self.buttons['slow'] = HackerButton(
            40, button_y - 80, speed_btn_width, speed_btn_height,
            Text.BTN_SLOW, on_press=self._on_slow
        )

        self.buttons['fast'] = HackerButton(
            40 + speed_btn_width + 10, button_y - 80, speed_btn_width, speed_btn_height,
            Text.BTN_FAST, on_press=self._on_fast
        )

        # File controls
        self.buttons['sort'] = HackerButton(
            Layout.LIST_X, button_y, 120, Layout.BUTTON_HEIGHT,
            Text.BTN_SORT, on_press=self._on_sort
        )

        self.buttons['delete'] = HackerButton(
            Layout.LIST_X + 130, button_y, 120, Layout.BUTTON_HEIGHT,
            Text.BTN_DELETE, on_press=self._on_delete
        )

        # Exit button (EXĪ) — top-right of the header, returns to Launcher
        self.buttons['exit'] = HackerButton(
            SCREEN_WIDTH - 110, 10, 90, 40,
            Text.BTN_EXIT, on_press=self._on_exit_pressed
        )

        # Draw all buttons
        for btn in self.buttons.values():
            btn.draw()

    def _on_rec(self):
        """Handle SCRĪBE (record) button press."""
        if self.audio.is_idle:
            self.audio.start_recording()
            self.buttons['rec'].set_active(True)
            self.status_bar.set_status(Text.STATUS_RECORDING)

    def _on_stop(self):
        """Handle DĒSINE (stop) button press."""
        if self.audio.is_recording:
            self._stop_was_manual = True
            self.audio.stop_recording()
            self.buttons['rec'].set_active(False)
            self.status_bar.set_status(Text.STATUS_STOPPED)
            self.status_bar.set_recording_time(0)
        elif self.audio.is_playing or self.audio.is_paused:
            self._stop_was_manual = True
            self.audio.stop()
            self.buttons['play'].set_active(False)
            self.buttons['play'].set_label(Text.BTN_PLAY)
            self.status_bar.set_status(Text.STATUS_STOPPED)

    def _on_play(self):
        """Handle RECITĀ (play) button press."""
        if self.audio.is_paused:
            self.audio.resume()
            self.buttons['play'].set_label(Text.BTN_PAUSE)
            self.status_bar.set_status(Text.STATUS_PLAYING)
        elif self.audio.is_playing:
            self.audio.pause()
            self.buttons['play'].set_label(Text.BTN_PLAY)
            self.status_bar.set_status(Text.STATUS_PAUSED)
        elif self.audio.is_idle:
            # Play buffer if available, else play selected file
            if self.audio.has_unsaved_recording():
                self.audio.play_buffer()
            else:
                selected = self.file_list.get_selected()
                if selected:
                    self.audio.play_file(selected.filepath)

            if self.audio.is_playing:
                self.buttons['play'].set_active(True)
                self.buttons['play'].set_label(Text.BTN_PAUSE)
                self.status_bar.set_status(Text.STATUS_PLAYING)

    def _on_save(self):
        """Handle SERVĀ (save) button press."""
        if self.audio.has_unsaved_recording():
            self.status_bar.set_status(Text.STATUS_SAVING)
            filename = self.files.generate_filename()
            filepath = self.audio.save_recording(filename)
            if filepath:
                self.status_bar.set_status(Text.STATUS_READY)
                self.refresh_file_list()
            else:
                self.status_bar.set_status(Text.STATUS_ERROR.format("Servāre nōn potuit"))

    def _on_slow(self):
        """Handle TARDĒ (slow) button press — toggles slow / normal speed."""
        if self.buttons['slow'].is_active:
            self.audio.set_speed_normal()
            self.buttons['slow'].set_active(False)
        else:
            self.audio.set_speed_slow()
            self.buttons['slow'].set_active(True)
            self.buttons['fast'].set_active(False)

    def _on_fast(self):
        """Handle CELER (fast) button press — toggles fast / normal speed."""
        if self.buttons['fast'].is_active:
            self.audio.set_speed_normal()
            self.buttons['fast'].set_active(False)
        else:
            self.audio.set_speed_fast()
            self.buttons['fast'].set_active(True)
            self.buttons['slow'].set_active(False)

    def _on_sort(self):
        """Handle ŌRDŌ (sort) button press."""
        mode = self.files.cycle_sort()
        self.buttons['sort'].set_label(self.files.get_sort_label())
        self.refresh_file_list()

    def _on_delete(self):
        """Handle DĒLĒ (delete) button press."""
        selected = self.file_list.get_selected()
        if selected:
            if self.files.delete_recording(selected):
                self.refresh_file_list()
                self.status_bar.set_status(Text.STATUS_READY)
            else:
                self.status_bar.set_status(Text.STATUS_ERROR.format("Dēlēre nōn potuit"))

    def _on_file_select(self, recording):
        """Handle file selection in list."""
        if DEBUG:
            print(f">>> Selected: {recording.name}")

    def _on_exit_pressed(self):
        """Handle EXĪ (exit) button — hand back to the caller to leave the app."""
        if self._on_exit:
            self._on_exit()

    def refresh_file_list(self):
        """Refresh the file list from disk."""
        recordings = self.files.refresh()
        if self.file_list:
            self.file_list.set_items(recordings)

    def handle_touch(self, x, y):
        """Handle touch event."""
        # Check buttons
        for btn in self.buttons.values():
            if btn.check_touch(x, y):
                return True

        # Check file list
        if self.file_list and self.file_list.check_touch(x, y):
            return True

        return False

    def handle_touch_release(self):
        """Handle touch release."""
        for btn in self.buttons.values():
            btn.release()

    def _reconcile_state(self):
        """Sync transport buttons/status to the engine's actual state.

        Catches transitions the press handlers can't see — playback finishing
        on its own, or recording auto-stopping at the duration cap.
        """
        is_idle = self.audio.is_idle
        if is_idle and not self._prev_idle:
            if 'play' in self.buttons:
                self.buttons['play'].set_active(False)
                self.buttons['play'].set_label(Text.BTN_PLAY)
            if 'rec' in self.buttons:
                self.buttons['rec'].set_active(False)
            if self.status_bar:
                self.status_bar.set_recording_time(0)
                # Preserve DĒSIĪ on a manual stop; show PARĀTUS otherwise.
                if self._stop_was_manual:
                    self._stop_was_manual = False
                else:
                    self.status_bar.set_status(Text.STATUS_READY)
        self._prev_idle = is_idle

    def update(self):
        """Main update loop - call frequently."""
        if not self._initialized:
            return

        # Drive the engine every frame: level metering while recording AND
        # end-of-playback detection while playing.
        level = self.audio.update()

        if self.audio.is_recording:
            if self.waveform:
                self.waveform.update(level)
            if self.status_bar:
                self.status_bar.set_recording_time(self.audio.recording_duration)

        # Reconcile transport controls with the engine's actual state
        # (resets play/rec buttons + status when playback or recording ends).
        self._reconcile_state()

        # Update status blink
        if self.status_bar:
            self.status_bar.update_blink()

        # Check for touch — edge-triggered + debounced so one tap fires
        # on_press exactly once (the loop polls every WAVE_UPDATE_MS).
        if HARDWARE_AVAILABLE:
            try:
                M5.update()
                if M5.Touch.getCount() > 0:
                    if not self._touch_active:
                        now = _now_ms()
                        if now - self._last_touch_ms >= Timing.BUTTON_DEBOUNCE_MS:
                            self._touch_active = True
                            self._last_touch_ms = now
                            self.handle_touch(M5.Touch.getX(), M5.Touch.getY())
                else:
                    if self._touch_active:
                        self._touch_active = False
                        self.handle_touch_release()
            except Exception:
                pass
