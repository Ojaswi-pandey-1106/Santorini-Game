from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.cell import Cell
    from models.player import Player
    from models.coordinate import Coordinate

from models.tower import Tower

class Worker:
    """The Worker class represents a player's game piece that can move and build"""
    
    def __init__(self, id: int, position: Cell, player: Player):
        self.id: int = id
        self.position: Cell = position
        self.player: Player = player
        self.name = f"{player.name}'s Worker {self.id}"
        # Tell the cell that this worker is standing on it
        position.assign_worker(self)
    
    def get_position(self) -> Cell:
        """Returns the current cell the worker is on"""
        return self.position
    
    def get_player(self) -> Player:
        """Returns the player this worker belongs to"""
        return self.player
    
    def set_position(self, cell: Cell):
        """Updates the worker's position to a new cell"""
        self.position = cell
    
    def apply_move(self, to_cell: Cell) -> bool:
        """
        Moves the worker to a new cell if the move is valid.
        """
        # Remove the worker from its current cell
        if self.position:
            self.position.remove_worker()
        
        # Update the worker's internal position
        self.set_position(to_cell)
        
        # Tell the new cell that the worker is now on it
        to_cell.assign_worker(self)
        
        return True
    
    def apply_build(self, target_cell: Cell) -> bool:
        """
        Builds on the target cell (adds level or dome).
        """
        # Get or create tower
        tower = target_cell.get_tower()
        if not tower:
            tower = Tower()
            target_cell.set_tower(tower)
        
        # Build level or dome based on current tower level
        if tower.get_tower_level() < 3:
            return tower.build_tower_level()
        elif tower.get_tower_level() == 3 and not tower.has_dome():
            return tower.add_dome()
        
        return False
    
    def __str__(self):
        return f"Worker(id={self.id}, position={self.position.coordinate}, player={self.player.name})"
    
    def __repr__(self):
        return self.__str__()
