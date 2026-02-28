"""
algorithms.py
─────────────────────────────────────────────────────────────
PURPOSE:
    Contains ONLY the search algorithm logic.
    No GUI, no colors, no buttons — just pure pathfinding math.
    Takes a grid as input, returns a path and visualization data.

WHY A SEPARATE FILE?
    Search logic is the CORE academic content of this project.
    Keeping it isolated means:
    - Easy to test algorithms without running the full GUI
    - Easy to swap in new algorithms later (e.g., D* Lite)
    - Clear separation: logic vs display

HOW IT JOINS:
    app.py (the main GUI controller) does:
        from modules.algorithms import astar, greedy_bfs, get_neighbors
    When user clicks "Start Search", app.py calls these functions
    and gets back (path, visited_order, frontier_log).
    Then app.py handles drawing those results on the canvas.
─────────────────────────────────────────────────────────────
"""

import heapq  # Python's built-in min-heap (priority queue)

from modules.constants import OBSTACLE


# ─────────────────────────────────────────────────────────
# HELPER: GET VALID NEIGHBORS
# ─────────────────────────────────────────────────────────

def get_neighbors(grid, row, col, rows, cols):
    """
    Returns all valid neighboring cells for a given position.

    We use 4-connectivity: UP, DOWN, LEFT, RIGHT only.
    No diagonal movement.

    For each direction, we check:
    1. Is it within grid bounds? (no IndexError)
    2. Is it not an obstacle? (can we actually walk there?)

    Args:
        grid : 2D list of cell states
        row  : current row
        col  : current column
        rows : total grid rows (for bounds check)
        cols : total grid cols (for bounds check)

    Returns:
        List of (row, col) tuples that are valid to move into
    """
    neighbors = []
    # The 4 cardinal directions as (row_delta, col_delta)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    for dr, dc in directions:
        nr = row + dr
        nc = col + dc
        # Bounds check
        if 0 <= nr < rows and 0 <= nc < cols:
            # Walkability check (anything that's not OBSTACLE is walkable)
            if grid[nr][nc] != OBSTACLE:
                neighbors.append((nr, nc))

    return neighbors


# ─────────────────────────────────────────────────────────
# PATH RECONSTRUCTION
# ─────────────────────────────────────────────────────────

def reconstruct_path(came_from, goal):
    """
    Traces backwards from goal to start using the came_from map.

    Think of came_from like a chain of breadcrumbs:
        goal → ... → node_B → node_A → start → None

    We follow this chain backwards, then reverse it to get
    the forward path from start → goal.

    Args:
        came_from : dict mapping {node: parent_node}
        goal      : the goal (row, col) tuple

    Returns:
        List of (row, col) from start to goal (inclusive)
    """
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()  # We built it goal→start, now flip to start→goal
    return path


# ─────────────────────────────────────────────────────────
# ALGORITHM 1: GREEDY BEST-FIRST SEARCH
# ─────────────────────────────────────────────────────────

def greedy_bfs(grid, start, goal, rows, cols, heuristic_fn):
    """
    Greedy Best-First Search (GBFS)
    ─────────────────────────────────────────────────────
    Key idea: ALWAYS expand the node that has the LOWEST h(n).
              Completely ignores how far we've already walked.

    Formula:   f(n) = h(n)

    Analogy:   Like a person who always walks toward where
               they THINK the goal is, ignoring the road behind them.
               Fast, but may take a longer route!

    Data Structures Used:
        open_list    → min-heap (heapq), sorted by h(n)
        came_from    → dict: how we reached each node
        visited      → list: records exploration order for animation

    Args:
        grid        : 2D list of cell states
        start       : (row, col) of start node
        goal        : (row, col) of goal node
        rows, cols  : grid dimensions
        heuristic_fn: function reference — manhattan or euclidean

    Returns:
        path             : list of (row,col) from start to goal, or None
        visited_order    : list of nodes in the order they were explored
        frontier_snapshots: list of frontier sets at each step (for animation)
    """
    # Priority queue: entries are (priority, node)
    # heapq is a min-heap → smallest priority pops first
    open_list = []
    heapq.heappush(open_list, (heuristic_fn(start, goal), start))

    # came_from: to reconstruct path later
    came_from = {start: None}

    # visited_order: for animating the blue "explored" cells
    visited_order = []

    # frontier_snapshots: for animating the yellow "frontier" cells
    # At each expansion step, we snapshot what's in the open list
    frontier_snapshots = []

    while open_list:
        # Pop node with lowest h(n)
        _, current = heapq.heappop(open_list)

        # Record as visited (for visualization)
        visited_order.append(current)

        # ✅ Found the goal!
        if current == goal:
            path = reconstruct_path(came_from, goal)
            return path, visited_order, frontier_snapshots

        # Expand all valid neighbors
        for neighbor in get_neighbors(grid, current[0], current[1], rows, cols):
            if neighbor not in came_from:  # Not yet discovered
                came_from[neighbor] = current
                priority = heuristic_fn(neighbor, goal)
                heapq.heappush(open_list, (priority, neighbor))

        # Snapshot the frontier (all nodes currently in open_list)
        frontier_now = frozenset(item[1] for item in open_list)
        frontier_snapshots.append(frontier_now)

    return None, visited_order, frontier_snapshots


