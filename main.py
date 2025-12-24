import tkinter as tk
from screens.game_setup import GameSetupScreen
from screens.game_board import GameBoardScreen  

def launch_game(game):
    for widget in root.winfo_children():
        widget.destroy()

    game_screen = GameBoardScreen(root, game)
    game_screen.grid(row=0, column=0, sticky="nsew")

root = tk.Tk()
root.title("Santorini Game")

GameSetupScreen(root, launch_game)

root.mainloop()
