import io
import os.path
import tkinter as tk
import tkinter.filedialog
import tkinter.ttk as ttk
from typing import Any, Dict, Iterator, List, Literal, TextIO, Tuple


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

    def __init__(self, parent: tk.Misc, *, label: str):
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

    def __init__(self, parent: tk.Misc, *, label: str):
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

    def __init__(self, parent: tk.Misc, *, label: str, values: List[str]):
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

    def __init__(self, parent: tk.Misc, *, label: str, width: int, height: int) -> None:
        self.frame = ttk.Frame(parent)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.label = ttk.Label(self.frame, text=label)
        self.text = tk.Text(self.frame, width=width, height=height)
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

    def get_text(self) -> str:
        return self.text.get('1.0', 'end')


class FilesOrText():
    """
    Two tabs: one for choosing a file, another for inputting text
    """

    def __init__(self, parent: tk.Misc, *, file_label: str, text_label: str, width: int, height: int, mode: Literal['open', 'save', 'opendir']) -> None:
        """
        width and height are the parameters of the textbox
        file_label is shown at the file name entry
        text_label is shown at the textbox
        """
        self.notebook = ttk.Notebook(parent)
        if mode == 'opendir':
            self.filechooser: FileChooser = FileOrDirChooser(
                self.notebook, label=file_label)
        else:
            self.filechooser = FileChooser(
                self.notebook, label=file_label, mode=mode)
        self.textbox = ScrolledText(
            self.notebook, label=text_label, width=width, height=height)
        self.notebook.add(self.filechooser.frame, text=file_label)
        self.notebook.add(self.textbox.frame, text=text_label)
        self.grid = self.notebook.grid

    def text(self) -> Iterator[TextIO]:
        if self.notebook.index('current') == 0:
            path = self.filechooser.file_var.get()
            if os.path.isdir(path):
                for entry in os.listdir(path):
                    with open(entry.path) as file:
                        yield file
            else:
                with open(path) as file:
                    yield file
        elif self.notebook.index('current') == 1:
            yield io.StringIO(self.textbox.get_text())

    def is_file(self) -> bool:
        return self.notebook.index('current') == 0

    def is_text(self) -> bool:
        return self.notebook.index('current') == 1

    def text_contents(self) -> str:
        return self.textbox.get_text()

    def file_name(self) -> str:
        return self.filechooser.file_var.get()


class RadioGroup():
    """
    Generates a group of exclusive radiobuttons
    """

    def __init__(self, parent: tk.Misc, *, label: str, values: Dict[str, str], direction: Literal['horizontal', 'vertical']) -> None:
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, text=label)
        self.subframe = ttk.Frame(self.frame, relief='sunken', padding=5)
        self.var = tk.StringVar()
        self.radiobuttons = []
        for name, value in values.items():
            self.radiobuttons.append(ttk.Radiobutton(
                self.subframe, text=name, variable=self.var, value=value))
        dx, dy = (1, 0) if direction == 'horizontal' else (0, 1)
        for i in range(len(values)):
            self.radiobuttons[i].grid(row=i*dy, column=i*dx, sticky="w")
        self.label.grid(row=0, column=0, sticky="w")
        self.subframe.grid(row=1, column=0, sticky="nsew")
        self.grid = self.frame.grid
