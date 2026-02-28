"""
visualizer.py
─────────────────────────────────────────────────────────────
PURPOSE:
    Handles ALL canvas drawing and animation.
    Draws cells, updates colors, plays back search animation
    frame by frame.

WHY A SEPARATE FILE?
    Visualization is purely about "how things look on screen".
    Separating it means:
    - app.py says "draw this path" without knowing how
    - If you switch from Tkinter to Pygame later, only THIS file changes
    - Animation timing logic stays in one place

HOW IT JOINS:
    app.py creates a Visualizer instance:
        self.viz = Visualizer(canvas, grid)
    Then calls:
        self.viz.draw_full_grid()
        self.viz.update_cell(row, col, color)
        self.viz.animate_search(visited, path, frontier_log, callback)
─────────────────────────────────────────────────────────────
"""

from modules.constants import (
    CELL_SIZE, ANIM_DELAY,
    COLOR_EMPTY, COLOR_OBSTACLE, COLOR_START, COLOR_GOAL,
    COLOR_VISITED, COLOR_FRONTIER, COLOR_PATH, COLOR_AGENT,
    COLOR_GRID,
    EMPTY, OBSTACLE, START, GOAL
)


class Visualizer:
    """
    Manages all canvas drawing operations.
    Keeps a dictionary of canvas rectangle IDs so we can
    update individual cell colors without redrawing everything.
    """

    def __init__(self, canvas, grid_manager, root):
        """
        Args:
            canvas       : Tkinter Canvas widget
            grid_manager : GridManager instance (to read cell states)
            root         : Tk root (needed for root.after() scheduling)
        """
        self.canvas  = canvas
        self.grid    = grid_manager
        self.root    = root

        # cell_rects: {(row, col): canvas_rectangle_id}
        # Stored so we can do fast color updates with itemconfig()
        self.cell_rects = {}

        # Animation job handles (so we can cancel them)
        self._anim_job = None

    # ─────────────────────────────────────────────────────
    # FULL GRID DRAWING
    # ─────────────────────────────────────────────────────

    def draw_full_grid(self):
        """
        Clears the canvas and draws every cell from scratch.
        Called on startup, resize, and full reset.

        Steps:
        1. Delete everything on canvas
        2. Set scroll region to match grid size
        3. Draw each cell as a colored rectangle
        4. Add S/G text labels on start/goal cells
        """
        self.canvas.delete("all")
        self.cell_rects = {}

        total_w = self.grid.cols * CELL_SIZE
        total_h = self.grid.rows * CELL_SIZE
        self.canvas.config(scrollregion=(0, 0, total_w + 4, total_h + 4))

        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = self._state_to_color(self.grid.get_cell(r, c))

                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline=COLOR_GRID, width=1
                )
                self.cell_rects[(r, c)] = rect_id

        # Draw S and G labels on top
        self._draw_labels()

    # ─────────────────────────────────────────────────────
    # SINGLE CELL UPDATE
    # ─────────────────────────────────────────────────────

    def update_cell(self, row, col, color):
        """
        Updates only the color of a single cell rectangle.
        This is MUCH faster than redrawing the entire grid.

        Called hundreds of times during animation — needs to be fast.

        Args:
            row, col : cell position
            color    : hex color string e.g. "#4895ef"
        """
        if (row, col) in self.cell_rects:
            self.canvas.itemconfig(self.cell_rects[(row, col)], fill=color)

    def reset_visited_colors(self):
        """
        Resets all EMPTY cells back to white (COLOR_EMPTY).
        Called before a new search to clear old blue/yellow/green colors.
        Preserves obstacle, start, goal colors.
        """
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                state = self.grid.get_cell(r, c)
                if state == EMPTY:
                    self.update_cell(r, c, COLOR_EMPTY)
        self._draw_labels()

    # ─────────────────────────────────────────────────────
    # LABEL DRAWING
    # ─────────────────────────────────────────────────────

    def _draw_labels(self):
        """Draws 'S' and 'G' text on start and goal cells."""
        self.canvas.delete("label")
        sr, sc = self.grid.start
        gr, gc = self.grid.goal

        self.canvas.create_text(
            sc * CELL_SIZE + CELL_SIZE // 2,
            sr * CELL_SIZE + CELL_SIZE // 2,
            text="S", fill="white",
            font=("Segoe UI", 10, "bold"), tags="label"
        )
        self.canvas.create_text(
            gc * CELL_SIZE + CELL_SIZE // 2,
            gr * CELL_SIZE + CELL_SIZE // 2,
            text="G", fill="white",
            font=("Segoe UI", 10, "bold"), tags="label"
        )

    # ─────────────────────────────────────────────────────
    # PIXEL → GRID CONVERSION
    # ─────────────────────────────────────────────────────

    def pixel_to_cell(self, canvas_x, canvas_y):
        """
        Converts a pixel coordinate (from mouse click) to
        a (row, col) grid coordinate.

        Must use canvas.canvasx/y to account for scrolling!

        Returns (row, col) or None if out of bounds.
        """
        col = int(canvas_x // CELL_SIZE)
        row = int(canvas_y // CELL_SIZE)
        if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
            return (row, col)
        return None

    # ─────────────────────────────────────────────────────
    # SEARCH ANIMATION
    # ─────────────────────────────────────────────────────

    def animate_search(self, visited, path, frontier_log, on_done_callback):
        """
        Animates the search exploration step-by-step.
        Uses root.after() — a non-blocking timer — to show
        each step with a delay, so the user can see progress.

        Phase 1: Show visited (blue) and frontier (yellow) cells
        Phase 2: Draw the final path (green)
        Then calls on_done_callback() so app.py can start agent walk.

        Args:
            visited           : list of (row,col) in exploration order
            path              : list of (row,col) from start to goal
            frontier_log      : list of frozensets showing frontier at each step
            on_done_callback  : function to call after animation finishes
        """
        self._anim_step    = 0
        self._visited      = visited
        self._path         = path
        self._frontier_log = frontier_log
        self._on_done      = on_done_callback

        self._run_search_step()

    def _run_search_step(self):
        """
        Internal method called repeatedly by root.after().
        Each call processes one exploration step.
        """
        if self._anim_step < len(self._visited):
            r, c = self._visited[self._anim_step]

            # Color this node as VISITED (blue)
            if (r, c) != self.grid.start and (r, c) != self.grid.goal:
                self.update_cell(r, c, COLOR_VISITED)

            # Color current frontier (yellow)
            if self._anim_step < len(self._frontier_log):
                for fr, fc in self._frontier_log[self._anim_step]:
                    if (fr, fc) != self.grid.start and (fr, fc) != self.grid.goal:
                        if self.grid.get_cell(fr, fc) != OBSTACLE:
                            self.update_cell(fr, fc, COLOR_FRONTIER)

            self._anim_step += 1
            # Schedule next step after ANIM_DELAY milliseconds
            self._anim_job = self.root.after(ANIM_DELAY, self._run_search_step)

        else:
            # All nodes visited — now draw the final path
            self._draw_path()

    def _draw_path(self):
        """Colors all cells on the final path GREEN."""
        for r, c in self._path:
            if (r, c) != self.grid.start and (r, c) != self.grid.goal:
                self.update_cell(r, c, COLOR_PATH)
        self._draw_labels()
        # Notify app.py that animation is done
        if self._on_done:
            self._on_done()

    def draw_agent(self, old_pos, new_pos):
        """
        Moves the agent marker from old_pos to new_pos.
        Repaints old position as PATH, new position as AGENT (red dot).
        """
        if old_pos and old_pos != self.grid.start and old_pos != self.grid.goal:
            self.update_cell(old_pos[0], old_pos[1], COLOR_PATH)
        if new_pos and new_pos != self.grid.goal:
            self.update_cell(new_pos[0], new_pos[1], COLOR_AGENT)
        self._draw_labels()

    def draw_new_path(self, old_remaining, new_path, agent_pos):
        """
        Called after replanning. Clears old path visualization
        and draws the new computed path in green.

        Args:
            old_remaining : remaining cells of the old blocked path
            new_path      : freshly computed path from current agent pos
            agent_pos     : current agent position (don't repaint this)
        """
        # Clear old remaining path
        for r, c in old_remaining:
            if (r, c) != self.grid.goal and (r, c) != agent_pos:
                if self.grid.get_cell(r, c) == EMPTY:
                    self.update_cell(r, c, COLOR_VISITED)

        # Draw new path
        for r, c in new_path:
            if (r, c) != self.grid.goal and (r, c) != agent_pos:
                self.update_cell(r, c, COLOR_PATH)

        self._draw_labels()

    def cancel_animation(self):
        """Cancels any pending animation callbacks."""
        if self._anim_job:
            self.root.after_cancel(self._anim_job)
            self._anim_job = None

    # ─────────────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────────────

    def _state_to_color(self, state):
        """Maps a cell state integer to its display color."""
        mapping = {
            EMPTY:    COLOR_EMPTY,
            OBSTACLE: COLOR_OBSTACLE,
            START:    COLOR_START,
            GOAL:     COLOR_GOAL,
        }
        return mapping.get(state, COLOR_EMPTY)
