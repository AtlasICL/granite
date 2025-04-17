import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont
from tkinter import ttk
from typing import Optional
from allocator.logic import load_blocks, assign_containers

# Settings for selection window
class GUI_SELECTION_settings:
    WINDOW_TITLE: str = "Geoinvest Block Allocator"
    WINDOW_GEOMETRY: str = "500x400"
    FONT_FAMILY: str = "Arial"
    FONT_SIZE: int = 14
    DATA_ENTRY_FONT_SIZE: int = 12
    CONTAINER_COUNT_TEXT: str = "Number of containers:"
    CONTAINER_PAYLOAD_TEXT: str = "Max weight per container:"

# Settings for results window
class GUI_RESULTS_settings:
    WINDOW_TITLE: str = "Block Allocations"
    WINDOW_GEOMETRY: str = "600x600"
    FONT_FAMILY: str = "Arial"
    FONT_SIZE: int = 14


class BlockAllocatorGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(GUI_SELECTION_settings.WINDOW_TITLE)
        self.geometry(GUI_SELECTION_settings.WINDOW_GEOMETRY)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            style.theme_use(style.theme_names()[0])
        style.configure('.', font=(GUI_SELECTION_settings.FONT_FAMILY, GUI_SELECTION_settings.FONT_SIZE), padding=6)
        entry_font = tkfont.Font(family=GUI_SELECTION_settings.FONT_FAMILY, size=GUI_SELECTION_settings.DATA_ENTRY_FONT_SIZE)

        # Main frame
        main_frame = ttk.Frame(self, padding=(20, 20))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Number of containers
        ttk.Label(main_frame, text=GUI_SELECTION_settings.CONTAINER_COUNT_TEXT).grid(row=0, column=0, sticky="e", padx=5, pady=10)
        self.container_count_var = tk.IntVar(value=2)
        ttk.Entry(main_frame, textvariable=self.container_count_var, width=10, font=entry_font).grid(row=0, column=1, sticky="w", padx=5)

        # Max weight per container
        ttk.Label(main_frame, text=GUI_SELECTION_settings.CONTAINER_PAYLOAD_TEXT).grid(row=1, column=0, sticky="e", padx=5, pady=10)
        self.capacity_var = tk.DoubleVar(value=0.0)
        ttk.Entry(main_frame, textvariable=self.capacity_var, width=10, font=entry_font).grid(row=1, column=1, sticky="w", padx=5)

        # File selection
        self.csv_path: Optional[str] = None
        ttk.Button(main_frame, text="Select CSV File...", command=self.browse_csv, width=20).grid(row=2, column=0, columnspan=2, pady=10)
        self.file_label = ttk.Label(main_frame, text="No file selected", wraplength=300)
        self.file_label.grid(row=3, column=0, columnspan=2)

        ttk.Label(
            main_frame,
            text="Make sure your CSV has columns named 'BlockNo' and 'Weight'",
            wraplength=400,
            foreground="blue",
        ).grid(row=4, column=0, columnspan=2, pady=(0, 15))

        # Run button
        ttk.Button(main_frame, text="Run allocation", command=self.run_allocation, width=20).grid(row=5, column=0, columnspan=2, pady=20)

        for col in range(2):
            main_frame.columnconfigure(col, weight=1)

    def browse_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Select block data CSV")
        if path:
            self.csv_path = path
            self.file_label.config(text=path)

    def run_allocation(self) -> None:
        if not self.csv_path:
            messagebox.showerror("Error", "Please select a CSV file before running.")
            return

        try:
            count = self.container_count_var.get()
            capacity = self.capacity_var.get()
            blocks = load_blocks(self.csv_path)
            assignments = assign_containers(blocks, capacity, count)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process data: {e}")
            return

        # Display results in new window
        result_win = tk.Toplevel(self)
        result_win.title(GUI_RESULTS_settings.WINDOW_TITLE)
        result_win.geometry(GUI_RESULTS_settings.WINDOW_GEOMETRY)

        # Apply same ttk style to results window
        style = ttk.Style(result_win)
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use(style.theme_names()[0])
        style.configure('.', font=(GUI_RESULTS_settings.FONT_FAMILY, GUI_RESULTS_settings.FONT_SIZE), padding=4)

        result_frame = ttk.Frame(result_win, padding=(10, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        cols = 2
        for idx, (cid, info) in enumerate(assignments.items()):
            row, col = divmod(idx, cols)
            blocks_list = info['blocks']
            blocks_str_to_display = ', '.join(str(b) for b in blocks_list) if len(blocks_list) >= 1 else "No blocks"
            total_wt = info['total_weight']
            text = f"Container {cid}:\nBlocks: {blocks_str_to_display}\nTotal: {total_wt:.2f}"
            lbl = ttk.Label(result_frame, text=text, relief=tk.RIDGE, padding=10, justify="left")
            lbl.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            result_frame.columnconfigure(col, weight=1)

if __name__ == '__main__':
    app = BlockAllocatorGUI()
    app.mainloop()
