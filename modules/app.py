"""
app.py
─────────────────────────────────────────────────────────────
PURPOSE:
    The CONTROLLER — the brain that connects every module together.
    Handles all user events, coordinates between grid, algorithms,
    and visualizer.

    Think of it like a manager:
    - GUI gives it inputs (button clicks, dropdown choices)
    - It asks algorithms for paths
    - It tells the visualizer what to draw
    - It manages the grid state

WHY A SEPARATE FILE?
    The controller should NOT know how to draw, how to search,
    or how to store grid data. It just COORDINATES.
    This is the "glue" between all other modules.

HOW IT JOINS:
    It imports from every other module:
        from modules.constants  import ...
        from modules.grid       import GridManager
        from modules.heuristics import get_heuristic
        from modules.algorithms import run_algorithm
        from modules.gui_builder import build_ui
        from modules.visualizer  import Visualizer

    main.py creates this class:
        app = PathfindingApp(root)
─────────────────────────────────────────────────────────────
"""

import time
import tkinter as tk
from tkinter import messagebox

from modules.constants  import (CELL_SIZE, DYN_DELAY,
                                  EMPTY, OBSTACLE, START, GOAL,
                                  COLOR_OBSTACLE, COLOR_EMPTY,
                                  ALGO_ASTAR, ALGO_GBFS,
                                  MODE_OBSTACLE, MODE_START, MODE_GOAL)
from modules.grid        import GridManager
from modules.heuristics  import get_heuristic
from modules.algorithms  import run_algorithm
from modules.gui_builder import build_ui
from modules.visualizer  import Visualizer


