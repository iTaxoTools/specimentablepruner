#!/usr/bin/env python3
from library.gui_utils import *
import pandas as pd
import tkinter.messagebox as tkmessagebox
from typing import Set

format_dict = {
    "tab": '\t',
    "CSV (comma delimited)": ',',
    "CSV (semicolon delimited)": ';'
}


class Pruner():

    def set_input_sep(self, sep: str) -> None:
        self.input_sep = sep

    def set_output_sep(self, sep: str) -> None:
        self.output_sep = sep

    def set_pruning_field(self, field: str) -> None:
        self.pruning_field = field

    def pruning_from_file(self, file: TextIO) -> None:
        column = pd.read_csv(file, sep=self.input_sep, usecols=[
                             self.pruning_field], squeeze=True)
        self.pruning_values: Set[str] = set(column.unique())

    def pruning_from_str(self, text: str) -> None:
        lines = text.split("\n")
        if len(lines) == 1:
            pruning_values = lines[0].split(',')
        else:
            pruning_values = lines
        self.pruning_values = set(pruning_values)

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
            table = table.loc[~table[self.pruning_field].isin(
                self.pruning_values)]
        except KeyError as ex:
            raise ValueError(f"Input file doesn't contain column {self.pruning_field}") from ex
        table.to_csv(self.output_file, sep=self.output_sep)


def gui_main() -> None:
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)

    input_widget = FilesOrText(
        root, file_label="Input file", text_label="Input_text", width=20, height=20, mode='opendir')
    output_file_chooser = FileChooser(
        input_widget.textbox.frame, label="Output file", mode="save")
    output_file_chooser.grid(row=3, column=0)

    prune_widget = FilesOrText(root, file_label="Prune file",
                               text_label="Prune values", width=20, height=20, mode='open')

    prune_field_cmb = LabeledCombobox(root, label="Field to prune", values=[
        "specimenid", "species", "voucher", "locality"])
    prune_field_cmb.var.set("specimenid")

    input_format_chooser = RadioGroup(
        root, label="Format of the input file", values=format_dict, direction='vertical')
    input_format_chooser.var.set('\t')
    output_format_chooser = RadioGroup(
        root, label="Format of the input file", values=format_dict, direction='vertical')
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

    prune_btn = ttk.Button(root, text="Prune", command=prune)

    input_widget.grid(row=0, column=0, sticky="nsew")
    prune_field_cmb.grid(row=1, column=0)
    prune_widget.grid(row=2, column=0, sticky="nsew")

    input_format_chooser.grid(row=1, column=1)
    prune_btn.grid(row=1, column=2)
    output_format_chooser.grid(row=1, column=3)

    root.mainloop()


def main() -> None:
    gui_main()


if __name__ == "__main__":
    main()
