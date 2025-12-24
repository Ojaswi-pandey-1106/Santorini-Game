# models/tower.py
from __future__ import annotations
from utils.constants import MAXIMUM_TOWER_LEVEL

class Tower:
    """
    Represents a buildable tower in Santorini. A tower has up to 3 levels,
    and optionally a dome that caps further building.
    """
    
    def __init__(self, level: int = 0, dome: bool = False):
        if level < 0 or level > MAXIMUM_TOWER_LEVEL:
            raise ValueError(f"Tower level must be between 0 and {MAXIMUM_TOWER_LEVEL}")
        if dome and level < MAXIMUM_TOWER_LEVEL:
            raise ValueError("Dome cannot be placed unless tower is at max level.")
        self._level = level
        self._dome = dome
    
    def can_build_level(self) -> bool:
        """
        Checks whether an additional level can be built (no dome, level < max).
        """
        return self._level < MAXIMUM_TOWER_LEVEL and not self._dome
    
    def build_tower_level(self) -> bool:
        """
        Adds one level to the tower, if allowed. Returns True if successful.
        """
        if self.can_build_level():
            self._level += 1
            return True
        return False
    
    def add_dome(self) -> bool:
        """
        Adds a dome if there isn't one already and tower is at max level.
        """
        if not self._dome and self._level == MAXIMUM_TOWER_LEVEL:
            self._dome = True
            return True
        return False
    
    def has_dome(self) -> bool:
        return self._dome
    
    def get_tower_level(self) -> int:
        return self._level
    
    def __str__(self) -> str:
        return f"Tower(level={self._level}, dome={self._dome})"
