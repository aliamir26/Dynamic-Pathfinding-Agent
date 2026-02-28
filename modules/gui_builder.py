"""
gui_builder.py
─────────────────────────────────────────────────────────────
PURPOSE:
    Responsible for BUILDING and LAYING OUT all Tkinter widgets.
    Left control panel + canvas + legend + metric labels.
    Does NOT handle logic — just creates widgets and returns
    references so app.py can interact with them.

WHY A SEPARATE FILE?
    GUI code is often the longest and most cluttered part.
    By separating "building widgets" from "handling events",
    we keep each file focused:
    - gui_builder.py  → WHAT the UI looks like (widgets, layout)
    - app.py          → WHAT happens when widgets are used (events)

HOW IT JOINS:
    app.py does:
        from modules.gui_builder import build_ui
        self.widgets = build_ui(self.root, self)
    build_ui returns a dictionary of important widget references
    (dropdowns, labels, canvas) that app.py uses to read/update.
─────────────────────────────────────────────────────────────
"""

import tkinter as tk
from tkinter import ttk
from modules.constants import (
    COLOR_PANEL_BG, COLOR_CANVAS_BG, COLOR_METRIC_BG,
    COLOR_ACCENT, COLOR_TEXT_MAIN, COLOR_TEXT_SUB, COLOR_TEXT_VALUE,
    COLOR_START, COLOR_GOAL, COLOR_PATH, COLOR_VISITED,
    COLOR_FRONTIER, COLOR_OBSTACLE, COLOR_AGENT,
    ALGO_ASTAR, ALGO_GBFS, HEURISTIC_MANHATTAN, HEURISTIC_EUCLIDEAN,
    MODE_OBSTACLE, MODE_START, MODE_GOAL
)


