from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from models.board import Board
from utils.enums import GameStatus

if TYPE_CHECKING:
    from models.player import Player
    from models.god_card import GodCard


class Game:
    def __init__(self, players: List[Player], board_size: int = 5):
        if len(players) != 2:
            raise ValueError("This game requires exactly two players.")

        self.board: Board = Board(rows=board_size, cols=board_size)
        self.players: List[Player] = players
        self.winning_player: Optional[Player] = None
        self.status: GameStatus = GameStatus.ONGOING


    def initialize_game(self, god_cards: List[GodCard]) -> None:
        if len(god_cards) != len(self.players):
            raise ValueError(
                "Number of god cards must match number of players.")

        for player, god_card in zip(self.players, god_cards):
            player.god_card = god_card

        for player in self.players:
            for worker in player.get_workers():
                position = worker.get_position()
                self.board.get_cell(position.coordinate).assign_worker(worker)

            self.board.place_workers_randomly(self.players)


    def get_board(self) -> Board:
        return self.board

    def get_players(self) -> List[Player]:
        return self.players

    def get_status(self) -> GameStatus:
        return self.status

    def set_status(self, status: GameStatus):
        self.status = status

    def set_winner(self, player: Player):
        self.status = GameStatus.PLAYER_WON
        self.winning_player = player

    def get_winner(self) -> Optional[Player]:
        return self.winning_player
    
    def check_lose_condition(self, player: Player) -> bool:
        """Check if player has lost (no valid moves)"""
        return not player.has_valid_moves(self.board)
    
