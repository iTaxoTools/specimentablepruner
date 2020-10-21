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

    def __init__(self, parent: tk.Widget, *, label: str):
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
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, text=label)
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable=self.var)
        self.frame.columnconfigure(1, weight=1)
        self.label.grid(column=0, row=0)
        self.entry.grid(column=1, row=0)
        self.grid = self.frame.grid


class LabeledCombobox():
    """
    Group of a label, combobox and a string variable
    """

    def __init__(self, parent: tk.Widget, *, label: str, values: List[str]):
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, text=label)
        self.var = tk.StringVar()
        self.combobox = ttk.Combobox(
            self.frame, textvariable=self.var, values=values)
        self.frame.columnconfigure(1, weight=1)
        self.label.grid(column=0, row=0)
        self.combobox.grid(column=1, row=0)
        self.grid = self.frame.grid


class ScrolledText():
    """
    A text input widget with two scrollbars
    """

    def __init__(self, parent: tk.Widget, *, label: str) -> None:
        self.frame = ttk.Frame(parent)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.label = ttk.Label(self.frame, text=label)
        self.text = tk.Text(self.frame, width=50, height=20)
        self.vbar = ttk.Scrollbar(
            self.frame, orient=tk.VERTICAL, command=self.text.yview)
        self.hbar = ttk.Scrollbar(
            self.frame, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(xscrollcommand=self.hbar.set,
                            yscrollcommand=self.vbar.set)
        self.label.grid(row=0, column=0, sticky='w')
        self.text.grid(row=1, column=0, sticky='nsew')
        self.vbar.grid(row=1, column=1, sticky='nsew')
        self.hbar.grid(row=2, column=0, sticky='nsew')
        self.grid = self.frame.grid