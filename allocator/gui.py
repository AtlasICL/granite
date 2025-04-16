import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont
from typing import Optional
from allocator.logic import load_blocks, assign_containers

class GUI_SELECTION_settings:
    WINDOW_TITLE: str = "Block allocator"
    WINDOW_GEOMETRY: str = "500x350"
    FONT: str = "Arial"
    FONT_SIZE: int = 12

class GUI_RESULTS_settings:
    WINDOW_TITLE: str = "Block allocations"
    WINDOW_GEOMETRY: str = "600x600"
    FONT: str = "Arial"
    FONT_SIZE: int = 11

class BlockAllocatorGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(GUI_SELECTION_settings.WINDOW_TITLE)
        self.geometry(GUI_SELECTION_settings.WINDOW_GEOMETRY)
        default_font = tkfont.Font(family=GUI_SELECTION_settings.FONT, size=GUI_SELECTION_settings.FONT_SIZE)
        self.option_add("*Font", default_font)

        # Main frame with padding
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Number of containers
        tk.Label(main_frame, text="Number of containers:").grid(
            row=0, column=0, sticky="e", padx=5, pady=10
        )
        self.container_count_var = tk.IntVar(value=1)
        tk.Entry(main_frame, textvariable=self.container_count_var, width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=10
        )

        # Max weight per container
        tk.Label(main_frame, text="Max weight per container:").grid(
            row=1, column=0, sticky="e", padx=5, pady=10
        )
        self.capacity_var = tk.DoubleVar(value=0.0)
        tk.Entry(main_frame, textvariable=self.capacity_var, width=10).grid(
            row=1, column=1, sticky="w", padx=5, pady=10
        )

        # File selection
        self.csv_path: Optional[str] = None
        tk.Button(
            main_frame, text="Select CSV File...", command=self.browse_csv,
            width=20
        ).grid(row=2, column=0, columnspan=2, pady=10)

        self.file_label = tk.Label(main_frame, text="No file selected", wraplength=300)
        self.file_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.help_text = tk.Label(
            main_frame,
            text="Make sure your CSV has columns named \"BlockNo\" and \"Weight\".",
            wraplength=400,
            fg="blue"
        )
        self.help_text.grid(row=4, column=0, columnspan=2, pady=(0, 15))

        # Run button
        tk.Button(
            main_frame, text="Run program", command=self.run_allocation,
            width=20
        ).grid(row=5, column=0, columnspan=2, pady=20)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def browse_csv(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Select block data CSV"
        )
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
            messagebox.showerror("Error", f"Failed to load or process data: {e}")
            return

        # Create results window
        result_win = tk.Toplevel(self)
        result_win.title(GUI_RESULTS_settings.WINDOW_TITLE)
        result_win.geometry(GUI_RESULTS_settings.WINDOW_GEOMETRY)
        result_font = tkfont.Font(family=GUI_RESULTS_settings.FONT, size=GUI_RESULTS_settings.FONT_SIZE)
        result_frame = tk.Frame(result_win, padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        cols = 2
        for idx, (cid, info) in enumerate(assignments.items()):
            row = idx // cols
            col = idx % cols
            blocks_list = info["blocks"]
            total_wt = info["total_weight"]
            text = f"Container {cid}:\nBlocks: {blocks_list}\nTotal: {total_wt}"
            lbl = tk.Label(
                result_frame, text=text, font=result_font,
                relief=tk.RIDGE, padx=10, pady=10, justify="left"
            )
            lbl.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            result_frame.grid_columnconfigure(col, weight=1)
