"""
melody_engine.py — Continuous melodic phrase playback loop.

Generates raga phrases from field state via raga_engine,
sends them to SuperCollider via OSC, waits for completion,
then generates the next phrase. Loops until stopped.

Phrases alternate between aroha, avaroha, and pakad,
weighted by time of day and rasa.
"""

import logging
import random
import threading
import time
from typing import Optional

log = logging.getLogger(__name__)

SC_HOST = "127.0.0.1"
SC_PORT = 57120

_playing = False
_thread: Optional[threading.Thread] = None
_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            from pythonosc.udp_client import SimpleUDPClient
            _client = SimpleUDPClient(SC_HOST, SC_PORT)
        except ImportError:
            log.warning("pythonosc not installed")
            return None
    return _client


def _send_phrase_osc(osc_messages: list):
    """Send a sequence of OSC phrase messages to SC."""
    client = _get_client()
    if not client:
        return

    for msg in osc_messages:
        addr = msg[0]  # '/atlas/phrase'
        args = msg[1]  # [freq1, freq2, freq3, dur1, dur2, dur3, ...]
        try:
            client.send_message(addr, [float(a) for a in args])
        except Exception as e:
            log.warning("melody OSC send failed: %s", e)


def _phrase_loop(field_state: dict):
    """Main melody loop — generates and sends phrases until stopped."""
    global _playing

    from npu_engine.sound.raga_engine import derive_raga_phrase

    log.info("Melody loop started — raga: %s",
             field_state.get("sound_state", {}).get("raga", "?"))

    # Notify SC
    client = _get_client()
    if client:
        client.send_message("/atlas/santoor/start", [])

    cycle_count = 0

    while _playing:
        try:
            # Generate phrase
            phrase = derive_raga_phrase(field_state)
            osc_messages = phrase.get("osc_messages", [])

            if not osc_messages:
                time.sleep(1.0)
                continue

            # Send all phrase segments
            _send_phrase_osc(osc_messages)

            # Calculate total phrase duration
            total_dur = 0
            for msg in osc_messages:
                args = msg[1]
                # args: [f1, f2, f3, d1, d2, d3, ...]
                if len(args) >= 6:
                    total_dur += args[3] + args[4] + args[5]  # dur1 + dur2 + dur3

            # Wait for phrase to complete
            time.sleep(max(0.5, total_dur))

            # Brief silence — 0.5 to 1 beat
            bpm = field_state.get("sound_state", {}).get("bpm", 84)
            if isinstance(bpm, str):
                try:
                    bpm = float(bpm)
                except ValueError:
                    bpm = 84
            beat_dur = 60.0 / max(bpm, 30)
            silence = random.uniform(beat_dur * 0.5, beat_dur * 1.5)
            time.sleep(silence)

            cycle_count += 1

            # Refresh field state every 10 phrases
            if cycle_count % 10 == 0:
                try:
                    import urllib.request
                    import json
                    with urllib.request.urlopen("http://localhost:5000/field", timeout=3) as r:
                        field_state = json.load(r)
                    # Also get svarodaya
                    try:
                        with urllib.request.urlopen("http://localhost:5000/svarodaya", timeout=3) as r2:
                            field_state["svarodaya"] = json.load(r2)
                    except Exception:
                        pass
                except Exception:
                    pass  # keep using old field state

        except Exception as e:
            log.warning("melody loop error: %s", e)
            time.sleep(1.0)

    # Notify SC stopped
    if client:
        client.send_message("/atlas/santoor/stop", [])
    log.info("Melody loop stopped after %d phrases", cycle_count)


def start_melody(field_state: dict):
    """Start the continuous melody loop."""
    global _playing, _thread
    if _playing:
        return
    _playing = True
    _thread = threading.Thread(
        target=_phrase_loop,
        args=(field_state,),
        daemon=True,
    )
    _thread.start()


def stop_melody():
    """Stop the melody loop."""
    global _playing
    _playing = False


def is_playing() -> bool:
    return _playing
