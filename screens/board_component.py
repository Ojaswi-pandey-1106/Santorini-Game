import tkinter as tk
from models.coordinate import Coordinate
from models.game import Game
from models.worker import Worker
from models.cell import Cell
from typing import Callable, Dict, List, Optional

class GameBoard(tk.Frame):
    """
    Visual representation of the Santorini game board.
    Follows SRP by only handling board visualization and basic cell interactions.
    """
    
    def __init__(self, master, game: Game, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.game = game
        self.board = game.get_board()
        self.grid_size = self.board.rows
        
        # UI state
        self.canvases: Dict[tuple, tk.Canvas] = {}
        self.highlighted_cells: List[Cell] = []
        self.selected_cell: Optional[Cell] = None
        
        # Callbacks for parent communication
        self.cell_click_callback: Optional[Callable[[int, int], None]] = None
        self.worker_click_callback: Optional[Callable[[Worker], None]] = None
        
        self._create_board_grid()
        self.refresh_display()
        
    def _create_board_grid(self):
        """Create the visual grid of canvas cells."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                canvas = tk.Canvas(
                    self, 
                    width=80, 
                    height=80, 
                    bg='lightblue',
                    highlightthickness=2, 
                    highlightbackground='darkblue'
                )
                canvas.grid(row=row, column=col, padx=1, pady=1)
                canvas.bind("<Button-1>", lambda e, r=row, c=col: self._on_canvas_click(r, c))
                self.canvases[(row, col)] = canvas
                
    def _on_canvas_click(self, row: int, col: int):
        """Handle clicks on canvas cells."""
        coordinate = Coordinate(row, col)
        cell = self.board.get_cell(coordinate)
        
        if not cell:
            return
            
        # Check if clicking on a worker
        if cell.worker and self.worker_click_callback:
            self.worker_click_callback(cell.worker)
        # Check if clicking on a valid target cell
        elif self.cell_click_callback:
            self.cell_click_callback(row, col)
            
    def set_cell_click_callback(self, callback: Callable[[int, int], None]):
        """Set callback for cell clicks."""
        self.cell_click_callback = callback
        
    def set_worker_click_callback(self, callback: Callable[[Worker], None]):
        """Set callback for worker clicks."""
        self.worker_click_callback = callback
        
    def highlight_cells(self, cells: List[Cell], color: str = 'lightgreen'):
        """Highlight specific cells with given color."""
        # Clear previous highlights
        self.clear_highlights()
        
        # Apply new highlights
        self.highlighted_cells = cells.copy()
        for cell in cells:
            row, col = cell.coordinate.row, cell.coordinate.col
            if (row, col) in self.canvases:
                self.canvases[(row, col)].config(bg=color)
                
    def clear_highlights(self):
        """Clear all cell highlights."""
        for cell in self.highlighted_cells:
            row, col = cell.coordinate.row, cell.coordinate.col
            if (row, col) in self.canvases:
                self.canvases[(row, col)].config(bg='lightblue')
        self.highlighted_cells.clear()
        
    def select_cell(self, cell: Cell, color: str = 'darkblue'):
        """Visually select a specific cell."""
        if self.selected_cell:
            self.deselect_cell()
            
        self.selected_cell = cell
        row, col = cell.coordinate.row, cell.coordinate.col
        if (row, col) in self.canvases:
            self.canvases[(row, col)].config(bg=color)
            
    def deselect_cell(self):
        """Deselect the currently selected cell."""
        if self.selected_cell:
            row, col = self.selected_cell.coordinate.row, self.selected_cell.coordinate.col
            if (row, col) in self.canvases:
                # Restore original color (check if it should be highlighted)
                if self.selected_cell in self.highlighted_cells:
                    self.canvases[(row, col)].config(bg='lightgreen')
                else:
                    self.canvases[(row, col)].config(bg='lightblue')
            self.selected_cell = None
            
    def refresh_display(self):
        """Refresh the entire board display."""
        # Clear all canvases
        for canvas in self.canvases.values():
            canvas.delete("all")
            canvas.config(bg='lightblue')
            
        # Redraw all cells
        for (row, col), canvas in self.canvases.items():
            coordinate = Coordinate(row, col)
            cell = self.board.get_cell(coordinate)
            
            if cell:
                # Draw tower if present
                if cell.tower:
                    self._draw_tower(canvas, cell.tower.get_tower_level(), cell.tower.has_dome())
                    
                # Draw worker if present
                if cell.worker:
                    self._draw_worker(canvas, cell.worker)
                    
        # Restore highlights and selection
        if self.highlighted_cells:
            for cell in self.highlighted_cells:
                row, col = cell.coordinate.row, cell.coordinate.col
                if (row, col) in self.canvases:
                    self.canvases[(row, col)].config(bg='lightgreen')
                    
        if self.selected_cell:
            row, col = self.selected_cell.coordinate.row, self.selected_cell.coordinate.col
            if (row, col) in self.canvases:
                self.canvases[(row, col)].config(bg='darkblue')
                
    def _draw_tower(self, canvas: tk.Canvas, level: int, has_dome: bool):
        """Draw a tower on the given canvas."""
        if level == 0 and not has_dome:
            return
            
        base_x, base_y = 15, 65
        block_height = 12
        block_width = 50
        
        # Colors for different levels
        colors = ['#e6e6fa', '#d8bfd8', '#dda0dd']
        
        # Draw blocks
        for i in range(level):
            y_offset = i * block_height
            canvas.create_rectangle(
                base_x, base_y - y_offset - block_height,
                base_x + block_width, base_y - y_offset,
                fill=colors[min(i, len(colors)-1)], 
                outline='#4b0082',
                width=1
            )
            
        # Draw dome if present
        if has_dome:
            dome_y = base_y - level * block_height - 8
            canvas.create_oval(
                base_x + 10, dome_y - 10,
                base_x + block_width - 10, dome_y + 5,
                fill="#ffd700", 
                outline="#8b4513",
                width=2
            )
            
    def _draw_worker(self, canvas: tk.Canvas, worker: Worker):
        """Draw a worker on the given canvas."""
        # Determine player color
        
        color = getattr(worker.player, "token_color", "gray")
        
        # Draw worker body
        canvas.create_oval(25, 20, 55, 50, fill=color, outline='black', width=2)
        
        # Draw worker ID
        canvas.create_text(40, 35, text=str(worker.id), fill='white', 
                          font=('Arial', 12, 'bold'))
