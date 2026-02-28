"""
grid.py
─────────────────────────────────────────────────────────────
PURPOSE:
    Manages the GRID DATA — the 2D list that stores cell states.
    Handles creation, reset, obstacle placement, random generation.
    This is the "map" of the world the agent lives in.

WHY A SEPARATE FILE?
    The grid is the shared "state" of the application.
    Separating it means:
    - GUI (app.py) just asks grid: "what's at (row, col)?"
    - Algorithms just read the grid — they never modify it
    - Dynamic obstacles write to the grid through this module
    - All grid rules (can't place obstacle on start) live here

HOW IT JOINS:
    - app.py creates a GridManager instance and passes it around
    - algorithms.py receives grid.cells (the raw 2D list) to read
    - dynamic.py calls grid.place_obstacle() to spawn new walls
─────────────────────────────────────────────────────────────
"""

import random
from modules.constants import EMPTY, OBSTACLE, START, GOAL


class GridManager:
    """
    Manages the state of the grid.
    Stores all cell values and provides clean methods
    to modify them safely.
    """

    def __init__(self, rows, cols):
        """
        Creates a new blank grid of given size.
        Automatically places start at (0,0) and goal at
        bottom-right corner.

        Args:
            rows : number of rows
            cols : number of columns
        """
        self.rows = rows
        self.cols = cols
        self.start = (0, 0)
        self.goal  = (rows - 1, cols - 1)

        # The core 2D list: self.cells[row][col] = state (int)
        self.cells = self._make_empty_grid()

        # Mark start and goal in the grid
        self.cells[self.start[0]][self.start[1]] = START
        self.cells[self.goal[0]][self.goal[1]]   = GOAL

    # ─────────────────────────────────────────────────────
    # CREATION & RESET
    # ─────────────────────────────────────────────────────

    def _make_empty_grid(self):
        """
        Creates a 2D list of all EMPTY cells.
        List comprehension builds rows × cols grid in one line.
        """
        return [[EMPTY for _ in range(self.cols)]
                for _ in range(self.rows)]

    def resize(self, new_rows, new_cols):
        """
        Resizes the grid, resets everything.
        Called when user changes rows/cols and clicks Apply.
        """
        self.rows  = new_rows
        self.cols  = new_cols
        self.start = (0, 0)
        self.goal  = (new_rows - 1, new_cols - 1)
        self.cells = self._make_empty_grid()
        self.cells[self.start[0]][self.start[1]] = START
        self.cells[self.goal[0]][self.goal[1]]   = GOAL

    def clear_obstacles(self):
        """
        Removes ALL obstacles from the grid.
        Preserves start and goal positions.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c] == OBSTACLE:
                    self.cells[r][c] = EMPTY

    def reset_visualization_state(self):
        """
        Only clears EMPTY cells (restores white color state).
        Does NOT touch obstacles, start, or goal.
        This is called before running a new search to wipe old
        blue/green/yellow visualization from previous run.
        """
        # No actual cell state change needed here for visualization
        # (colors are drawn by the GUI) — but this keeps grid data clean
        pass  # GUI handles color resets directly

    # ─────────────────────────────────────────────────────
    # OBSTACLE MANAGEMENT
    # ─────────────────────────────────────────────────────

    def toggle_obstacle(self, row, col):
        """
        Toggles a cell between EMPTY and OBSTACLE.
        Called when user clicks a cell in obstacle edit mode.

        Returns: the new state of the cell (EMPTY or OBSTACLE)
        """
        if not self._is_safe_to_edit(row, col):
            return None  # Can't edit start or goal

        if self.cells[row][col] == OBSTACLE:
            self.cells[row][col] = EMPTY
            return EMPTY
        else:
            self.cells[row][col] = OBSTACLE
            return OBSTACLE

    def place_obstacle(self, row, col):
        """
        Places an obstacle at (row, col).
        Safe version: checks bounds and protection.
        Returns True if obstacle was placed, False otherwise.
        """
        if not self._is_safe_to_edit(row, col):
            return False
        if self.cells[row][col] == OBSTACLE:
            return False  # Already an obstacle
        self.cells[row][col] = OBSTACLE
        return True

    def generate_random(self, density_percent):
        """
        Fills the grid with random obstacles based on density %.

        Algorithm:
        - For every cell that's not start or goal:
          - Generate a random float 0.0 to 1.0
          - If it's less than density (e.g., 0.30 for 30%) → obstacle

        Args:
            density_percent: integer like 30 (means 30% obstacles)
        """
        density = density_percent / 100.0  # Convert 30 → 0.30

        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) == self.start or (r, c) == self.goal:
                    continue  # Never block start or goal
                if random.random() < density:
                    self.cells[r][c] = OBSTACLE
                else:
                    self.cells[r][c] = EMPTY  # Clear in case it was obstacle before

    def try_spawn_dynamic_obstacle(self, agent_pos, current_path, spawn_prob):
        """
        Tries to spawn a single random obstacle during agent movement.
        This is the DYNAMIC part of the project!

        Logic:
        1. Roll a random number — if > spawn_prob, don't spawn anything
        2. Pick a random empty cell that's not start/goal/agent
        3. Place the obstacle
        4. Check if it's on the remaining path
        5. Return (spawned_position, did_it_block_path)

        Args:
            agent_pos    : current (row, col) of the agent
            current_path : list of remaining path cells to check
            spawn_prob   : float 0.0–1.0, chance of spawning

        Returns:
            (row, col) of spawned obstacle, or None if nothing spawned
            bool: True if the new obstacle blocks the current path
        """
        if random.random() > spawn_prob:
            return None, False  # No obstacle this step

        # Try up to 20 random cells to find a valid placement spot
        for _ in range(20):
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            # Skip protected positions
            if (r, c) == self.start:    continue
            if (r, c) == self.goal:     continue
            if (r, c) == agent_pos:     continue
            if self.cells[r][c] == OBSTACLE: continue

            # Place the obstacle
            self.cells[r][c] = OBSTACLE

            # Check if it's on the remaining (unwalked) path
            blocks_path = (r, c) in current_path

            return (r, c), blocks_path

        return None, False  # Couldn't find a valid spot

    # ─────────────────────────────────────────────────────
    # START / GOAL MOVEMENT
    # ─────────────────────────────────────────────────────

    def move_start(self, new_row, new_col):
        """
        Moves the start position to a new cell.
        Clears the old start cell, marks the new one.

        Returns: old start position (so GUI can repaint it)
        """
        if (new_row, new_col) == self.goal:
            return None  # Can't place start on goal

        old_start = self.start
        self.cells[old_start[0]][old_start[1]] = EMPTY

        self.start = (new_row, new_col)
        self.cells[new_row][new_col] = START

        return old_start

    def move_goal(self, new_row, new_col):
        """
        Moves the goal position to a new cell.
        Returns: old goal position (so GUI can repaint it)
        """
        if (new_row, new_col) == self.start:
            return None  # Can't place goal on start

        old_goal = self.goal
        self.cells[old_goal[0]][old_goal[1]] = EMPTY

        self.goal = (new_row, new_col)
        self.cells[new_row][new_col] = GOAL

        return old_goal

    # ─────────────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────────────

    def _is_safe_to_edit(self, row, col):
        """
        Returns True if a cell can be edited (not start or goal).
        """
        if (row, col) == self.start: return False
        if (row, col) == self.goal:  return False
        if not (0 <= row < self.rows): return False
        if not (0 <= col < self.cols): return False
        return True

    def get_cell(self, row, col):
        """Returns the state of a cell (EMPTY, OBSTACLE, START, GOAL)."""
        return self.cells[row][col]

    def is_obstacle(self, row, col):
        """Convenience check — is this cell an obstacle?"""
        return self.cells[row][col] == OBSTACLE
