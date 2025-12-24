from __future__ import annotations
from typing import TYPE_CHECKING

from logic.actions.action import Action

if TYPE_CHECKING:
    from models.player import Player
    from models.cell import Cell
    from models.worker import Worker

class MoveAction(Action):
    """Handles the movement of a worker to a valid adjacent cell"""
    
    def __init__(self, player: Player, worker: Worker, target_cell: Cell):
        super().__init__(player, worker)
        self.target_cell = target_cell
    
    def is_valid(self) -> bool:
        """Check if the move is valid according to game rules"""
        current_cell = self.worker.get_position()
        
        # Must be adjacent
        if not current_cell.is_adjacent_to(self.target_cell):
            return False
        
        # Must be a legal move according to board/tower rules
        if not current_cell.can_move_to(self.target_cell):
            return False
        
        # Prevent no-op move (same cell)
        if self.target_cell == current_cell:
            return False
        
        return True
    
    def execute(self) -> bool:
        """Execute the move if valid"""
        if not self.is_valid():
            return False
        
        return self.worker.apply_move(self.target_cell)
    
    def __str__(self):
        return f"MoveAction(Player={self.player.name}, Worker={self.worker.id}, To={self.target_cell.coordinate})"
