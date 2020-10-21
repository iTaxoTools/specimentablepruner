import os.path
import tkinter as tk
import tkinter.filedialog
import tkinter.ttk as ttk
from typing import Literal, Any, Dict, Tuple, List


class FileChooser():
    """
    Creates a frame with a label, entry and browse button for choosing files
    """

    def __init__(self, parent: Any, *, label: str, mode: Literal["open", "save"]):
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure([0, 1], weight=1)
        self.label = ttk.Label(self.frame, text=label)
        self.file_var = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable=self.file_var)
        if mode == "open":
            self._dialog = tk.filedialog.askopenfilename
        elif mode == "save":
            self._dialog = tk.filedialog.asksaveasfilename

        def browse() -> None:
            if (newpath := self._dialog()):
                try:
                    newpath = os.path.relpath(newpath)
                except:
                    newpath = os.path.abspath(newpath)
                self.file_var.set(newpath)

        self.button = ttk.Button(self.frame, text="Browse", command=browse)

        self.label.grid(row=0, column=0, sticky='nws')
        self.entry.grid(row=1, column=0, sticky='nwse')
        self.button.grid(row=1, column=1)
        self.grid = self.frame.grid


class FileOrDirChooser(FileChooser):
    """
    Adds a button to choose a directory to FileChooser
    """

    def __init__(self, parent, *, label: str):
        super().__init__(parent, label=label, mode="open")

        def browse_dir() -> None:
            if (newpath := tk.filedialog.askdirectory()):
                try:
                    newpath = os.path.relpath(newpath)
                except:
                    newpath = os.path.abspath(newpath)
                self.file_var.set(newpath)

        self.dir_button = ttk.Button(
            self.frame, text="Browse dir", command=browse_dir)
        self.dir_button.grid(row=2, column=1)


class LabeledEntry():
    """
    Group of a label, entry and a string variable
    """

    def __init__(self, parent: tk.Widget, *, label: str):
        self.frame = tk.Frame(parent)
        self.label = tk.Label(self.frame, text=label)
        self.var = tk.StringVar()
        self.entry = tk.Entry(self.frame, textvariable=self.var)
        self.frame.columnconfigure(1, weight=1)
        self.label.grid(column=0, row=0)
        self.entry.grid(column=1, row=0)
        self.grid = self.frame.grid
