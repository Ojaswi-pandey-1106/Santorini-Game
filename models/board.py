from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING
import random

from models.coordinate import Coordinate
from models.cell import Cell
from models.tower import Tower
from models.worker import Worker

if TYPE_CHECKING:
    from models.player import Player

class Board:
    """Represents the game board"""
    
    def __init__(self, rows: int, cols: int):
        self.rows: int = rows
        self.cols: int = cols
        self.grid: Dict[Coordinate, Cell] = self._create_grid(rows, cols)
        self.hidden_cells_created: bool = False
    
    def _create_grid(self, rows: int, cols: int) -> Dict[Coordinate, Cell]:
        """Creates a grid of cells based on the specified number of rows and columns"""
        grid: Dict[Coordinate, Cell] = {}
        for row in range(rows):
            for col in range(cols):
                coordinate = Coordinate(row, col)
                grid[coordinate] = Cell(coordinate)
        return grid
    
    def get_cell(self, coordinate: Coordinate) -> Optional[Cell]:
        """Return the cell at this coordinate (or None if it's out of bounds)"""
        return self.grid.get(coordinate)
    
    def is_valid_coordinate(self, coordinate: Coordinate) -> bool:
        """Check if coordinate is within board bounds"""
        return (0 <= coordinate.row < self.rows and 
                0 <= coordinate.col < self.cols)
    
    def get_adjacent_cells(self, coordinate: Coordinate) -> List[Cell]:
        """Return all cells that are adjacent to this coordinate"""
        adjacent_cells = []
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue  # Skip the current cell
                
                adj_coord = Coordinate(
                    coordinate.row + row_offset,
                    coordinate.col + col_offset
                )
                
                if self.is_valid_coordinate(adj_coord):
                    cell = self.get_cell(adj_coord)
                    if cell:
                        adjacent_cells.append(cell)
        
        return adjacent_cells
    
    def get_available_move_cells(self, worker: Worker) -> List[Cell]:
        """Return a list of cells that this worker can move to"""
        current_cell = worker.get_position()
        if not current_cell:
            return []
        
        adjacent_cells = self.get_adjacent_cells(current_cell.coordinate)
        available_cells = []
        
        for cell in adjacent_cells:
            if current_cell.can_move_to(cell):
                available_cells.append(cell)
        
        return available_cells
    
    def get_available_build_cells(self, worker: Worker) -> List[Cell]:
        """Return cells that are legal to build on from worker's position"""
        current_cell = worker.get_position()
        if not current_cell:
            return []
        
        adjacent_cells = self.get_adjacent_cells(current_cell.coordinate)
        available_cells = []
        
        for cell in adjacent_cells:
            if cell.is_available_for_build():
                available_cells.append(cell)
        
        return available_cells
    
    def place_workers_randomly(self, players: List[Player]) -> None:
        """Randomly place workers on unoccupied ground-level spaces"""
        ground_level_cells = [
            cell for cell in self.grid.values() 
            if (not cell.tower or cell.tower.get_tower_level() == 0) and not cell.worker
        ]
        
        if len(ground_level_cells) < sum(len(player.workers) for player in players):
            raise ValueError("Not enough ground-level spaces for all workers")
        
        available_cells = ground_level_cells.copy()
        random.shuffle(available_cells)
        
        cell_index = 0
        for player in players:
            for worker in player.workers:
                if cell_index < len(available_cells):
                    cell = available_cells[cell_index]
                    # Remove worker from current position if any
                    if worker.position:
                        worker.position.remove_worker()
                    
                    # Set new position
                    worker.set_position(cell)
                    cell.assign_worker(worker)
                    cell_index += 1
    
    def get_tower_at(self, coordinate: Coordinate) -> Optional[Tower]:
        """Get tower at specific coordinate"""
        cell = self.get_cell(coordinate)
        return cell.tower if cell else None
    
    def create_hidden_cells(self, num_hidden_cells: int = 2) -> None:
        """
        Creates hidden cells randomly on the board.
        Should be called after workers are placed to avoid conflicts.
        """
        if self.hidden_cells_created:
            return
        
        # Get all empty cells (no workers, ground level)
        available_cells = [
            cell for cell in self.grid.values()
            if not cell.worker and (not cell.tower or cell.tower.get_tower_level() == 0)
        ]
        
        if len(available_cells) < num_hidden_cells:
            num_hidden_cells = len(available_cells)
        
        # Randomly select cells to be hidden
        import random
        selected_cells = random.sample(available_cells, num_hidden_cells)
        
        # Hidden messages that could appear
        hidden_messages = [
            "You found an ancient blessing! +10 seconds granted.",
            "The gods smile upon you! Time flows slower now.",
            "A divine gift has been bestowed upon you!",
            "The spirits of Santorini aid your cause!",
            "Ancient magic flows through this sacred ground!"
        ]
        
        for i, cell in enumerate(selected_cells):
            cell.is_hidden = True
            cell.hidden_message = hidden_messages[i % len(hidden_messages)]
        
        self.hidden_cells_created = True
    
    def get_hidden_cells(self) -> List[Cell]:
        """Returns all hidden cells on the board."""
        return [cell for cell in self.grid.values() if cell.is_hidden]
