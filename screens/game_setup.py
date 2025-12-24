import tkinter as tk
import random
from tkinter import messagebox

from models.game import Game
from models.player import Player
from models.worker import Worker
from models.god_card import Artemis, Demeter, Triton
from models.coordinate import Coordinate
from typing import Callable, List

class GameSetupScreen(tk.Frame):
    """
    Game setup screen for configuring players and starting the game.
    Follows SRP by only handling setup logic.
    """
    
    def __init__(self, master, start_game_callback: Callable[[Game], None]):
        super().__init__(master)
        self.start_game_callback = start_game_callback
        self.pack(expand=True, fill='both')
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the setup user interface."""
        # Title
        title_label = tk.Label(
            self, 
            text="Santorini Game Setup", 
            bg='lightblue',
            fg='darkblue',
            padx=20,
            pady=10,
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # Setup frame
        setup_frame = tk.Frame(self, relief='raised', bd=2)
        setup_frame.pack(pady=20, padx=40, fill='x')
        
        # Player names
        tk.Label(setup_frame, text="Player Names:", font=("Arial", 14)).pack(pady=10)
        
        name_frame = tk.Frame(setup_frame)
        name_frame.pack(pady=10)
        
        tk.Label(name_frame, text="Player 1:").grid(row=0, column=0, padx=5, pady=5)
        self.player1_entry = tk.Entry(name_frame, width=20)
        self.player1_entry.insert(0, "Player 1")
        self.player1_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(name_frame, text="Player 2:").grid(row=1, column=0, padx=5, pady=5)
        self.player2_entry = tk.Entry(name_frame, width=20)
        self.player2_entry.insert(0, "Player 2")
        self.player2_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Board size
        tk.Label(setup_frame, text="Board Size:", font=("Arial", 14)).pack(pady=(20, 10))
        
        size_frame = tk.Frame(setup_frame)
        size_frame.pack(pady=10)
        
        self.board_size_var = tk.IntVar(value=5)
        for size in [4, 5, 6]:
            tk.Radiobutton(
                size_frame,
                text=f"{size}x{size}",
                variable=self.board_size_var,
                value=size
            ).pack(side='left', padx=10)
            
        
        # Start button
        start_button = tk.Button(
            self,
            text="Start Game",
            font=("Arial", 16),
            command=self._start_game,
            bg='darkblue',
            fg='black',
            activebackground='midnight blue',
            activeforeground='white',
            relief='raised',
            bd=4,
            highlightthickness=2,
            highlightbackground='white',
            padx=20,
            pady=10
        )
        start_button.pack(pady=30)
        
    def _start_game(self):
        """Initialize and start a new game."""
        try:
            # Get player names
            player1_name = self.player1_entry.get().strip() or "Player 1"
            player2_name = self.player2_entry.get().strip() or "Player 2"
            
            if player1_name == player2_name:
                messagebox.showerror("Invalid Names", "Players must have different names.")
                return
                
            # Create players
            player1 = Player(player1_name)
            player2 = Player(player2_name)

            # Assign token colors explicitly
            player1.token_color = "green"
            player2.token_color = "red"
            
            # Create game
            board_size = self.board_size_var.get()
            game = Game(players=[player1, player2], board_size=board_size)
            
            # Setup god cards if enabled
            god_cards = [Artemis(), Demeter(), Triton()]
            random.shuffle(god_cards)
            game.initialize_game(god_cards[:2])
            
                
            # Place workers randomly
            self._place_workers_randomly(game)
            
            # Start the game
            self.start_game_callback(game)
            
        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to start game: {str(e)}")
            
    def _place_workers_randomly(self, game: Game):
        """Randomly place workers on the board."""
        board = game.get_board()
        available_coords = []
        
        # Get all ground-level coordinates
        for coord, cell in board.grid.items():
            if not cell.tower or cell.tower.get_tower_level() == 0:
                available_coords.append(coord)
                
        # Shuffle coordinates
        random.shuffle(available_coords)
        
        # Place workers
        worker_id = 1
        for player in game.get_players():
            for _ in range(1,3):  # Each player gets 2 workers
                if not available_coords:
                    raise ValueError("Not enough space to place all workers")
                    
                coord = available_coords.pop()
                cell = board.get_cell(coord)
                worker = Worker(id=worker_id, position=cell, player=player)
                player.add_worker(worker)
                worker_id += 1
