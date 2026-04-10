"""Shared mutable state for sound routes.

Both kernel.py (_spine) and sound_bp.py read/write these.
"""

sound_mode = "field"
perform_mode = False

# OSC client — initialized once
_osc_client = None
try:
    from pythonosc import udp_client as _osc_udp
    _osc_client = _osc_udp.SimpleUDPClient("127.0.0.1", 57121)
except Exception:
    pass


def send_osc(path, args):
    """Send an OSC message to SuperCollider. Silently fails if unavailable."""
    if _osc_client:
        try:
            _osc_client.send_message(path, args)
        except Exception:
            pass
