from __future__ import annotations
from typing import TYPE_CHECKING

from logic.actions.action import Action

if TYPE_CHECKING:
    from models.player import Player
    from models.cell import Cell
    from models.worker import Worker

class BuildAction(Action):
    """Handles the building of a tower or dome by a worker"""
    
    def __init__(self, player: Player, worker: Worker, target_cell: Cell):
        super().__init__(player, worker)
        self.target_cell = target_cell
    
    def is_valid(self) -> bool:
        """Check if the build is valid according to game rules"""
        current_cell = self.worker.get_position()
        
        # Must be adjacent
        if not current_cell.is_adjacent_to(self.target_cell):
            return False
        
        # Must be available for building
        if not self.target_cell.is_available_for_build():
            return False
        
        # Cannot build on occupied cell
        if self.target_cell.worker is not None:
            return False
        
        return True
    
    def execute(self) -> bool:
        """Execute the build if valid"""
        if not self.is_valid():
            return False
        
        return self.worker.apply_build(self.target_cell)
    
    def __str__(self):
        return f"BuildAction(Player={self.player.name}, Worker={self.worker.id}, At={self.target_cell.coordinate})"
