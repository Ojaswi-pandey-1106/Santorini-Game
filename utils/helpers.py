import tkinter as tk
from tkinter import simpledialog

class RadioSelectionDialog(simpledialog.Dialog):
    def __init__(self, parent, title, prompt, options):
        self.prompt = prompt
        self.options = options
        self.selection = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(pady=5)

        self.var = tk.StringVar(value=self.options[0])
        for option in self.options:
            tk.Radiobutton(master, text=option, variable=self.var, value=option).pack(anchor='w')

        return master

    def apply(self):
        self.selection = self.var.get()


def show_radio_selection(title, prompt, options, parent=None):
    dialog = RadioSelectionDialog(parent, title, prompt, options)
    return dialog.selection
