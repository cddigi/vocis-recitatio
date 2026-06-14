"""
VŌCIS RECITĀTIŌ File Manager
=============================
Recording file management, sorting, and metadata.

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.
"""

import os
import time
from config import Files, Audio, DEBUG


class RecordingInfo:
    """Information about a single recording (recitātiō)."""

    def __init__(self, filepath, name, size, modified_time):
        self.filepath = filepath
        self.name = name
        self.size = size  # bytes
        self.modified_time = modified_time  # unix timestamp

    @property
    def size_str(self):
        """Human-readable file size."""
        if self.size < 1024:
            return f"{self.size}B"
        elif self.size < 1024 * 1024:
            return f"{self.size // 1024}KB"
        else:
            return f"{self.size // (1024 * 1024)}MB"

    @property
    def date_str(self):
        """Human-readable date string."""
        try:
            t = time.localtime(self.modified_time)
            return f"{t[1]:02d}/{t[2]:02d} {t[3]:02d}:{t[4]:02d}"
        except Exception:
            return "--/-- --:--"

    @property
    def duration_estimate(self):
        """Estimated duration based on file size."""
        # WAV: sample_rate * channels * bytes_per_sample * seconds
        bytes_per_second = Audio.SAMPLE_RATE * (1 if not Audio.STEREO else 2) * (Audio.BIT_DEPTH // 8)
        # Subtract WAV header (44 bytes)
        audio_bytes = max(0, self.size - 44)
        seconds = audio_bytes / bytes_per_second
        return seconds

    @property
    def duration_str(self):
        """Human-readable duration estimate."""
        secs = int(self.duration_estimate)
        mins = secs // 60
        secs = secs % 60
        return f"{mins}:{secs:02d}"

    def __repr__(self):
        return f"Recitatio({self.name}, {self.size_str}, {self.date_str})"


class FileManager:
    """
    Manages recording files on the SD card.

    Handles:
    - Listing recitationes (recordings)
    - Sorting by date/name/size (ōrdō)
    - Deleting recordings (dēlēre)
    - Generating unique filenames
    """

    def __init__(self):
        self._recordings = []
        self._sort_mode = Files.DEFAULT_SORT
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure app directories exist on SD card."""
        try:
            # Check if SD card is mounted
            if not self._is_sd_mounted():
                if DEBUG:
                    print(">>> WARNING: SD card not mounted")
                return False

            # Create app folder
            self._mkdir_if_needed(Files.APP_FOLDER)

            # Create recordings folder (recitationes)
            self._mkdir_if_needed(Files.RECORDINGS_FOLDER)

            if DEBUG:
                print(f">>> Directories ready: {Files.RECORDINGS_FOLDER}")
            return True

        except Exception as e:
            if DEBUG:
                print(f">>> ERROR creating directories: {e}")
            return False

    def _is_sd_mounted(self):
        """Check if SD card is mounted."""
        try:
            os.listdir(Files.SD_ROOT)
            return True
        except OSError:
            return False

    def _mkdir_if_needed(self, path):
        """Create directory if it doesn't exist."""
        try:
            os.stat(path)
        except OSError:
            # Directory doesn't exist, create it
            parts = path.split('/')
            current = ''
            for part in parts:
                if part:
                    current += '/' + part
                    try:
                        os.stat(current)
                    except OSError:
                        os.mkdir(current)

    def refresh(self):
        """Scan the recordings folder and update the file list."""
        self._recordings = []

        if not self._is_sd_mounted():
            if DEBUG:
                print(">>> Cannot refresh: SD card not mounted")
            return []

        try:
            files = os.listdir(Files.RECORDINGS_FOLDER)

            for filename in files:
                # Only include audio files
                if not filename.endswith(('.wav', '.amr', '.mp3')):
                    continue

                filepath = f"{Files.RECORDINGS_FOLDER}/{filename}"

                try:
                    stat = os.stat(filepath)
                    size = stat[6]  # File size
                    mtime = stat[8]  # Modified time

                    info = RecordingInfo(
                        filepath=filepath,
                        name=filename,
                        size=size,
                        modified_time=mtime
                    )
                    self._recordings.append(info)

                except OSError as e:
                    if DEBUG:
                        print(f">>> ERROR reading {filename}: {e}")

            # Apply current sort
            self._apply_sort()

            if DEBUG:
                print(f">>> Found {len(self._recordings)} recitationes")

        except OSError as e:
            if DEBUG:
                print(f">>> ERROR scanning recordings: {e}")

        return self._recordings

    def _apply_sort(self):
        """Sort recordings based on current sort mode (ōrdō)."""
        if self._sort_mode == Files.SORT_DATE_DESC:
            self._recordings.sort(key=lambda r: r.modified_time, reverse=True)
        elif self._sort_mode == Files.SORT_DATE_ASC:
            self._recordings.sort(key=lambda r: r.modified_time)
        elif self._sort_mode == Files.SORT_NAME_ASC:
            self._recordings.sort(key=lambda r: r.name.lower())
        elif self._sort_mode == Files.SORT_NAME_DESC:
            self._recordings.sort(key=lambda r: r.name.lower(), reverse=True)
        elif self._sort_mode == Files.SORT_SIZE_DESC:
            self._recordings.sort(key=lambda r: r.size, reverse=True)
        elif self._sort_mode == Files.SORT_SIZE_ASC:
            self._recordings.sort(key=lambda r: r.size)

    @property
    def recordings(self):
        """List of RecordingInfo objects (recitationes)."""
        return self._recordings

    @property
    def recording_count(self):
        """Number of recordings."""
        return len(self._recordings)

    @property
    def sort_mode(self):
        """Current sort mode (ōrdō)."""
        return self._sort_mode

    def set_sort(self, mode):
        """
        Set the sort mode and re-sort.

        Args:
            mode: One of Files.SORT_* constants
        """
        self._sort_mode = mode
        self._apply_sort()
        if DEBUG:
            print(f">>> Ōrdō: {mode}")

    def cycle_sort(self):
        """Cycle through sort modes."""
        modes = [
            Files.SORT_DATE_DESC,
            Files.SORT_DATE_ASC,
            Files.SORT_NAME_ASC,
            Files.SORT_NAME_DESC,
            Files.SORT_SIZE_DESC,
            Files.SORT_SIZE_ASC,
        ]
        try:
            idx = modes.index(self._sort_mode)
            self._sort_mode = modes[(idx + 1) % len(modes)]
        except ValueError:
            self._sort_mode = modes[0]

        self._apply_sort()
        return self._sort_mode

    def get_sort_label(self):
        """Get human-readable sort mode label."""
        labels = {
            Files.SORT_DATE_DESC: "DIĒS ↓",
            Files.SORT_DATE_ASC: "DIĒS ↑",
            Files.SORT_NAME_ASC: "NŌMEN A-Z",
            Files.SORT_NAME_DESC: "NŌMEN Z-A",
            Files.SORT_SIZE_DESC: "MAG ↓",
            Files.SORT_SIZE_ASC: "MAG ↑",
        }
        return labels.get(self._sort_mode, "---")

    def delete_recording(self, recording):
        """
        Delete a recording file (dēlēre).

        Args:
            recording: RecordingInfo object or filepath string

        Returns:
            True if deleted successfully
        """
        if isinstance(recording, RecordingInfo):
            filepath = recording.filepath
        else:
            filepath = recording

        try:
            os.remove(filepath)
            # Remove from list
            self._recordings = [r for r in self._recordings if r.filepath != filepath]
            if DEBUG:
                print(f">>> Dēlētum: {filepath}")
            return True
        except OSError as e:
            if DEBUG:
                print(f">>> ERROR deleting {filepath}: {e}")
            return False

    def generate_filename(self, prefix=None):
        """
        Generate a unique filename for a new recording.

        Args:
            prefix: Optional prefix (default: from config)

        Returns:
            Unique filename (without path or extension)
        """
        prefix = prefix or Audio.FILE_PREFIX

        # Use timestamp for uniqueness
        try:
            t = time.localtime()
            timestamp = f"{t[0]}{t[1]:02d}{t[2]:02d}_{t[3]:02d}{t[4]:02d}{t[5]:02d}"
        except Exception:
            timestamp = str(int(time.time()))

        filename = f"{prefix}{timestamp}"

        # Verify it doesn't exist
        full_path = f"{Files.RECORDINGS_FOLDER}/{filename}.{Audio.FILE_FORMAT}"
        counter = 1
        while self._file_exists(full_path):
            filename = f"{prefix}{timestamp}_{counter}"
            full_path = f"{Files.RECORDINGS_FOLDER}/{filename}.{Audio.FILE_FORMAT}"
            counter += 1

        return filename

    def _file_exists(self, filepath):
        """Check if a file exists."""
        try:
            os.stat(filepath)
            return True
        except OSError:
            return False

    def get_recording_by_index(self, index):
        """Get a recording by its index in the list."""
        if 0 <= index < len(self._recordings):
            return self._recordings[index]
        return None

    def get_recording_by_name(self, name):
        """Get a recording by filename."""
        for rec in self._recordings:
            if rec.name == name:
                return rec
        return None

    def get_total_size(self):
        """Get total size of all recordings."""
        return sum(r.size for r in self._recordings)

    def get_total_size_str(self):
        """Get human-readable total size."""
        total = self.get_total_size()
        if total < 1024:
            return f"{total}B"
        elif total < 1024 * 1024:
            return f"{total // 1024}KB"
        else:
            return f"{total // (1024 * 1024)}MB"

    def is_sd_available(self):
        """Check if SD card is available."""
        return self._is_sd_mounted()
