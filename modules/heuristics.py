"""
heuristics.py
─────────────────────────────────────────────────────────────
PURPOSE:
    Contains ONLY the heuristic (distance estimation) functions.
    These are the "brain" formulas the search algorithms use to
    guess how far away the goal is.

WHY A SEPARATE FILE?
    The heuristic is a plug-in piece — you might want to add new
    ones later (e.g., Chebyshev, Diagonal). Keeping them isolated
    means you add ONE function here and everything else works.

HOW IT JOINS:
    algorithms.py does:
        from modules.heuristics import manhattan_distance, euclidean_distance
    The GUI lets user pick which one, then passes the function
    as a parameter to the algorithm.
─────────────────────────────────────────────────────────────
"""

import math  # Needed for sqrt in Euclidean


def manhattan_distance(a, b):
    """
    Manhattan Distance — h(n) = |Δrow| + |Δcol|
    ─────────────────────────────────────────────
    Imagine walking on a city grid where you can only move
    UP, DOWN, LEFT, RIGHT (no diagonals).
    Count the total blocks you need to walk — that's Manhattan.

    Example:
        a = (0, 0),  b = (3, 4)
        h = |0-3| + |0-4| = 3 + 4 = 7

    Best for: Grids with 4-directional movement (like this project).
    It NEVER overestimates → makes A* optimal (admissible heuristic).

    Args:
        a: (row, col) tuple of node A
        b: (row, col) tuple of node B

    Returns:
        Integer — estimated steps between A and B
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean_distance(a, b):
    """
    Euclidean Distance — h(n) = sqrt(Δrow² + Δcol²)
    ─────────────────────────────────────────────────
    The straight-line "as the crow flies" distance between
    two points. Like drawing a ruler on paper between them.

    Example:
        a = (0, 0),  b = (3, 4)
        h = sqrt(9 + 16) = sqrt(25) = 5.0

    Note: In a 4-connected grid, Euclidean can *slightly*
    underestimate (because you can't actually walk diagonally).
    This means it's still admissible → A* is still optimal.

    Best for: When diagonal movement is allowed, or for
    comparison/experimentation purposes.

    Args:
        a: (row, col) tuple of node A
        b: (row, col) tuple of node B

    Returns:
        Float — straight-line distance between A and B
    """
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def get_heuristic(name):
    """
    Factory function — returns the heuristic function by name string.
    This is used by the GUI to convert a dropdown selection into
    an actual callable function.

    Usage:
        h_fn = get_heuristic("Manhattan")
        cost = h_fn((0,0), (5,5))  # → 10

    Args:
        name: string — "Manhattan" or "Euclidean"

    Returns:
        A function reference (not the result — the function itself!)
    """
    if name == "Manhattan":
        return manhattan_distance
    elif name == "Euclidean":
        return euclidean_distance
    else:
        # Default fallback — Manhattan is safer for 4-connected grids
        return manhattan_distance
