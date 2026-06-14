# CLAUDE.md

## Project Overview

Vōcis Recitātiō — a TalkBoy-style voice recorder for the M5Stack M5Tab5
(ESP32-P4), with a *Hackers* (1995) cyberpunk aesthetic and a Classical Latin
interface. Records from the dual-mic array and plays back at variable speed for
the classic deep-voice / chipmunk-voice effect.

Hobby project, built for my son to play with. Prioritize fun, reliability, and
simplicity over enterprise patterns. Don't over-engineer.

## Stack

- **Language:** MicroPython (the whole codebase is Python — keep it that way)
- **Runtime:** UIFlow2 firmware on the M5Tab5
- **Distribution:** runs as a Launcher app (bmorcelli/Launcher) off the SD card
- The APP SOURCE is NOT an Arduino/C++ project. Do not suggest M5Unified,
  M5GFX, arduino-cli, or .ino sketches for the app. Use the UIFlow2 `M5`
  MicroPython module. (The prebuilt `firmware/` image is a separate, legit
  flashable artifact — this rule is about keeping app code pure Python.)

## Hardware

- M5Stack M5Tab5: ESP32-P4, 1280x720 5" IPS touchscreen, ES8388 codec,
  ES7210 AEC dual-mic front-end, microSD slot, onboard speaker
- The mic and speaker CANNOT run at the same time. Always tear down one path
  before starting the other (end recording before playback, and vice versa).

## File Structure

```
vocis-recitatio/
├── boot.py              # Launcher entry shim — puts src/ on sys.path,
│                        #   then runs src/main.py (manifest "main": "boot.py")
├── manifest.json        # Launcher metadata
├── docs/
│   └── ux-mockup.svg    # UX mockup (1280x720 CRT-terminal layout)
├── firmware/            # gitignored — local build artifact, not committed
│   └── vocis-recitatio-tab5.bin  # compiled flashable image (do not hand-edit)
├── UNLICENSE            # Public domain dedication
└── README.md
```

The app code lives in `src/`; `boot.py` at the repo root is just the Launcher
entry shim (it adds `src/` to `sys.path` so the flat sibling imports keep
working, then calls `src/main.py`). Don't move `boot.py` into `src/` — the
Launcher and `manifest.json` expect it at the root.

Keep responsibilities in their existing module — audio logic in
`src/audio_engine.py`, all drawing/touch in `src/ui.py`, SD operations in
`src/file_manager.py`, tunables in `src/config.py`. Don't scatter constants;
they live in `src/config.py`.

### firmware/vocis-recitatio-tab5.bin

A ~10.9 MB compiled UIFlow2 image with the app baked in — a direct-flash
alternative to the Launcher-off-SD distribution (flash it and the toy just
runs). It's a generated build artifact: regenerate it by recompiling, never
by hand-editing. It is gitignored (`firmware/`) and NOT committed — rebuild
it locally rather than expecting it from the repo, and don't re-add it to
version control.

## Audio Engine Notes

- Recordings: 16-bit PCM, 16 kHz, mono, saved as WAV
- Saved to `/sd/vocis-recitatio/recitationes/` with filenames
  `vocis_YYYYMMDD_HHMMSS.wav`
- Variable-speed playback is achieved by changing the PLAYBACK SAMPLE RATE, not
  by DSP pitch-shifting. This is the whole point of the toy and mirrors how the
  original cassette TalkBoy worked. Do not add pitch-shift libraries.
  - TARDĒ = 0.5x → vōx gravis (deep)
  - Normal = 1.0x
  - CELER = 1.5x → vōx acūta (high)

### Public APIs (keep these stable)

```python
# src/audio_engine.py
engine.start_recording()
engine.stop_recording()
engine.save_recording("name")
engine.play_file("/path")
engine.set_speed_slow()   # 0.5x
engine.set_speed_fast()   # 1.5x

# src/file_manager.py
files.refresh()                 # returns recordings list
files.set_sort("date_desc")
files.delete_recording(rec)
```

## Latin Interface Conventions

The UI uses Classical Latin imperative verbs and first-person status messages.
Preserve this — it's the soul of the project. When adding UI elements, match the
established vocabulary and macron usage (ā, ē, ī, ō, ū).

Buttons: SCRĪBE (record), RECITĀ (play), DĒSINE (stop), SERVĀ (save),
TARDĒ (slow), CELER (fast), ŌRDŌ (sort), DĒLĒ (delete).

Status messages are first-person Latin: `PARĀTUS_` (ready), `SCRĪBŌ...`
(recording, "I am writing"), `RECITŌ...` (playing, "I am reciting"),
`INTERMISSIŌ` (paused), `DĒSIĪ` (stopped), `SERVŌ AD DISCUM...` (saving).

If you add new strings, get the Latin right (correct case, mood, and macrons);
ask me if unsure rather than inventing dog-Latin.

## UI Style

- Green phosphor terminal text on black, neon cyan/magenta/yellow accents
- Matrix-style waveform visualization, blinking terminal cursor
- "Hack the Planet" energy; skeuomorphic where it's fun
- Big touch targets — the user is a child, so keep buttons large

## Workflow

- Test on device through UIFlow2 / the Launcher; there's no desktop simulator
  for the audio path
- For pushing files to the device, an `mpremote`-style copy works, or copy the
  folder onto the SD card for Launcher
- Keep `manifest.json` in sync when files or app metadata change

## Sub-agent Handoff

The modules are cleanly separated, so parallel sub-agents work well *when it
makes sense* — i.e. when the changes land in DIFFERENT files (audio in
`src/audio_engine.py`, UI/drawing/touch in `src/ui.py`, SD ops in
`src/file_manager.py`, tunables in `src/config.py`). Independent work in
separate modules can run in
parallel safely. Changes that touch the SAME file should go to a single agent
to avoid conflicting edits. Doc-only edits to `CLAUDE.md` / `README.md` can
run alongside code edits without stepping on anything.

## License

Released under the UNLICENSE (public domain). Do NOT add copyright headers,
license boilerplate, or attribution comments to source files — the single
UNLICENSE file at the repo root covers everything. Any third-party code must be
public-domain-compatible (no GPL/copyleft snippets).

## Things NOT To Do

- Don't run mic and speaker simultaneously (hardware constraint)
- Don't convert the app source to Arduino/C++ or add a second app toolchain
  (the prebuilt `firmware/` .bin is fine — it's a flashable build artifact)
- Don't add pitch-shift DSP — sample-rate change IS the effect
- Don't add networking, telemetry, accounts, or cloud features — it's a toy
- Don't add per-file license/copyright headers
- Don't write fake or approximate Latin; ask if a form is uncertain
