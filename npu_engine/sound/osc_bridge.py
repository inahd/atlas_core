"""
osc_bridge.py — Sends derive_sound_spec() output to SuperCollider.

Fires all osc_messages from a sound spec to sclang on 127.0.0.1:57120.
Called by kernel.py on field update and on mode change.
"""

import logging

log = logging.getLogger(__name__)

SC_HOST = "127.0.0.1"
SC_PORT = 57120

_client = None


def _get_client():
    """Lazy-init OSC client."""
    global _client
    if _client is None:
        try:
            from pythonosc import udp_client
            _client = udp_client.SimpleUDPClient(SC_HOST, SC_PORT)
        except ImportError:
            log.warning("pythonosc not installed — OSC bridge disabled")
            return None
    return _client


def send_sound_spec(spec: dict) -> bool:
    """Fire all osc_messages from a sound spec to SC.

    Args:
        spec: output of derive_sound_spec() — must contain 'osc_messages' list.
              Each message: [osc_address, [arg1, arg2, ...]]

    Returns:
        True if all messages sent, False on any failure.
    """
    client = _get_client()
    if client is None:
        return False

    messages = spec.get("osc_messages", [])
    if not messages:
        return True

    try:
        for msg in messages:
            addr = msg[0]
            args = msg[1] if len(msg) > 1 else []
            client.send_message(addr, args)
        return True
    except Exception as e:
        log.warning("osc_bridge send failed: %s", e)
        return False
