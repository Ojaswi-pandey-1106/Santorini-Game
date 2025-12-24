# models/god_card.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from models.game import Game
    from models.player import Player
    from logic.actions.action import Action
    from models.worker import Worker
    from models.cell import Cell 
    from models.coordinate import Coordinate

class GodCard(ABC):
    """Abstract base class for all god powers"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def apply_god_power(self, player: Player, game: Game, action: Action) -> Optional[str]:
        """
        Applies the god power and returns an optional control signal
        like 'SECOND_MOVE' or 'SECOND_BUILD'.
        Now takes the action as a parameter to know what was just performed.
        """
        pass
    
    def reset(self) -> None:
        """
        Resets any internal god-specific flags at end of turn.
        Can be overridden by subclasses.
        """
        pass
    
    def __str__(self):
        return self.name

class Artemis(GodCard):
    """Artemis — allows a second move to a different cell"""
    
    def __init__(self):
        super().__init__("Artemis")
        self.has_used_second_move = False
        self.first_move_from_cell = None
    
    def apply_god_power(self, player: Player, game: Game, action: Action) -> Optional[str]:
        from logic.actions.move_action import MoveAction
        
        # Only trigger after move actions
        if not isinstance(action, MoveAction):
            return None
        
        # If we haven't used the second move yet, offer it
        if not self.has_used_second_move:
            self.has_used_second_move = True
            self.first_move_from_cell = action.worker.get_position()  # Store where we moved FROM
            return "SECOND_MOVE"
        
        return None
    
    def can_move_to_cell(self, target_cell: Cell) -> bool:
        """Check if Artemis can move to the target cell (not back to initial position)"""
        if self.first_move_from_cell is None:
            return True
        return target_cell.coordinate != self.first_move_from_cell.coordinate
    
    def reset(self):
        self.has_used_second_move = False
        self.first_move_from_cell = None

class Demeter(GodCard):
    """Demeter — allows a second build on a different cell"""
    
    def __init__(self):
        super().__init__("Demeter")
        self.has_used_second_build = False
        self.first_build_cell = None
    
    def apply_god_power(self, player: Player, game: Game, action: Action) -> Optional[str]:
        from logic.actions.build_action import BuildAction
        
        # Only trigger after build actions
        if not isinstance(action, BuildAction):
            return None
        
        # If we haven't used the second build yet, offer it
        if not self.has_used_second_build:
            self.has_used_second_build = True
            self.first_build_cell = action.target_cell
            return "SECOND_BUILD"
        
        return None
    
    def can_build_on_cell(self, target_cell: Cell) -> bool:
        """Check if Demeter can build on the target cell (not same as first build)"""
        if self.first_build_cell is None:
            return True
        return target_cell.coordinate != self.first_build_cell.coordinate
    
    def reset(self):
        self.has_used_second_build = False
        self.first_build_cell = None

class Triton(GodCard):
    """
    Triton — “Each time your Worker moves into a perimeter space,
    it may immediately move again.”
    """

    def __init__(self):
        super().__init__("Triton")
       
    
    def apply_god_power(self, player: Player, game: Game, action: Action) -> Optional[str]:
        from logic.actions.move_action import MoveAction
        
        # Only trigger after move actions
        if not isinstance(action, MoveAction):
            return None
        
        # Get the cell where the worker just moved to
        target_cell = action.target_cell
        
        # Check if the worker moved to a perimeter space
        if self._is_on_perimeter(target_cell.coordinate, game.get_board()):
            return "TRITON_EXTRA_MOVE"
        
        return None
    
    def _is_on_perimeter(self, coordinate, board) -> bool:
        """
        Helper method to check if a coordinate is on the perimeter.
        A coordinate is on the perimeter if it's on any edge of the board.
        """
        row, col = coordinate.row, coordinate.col
        board_rows, board_cols = board.rows, board.cols
        
        # Check if coordinate is on any edge of the board
        return (row == 0 or row == board_rows - 1 or 
                col == 0 or col == board_cols - 1)
    



