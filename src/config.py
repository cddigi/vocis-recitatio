"""
VŌCIS RECITĀTIŌ Configuration
==============================
Hackers (1995) aesthetic - green phosphor, neon accents, terminal vibes.
"Hack the Planet!"

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.
"""

# =============================================================================
# DISPLAY CONFIGURATION (M5Tab5: 1280x720)
# =============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# =============================================================================
# HACKERS (1995) COLOR PALETTE
# =============================================================================
# All colors in 16-bit RGB565 format for LVGL

class Colors:
    """Green phosphor terminal with neon accents."""

    # Primary background - deep black with slight blue tint
    BG_PRIMARY = 0x0000      # Pure black
    BG_SECONDARY = 0x0841    # Very dark gray-blue
    BG_TERMINAL = 0x0020     # Slight green tint black

    # Green phosphor text (the classic terminal look)
    PHOSPHOR_BRIGHT = 0x07E0   # Bright green (main text)
    PHOSPHOR_DIM = 0x0400      # Dim green (secondary)
    PHOSPHOR_GLOW = 0x47E0     # Green with slight yellow (highlight)

    # Neon accents (Hackers movie palette)
    NEON_CYAN = 0x07FF         # Acid cyan
    NEON_MAGENTA = 0xF81F      # Electric magenta
    NEON_YELLOW = 0xFFE0       # Warning yellow
    NEON_ORANGE = 0xFD20       # Alert orange
    NEON_RED = 0xF800          # Error red

    # UI element colors
    BUTTON_BG = 0x0841         # Button background
    BUTTON_BORDER = 0x07E0     # Green border
    BUTTON_ACTIVE = 0x0400     # Pressed state
    BUTTON_TEXT = 0x07E0       # Button text

    # Recording states
    REC_ACTIVE = 0xF800        # Recording indicator (red)
    REC_STANDBY = 0x0400       # Standby (dim green)

    # Playback states
    PLAY_ACTIVE = 0x07E0       # Playing (bright green)
    PLAY_PAUSED = 0xFFE0       # Paused (yellow)

    # Waveform visualization
    WAVE_PRIMARY = 0x07E0      # Main waveform
    WAVE_SECONDARY = 0x07FF    # Secondary/echo
    WAVE_PEAK = 0xFFE0         # Peak indicator

    # File list
    FILE_SELECTED = 0x07FF     # Selected file (cyan)
    FILE_NORMAL = 0x07E0       # Normal file (green)
    FILE_SIZE = 0x0400         # File size (dim)


# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================
class Audio:
    """Audio recording and playback settings."""

    # Recording defaults
    SAMPLE_RATE = 16000        # 16kHz (good for voice)
    BIT_DEPTH = 16             # 16-bit PCM
    STEREO = False             # Mono recording

    # Supported sample rates for speed control
    SAMPLE_RATES = [8000, 11025, 16000, 22050, 32000, 44100]

    # File format
    FILE_FORMAT = "wav"
    FILE_PREFIX = "vocis_"

    # Recording limits
    MAX_RECORDING_TIME = 300   # 5 minutes max
    MIN_RECORDING_TIME = 1     # 1 second min

    # Buffer settings
    BUFFER_SIZE = 4096         # Audio buffer size

    # Volume range
    VOLUME_MIN = 0
    VOLUME_MAX = 100
    VOLUME_DEFAULT = 80

    # Speed control (playback rate multipliers)
    # Latin: tardē (slowly), celeriter (quickly)
    SPEED_SLOW = 0.5           # Half speed (vōx gravis - deep voice)
    SPEED_NORMAL = 1.0         # Normal speed
    SPEED_FAST = 1.5           # Fast (vōx acūta - high voice)
    SPEED_TURBO = 2.0          # Double speed


# =============================================================================
# FILE MANAGEMENT
# =============================================================================
class Files:
    """File storage and organization."""

    # Storage paths
    SD_ROOT = "/sd"
    APP_FOLDER = "/sd/vocis-recitatio"
    RECORDINGS_FOLDER = "/sd/vocis-recitatio/recitationes"
    CONFIG_FILE = "/sd/vocis-recitatio/config.json"

    # Sorting options (Latin: ōrdō = order)
    SORT_DATE_DESC = "date_desc"    # Newest first (default)
    SORT_DATE_ASC = "date_asc"      # Oldest first
    SORT_NAME_ASC = "name_asc"      # A-Z
    SORT_NAME_DESC = "name_desc"    # Z-A
    SORT_SIZE_DESC = "size_desc"    # Largest first
    SORT_SIZE_ASC = "size_asc"      # Smallest first

    DEFAULT_SORT = SORT_DATE_DESC


