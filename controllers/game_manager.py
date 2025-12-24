from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

from models.god_card import Artemis
from utils.enums import GameStatus

if TYPE_CHECKING:
    from logic.actions.action import Action
    from models.game import Game
    from models.player import Player
    from models.worker import Worker
    from models.cell import Cell

class GameManager:
    """Manages the game flow and turn sequence"""
    
    def __init__(self, game: Game):
        self.game = game
        self.current_player_index = 0
        self.game_status = GameStatus.ONGOING
        self.hidden_cells_revealed: int = 0  # Track how many hidden cells have been revealed
        self.max_hidden_reveals: int = 2  # Maximum reveals per game
    
    def start_game(self):
        """Start the game"""
        self.current_player_index = 0
        self.game_status = GameStatus.ONGOING
        self.game.set_status(GameStatus.ONGOING)
    
    def end_game(self, winner: Optional[Player] = None):
        """End the game with optional winner"""
        if winner:
            self.game.set_winner(winner)
            self.game_status = GameStatus.PLAYER_WON
        else:
            self.game_status = GameStatus.PLAYER_LOST
        self.game.set_status(self.game_status)
    
    def get_current_player(self) -> Player:
        """Get the current player"""
        return self.game.get_players()[self.current_player_index]
    
    def switch_turn(self):
        """Switch to the next player"""
        self.current_player_index = (self.current_player_index + 1) % len(self.game.get_players())
    
    def start_turn(self):
        """Start a player's turn"""
        current_player = self.get_current_player()
        print(f"{current_player.name}'s turn started.")
        
        # Check lose condition at start of turn
        if self.game.check_lose_condition(current_player):
            print(f"{current_player.name} has no valid moves and loses!")
            self.end_game()
            return False
        
        return True
    
    def execute_turn(self, action: Action) -> bool | str:
        """
        Executes a player action (move/build). Returns:
        - True if successful
        - False if invalid
        - A string (e.g., 'SECOND_MOVE', 'SECOND_BUILD') if god power activates
        """
        if not self.validate_turn(action):
            return False
        
        success = action.execute()
        if not success:
            return False
        
        # Check for hidden cell reveal on move actions
        from logic.actions.move_action import MoveAction
        if isinstance(action, MoveAction):
            hidden_message = self._check_hidden_cell_reveal(action.target_cell, action.player)
            if hidden_message:
                return f"HIDDEN_CELL_REVEALED:{hidden_message}"
        
        # Check win condition after move
        if self.check_win_condition(action):
            self.end_game(winner=action.player)
            return True
        
        # Check for god power activation
        god_card = action.player.get_god_card()
        if god_card:
            power_result = god_card.apply_god_power(action.player, self.game, action)
            if power_result:
                return power_result
        
        return True
    
    def validate_turn(self, action: Action) -> bool:
        """Validate if the action is legal"""
        god_card = action.player.get_god_card()
        
        if god_card:
            # Artemis move restriction
            if god_card.__class__.__name__ == "Artemis":
                from logic.actions.move_action import MoveAction
                if isinstance(action, MoveAction):
                    if not god_card.can_move_to_cell(action.target_cell):
                        return False
            
            # Demeter build restriction  
            elif god_card.__class__.__name__ == "Demeter":
                from logic.actions.build_action import BuildAction
                if isinstance(action, BuildAction):
                    if not god_card.can_build_on_cell(action.target_cell):
                        return False
        
        return action.is_valid()
    
    def check_win_condition(self, action: Action) -> bool:
        """
        Win condition: a worker moved from level 2 to level 3.
        """
        from logic.actions.move_action import MoveAction
        
        # Only check win condition for move actions
        if not isinstance(action, MoveAction):
            return False
        
        worker: Worker = action.worker
        position = worker.get_position()
        
        if position:
            tower = position.get_tower()
            if tower and tower.get_tower_level() == 3:
                return True
        
        return False
    
    def end_turn(self):
        """End the current player's turn"""
        current_player = self.get_current_player()
        
        # Reset god power flags
        if current_player.get_god_card():
            current_player.get_god_card().reset()
        
        self.switch_turn()

    def _check_hidden_cell_reveal(self, cell: Cell, player: Player) -> Optional[str]:
        """
        Check if a cell is hidden and reveal it if so.
        Returns the hidden message if revealed, None otherwise.
        """
        if self.hidden_cells_revealed >= self.max_hidden_reveals:
            return None
        
        hidden_message = cell.reveal_hidden_cell()
        if hidden_message:
            self.hidden_cells_revealed += 1
            # Add 10 seconds to the player's timer
            player.remaining_time_secs += 10
            return hidden_message
        
        return None
