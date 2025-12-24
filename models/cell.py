from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING: 
    from models.coordinate import Coordinate
    from models.worker import Worker
    from models.tower import Tower

class Cell:
    """
    A Cell represents a single square on the game board.
    """
    
    def __init__(self, coordinate: Coordinate, worker: Optional[Worker] = None, tower: Optional[Tower] = None, is_hidden: bool = False, hidden_message: str = ""):
        self.coordinate: Coordinate = coordinate
        self.worker: Optional[Worker] = worker
        self.tower: Optional[Tower] = tower
        self.is_hidden: bool = is_hidden
        self.hidden_message: str = hidden_message
        self.has_been_revealed: bool = False
    
    def is_adjacent_to(self, other: Cell) -> bool:
        """Check if another cell is next to this one (diagonals included)"""
        return self.coordinate.is_adjacent(other.coordinate)
    
    def reveal_hidden_cell(self) -> Optional[str]:
        """
        Reveals a hidden cell and returns its message if it hasn't been revealed before.
        Returns None if already revealed or not a hidden cell.
        """
        if self.is_hidden and not self.has_been_revealed:
            self.has_been_revealed = True
            return self.hidden_message
        return None
    
    def can_move_to(self, other: Cell) -> bool:
        """
        Returns True if a worker can move from this cell to the other cell.
        Rules:
        - Target cell can't have a worker
        - Target cell can't have a dome
        - Can only climb up one level max, but can go down any levels
        """
        # Target cell can't already have a worker
        if other.worker:
            return False
        
        # Target cell can't have a dome
        if other.tower and other.tower.has_dome():
            return False
        
        # Height difference check
        current_level = self.tower.get_tower_level() if self.tower else 0
        target_level = other.tower.get_tower_level() if other.tower else 0
        
        # Can move down any levels, but can only climb up one level
        if target_level - current_level > 1:
            return False
        
        return True
    
    def is_available_for_build(self) -> bool:
        """
        Returns True if this cell is available for building.
        Rules:
        - No worker on it
        - No dome on it
        - Tower level must be buildable (< 3 or == 3 for dome)
        """
        # No worker on it
        if self.worker is not None:
            return False
        
        # If there's a tower, check if it has a dome
        if self.tower and self.tower.has_dome():
            return False
        
        return True
    
    def assign_worker(self, worker: Worker) -> bool:
        """Place a worker on this cell"""
        if self.worker is None and worker is not None:
            self.worker = worker
            return True
        return False
    
    def remove_worker(self) -> bool:
        """Remove a worker from this cell"""
        if self.worker is not None:
            self.worker = None
            return True
        return False
    
    def get_tower(self) -> Optional[Tower]:
        """Get the tower object (if any)"""
        return self.tower
    
    def set_tower(self, tower: Tower) -> None:
        """Set a new tower on this cell"""
        self.tower = tower
    
    def __str__(self):
        worker_str = f"Worker: {self.worker.id}" if self.worker else "No Worker"
        tower_str = f"Tower Level: {self.tower.get_tower_level()}" if self.tower else "No Tower"
        return f"Cell at {self.coordinate} - {worker_str}, {tower_str}"
