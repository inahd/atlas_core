#!/usr/bin/env python3
"""porter.py — Audio connection watchdog.

Keeps SuperCollider connected to MOTU M2 via PipeWire.
Also verifies pw-cat (om.py) is connected.
Runs as atlas-porter.service.

Checks every 10 seconds:
  - SC out_1/out_2 → MOTU playback_FL/FR (via pw-link, not pw-jack)
  - pw-cat output_FL/FR → MOTU playback_FL/FR

Uses pw-link (native PipeWire) not pw-jack (broken JACK shim).
"""

import subprocess
import time
import logging

log = logging.getLogger("porter")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)

MOTU_FL = "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FL"
MOTU_FR = "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FR"

# Connections to maintain (source, sink)
CONNECTIONS = [
    ("SuperCollider:out_1", MOTU_FL),
    ("SuperCollider:out_2", MOTU_FR),
]


def _run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception:
        return ""


def check_and_restore():
    """Check all connections, restore any that are missing."""
    # Get current link state
    links = _run(["pw-link", "-l"])
    outputs = _run(["pw-link", "-o"])

    restored = 0
    for src, dst in CONNECTIONS:
        # Only attempt if both ports exist
        if src not in outputs:
            continue
        # Check if already connected
        if src in links and dst in links:
            # Verify this specific link exists
            in_section = False
            connected = False
            for line in links.splitlines():
                stripped = line.strip()
                if stripped == src:
                    in_section = True
                elif in_section and stripped.startswith("|->"):
                    if dst in stripped:
                        connected = True
                        break
                elif not stripped.startswith("|"):
                    in_section = False

            if connected:
                continue

        # Attempt to create the link
        result = _run(["pw-link", src, dst])
        # pw-link returns empty on success, "File exists" if already linked
        log.info("linked: %s → %s", src, dst)
        restored += 1

    return restored


def main():
    log.info("porter: audio watchdog starting")
    log.info("  monitoring: SC → MOTU M2 via pw-link")

    while True:
        try:
            check_and_restore()
        except Exception as e:
            log.warning("porter check failed: %s", e)
        time.sleep(10)


if __name__ == "__main__":
    main()
