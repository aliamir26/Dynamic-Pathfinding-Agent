"""
constants.py
─────────────────────────────────────────────────────────────
PURPOSE:
    One single place to store ALL constant values used across
    the entire project.

WHY A SEPARATE FILE?
    Imagine you want to change the cell size from 40 to 60 pixels.
    Without this file, you'd have to hunt through every file.
    With this file → change ONE line here → done everywhere!

HOW IT JOINS:
    Every other module does:
        from modules.constants import CELL_SIZE, COLOR_PATH, ...
    They READ from here but never write back.
─────────────────────────────────────────────────────────────
"""

# ── Grid Cell Visual Size ──────────────────────────────────
CELL_SIZE = 40          # Width & height of each grid square in pixels

# ── Animation Timing ──────────────────────────────────────
ANIM_DELAY = 80         # Milliseconds between each search visualization step
DYN_DELAY  = 350        # Milliseconds between agent movement steps

# ── Cell State Codes (stored in the 2D grid list) ─────────
# These are just integers — easy to compare: if cell == OBSTACLE
EMPTY    = 0
OBSTACLE = 1
START    = 2
GOAL     = 3

# ── Color Palette (Tkinter hex color strings) ─────────────
COLOR_EMPTY    = "#FFFFFF"   # White  → empty walkable cell
COLOR_OBSTACLE = "#1a1a2e"   # Dark   → wall / blocked cell
COLOR_START    = "#f77f00"   # Orange → start node
COLOR_GOAL     = "#7b2d8b"   # Purple → goal node
COLOR_FRONTIER = "#ffd700"   # Yellow → nodes in priority queue (open list)
COLOR_VISITED  = "#4895ef"   # Blue   → nodes already explored
COLOR_PATH     = "#2dc653"   # Green  → final computed path
COLOR_AGENT    = "#e63946"   # Red    → agent's current live position
COLOR_GRID     = "#cccccc"   # Grey   → grid line borders

# ── UI Theme Colors ────────────────────────────────────────
COLOR_PANEL_BG   = "#16213e"  # Dark blue → left control panel
COLOR_CANVAS_BG  = "#0f0f1a"  # Darkest   → canvas background
COLOR_METRIC_BG  = "#0f3460"  # Medium    → metrics box background
COLOR_ACCENT     = "#4cc9f0"  # Cyan      → section header labels
COLOR_TEXT_MAIN  = "#e2e2e2"  # Light     → main text
COLOR_TEXT_SUB   = "#adb5bd"  # Muted     → secondary labels
COLOR_TEXT_VALUE = "#ffd700"  # Yellow    → metric values

# ── Algorithm Names (used in dropdowns) ───────────────────
ALGO_ASTAR = "A*"
ALGO_GBFS  = "Greedy BFS"

# ── Heuristic Names ────────────────────────────────────────
HEURISTIC_MANHATTAN  = "Manhattan"
HEURISTIC_EUCLIDEAN  = "Euclidean"

# ── Edit Modes (what a cell-click does) ───────────────────
MODE_OBSTACLE = "obstacle"
MODE_START    = "start"
MODE_GOAL     = "goal"
