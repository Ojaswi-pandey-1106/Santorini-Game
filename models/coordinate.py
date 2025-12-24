from __future__ import annotations

class Coordinate:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
    
    def is_adjacent(self, other: Coordinate) -> bool:
        """
        Returns True if the other coordinate is adjacent (in any direction), based on Chebyshev distance.
        """
        return max(abs(self.row - other.row), abs(self.col - other.col)) == 1
    
    def distance_to(self, other: Coordinate) -> int:
        """
        Returns how far this coordinate is from another one,
        measured using Chebyshev distance.
        """
        return max(abs(self.row - other.row), abs(self.col - other.col))
    
    def __eq__(self, other):
        """
        Checks if two coordinates are equal based on their row and column values.
        """
        return isinstance(other, Coordinate) and self.row == other.row and self.col == other.col
    
    def __hash__(self):
        """
        Makes Coordinate usable as a dictionary key.
        """
        return hash((self.row, self.col))
    
    def __str__(self) -> str:
        return f"Coordinate(row={self.row}, col={self.col})"
