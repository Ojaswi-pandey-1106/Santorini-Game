from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
    from models.worker import Worker

class Action(ABC):
    """Abstract base class for all player actions"""
    
    def __init__(self, player: Player, worker: Worker):
        self.player = player
        self.worker = worker
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if this action is valid"""
        pass
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute this action"""
        pass
