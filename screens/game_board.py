import random
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional
from random import shuffle
from models.board import Board
from random import Random
from models.cell import Cell
from models.coordinate import Coordinate
from models.game import Game
from models.player import Player
from models.worker import Worker
from controllers.game_manager import GameManager
from logic.actions.move_action import MoveAction
from logic.actions.build_action import BuildAction
from screens.board_component import GameBoard
from enum import Enum

class TurnPhase(Enum):
    """Enumeration for different phases of a turn."""
    WORKER_SELECTION = "worker_selection"
    MOVE_SELECTION = "move_selection"
    MOVE_EXECUTION = "move_execution"
    BUILD_SELECTION = "build_selection"
    BUILD_EXECUTION = "build_execution"
    TURN_END = "turn_end"

class GameBoardScreen(tk.Frame):
    """
    Main game screen that orchestrates the game flow.
    Follows SRP by handling game state management and UI coordination.
    """
    
    def __init__(self, master, game: Game, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        # Core game components
        self.game = game
        self.game_manager = GameManager(game)
        
        # Turn state management
        self.current_player: Player = self.game_manager.get_current_player()
        self.turn_phase: TurnPhase = TurnPhase.WORKER_SELECTION
        self.selected_worker: Optional[Worker] = None
        self.selected_target_cell: Optional[Cell] = None
        
        # Action tracking for god powers
        self.has_moved = False
        self.has_built = False
        self.move_count = 0
        self.build_count = 0
        self.previous_move_cell: Optional[Cell] = None
        self.first_build_cell: Optional[Cell] = None

        
        self._create_ui()
        self.game.get_board().create_hidden_cells(2)
        self._start_turn()
        
    def _create_ui(self):
        """Create the user interface components."""
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Player info panel
        self._create_info_panel()
        
        # Game board
        self.board_display = GameBoard(self, self.game)
        self.board_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.board_display.set_worker_click_callback(self._on_worker_clicked)
        self.board_display.set_cell_click_callback(self._on_cell_clicked)

        self._create_info_buttons_panel()
        
        # Control panel
        self._create_control_panel()
        
    def _create_info_panel(self):
        """Create the player information panel."""
        self.info_frame = tk.Frame(self, bg='lightblue', relief='raised', bd=2)
        self.info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.side_info_frame = tk.Frame(self, bg='darkgray', relief='groove', bd=2)
        self.side_info_frame.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=10)
        
        self.player_label = tk.Label(
            self.info_frame, 
            text="", 
            font=('Arial', 14, 'bold'),
            bg='lightblue',
            fg='darkblue'
        )
        self.player_label.pack(pady=10)
        
        self.phase_label = tk.Label(
            self.info_frame,
            text="",
            font=('Arial', 12),
            bg='lightblue',
            fg='darkblue'
        )
        self.phase_label.pack(pady=5)


        players = self.game.get_players()
        # If players[0] has not yet been named, fallback to "Player 1"
        name0 = players[0].name if players and len(players) > 0 else "Player 1"
        name1 = players[1].name if players and len(players) > 1 else "Player 2"

        # Label for Player 1's remaining time
        self.timer_label_p0 = tk.Label(
            self.info_frame,
            text=f"{name0} Time: 15:00",
            font=('Arial', 12),
            bg='green'
        )
        self.timer_label_p0.pack(pady=2)
        
        # Label for Player 2's remaining time
        self.timer_label_p1 = tk.Label(
            self.info_frame,
            text=f"{name1} Time: 15:00",
            font=('Arial', 12),
            bg='red'
        )
        self.timer_label_p1.pack(pady=2)
        
    def _create_control_panel(self):
        """Create the control button panel."""
        self.control_frame = tk.Frame(self, bg='lightblue', relief='raised', bd=2)
        self.control_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # Action buttons
        self.move_button = tk.Button(
            self.control_frame, 
            text="Execute Move", 
            command=self._execute_move,
            state='disabled'
        )
        self.move_button.pack(side='left', padx=5, pady=5)
        
        self.build_button = tk.Button(
            self.control_frame, 
            text="Execute Build", 
            command=self._execute_build,
            state='disabled'
        )
        self.build_button.pack(side='left', padx=5, pady=5)
        
        self.end_turn_button = tk.Button(
            self.control_frame, 
            text="End Turn", 
            command=self._end_turn,
            state='disabled'
        )
        self.end_turn_button.pack(side='right', padx=5, pady=5)

    def _create_info_buttons_panel(self):
        """Create a right-hand panel for informational buttons."""
        self.side_info_frame = tk.Frame(self, bg='lightblue', relief='groove', bd=2)
        self.side_info_frame.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=10)

        tk.Label(self.side_info_frame, text="Game Info", font=("Arial", 12, "bold"), bg='darkblue').pack(pady=10)

        self.rules_button = tk.Button(
            self.side_info_frame,
            text="Rules",
            width=15,
            command=self._show_rules
        )
        self.rules_button.pack(pady=5)

        self.god_info_button = tk.Button(
            self.side_info_frame,
            text="God Info",
            width=15,
            command=self._show_god_info
        )
        self.god_info_button.pack(pady=5)

        self.draw_button = tk.Button(
            self.side_info_frame,
            text="Propose Draw",
            width=15,
            command=self._propose_draw
        )
        self.draw_button.pack(pady=20)



        
    def _update_display(self):
        """Update all display elements."""
        # Update player info
        god_name = self.current_player.get_god_card().__class__.__name__ if self.current_player.get_god_card() else "None"
        self.player_label.config(
            text=f"Current Player: {self.current_player.name} (God: {god_name})"
        )
        
        # Update phase info
        phase_text = self._get_phase_description()
        self.phase_label.config(text=phase_text)
        
        # Update board
        self.board_display.refresh_display()
        
        # Update button states
        self._update_button_states()
        
    def _get_phase_description(self) -> str:
        """Get human-readable description of current turn phase."""
        phase_descriptions = {
            TurnPhase.WORKER_SELECTION: "Select a worker to use this turn",
            TurnPhase.MOVE_SELECTION: f"Select where to move {self.selected_worker.name if self.selected_worker else 'worker'}",
            TurnPhase.MOVE_EXECUTION: "Click 'Execute Move' to confirm movement",
            TurnPhase.BUILD_SELECTION: "Select where to build",
            TurnPhase.BUILD_EXECUTION: "Click 'Execute Build' to confirm building",
            TurnPhase.TURN_END: "Turn complete - click 'End Turn'"
        }
        return phase_descriptions.get(self.turn_phase, "")
        
    def _update_button_states(self):
        """Update the enabled/disabled state of control buttons."""
        # Move button
        if self.turn_phase == TurnPhase.MOVE_EXECUTION:
            self.move_button.config(state='normal')
        else:
            self.move_button.config(state='disabled')
            
        # Build button
        if self.turn_phase == TurnPhase.BUILD_EXECUTION:
            self.build_button.config(state='normal')
        else:
            self.build_button.config(state='disabled')
            
        # End turn button
        if (self.turn_phase == TurnPhase.TURN_END and 
            self.has_moved and self.has_built):
            self.end_turn_button.config(state='normal')
        else:
            self.end_turn_button.config(state='disabled')

    def _format_secs_to_mmss(self, total_secs: int) -> str:
        """Convert seconds into 'MM:SS' string."""
        minutes, seconds = divmod(total_secs, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_timer_labels(self):
        """Refresh both players’ timer labels based on their remaining_time_secs."""
        players = self.game.get_players()
        # Player 0
        secs0 = players[0].remaining_time_secs
        self.timer_label_p0.config(text=f"{players[0].name} Time: {self._format_secs_to_mmss(secs0)}")
        # Player 1
        secs1 = players[1].remaining_time_secs
        self.timer_label_p1.config(text=f"{players[1].name} Time: {self._format_secs_to_mmss(secs1)}")

    def _start_timer(self):
        """Start ticking down the current player's clock once per second."""
        # First, cancel any existing job (just in case)
        if hasattr(self, 'timer_job_id') and self.timer_job_id is not None:
            self.after_cancel(self.timer_job_id)

        # Schedule the first tick immediately:
        self._tick_timer()

    def _tick_timer(self):
        """Decrement the current player's remaining_time_secs by 1 second, update the label,
           then reschedule itself in 1 000 ms if time remains."""
        # Identify which player is active
        current_player = self.current_player
        # Decrement one second
        current_player.remaining_time_secs -= 1
        
        # Update both labels so the non-active player's label remains correct
        self._update_timer_labels()
        
        if current_player.remaining_time_secs <= 0:
            # The current player’s clock just hit zero
            self._handle_time_expired(current_player)
            return
        else:
            # Reschedule the next tick in 1 000 ms
            self.timer_job_id = self.after(1000, self._tick_timer)

    def _stop_timer(self):
        """Stop the countdown for whichever player is ticking now."""
        if hasattr(self, 'timer_job_id') and self.timer_job_id is not None:
            self.after_cancel(self.timer_job_id)
            self.timer_job_id = None

    def _handle_time_expired(self, player: Player):
        """Called the instant a player's clock hits zero → that player loses immediately."""
        # End the timer (just in case)
        self._stop_timer()

        # Declare the other player the winner
        other = [p for p in self.game.get_players() if p is not player][0]
        messagebox.showinfo("Time's Up!", f"{player.name}'s time has expired.\n{other.name} wins!")
        
        # Tell the GameManager to end the game:
        self.game_manager.end_game(winner=other)

        # Disable all further UI interactions
        self.move_button.config(state='disabled')
        self.build_button.config(state='disabled')
        self.end_turn_button.config(state='disabled')
            

    def _start_turn(self):
        """Initialize a new turn."""
        self.game_manager.start_turn()
        self.current_player = self.game_manager.get_current_player()
        
        # Reset turn state
        self.turn_phase = TurnPhase.WORKER_SELECTION
        self.selected_worker = None
        self.selected_target_cell = None
        self.has_moved = False
        self.has_built = False
        self.move_count = 0
        self.build_count = 0
        self.previous_move_cell = None
        self.first_build_cell = None
        
        # Check for loss condition
        if self._check_loss_condition():
            winner = self.game.get_players()[1] if self.current_player == self.game.get_players()[0] else self.game.get_players()[0]
            self._handle_game_end(winner)
            return
        
        self._start_timer()
            
        self._update_display()
        
    def _check_loss_condition(self) -> bool:
        """Check if current player has lost (no valid moves)."""
        for worker in self.current_player.get_workers():
            available_moves = self.game.get_board().get_available_move_cells(worker)
            if available_moves:
                return False
        return True
        
    def _on_worker_clicked(self, worker: Worker):
        """Handle worker selection."""
        if worker.player != self.current_player:
            messagebox.showwarning("Invalid Selection", "You can only select your own workers.")
            return
            
        if self.turn_phase != TurnPhase.WORKER_SELECTION:
            messagebox.showwarning("Invalid Action", "You can only select workers at the start of your turn.")
            return
            
        self.selected_worker = worker
        self.turn_phase = TurnPhase.MOVE_SELECTION
        
        # Show available moves
        available_moves = self.game.get_board().get_available_move_cells(worker)
        if not available_moves:
            messagebox.showerror("No Moves", "This worker has no valid moves.")
            self.selected_worker = None
            self.turn_phase = TurnPhase.WORKER_SELECTION
            return
            
        self.board_display.highlight_cells(available_moves)
        self._update_display()
        
    def _on_cell_clicked(self, row: int, col: int):
        """Handle cell selection for moves or builds."""
        coordinate = Coordinate(row, col)
        cell = self.game.get_board().get_cell(coordinate)
        
        if not cell:
            return
            
        if self.turn_phase == TurnPhase.MOVE_SELECTION:
            self._select_move_target(cell)
        elif self.turn_phase == TurnPhase.BUILD_SELECTION:
            self._select_build_target(cell)
            
    def _select_move_target(self, cell: Cell):
        """Handle move target selection."""
        if not self.selected_worker:
            return
            
        # Validate move
        available_moves = self.game.get_board().get_available_move_cells(self.selected_worker)
        if cell not in available_moves:
            messagebox.showwarning("Invalid Move", "That cell is not a valid move target.")
            return
            
        # Special validation for Artemis second move
        god_card = self.current_player.get_god_card()
        if (self.move_count > 0 and god_card and god_card.__class__.__name__ == "Artemis" 
            and self.previous_move_cell and cell.coordinate == self.previous_move_cell.coordinate):
            messagebox.showwarning("Invalid Move", "Artemis cannot move back to the previous cell.")
            return
            
        self.selected_target_cell = cell
        self.board_display.select_cell(cell)
        self.turn_phase = TurnPhase.MOVE_EXECUTION
        self._update_display()
        
    def _select_build_target(self, cell: Cell):
        """Handle build target selection."""
        if not self.selected_worker:
            return
            
        # Validate build
        available_builds = self.game.get_board().get_available_build_cells(self.selected_worker)
        if cell not in available_builds:
            messagebox.showwarning("Invalid Build", "That cell is not a valid build target.")
            return
            
        # Special validation for Demeter
        god_card = self.current_player.get_god_card()
        if (self.build_count > 0 and god_card and god_card.__class__.__name__ == "Demeter"
            and self.first_build_cell and cell.coordinate == self.first_build_cell.coordinate):
            messagebox.showwarning("Invalid Build", "Demeter cannot build twice on the same cell.")
            return
            
        self.selected_target_cell = cell
        self.board_display.select_cell(cell)
        self.turn_phase = TurnPhase.BUILD_EXECUTION
        self._update_display()
        
    def _execute_move(self):
        """Execute the selected move."""
        if not self.selected_worker or not self.selected_target_cell:
            return
            
        # Save previous position for Artemis
        self.previous_move_cell = self.selected_worker.get_position()
        
        # Create and execute move action
        action = MoveAction(self.current_player, self.selected_worker, self.selected_target_cell)
        result = self.game_manager.execute_turn(action)
        
        if result is True or isinstance(result, str):
            self.has_moved = True
            self.move_count += 1

            # Check for win condition
            if self.game_manager.check_win_condition(action):
                self._handle_game_end(self.current_player)
                return
            
            # Handle hidden cell reveal
            if isinstance(result, str) and result.startswith("HIDDEN_CELL_REVEALED:"):
                hidden_message = result.split(":", 1)[1]
                self._handle_hidden_cell_reveal(hidden_message)
                # Continue with normal flow after showing the message
                result = True
                
            # Handle god power results
            god_card = self.current_player.get_god_card()
            if result == "SECOND_MOVE" and god_card and god_card.__class__.__name__ == "Artemis":
                # Allow second move
                self.turn_phase = TurnPhase.MOVE_SELECTION
                available_moves = self.game.get_board().get_available_move_cells(self.selected_worker)
                self.board_display.clear_highlights()
                self.board_display.deselect_cell()
                self.board_display.highlight_cells(available_moves)
                self.selected_target_cell = None
                messagebox.showinfo("Artemis Power", "You may move again (but not back to the previous cell).")
            elif result == "TRITON_EXTRA_MOVE" and god_card and god_card.__class__.__name__ == "Triton":
                # Triton: may chain indefinitely while landing on perimeter
                self.turn_phase = TurnPhase.MOVE_SELECTION
                available_moves = self.game.get_board().get_available_move_cells(self.selected_worker)
                self.board_display.clear_highlights()
                self.board_display.deselect_cell()
                self.board_display.highlight_cells(available_moves)
                self.selected_target_cell = None
                messagebox.showinfo("Triton Power", "Your worker moved to a perimeter space - you may move again!")

            else:
                # No further moves → proceed to build phase
                self._transition_to_build()
        else:
            messagebox.showerror("Invalid Move", "The move could not be executed.")
            
        self._update_display()
        
    def _execute_build(self):
        """Execute the selected build."""
        if not self.selected_worker or not self.selected_target_cell:
            return
        
        # Create and execute build action
        action = BuildAction(self.current_player, self.selected_worker, self.selected_target_cell)
        result = self.game_manager.execute_turn(action)
        
        if result is True or isinstance(result, str):
            self.has_built = True
            self.build_count += 1
            
            # Save first build cell for Demeter
            if self.build_count == 1:
                self.first_build_cell = self.selected_target_cell
            
            # Handle god power results
            god_card = self.current_player.get_god_card()
            if result == "SECOND_BUILD" and god_card and god_card.__class__.__name__ == "Demeter":
                # Allow second build
                self.turn_phase = TurnPhase.BUILD_SELECTION
                available_builds = self.game.get_board().get_available_build_cells(self.selected_worker)
                self.board_display.clear_highlights()
                self.board_display.deselect_cell()
                self.board_display.highlight_cells(available_builds)
                self.selected_target_cell = None
                messagebox.showinfo("Demeter Power", "You may build again (but not on the same cell).")
            else:

                self.turn_phase = TurnPhase.TURN_END
        else:
            messagebox.showerror("Invalid Build", "The build could not be executed.")
        
        self._update_display()
        
    def _transition_to_build(self):
        """Transition from move phase to build phase."""
        self.turn_phase = TurnPhase.BUILD_SELECTION
        available_builds = self.game.get_board().get_available_build_cells(self.selected_worker)
        
        self.board_display.clear_highlights()
        self.board_display.deselect_cell()
        self.board_display.highlight_cells(available_builds)
        self.selected_target_cell = None
        
    def _end_turn(self):
        """End the current turn and start the next."""
        self._stop_timer()
        self.game_manager.end_turn()
        self.board_display.clear_highlights()
        self.board_display.deselect_cell()
        self._start_turn()

    def _show_rules(self):
        rules_text = (
            "Santorini Rules:\n\n"
            "- Move a worker to an adjacent space.\n"
            "- Then build on an adjacent space.\n"
            "- You win by moving a worker to level 3.\n"
            "- Domes (level 4) block spaces.\n"
            "- Each god card has special powers.\n"
            "- Look out for ancestral cells!!!! - Hidden cells which grant 10 seconds to your timer when you move on them .\n"
        )
        messagebox.showinfo("Game Rules", rules_text)

    def _show_god_info(self):
        god_window = tk.Toplevel(self)
        god_window.title("God Powers")

        text = tk.Text(god_window, wrap=tk.WORD, height=15, width=50)
        text.pack(expand=True, fill=tk.BOTH)

        god_info = {
            "Artemis": "Can move one additional time, but not back to the original space.",
            "Demeter": "Can build an additional time, but not on the same space.",
            "Triton": "Can move again if on the perimeter after moving.",
        }

        for god, desc in god_info.items():
            text.insert(tk.END, f"{god}:\n{desc}\n\n")

    def _propose_draw(self):
        """Offer the opponent a draw."""
        proposer = self.current_player
        opponent = [p for p in self.game.get_players() if p != proposer][0]

        response = messagebox.askyesno(
            "Draw Proposal",
            f"{proposer.name} has proposed a draw.\n\n{opponent.name}, do you accept?"
        )

        if response:
            self._stop_timer()
            self.game_manager.end_game()  # No winner
            messagebox.showinfo("Game Drawn", "The game ends in a draw. You both win!")
            
            # Disable all buttons
            self.move_button.config(state='disabled')
            self.build_button.config(state='disabled')
            self.end_turn_button.config(state='disabled')
            self.draw_button.config(state='disabled')
        else:
            messagebox.showinfo("Draw Rejected", f"{opponent.name} rejected the draw offer.")

    def _handle_game_end(self, winner: Optional[Player]):
        """Display a full-screen end screen and lock out the game."""
        self._stop_timer()

        # Disable main game UI completely
        self.move_button.config(state='disabled')
        self.build_button.config(state='disabled')
        self.end_turn_button.config(state='disabled')
        self.draw_button.config(state='disabled')

        # Create overlay frame
        end_screen = tk.Toplevel(self)
        end_screen.title("Game Over")
        end_screen.geometry("600x400")
        end_screen.configure(bg='lightblue')
        end_screen.grab_set()  # Block interaction with other windows

        message = "🏆 " + (f"{winner.name} wins the game!" if winner else "The game ends in a draw. You both win!")
        
        label = tk.Label(
            end_screen,
            text=message,
            font=("Times New Roman", 24, "bold"),
            fg="gold",
            bg="darkblue",
            wraplength=500,
            justify="center"
        )
        label.pack(pady=80)

        exit_button = tk.Button(
            end_screen,
            text="Exit Game",
            font=("Arial", 14, "bold"),
            bg="lightblue",
            fg="darkblue",
            width=15,
            height=2,
            command=self.quit  # Cleanly exits the application
        )
        exit_button.pack(pady=20)

    def _handle_hidden_cell_reveal(self, message: str):
        """Handle the reveal of a hidden cell."""
        # Update timer display immediately
        self._update_timer_labels()
        
        # Show the hidden message with special styling
        messagebox.showinfo(
            "Hidden Cell Discovered!", 
            f"✨ {message} ✨\n\n+10 seconds added to your timer!",
            icon='info'
        )
        self.board_display.refresh_display()


    
    