# ─────────────────────────────────────────────────────────
# ALGORITHM 2: A* SEARCH
# ─────────────────────────────────────────────────────────

def astar(grid, start, goal, rows, cols, heuristic_fn):
    """
    A* (A-Star) Search Algorithm
    ─────────────────────────────────────────────────────
    Key idea: Expand the node with lowest f(n) = g(n) + h(n).
              g(n) = actual cost paid so far (number of steps)
              h(n) = heuristic estimate to goal

    Formula:   f(n) = g(n) + h(n)

    Analogy:   Like a person who considers BOTH how far they've
               walked AND how far they estimate to go.
               Slower than GBFS but finds the SHORTEST path!

    Why is A* optimal?
        Because h(n) never overestimates (admissible heuristic).
        This means A* never "gives up" on a short path too early.

    Data Structures Used:
        open_list : min-heap sorted by f(n)
        came_from : dict — path reconstruction
        g_score   : dict — cheapest known cost to reach each node

    Args:
        Same as greedy_bfs

    Returns:
        Same format as greedy_bfs
    """
    # Heap entries: (f_score, g_score, node)
    # We store g_score in heap so we can compute f without extra lookup
    open_list = []
    start_h = heuristic_fn(start, goal)
    heapq.heappush(open_list, (start_h, 0, start))

    came_from = {start: None}

    # g_score: cheapest path cost found so far to each node
    # Initialized with start=0; everything else is "infinity"
    g_score = {start: 0}

    visited_order = []
    frontier_snapshots = []

    # closed_set: nodes we've fully expanded (to skip duplicates in heap)
    closed_set = set()

    while open_list:
        f, g, current = heapq.heappop(open_list)

        # Skip if we already processed this node with a better cost
        # (heapq doesn't support "update priority", so we may have duplicates)
        if current in closed_set:
            continue

        closed_set.add(current)
        visited_order.append(current)

        # ✅ Found the goal!
        if current == goal:
            path = reconstruct_path(came_from, goal)
            return path, visited_order, frontier_snapshots

        # Expand neighbors
        for neighbor in get_neighbors(grid, current[0], current[1], rows, cols):
            if neighbor in closed_set:
                continue  # Already fully processed

            # Cost to reach neighbor via current path = g(current) + 1 step
            tentative_g = g_score[current] + 1

            # Is this a better path to neighbor than what we've seen before?
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                # Yes! Update the best known path to neighbor
                g_score[neighbor]  = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + heuristic_fn(neighbor, goal)
                heapq.heappush(open_list, (f_score, tentative_g, neighbor))

        # Snapshot frontier
        frontier_now = frozenset(item[2] for item in open_list)
        frontier_snapshots.append(frontier_now)

    # ❌ No path found
    return None, visited_order, frontier_snapshots


# ─────────────────────────────────────────────────────────
# SELECTOR FUNCTION (used by app.py)
# ─────────────────────────────────────────────────────────

def run_algorithm(algo_name, grid, start, goal, rows, cols, heuristic_fn):
    """
    Convenience wrapper — calls the right algorithm by name.

    This way, app.py just calls:
        run_algorithm("A*", ...)
    Without needing to import both astar and greedy_bfs separately.

    Args:
        algo_name : "A*" or "Greedy BFS"
        rest      : same as individual algorithm functions

    Returns:
        (path, visited_order, frontier_snapshots)
    """
    if algo_name == "A*":
        return astar(grid, start, goal, rows, cols, heuristic_fn)
    else:
        return greedy_bfs(grid, start, goal, rows, cols, heuristic_fn)
