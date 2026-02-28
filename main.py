"""
main.py
─────────────────────────────────────────────────────────────
PURPOSE:
    The single entry point of the entire application.
    This is the ONLY file the user runs:
        python main.py

WHY IS THIS THE ENTRY POINT?
    By convention in Python projects, main.py is where
    execution begins. It should be SHORT and do only 3 things:
    1. Create the window
    2. Create the app
    3. Start the event loop

    All actual logic lives in the modules/ folder.

HOW DOES IT JOIN EVERYTHING?
    It imports PathfindingApp from modules/app.py.
    PathfindingApp's __init__() then imports and uses:
        ├── modules/gui_builder.py  (builds widgets)
        ├── modules/grid.py         (creates grid data)
        ├── modules/visualizer.py   (draws on canvas)
        ├── modules/algorithms.py   (runs search)
        ├── modules/heuristics.py   (distance formulas)
        └── modules/constants.py    (shared values)

THE FULL IMPORT CHAIN:
    main.py
        └── app.py (PathfindingApp)
                ├── constants.py   ← imported by ALL modules
                ├── gui_builder.py ← builds the Tkinter layout
                ├── grid.py        ← manages 2D grid state
                ├── heuristics.py  ← manhattan / euclidean
                ├── algorithms.py  ← GBFS + A*
                │       └── constants.py (OBSTACLE check)
                └── visualizer.py  ← canvas drawing & animation
─────────────────────────────────────────────────────────────
"""

import tkinter as tk
from modules.app import PathfindingApp


def main():
    """
    Application entry point.
    Creates the Tkinter root window, initializes the app, starts loop.
    """
    # Create the main window
    root = tk.Tk()

    # Hand it to the app controller — this builds all widgets
    app = PathfindingApp(root)

    # Start Tkinter event loop — keeps window open, handles clicks
    # This line blocks until the window is closed
    root.mainloop()


# ── Standard Python guard ─────────────────────────────────
# This check ensures main() only runs when you run this file
# directly (python main.py), NOT when it's imported by something else.
if __name__ == "__main__":
    main()
