"""
VŌCIS RECITĀTIŌ for M5Stack M5Tab5
===================================
App entry point. This is the Launcher "main" (manifest -> src/main.py); the
Launcher runs it directly from the src/ folder.

Voice recorder inspired by the Talkboy from Home Alone 2,
with a Hackers (1995) aesthetic and Classical Latin interface.

Hardware: M5Stack M5Tab5 (ESP32-P4)
Display: 1280x720 IPS LCD
Audio: ES8388 codec, ES7210 AEC, dual microphones

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.

Repository: https://github.com/cddigi/vocis-recitatio
License: UNLICENSE (Public Domain)
"""

# ============================================================================
# VŌCIS RECITĀTIŌ LAUNCHER ENTRY
# ============================================================================
#
#  ██╗   ██╗ ██████╗  ██████╗██╗███████╗
#  ██║   ██║██╔═══██╗██╔════╝██║██╔════╝
#  ██║   ██║██║   ██║██║     ██║███████╗
#  ╚██╗ ██╔╝██║   ██║██║     ██║╚════██║
#   ╚████╔╝ ╚██████╔╝╚██████╗██║███████║
#    ╚═══╝   ╚═════╝  ╚═════╝╚═╝╚══════╝
#
#  ██████╗ ███████╗ ██████╗██╗████████╗ █████╗ ████████╗██╗ ██████╗
#  ██╔══██╗██╔════╝██╔════╝██║╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔═══██╗
#  ██████╔╝█████╗  ██║     ██║   ██║   ███████║   ██║   ██║██║   ██║
#  ██╔══██╗██╔══╝  ██║     ██║   ██║   ██╔══██║   ██║   ██║██║   ██║
#  ██║  ██║███████╗╚██████╗██║   ██║   ██║  ██║   ██║   ██║╚██████╔╝
#  ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝
#
#                    [ HACK THE PLANET ]
#
# ============================================================================

from vocis_recitatio import main

if __name__ == "__main__":
    main()