class PathfindingApp:
    """
    Main application controller.
    Connects all modules and handles user interaction.
    """

    def __init__(self, root):
        """
        Sets up the application:
        1. Build the Tkinter UI (gui_builder)
        2. Create the grid manager (grid)
        3. Create the visualizer (visualizer)
        4. Bind canvas click event
        5. Draw initial grid
        """
        self.root = root

        # ── 1. Build GUI — get widget references ──────────────
        # build_ui returns a dict of all important widget references
        self.w = build_ui(root, self)   # self.w = widgets dict

        # ── 2. Create Grid Manager ─────────────────────────────
        rows = self.w["rows_var"].get()
        cols = self.w["cols_var"].get()
        self.grid = GridManager(rows, cols)

        # ── 3. Create Visualizer ───────────────────────────────
        self.viz = Visualizer(self.w["canvas"], self.grid, root)

        # ── 4. Bind canvas mouse click ─────────────────────────
        self.w["canvas"].bind("<Button-1>", self._on_canvas_click)

        # ── 5. Draw initial empty grid ─────────────────────────
        self.viz.draw_full_grid()

        # ── Animation & agent state ───────────────────────────
        self.is_running      = False   # Prevents double-starting
        self.current_path    = []      # Active path being walked
        self.agent_pos       = None    # Agent's current grid position
        self.agent_path_idx  = 0       # Index into current_path
        self._dyn_job        = None    # Dynamic timer job handle

    # ─────────────────────────────────────────────────────
    # SECTION A: BUTTON CALLBACKS
    # Called directly by gui_builder button commands
    # ─────────────────────────────────────────────────────

    def apply_grid_size(self):
        """Resize grid based on spinbox values."""
        if self.is_running:
            return
        new_rows = self.w["rows_var"].get()
        new_cols = self.w["cols_var"].get()
        self.grid.resize(new_rows, new_cols)
        self.viz.draw_full_grid()
        self._status("Grid resized to {}×{}. Ready.".format(new_rows, new_cols))

    def generate_random_map(self):
        """Generate random obstacles at the set density."""
        if self.is_running:
            return
        density = self.w["density_var"].get()
        self.grid.generate_random(density)
        self.viz.draw_full_grid()
        self._status("Random map generated ({}% obstacle density).".format(density))

    def clear_obstacles(self):
        """Remove all obstacles from the grid."""
        if self.is_running:
            return
        self.grid.clear_obstacles()
        self.viz.draw_full_grid()
        self._status("All obstacles cleared.")

    def start_search(self):
        """
        Main search trigger — called when user clicks ▶ Start Search.

        Flow:
        1. Reset visualization colors
        2. Get algorithm + heuristic from dropdowns
        3. Run selected algorithm → get path + visited + frontier_log
        4. Update metrics
        5. Start animation
        """
        if self.is_running:
            return

        # Wipe previous visualization colors
        self.viz.reset_visited_colors()
        self._reset_agent_state()
        self.is_running = True

        # ── Get settings ──────────────────────────────────────
        algo_name  = self.w["algo_var"].get()
        heur_name  = self.w["heuristic_var"].get()
        h_fn       = get_heuristic(heur_name)

        # ── Run algorithm (this is INSTANT — just builds path data) ──
        t0 = time.time()
        path, visited, frontier_log = run_algorithm(
            algo_name,
            self.grid.cells,
            self.grid.start,
            self.grid.goal,
            self.grid.rows,
            self.grid.cols,
            h_fn
        )
        exec_ms = (time.time() - t0) * 1000

        # ── No path found? ─────────────────────────────────────
        if path is None:
            self.is_running = False
            self._update_metrics(len(visited), 0, exec_ms)
            messagebox.showwarning(
                "No Path Found",
                "The goal is unreachable!\n"
                "Try clearing some obstacles or moving start/goal."
            )
            return

        # ── Update metrics ─────────────────────────────────────
        self._update_metrics(len(visited), len(path) - 1, exec_ms)
        self._status("{} + {} | {} nodes | Cost: {} | {:.1f}ms".format(
            algo_name, heur_name, len(visited), len(path)-1, exec_ms))

        # ── Start animation ────────────────────────────────────
        # When animation finishes, _on_search_done() is called
        self.viz.animate_search(visited, path, frontier_log,
                                on_done_callback=lambda: self._on_search_done(path))

    def stop_reset(self):
        """Stop animation and reset everything."""
        self._cancel_timers()
        self.is_running = False
        self.viz.reset_visited_colors()
        self._reset_agent_state()
        self._update_metrics(0, 0, 0.0)
        self._status("Reset. Ready to search again.")

    # ─────────────────────────────────────────────────────
    # SECTION B: POST-SEARCH & AGENT MOVEMENT
    # ─────────────────────────────────────────────────────

    def _on_search_done(self, path):
        """
        Called by visualizer when search animation finishes.
        If dynamic mode is ON → start agent walking.
        Otherwise → done.
        """
        if self.w["dynamic_var"].get():
            # Set up agent state
            self.current_path   = path[:]
            self.agent_pos      = self.grid.start
            self.agent_path_idx = 0
            self._step_agent()
        else:
            self.is_running = False
            self._status("Search complete ✅  |  Path shown in green.")

    def _step_agent(self):
        """
        Moves the agent one step along current_path.
        Called repeatedly via root.after() (like an animation frame).

        At each step:
        1. Move agent to next cell
        2. Try spawning a dynamic obstacle
        3. If obstacle blocks path → replan
        4. Otherwise → schedule next step
        """
        if not self.is_running:
            return

        # ── Check if agent reached goal ────────────────────────
        if self.agent_path_idx >= len(self.current_path):
            self.is_running = False
            self._status("🎯 Agent reached the goal!")
            return

        # ── Move agent one step ────────────────────────────────
        old_pos  = self.agent_pos
        new_pos  = self.current_path[self.agent_path_idx]
        self.agent_path_idx += 1

        self.viz.draw_agent(old_pos, new_pos)
        self.agent_pos = new_pos

        # ── Try spawning a dynamic obstacle ────────────────────
        spawn_prob    = self.w["spawn_var"].get() / 100.0
        remaining     = self.current_path[self.agent_path_idx:]  # Unwalked path
        obs_pos, blocked = self.grid.try_spawn_dynamic_obstacle(
            self.agent_pos, remaining, spawn_prob
        )

        if obs_pos:
            # Show the new obstacle on canvas
            self.viz.update_cell(obs_pos[0], obs_pos[1], COLOR_OBSTACLE)

        if blocked:
            # Path is now blocked → REPLAN from current position
            self._status("⚠️ Obstacle blocked path! Replanning...")
            self._replan()
            return   # _replan will reschedule _step_agent

        # ── Schedule next step ────────────────────────────────
        self._dyn_job = self.root.after(DYN_DELAY, self._step_agent)

    def _replan(self):
        """
        Runs the search algorithm again from the agent's CURRENT position.

        Key optimization:
        We only do this when an obstacle actually lands on the path.
        If obstacle appears somewhere else → we skip replanning entirely!
        This is what "avoid recomputing if path not affected" means.
        """
        algo_name = self.w["algo_var"].get()
        h_fn      = get_heuristic(self.w["heuristic_var"].get())

        new_path, visited, frontier_log = run_algorithm(
            algo_name,
            self.grid.cells,
            self.agent_pos,       # ← Start from HERE, not original start!
            self.grid.goal,
            self.grid.rows,
            self.grid.cols,
            h_fn
        )

        if new_path is None:
            self.is_running = False
            messagebox.showerror(
                "Trapped!",
                "Agent is completely blocked!\n"
                "No path exists from current position to goal."
            )
            return

        # ── Redraw paths ───────────────────────────────────────
        old_remaining = self.current_path[self.agent_path_idx:]
        self.viz.draw_new_path(old_remaining, new_path, self.agent_pos)

        # ── Update agent state with new path ───────────────────
        self.current_path   = new_path
        self.agent_path_idx = 1  # Index 0 = current position, skip it

        # ── Update cumulative metrics ──────────────────────────
        curr_visited = int(self.w["lbl_visited"].cget("text").replace("—", "0"))
        curr_cost    = int(self.w["lbl_cost"].cget("text").replace("—", "0"))
        self._update_metrics(
            curr_visited + len(visited),
            curr_cost    + len(new_path) - 1,
            None   # Don't overwrite exec time
        )

        self._status("🔄 Replanned! New segment cost: {}".format(len(new_path)-1))

        # Resume stepping
        self._dyn_job = self.root.after(DYN_DELAY, self._step_agent)

    # ─────────────────────────────────────────────────────
    # SECTION C: CANVAS CLICK HANDLER
    # ─────────────────────────────────────────────────────

    def _on_canvas_click(self, event):
        """
        Handles mouse click on the canvas grid.
        Converts pixel → cell, then applies the current edit mode.
        """
        if self.is_running:
            return  # No editing during search

        # Convert pixel to grid coordinates (account for scrolling!)
        cx = self.w["canvas"].canvasx(event.x)
        cy = self.w["canvas"].canvasy(event.y)
        cell = self.viz.pixel_to_cell(cx, cy)

        if cell is None:
            return  # Clicked outside grid

        row, col = cell
        mode = self.w["edit_mode_var"].get()

        if mode == MODE_OBSTACLE:
            new_state = self.grid.toggle_obstacle(row, col)
            if new_state == OBSTACLE:
                self.viz.update_cell(row, col, COLOR_OBSTACLE)
            elif new_state == EMPTY:
                self.viz.update_cell(row, col, COLOR_EMPTY)

        elif mode == MODE_START:
            old = self.grid.move_start(row, col)
            if old:
                self.viz.update_cell(old[0], old[1], COLOR_EMPTY)
                self.viz.update_cell(row, col,
                    self.viz._state_to_color(self.grid.get_cell(row, col)))
                self.viz._draw_labels()

        elif mode == MODE_GOAL:
            old = self.grid.move_goal(row, col)
            if old:
                self.viz.update_cell(old[0], old[1], COLOR_EMPTY)
                self.viz.update_cell(row, col,
                    self.viz._state_to_color(self.grid.get_cell(row, col)))
                self.viz._draw_labels()

    # ─────────────────────────────────────────────────────
    # SECTION D: UTILITY HELPERS
    # ─────────────────────────────────────────────────────

    def _cancel_timers(self):
        """Cancel all pending root.after() jobs."""
        self.viz.cancel_animation()
        if self._dyn_job:
            self.root.after_cancel(self._dyn_job)
            self._dyn_job = None

    def _reset_agent_state(self):
        """Resets all agent tracking variables."""
        self.current_path   = []
        self.agent_pos      = None
        self.agent_path_idx = 0

    def _update_metrics(self, visited, cost, exec_ms):
        """Updates the metrics labels in the GUI."""
        self.w["lbl_visited"].config(text=str(visited) if visited else "—")
        self.w["lbl_cost"].config(text=str(cost)    if cost    else "—")
        if exec_ms is not None:
            self.w["lbl_time"].config(text="{:.2f}".format(exec_ms))

    def _status(self, msg):
        """Updates status bar and forces immediate repaint."""
        self.w["status_var"].set(msg)
        self.root.update_idletasks()