def build_ui(root, app):
    """
    Builds the entire Tkinter UI and returns a widget dictionary.

    Args:
        root : the Tk root window
        app  : the PathfindingApp instance (for binding callbacks)

    Returns:
        dict with keys pointing to important widget references
        that app.py needs to read values from or update.
    """
    root.title("🧭 Dynamic Pathfinding Agent")
    root.configure(bg=COLOR_CANVAS_BG)
    root.minsize(900, 600)
    root.geometry("1150x720")

    # ── Left Control Panel ──────────────────────────────────
    left_panel = tk.Frame(root, bg=COLOR_PANEL_BG, padx=12, pady=12, width=265)
    left_panel.pack(side=tk.LEFT, fill=tk.Y)
    left_panel.pack_propagate(False)  # Keep fixed width

    # ── Title ─────────────────────────────────────────────
    tk.Label(left_panel, text="🧭 Pathfinding Agent",
             font=("Segoe UI", 14, "bold"),
             bg=COLOR_PANEL_BG, fg=COLOR_TEXT_MAIN).pack(pady=(0, 12))

    # ── Section: Grid Settings ─────────────────────────────
    _section(left_panel, "Grid Settings")

    rows_var = tk.IntVar(value=10)
    cols_var = tk.IntVar(value=10)
    _spinrow(left_panel, "Rows:", rows_var, 5, 25)
    _spinrow(left_panel, "Cols:", cols_var, 5, 25)
    _btn(left_panel, "🔄 Apply Grid Size", app.apply_grid_size)

    # ── Section: Map Generation ────────────────────────────
    _section(left_panel, "Map Generation")

    density_var = tk.IntVar(value=30)
    _spinrow(left_panel, "Obstacle %:", density_var, 5, 70)
    _btn(left_panel, "🎲 Generate Random Map", app.generate_random_map)
    _btn(left_panel, "🧹 Clear All Obstacles",  app.clear_obstacles)

    # ── Section: Map Editor ────────────────────────────────
    _section(left_panel, "Map Editor  (Click Cells)")

    edit_mode_var = tk.StringVar(value=MODE_OBSTACLE)
    for label, val in [("✏️ Add/Remove Wall", MODE_OBSTACLE),
                       ("🟠 Set Start",        MODE_START),
                       ("🟣 Set Goal",         MODE_GOAL)]:
        tk.Radiobutton(
            left_panel, text=label,
            variable=edit_mode_var, value=val,
            bg=COLOR_PANEL_BG, fg=COLOR_TEXT_SUB,
            selectcolor="#0f3460", activebackground=COLOR_PANEL_BG,
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W)

    # ── Section: Algorithm ─────────────────────────────────
    _section(left_panel, "Algorithm Settings")

    tk.Label(left_panel, text="Algorithm:", bg=COLOR_PANEL_BG,
             fg=COLOR_TEXT_SUB, font=("Segoe UI", 9)).pack(anchor=tk.W)
    algo_var = tk.StringVar(value=ALGO_ASTAR)
    algo_combo = ttk.Combobox(left_panel, textvariable=algo_var,
                               values=[ALGO_ASTAR, ALGO_GBFS],
                               state="readonly", font=("Segoe UI", 9))
    algo_combo.pack(fill=tk.X, pady=2)

    tk.Label(left_panel, text="Heuristic:", bg=COLOR_PANEL_BG,
             fg=COLOR_TEXT_SUB, font=("Segoe UI", 9)).pack(anchor=tk.W)
    heuristic_var = tk.StringVar(value=HEURISTIC_MANHATTAN)
    heur_combo = ttk.Combobox(left_panel, textvariable=heuristic_var,
                               values=[HEURISTIC_MANHATTAN, HEURISTIC_EUCLIDEAN],
                               state="readonly", font=("Segoe UI", 9))
    heur_combo.pack(fill=tk.X, pady=2)

    # ── Section: Dynamic Mode ──────────────────────────────
    _section(left_panel, "Dynamic Mode")

    dynamic_var = tk.BooleanVar(value=False)
    tk.Checkbutton(left_panel, text="Enable Dynamic Obstacles",
                   variable=dynamic_var,
                   bg=COLOR_PANEL_BG, fg=COLOR_TEXT_SUB,
                   selectcolor="#0f3460", activebackground=COLOR_PANEL_BG,
                   font=("Segoe UI", 9)).pack(anchor=tk.W)

    spawn_var = tk.IntVar(value=10)
    _spinrow(left_panel, "Spawn Prob %:", spawn_var, 1, 40)

    # ── Section: Controls ──────────────────────────────────
    _section(left_panel, "Controls")
    _btn(left_panel, "▶  Start Search",  app.start_search,  color="#2dc653")
    _btn(left_panel, "⏹  Stop / Reset", app.stop_reset,     color="#e63946")

    # ── Section: Metrics ───────────────────────────────────
    _section(left_panel, "Real-Time Metrics")
    metrics_box = tk.Frame(left_panel, bg=COLOR_METRIC_BG, padx=8, pady=8)
    metrics_box.pack(fill=tk.X, pady=4)

    lbl_visited = _metric(metrics_box, "Nodes Visited:")
    lbl_cost    = _metric(metrics_box, "Path Cost:")
    lbl_time    = _metric(metrics_box, "Exec Time (ms):")

    # ── Status Bar ─────────────────────────────────────────
    status_var = tk.StringVar(value="Ready. Configure settings and click ▶ Start Search.")
    tk.Label(left_panel, textvariable=status_var,
             bg=COLOR_PANEL_BG, fg="#ffd700",
             font=("Segoe UI", 8), wraplength=238,
             justify=tk.LEFT).pack(pady=(10, 0))

    # ── Right Canvas Area ──────────────────────────────────
    right_frame = tk.Frame(root, bg=COLOR_CANVAS_BG)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

    canvas_frame = tk.Frame(right_frame, bg=COLOR_CANVAS_BG)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(canvas_frame,
                       bg=COLOR_CANVAS_BG,
                       xscrollcommand=h_scroll.set,
                       yscrollcommand=v_scroll.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    h_scroll.config(command=canvas.xview)
    v_scroll.config(command=canvas.yview)

    # ── Legend ─────────────────────────────────────────────
    _build_legend(right_frame)

    # ── Return all important widget refs ───────────────────
    # app.py uses these to read values and update labels
    return {
        "canvas"       : canvas,
        "rows_var"     : rows_var,
        "cols_var"     : cols_var,
        "density_var"  : density_var,
        "edit_mode_var": edit_mode_var,
        "algo_var"     : algo_var,
        "heuristic_var": heuristic_var,
        "dynamic_var"  : dynamic_var,
        "spawn_var"    : spawn_var,
        "status_var"   : status_var,
        "lbl_visited"  : lbl_visited,
        "lbl_cost"     : lbl_cost,
        "lbl_time"     : lbl_time,
    }


# ─────────────────────────────────────────────────────────
# PRIVATE HELPER FUNCTIONS (only used inside this file)
# ─────────────────────────────────────────────────────────

def _section(parent, text):
    """Styled section header label."""
    tk.Label(parent, text=text,
             font=("Segoe UI", 9, "bold"),
             bg=COLOR_PANEL_BG, fg=COLOR_ACCENT).pack(anchor=tk.W, pady=(10, 2))


def _btn(parent, text, command, color="#4895ef"):
    """Styled action button."""
    tk.Button(parent, text=text, command=command,
              bg=color, fg="white",
              font=("Segoe UI", 9, "bold"),
              relief=tk.FLAT, padx=6, pady=4,
              cursor="hand2").pack(fill=tk.X, pady=2)


def _spinrow(parent, label_text, var, from_, to):
    """A label + spinbox in one horizontal row."""
    frame = tk.Frame(parent, bg=COLOR_PANEL_BG)
    frame.pack(fill=tk.X, pady=2)
    tk.Label(frame, text=label_text, bg=COLOR_PANEL_BG,
             fg=COLOR_TEXT_SUB, font=("Segoe UI", 9)).pack(side=tk.LEFT)
    tk.Spinbox(frame, from_=from_, to=to, textvariable=var,
               width=5, font=("Segoe UI", 9)).pack(side=tk.RIGHT)


def _metric(parent, label_text):
    """
    Creates one metric row (label + value).
    Returns the VALUE label so app.py can call .config(text=...) on it.
    """
    frame = tk.Frame(parent, bg=COLOR_METRIC_BG)
    frame.pack(fill=tk.X, pady=1)
    tk.Label(frame, text=label_text, bg=COLOR_METRIC_BG,
             fg=COLOR_TEXT_SUB, font=("Segoe UI", 8)).pack(side=tk.LEFT)
    val_lbl = tk.Label(frame, text="—", bg=COLOR_METRIC_BG,
                       fg=COLOR_TEXT_VALUE, font=("Segoe UI", 8, "bold"))
    val_lbl.pack(side=tk.RIGHT)
    return val_lbl


def _build_legend(parent):
    """Builds the color key legend at the bottom of the canvas area."""
    legend = tk.Frame(parent, bg=COLOR_CANVAS_BG)
    legend.pack(fill=tk.X, pady=4)

    items = [
        ("Start",    COLOR_START),
        ("Goal",     COLOR_GOAL),
        ("Path",     COLOR_PATH),
        ("Visited",  COLOR_VISITED),
        ("Frontier", COLOR_FRONTIER),
        ("Obstacle", COLOR_OBSTACLE),
        ("Agent",    COLOR_AGENT),
    ]
    for name, color in items:
        box = tk.Frame(legend, bg=color, width=14, height=14)
        box.pack(side=tk.LEFT, padx=(6, 2))
        box.pack_propagate(False)
        tk.Label(legend, text=name, bg=COLOR_CANVAS_BG,
                 fg=COLOR_TEXT_SUB, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(0, 6))