# =============================================================================
# UI LAYOUT (for 1280x720 display)
# =============================================================================
class Layout:
    """UI element positions and sizes."""

    # Header area
    HEADER_HEIGHT = 60
    HEADER_Y = 0

    # Main control buttons (bottom area)
    BUTTON_HEIGHT = 100
    BUTTON_WIDTH = 180
    BUTTON_MARGIN = 20
    BUTTON_Y = 600

    # Waveform display
    WAVE_X = 40
    WAVE_Y = 80
    WAVE_WIDTH = 800
    WAVE_HEIGHT = 200

    # File list (right panel)
    LIST_X = 880
    LIST_Y = 80
    LIST_WIDTH = 360
    LIST_HEIGHT = 500
    LIST_ITEM_HEIGHT = 50

    # Status display
    STATUS_X = 40
    STATUS_Y = 300
    STATUS_WIDTH = 800
    STATUS_HEIGHT = 280

    # Transport controls (center bottom)
    TRANSPORT_Y = 600
    TRANSPORT_BUTTON_SIZE = 80

    # Volume/Speed sliders
    SLIDER_WIDTH = 300
    SLIDER_HEIGHT = 30


# =============================================================================
# TEXT STRINGS (Latin/English hybrid for that classical hacker vibe)
# =============================================================================
class Text:
    """Text strings and ASCII art for UI."""

    # App title
    TITLE = "VŌCIS RECITĀTIŌ//v1.0"
    SUBTITLE = "[ HACK THE PLANET ]"

    # Status messages (Latin imperatives and gerunds mixed with terminal speak)
    STATUS_READY = ">>> PARĀTUS_"                    # Ready
    STATUS_RECORDING = ">>> SCRĪBŌ..."               # I am writing/recording
    STATUS_PLAYING = ">>> RECITŌ..."                 # I am reciting/playing
    STATUS_PAUSED = ">>> INTERMISSIŌ"                # Pause/intermission
    STATUS_STOPPED = ">>> DĒSIĪ"                     # I have stopped
    STATUS_SAVING = ">>> SERVŌ AD DISCUM..."         # Saving to disk
    STATUS_LOADING = ">>> LEGŌ..."                   # Reading/Loading
    STATUS_ERROR = ">>> ERROR: {}"

    # Button labels (Latin imperatives - commands)
    BTN_REC = "SCRĪBE"      # Write! (Record)
    BTN_STOP = "DĒSINE"     # Stop!
    BTN_PLAY = "RECITĀ"     # Recite! (Play)
    BTN_PAUSE = "INTERMITTE" # Pause!
    BTN_SAVE = "SERVĀ"      # Save!
    BTN_DELETE = "DĒLĒ"     # Delete!
    BTN_SLOW = "TARDĒ"      # Slowly
    BTN_FAST = "CELER"      # Quickly
    BTN_SORT = "ŌRDŌ"       # Order/Sort
    BTN_EXIT = "EXĪ"        # Exit!
    BTN_YES = "ITA"        # Yes (lit. "thus/so")
    BTN_NO = "NŌN"         # No (lit. "not")

    # Control labels
    LBL_VOLUME = "SONITUS"  # "a sound" — volume level label

    # File info
    FILE_INFO = "{name} | {size} | {date}"
    NO_FILES = "[ NŪLLAE RECITĀTIŌNĒS ]"  # No recordings

    # Confirmation prompts
    CONFIRM_DELETE = "DĒLĒRE {filename}? [ITA/NŌN]"  # Delete? Yes/No
    CONFIRM_OVERWRITE = "SUPERSCRIBERE? [ITA/NŌN]"   # Overwrite?


# =============================================================================
# TIMING & ANIMATION
# =============================================================================
class Timing:
    """Animation and timing settings."""

    # UI refresh rates (milliseconds)
    WAVE_UPDATE_MS = 50        # Waveform refresh
    STATUS_BLINK_MS = 500      # Status indicator blink
    BUTTON_DEBOUNCE_MS = 100   # Touch debounce

    # Animation durations
    FADE_DURATION_MS = 200
    SLIDE_DURATION_MS = 300

    # Auto-save delay
    AUTO_SAVE_DELAY_MS = 1000


# =============================================================================
# DEBUG & DEVELOPMENT
# =============================================================================
DEBUG = False
SIMULATE_AUDIO = False  # For testing without hardware
