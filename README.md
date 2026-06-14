# VŌCIS RECITĀTIŌ

```
██╗   ██╗ ██████╗  ██████╗██╗███████╗
██║   ██║██╔═══██╗██╔════╝██║██╔════╝
██║   ██║██║   ██║██║     ██║███████╗
╚██╗ ██╔╝██║   ██║██║     ██║╚════██║
 ╚████╔╝ ╚██████╔╝╚██████╗██║███████║
  ╚═══╝   ╚═════╝  ╚═════╝╚═╝╚══════╝

██████╗ ███████╗ ██████╗██╗████████╗ █████╗ ████████╗██╗ ██████╗
██╔══██╗██╔════╝██╔════╝██║╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔═══██╗
██████╔╝█████╗  ██║     ██║   ██║   ███████║   ██║   ██║██║   ██║
██╔══██╗██╔══╝  ██║     ██║   ██║   ██╔══██║   ██║   ██║██║   ██║
██║  ██║███████╗╚██████╗██║   ██║   ██║  ██║   ██║   ██║╚██████╔╝
╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝

                  [ HACK THE PLANET ]
```

Voice recorder for M5Stack M5Tab5, inspired by the **Talkboy** from _Home Alone 2_,
with a **Hackers (1995)** aesthetic and **Classical Latin** interface.

> _recitātiō vōcis_ — "a recitation of voice"

## Features

| Button     | Latin                  | Meaning       |
| ---------- | ---------------------- | ------------- |
| **SCRĪBE** | _scrībere_ (to write)  | Record        |
| **RECITĀ** | _recitāre_ (to recite) | Play          |
| **DĒSINE** | _dēsinere_ (to stop)   | Stop          |
| **SERVĀ**  | _servāre_ (to save)    | Save          |
| **TARDĒ**  | _tardē_ (slowly)       | Slow playback |
| **CELER**  | _celer_ (quickly)      | Fast playback |
| **ŌRDŌ**   | _ōrdō_ (order)         | Sort files    |
| **DĒLĒ**   | _dēlēre_ (to destroy)  | Delete        |

## Status Messages

| Status    | Latin                | Translation    |
| --------- | -------------------- | -------------- |
| Ready     | `PARĀTUS_`           | Prepared       |
| Recording | `SCRĪBŌ...`          | I am writing   |
| Playing   | `RECITŌ...`          | I am reciting  |
| Paused    | `INTERMISSIŌ`        | Intermission   |
| Stopped   | `DĒSIĪ`              | I have stopped |
| Saving    | `SERVŌ AD DISCUM...` | Saving to disk |

## Hardware Requirements

- **M5Stack M5Tab5** (ESP32-P4)
  - 1280×720 5" IPS touchscreen
  - ES8388 audio codec
  - ES7210 AEC front-end (dual microphones)
  - MicroSD card slot

## Installation

### Via Launcher (Recommended)

1. Copy the `vocis-recitatio` folder to your SD card
2. Launch via [Launcher](https://github.com/bmorcelli/Launcher)

### Direct Flash

1. Install [UIFlow2](https://uiflow2.m5stack.com/) on your M5Tab5
2. Copy all files to the device (keep `boot.py` and `src/` together)
3. Run `boot.py`

## File Structure

```
vocis-recitatio/
├── boot.py              # Launcher entry shim (puts src/ on sys.path)
├── manifest.json        # Launcher metadata ("main": "boot.py")
├── src/
│   ├── main.py          # App entry point
│   ├── vocis_recitatio.py  # Main application class
│   ├── audio_engine.py  # Recording/playback engine
│   ├── ui.py            # Hackers-style touch UI
│   ├── file_manager.py  # SD card file management
│   └── config.py        # Colors, layout, settings
├── docs/
│   └── ux-mockup.svg    # UX mockup (1280x720 layout)
├── firmware/            # compiled flashable image (gitignored, not committed)
├── .gitignore
├── UNLICENSE            # Public domain dedication
└── README.md            # This file
```

## Recordings

Recordings are saved to `/sd/vocis-recitatio/recitationes/` as WAV files:

- Format: 16-bit PCM
- Sample rate: 16kHz
- Channels: Mono

Filenames use the format: `vocis_YYYYMMDD_HHMMSS.wav`

## UI Design

The interface combines **Hackers (1995)** cyberpunk aesthetic with **Classical Latin**:

- Green phosphor terminal text on black
- Neon cyan, magenta, and yellow accents
- Matrix-style waveform visualization
- Terminal cursor blink effects
- Latin imperative verbs for commands
- "Hack the Planet" vibes

## Speed Control

Like the original Talkboy, variable-speed playback:

- **TARDĒ (0.5x)** — _vōx gravis_ (deep voice)
- **Normal (1.0x)** — Standard speed
- **CELER (1.5x)** — _vōx acūta_ (high voice)

## API Reference

### AudioEngine

```python
from audio_engine import AudioEngine

engine = AudioEngine()
engine.start_recording()      # Incipit scrībere
engine.stop_recording()       # Dēsinit scrībere
engine.save_recording("name") # Servat ad discum
engine.play_file("/path")     # Recitat
engine.set_speed_slow()       # Tardē (0.5x)
engine.set_speed_fast()       # Celeriter (1.5x)
```

### FileManager

```python
from file_manager import FileManager

files = FileManager()
recordings = files.refresh()  # Legit discum
files.set_sort("date_desc")   # Ōrdō per diem
files.delete_recording(rec)   # Dēlet recitātiōnem
```

## Etymology

- **vōx, vōcis** (f.) — voice, sound
- **recitātiō, recitātiōnis** (f.) — a reading aloud, recitation
- **vōcis** — genitive singular, "of voice"
- **recitātiō vōcis** — "a recitation of voice" (objective genitive)

## License

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute
this software, either in source code form or as a compiled binary, for any
purpose, commercial or non-commercial, and by any means.

See [UNLICENSE](UNLICENSE) for full details.

## Credits

- Inspired by the [Talkboy](https://en.wikipedia.org/wiki/Talkboy) by Tiger Electronics
- Visual aesthetic from _Hackers_ (1995) directed by Iain Softley
- Built for [M5Stack M5Tab5](https://shop.m5stack.com/products/m5stack-tab5-iot-development-kit-esp32-p4)
- Launcher integration via [bmorcelli/Launcher](https://github.com/bmorcelli/Launcher)

## Links

- [UIFlow2 Documentation](https://uiflow2.m5stack.com/)
- [UIFlow MicroPython Docs](https://uiflow-micropython.readthedocs.io/)
- [M5Stack GitHub](https://github.com/m5stack/uiflow-micropython)

---

_"Mess with the best, die like the rest."_ — Hackers (1995)

_"Certā cum optimīs, morere cum cēterīs."_ — (rough Latin equivalent)

# vocis-recitatio
