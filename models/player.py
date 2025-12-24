from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.game import Game
    from models.worker import Worker
    from models.god_card import GodCard

class Player:
    """Represents a player in the Santorini game"""
    
    def __init__(self, name: str, god_card: Optional[GodCard] = None):
        self.name = name
        self.workers: List[Worker] = []
        self.god_card = god_card

        self.remaining_time_secs: int = 15 * 60 # 15 minutes in seconds

        
    
    def get_god_card(self) -> Optional[GodCard]:
        """Returns the god card this player is using"""
        return self.god_card
    
    def set_god_card(self, god_card: GodCard) -> None:
        """Sets the god card for this player"""
        self.god_card = god_card
    
    def get_workers(self) -> List[Worker]:
        """Returns the list of workers owned by this player"""
        return self.workers
    
    def get_worker_by_id(self, worker_id: int) -> Optional[Worker]:
        """Returns a specific worker by its ID, if it exists"""
        for worker in self.workers:
            if worker.id == worker_id:
                return worker
        return None
    
    def add_worker(self, worker: Worker):
        """Adds a new worker to this player's list"""
        self.workers.append(worker)
    
    def has_valid_moves(self, board) -> bool:
        """Check if player has any valid moves with any of their workers"""
        for worker in self.workers:
            if board.get_available_move_cells(worker):
                return True
        return False
    
    def __str__(self):
        god_card_str = str(self.god_card) if self.god_card else "No GodCard"
        return f"Player(name={self.name}, GodCard={god_card_str}, Workers={len(self.workers)})"
    
    def __repr__(self):
        return self.__str__()
    