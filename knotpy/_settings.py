"""
Global settings/flags of KnotPy.
"""

import re

_DEFAULT_ALLOWED_MOVES = ["R1", "R2", "R3"]
_ALLOWED_REIDEMEISTER_MOVES = ["R1", "R2", "R3"]  # default moves
_EXISTING_REIDEMEISTER_MOVES = ["R1", "R2", "R3", "R4", "R5", "FLIP"]

_TRACE_REIDEMEISTER_MOVES = True  # default moves

# Use descriptors
class SettingProxyBool:
    def __get__(self, obj, objtype=None):
        global _TRACE_REIDEMEISTER_MOVES
        return _TRACE_REIDEMEISTER_MOVES

    def __set__(self, obj, value):
        global _TRACE_REIDEMEISTER_MOVES
        if value not in [True, False]:
            raise ValueError("Value must be True or False")
        _TRACE_REIDEMEISTER_MOVES = value


def _clean_allowed_moves(allowed_moves) -> list:
    """From the input parameter, e.g. "R1,R2,R3" or {"R1", "R2", "R3"}, return a set of allowed moves as a a set of ."""

    # If no moves are given, set it at the default (R1, R2, R3)
    if allowed_moves is None:
        return set(_DEFAULT_ALLOWED_MOVES)

    # If string is given, parse from string
    if isinstance(allowed_moves, str):
        allowed_moves = allowed_moves.split(",")

    # Clean the set
    allowed_moves = [re.sub(r'[^A-Za-z0-9]', '', s).upper() for s in allowed_moves]
    allowed_moves = {s for s in allowed_moves if s}

    if not allowed_moves.issubset(_EXISTING_REIDEMEISTER_MOVES):
        raise ValueError(f"Unknown (Reidemeister) modes {allowed_moves - _EXISTING_REIDEMEISTER_MOVES}")

    return list(allowed_moves)

class SettingProxyReidemeisterMoves:
    def __get__(self, obj, objtype=None):
        global _ALLOWED_REIDEMEISTER_MOVES
        return _ALLOWED_REIDEMEISTER_MOVES

    def __set__(self, obj, value):
        global _ALLOWED_REIDEMEISTER_MOVES
        _ALLOWED_REIDEMEISTER_MOVES = _clean_allowed_moves(value)

class Settings:
    allowed_reidemeister_moves = SettingProxyReidemeisterMoves()
    trace_reidemeister_moves = SettingProxyBool()

settings = Settings()

if __name__ == "__main__":
    print(settings.allowed_reidemeister_moves)
    settings.allowed_reidemeister_moves = "R1,R2"
    print(settings.allowed_reidemeister_moves)