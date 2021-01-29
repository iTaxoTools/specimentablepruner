#!/usr/bin/env python3
from library.gui_utils import *
import pandas as pd
import tkinter.messagebox as tkmessagebox
import tkinter.font as tkfont
from typing import Set
import re
import sys

format_dict = {
    "tab": '\t',
    "CSV (comma delimited)": ',',
    "CSV (semicolon delimited)": ';'
}

fuzzy_pruning_regex = re.compile(r'[- _./\\]+')


class Pruner():

    def __init__(self) -> None:
        self.fuzzy_pruning = False

    def set_input_sep(self, sep: str) -> None:
        self.input_sep = sep

    def set_output_sep(self, sep: str) -> None:
        self.output_sep = sep

    def set_pruning_field(self, field: str) -> None:
        self.pruning_field = field

    def pruning_from_file(self, file: TextIO) -> None:
        try:
            column = pd.read_csv(file, sep=self.input_sep, usecols=[
                                 self.pruning_field], squeeze=True)
        except ValueError:
            raise ValueError(f"Pruning file {file.name} seems to be missing {self.pruning_field}")
        self.pruning_values: Set[str] = set(column.unique())

    def pruning_from_str(self, text: str) -> None:
        lines = text.split("\n")
        if len(lines) == 1:
            pruning_values = lines[0].split(',')
        else:
            pruning_values = lines
        self.pruning_values = set(pruning_values)

    def set_fuzzy_pruning(self) -> None:
        self.fuzzy_pruning = True
        self.pruning_values = {fuzzy_pruning_regex.sub("", s.casefold()) for s in self.pruning_values}


    def set_files(self, infile: TextIO, backup_outname: str) -> None:
        self.input_file = infile
        try:
            input_name = infile.name
        except AttributeError:
            output_name = backup_outname
        else:
            base, ext = os.path.splitext(input_name)
            output_name = base + "_pruned" + ext
        self.output_file = open(output_name, mode='w', newline='', errors='replace')

    def prune(self) -> None:
        table = pd.read_csv(self.input_file, sep=self.input_sep)
        try:
            pruning_column = table[self.pruning_field]
        except KeyError as ex:
            raise ValueError(f"Input file doesn't contain column {self.pruning_field}") from ex
        else:
            if self.fuzzy_pruning:
                pruning_column = pruning_column.str.casefold().replace(fuzzy_pruning_regex, "")
            table = table.loc[~pruning_column.isin(
                self.pruning_values)]
        table.to_csv(self.output_file, sep=self.output_sep, index=False)


def gui_main() -> None:
    root = tk.Tk()
    root.title("Specimentablepruner")
    if os.name == "nt":
        root.wm_iconbitmap(os.path.join(sys.path[0], 'data', 'specimentablepruner_icon.ico'))

    stype = ttk.Style()
    stype.configure(style="PruneButton.TButton", background="blue")

    banner_frame = ttk.Frame(root)
    logo_img = tk.PhotoImage(file=os.path.join(sys.path[0], 'data', 'iTaxoTools Digital linneaeus MICROLOGO.png'))
    ttk.Label(banner_frame, image=logo_img).grid(row=0, column=0, sticky="nsw")
    ttk.Label(banner_frame, text="Tool to merge the content of tables based on specimen identifiers or species names", font = tkfont.Font(size=14)).grid(row=0, column=2) 

    input_widget = FilesOrText(
        root, file_label="Input file", text_label="Input_text", width=35, height=10, mode='opendir')
    output_file_chooser = FileChooser(
        input_widget.textbox.frame, label="Output file", mode="save")
    output_file_chooser.grid(row=3, column=0)

    prune_widget = FilesOrText(root, file_label="Prune file",
                               text_label="Prune values", width=35, height=10, mode='open')

    prune_field_cmb = LabeledCombobox(root, label="Field to prune", values=[
        "specimenid", "species", "voucher", "locality"])
    prune_field_cmb.var.set("specimenid")

    bottom_frame = ttk.Frame(root)
    input_format_chooser = RadioGroup(
        bottom_frame, label="Format of the input file", values=format_dict, direction='vertical')
    input_format_chooser.var.set('\t')
    output_format_chooser = RadioGroup(
        bottom_frame, label="Format of the output file", values=format_dict, direction='vertical')
    output_format_chooser.var.set('\t')

    pruner = Pruner()

    def prune() -> None:
        try:
            pruner.set_input_sep(input_format_chooser.var.get())
            pruner.set_output_sep(output_format_chooser.var.get())

            pruner.set_pruning_field(prune_field_cmb.var.get())

            if prune_widget.is_file():
                with open(prune_widget.file_name(), errors='replace') as prune_file:
                    pruner.pruning_from_file(prune_file)
            elif prune_widget.is_text():
                pruner.pruning_from_str(prune_widget.text_contents())

            if "fuzzy" in sys.argv:
                pruner.set_fuzzy_pruning()

            backup_outfile_name = output_file_chooser.file_var.get()

            for infile in input_widget.text():
                pruner.set_files(infile, backup_outfile_name)
                pruner.prune()
                pruner.output_file.close()
        except Exception as ex:
            tkmessagebox.showerror("Error", str(ex))
            raise Exception from ex
        else:
            tkmessagebox.showinfo("Done", "Pruning is complete")

    prune_btn = ttk.Button(bottom_frame, text="Prune", command=prune, style="PruneButton.TButton")

    banner_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    ttk.Separator(root, orient='horizontal').grid(row=1, column=0, columnspan=2, sticky="nsew")

    input_widget.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
    prune_field_cmb.grid(row=3, column=0, columnspan=2)
    prune_widget.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

    input_format_chooser.grid(row=2, column=0)
    prune_btn.grid(row=2, column=1, padx=10)
    output_format_chooser.grid(row=2, column=2)
    bottom_frame.grid(row=4, column=0, columnspan=2)

    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    root.mainloop()


def main() -> None:
    gui_main()


if __name__ == "__main__":
    main()
