# Simple in-memory threat state (per session / global)

CURRENT_THREAT_LEVEL = "LOW"

def set_threat_level(level: str):
    global CURRENT_THREAT_LEVEL
    CURRENT_THREAT_LEVEL = level


def get_threat_level():
    return CURRENT_THREAT_LEVEL
