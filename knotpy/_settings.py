"""
Global settings/flags of KnotPy.
"""

import re

_DEFAULT_ALLOWED_MOVES = ["R1", "R2", "R3"]
_EXISTING_REIDEMEISTER_MOVES = ["R1", "R2", "R3", "R4", "R5", "FLIP"]

_DEFAULT_TRACE_REIDEMEISTER_MOVES = True  # default
_DEFAULT_ALLOW_R4_ONLY_ON_TRIVALENT_VERTICES = False  # default moves

def _clean_allowed_moves(allowed_moves) -> list:
    """From the input parameter, e.g. "R1,R2,R3" or {"R1", "R2", "R3"}, return a set of allowed moves as a a set of ."""

    # If no moves are given, set it at the default (R1, R2, R3)
    if allowed_moves is None:
        return list(_DEFAULT_ALLOWED_MOVES)

    # If string is given, parse from string
    if isinstance(allowed_moves, str):
        allowed_moves = allowed_moves.split(",")

    # Clean the set
    allowed_moves = [re.sub(r'[^A-Za-z0-9]', '', s).upper() for s in allowed_moves]
    allowed_moves = {s for s in allowed_moves if s}

    if not allowed_moves.issubset(_EXISTING_REIDEMEISTER_MOVES):
        raise ValueError(f"Unknown (Reidemeister) modes {allowed_moves - _EXISTING_REIDEMEISTER_MOVES}")

    return list(allowed_moves)


# Use descriptors
class SettingProxyBool:

    def __init__(self, default_value):
        self._value = default_value

    def __get__(self, obj, objtype=None):
        return self._value

    def __set__(self, obj, value):
        if value not in [True, False]:
            raise ValueError("Value must be True or False")
        self._value = value


class SettingProxyReidemeisterMoves:

    def __init__(self, default_value):
        self._value = _clean_allowed_moves(default_value)

    def __get__(self, obj, objtype=None):
        return self._value

    def __set__(self, obj, value):
        self._value = _clean_allowed_moves(value)

class Settings:
    allowed_reidemeister_moves = SettingProxyReidemeisterMoves(_DEFAULT_ALLOWED_MOVES)
    trace_reidemeister_moves = SettingProxyBool(_DEFAULT_TRACE_REIDEMEISTER_MOVES)
    allow_reidemeister_5_only_on_trivalent_vertices = SettingProxyBool(_DEFAULT_ALLOW_R4_ONLY_ON_TRIVALENT_VERTICES)

settings = Settings()

if __name__ == "__main__":
    print(settings.allowed_reidemeister_moves)
    settings.allowed_reidemeister_moves = "R1,R2"
    print(settings.allowed_reidemeister_moves)