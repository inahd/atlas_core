"""Shared mutable state for sound routes.

Both kernel.py (_spine) and sound_bp.py read/write these.
"""

sound_mode = "field"
perform_mode = False

# SuperCollider state — updated by sc/start_atlas.sh via /sound/sc_ready
sc_state = {"status": "unknown", "port": 57110}

# OSC client — initialized once
_osc_client = None
try:
    from pythonosc import udp_client as _osc_udp
    _osc_client = _osc_udp.SimpleUDPClient("127.0.0.1", 57120)
except Exception:
    pass


def send_osc(path, args):
    """Send an OSC message to SuperCollider. Silently fails if unavailable."""
    if _osc_client:
        try:
            _osc_client.send_message(path, args)
        except Exception:
            pass
