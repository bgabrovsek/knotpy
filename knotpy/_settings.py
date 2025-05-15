"""
Global settings/flags of KnotPy.
Using descriptors for verifying the input.
"""

import re

_DEFAULT_ALLOWED_MOVES = ["R1", "R2", "R3", "R4", "R5"]
_EXISTING_REIDEMEISTER_MOVES = ["R1", "R2", "R3", "R4", "R5", "FLIP"]

_DEFAULT_trace_moves = True  # let the Reidemeister moves be traced
_DEFAULT_ALLOW_R4_ONLY_ON_TRIVALENT_VERTICES = False  # by default graphs are topological (not rigid)
_DEFAULT_FRAMED = False  # track framing on Reidemeister moves (R1, R4)

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
    allowed_moves = SettingProxyReidemeisterMoves(_DEFAULT_ALLOWED_MOVES)
    trace_moves = SettingProxyBool(_DEFAULT_trace_moves)
    r5_only_trivalent = SettingProxyBool(_DEFAULT_ALLOW_R4_ONLY_ON_TRIVALENT_VERTICES)
    framed = SettingProxyBool(_DEFAULT_FRAMED)

    def dump(self) -> dict:
        # return settings in form of a dictionary
        return {
            "allowed_moves": self.allowed_moves,
            "trace_moves": self.trace_moves,
            "r5_only_trivalent": self.r5_only_trivalent,
            "framed": self.framed,
        }

    def update(self, data: dict):
        # update the settings
        if "allowed_moves" in data:
            self.allowed_moves = data["allowed_moves"]
        if "trace_moves" in data:
            self.trace_moves = data["trace_moves"]
        if "r5_only_trivalent" in data:
            self.r5_only_trivalent = data["r5_only_trivalent"]
        if "framed" in data:
            self.framed = data["framed"]


    def load(self, data: dict):
        # load settings (default + update data)
        self.allowed_moves = data["allowed_moves"] if "allowed_moves" in data else _DEFAULT_ALLOWED_MOVES
        self.trace_moves = data["trace_moves"] if "trace_moves" in data else _DEFAULT_trace_moves
        self.r5_only_trivalent = data["r5_only_trivalent"] if "r5_only_trivalent" in data else _DEFAULT_ALLOW_R4_ONLY_ON_TRIVALENT_VERTICES
        self.framed = data["framed"] if "framed" in data else _DEFAULT_FRAMED


settings = Settings()


if __name__ == "__main__":
    data = settings.dump()
    print(data)
    settings.r5_only_trivalent = True
    settings.trace_moves = False
    print(settings.dump())
    settings.load(data)
    print(settings.dump())

    # print(settings.allowed_moves)
    # settings.allowed_moves = "R1,R2"
    # print(settings.allowed_moves)