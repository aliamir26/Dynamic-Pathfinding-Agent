# 🧭 Dynamic Pathfinding Agent

A Python + Tkinter GUI that implements **Greedy Best-First Search (GBFS)** and **A\* Search** on a dynamic grid environment. The agent navigates from a start point to a goal while new obstacles appear in real time, triggering automatic path re-planning.

---

## 📸 Screenshots

> **How to add your own screenshots:**
> 1. Run the program with `python main.py`
> 2. Set up each scenario described below
> 3. Take a screenshot (Windows: `Win + Shift + S` | Mac: `Cmd + Shift + 4` | Linux: `PrtScn`)
> 4. Save each image inside a `screenshots/` folder in your project root
> 5. Replace the placeholder paths below with your actual filenames

### Main Interface
<!-- Take a screenshot of the app when it first opens — empty grid + control panel visible -->

![Main Interface](screenshots/main_interface.png)

---

### A\* Search — Best Case (Open Grid)
<!-- Settings: 10x10 grid, no obstacles, A*, Manhattan Distance, click Start Search -->

![A* Best Case](screenshots/astar_best_case.png)

---

### A\* Search — Worst Case (Dense Obstacles)
<!-- Settings: 10x10 grid, 35% random obstacles, A*, Manhattan Distance, click Start Search -->

![A* Worst Case](screenshots/astar_worst_case.png)

---

### Greedy BFS — Best Case (Open Grid)
<!-- Settings: 10x10 grid, no obstacles, Greedy BFS, Manhattan Distance, click Start Search -->

![GBFS Best Case](screenshots/gbfs_best_case.png)

---

### Greedy BFS — Worst Case (Dense Obstacles)
<!-- Settings: 10x10 grid, 35% random obstacles, Greedy BFS, Manhattan Distance, click Start Search -->

![GBFS Worst Case](screenshots/gbfs_worst_case.png)

---

### Dynamic Re-planning in Action
<!-- Settings: 10x10 grid, light obstacles, A*, Dynamic Mode ON at 15% spawn, click Start Search -->

![Dynamic Replanning](screenshots/dynamic_replanning.png)

---

## ✨ Features

- **Dynamic Grid Sizing** — Set any grid dimension from 5×5 up to 25×25 before searching
- **Two Search Algorithms** — Greedy Best-First Search and A*, selectable from a dropdown
- **Two Heuristic Functions** — Manhattan Distance and Euclidean Distance, switchable at any time
- **Random Map Generation** — Generate obstacle layouts at any density (5% to 70%) with one click
- **Interactive Map Editor** — Click any cell to toggle walls; click-and-set Start or Goal position anywhere
- **Dynamic Obstacle Mode** — New obstacles spawn randomly while the agent is moving, with user-controlled spawn probability
- **Automatic Re-planning** — When a new obstacle blocks the current path, the agent detects it instantly and re-computes a new route from its current position
- **Efficient Re-planning** — If a new obstacle does not fall on the current path, no re-computation is triggered at all
- **Step-by-Step Animation** — Watch the search exploration play out cell by cell in real time
- **Live Metrics Dashboard** — Nodes Visited, Path Cost, and Execution Time update after every search
- **Color-Coded Visualization** — Every element has a distinct color for clear understanding
- **Scrollable Canvas** — Large grids scroll smoothly inside the window

---

## ⚡ Algorithm Advantages

### Greedy Best-First Search
- Faster than A* in open environments because it only evaluates `f(n) = h(n)`
- Uses less memory since it does not track g-scores for each node
- Good choice when speed matters and a slightly longer path is acceptable

### A\* Search
- Always finds the **shortest possible path** — guaranteed optimal with admissible heuristics
- Balances actual cost `g(n)` and estimated remaining cost `h(n)` for smarter exploration
- Best choice for dynamic re-planning because every re-computed path is also optimal
- Complete — will always find a path if one exists

---

## 📁 Project Structure

```
dynamic-pathfinding-agent/
│
├── main.py                    ← RUN THIS FILE
│
├── modules/
│   ├── __init__.py            ← Makes 'modules' a Python package
│   ├── constants.py           ← All shared colors, sizes, and state codes
│   ├── heuristics.py          ← Manhattan + Euclidean distance formulas
│   ├── algorithms.py          ← GBFS and A* search logic
│   ├── grid.py                ← Grid state, obstacle management, dynamic spawning
│   ├── gui_builder.py         ← Tkinter widget layout and control panel
│   ├── app.py                 ← Main controller — connects all modules
│   └── visualizer.py          ← Canvas drawing and step-by-step animation
│
├── screenshots/               ← Add your screenshots here
│   ├── main_interface.png
│   ├── astar_best_case.png
│   ├── astar_worst_case.png
│   ├── gbfs_best_case.png
│   ├── gbfs_worst_case.png
│   └── dynamic_replanning.png
│
└── README.md
```

---

## 🚀 How to Run

**No external libraries required.** The entire project uses Python's standard library only.

```bash
# Step 1 — Clone the repository
git clone https://github.com/YOUR_USERNAME/dynamic-pathfinding-agent.git

# Step 2 — Navigate into the project folder
cd dynamic-pathfinding-agent

# Step 3 — Run the program
python main.py
```

> **Linux only** — if Tkinter is not installed:
> ```bash
> sudo apt-get install python3-tk
> ```

> **Windows / Mac** — Tkinter comes bundled with Python by default. No extra steps needed.

---

## 🎮 How to Use

| Step | What to Do |
|------|------------|
| 1 | Enter Rows and Cols in the left panel, then click **Apply Grid Size** |
| 2 | Click **Generate Random Map** to auto-fill obstacles, or click cells manually |
| 3 | Use radio buttons to switch between **Add/Remove Wall**, **Set Start**, or **Set Goal** mode |
| 4 | Select your **Algorithm** — A\* or Greedy BFS |
| 5 | Select your **Heuristic** — Manhattan or Euclidean |
| 6 | Optionally enable **Dynamic Obstacles** and set the spawn probability |
| 7 | Click **▶ Start Search** |
| 8 | Watch the animation — yellow frontier, blue visited, green final path |
| 9 | Check the **Metrics** panel for nodes visited, path cost, and execution time |
| 10 | Click **⏹ Stop / Reset** to clear and try again |

---

## 🎨 Color Legend

| Color | Element | Meaning |
|-------|---------|---------|
| 🟠 Orange | Start node | Where the agent begins |
| 🟣 Purple | Goal node | Where the agent must reach |
| 🟡 Yellow | Frontier | Nodes currently in the priority queue |
| 🔵 Blue | Visited | Nodes fully explored by the algorithm |
| 🟢 Green | Final path | The computed route from Start to Goal |
| ⬛ Black | Obstacle | Impassable wall cell |
| 🔴 Red | Agent | The agent's live position during movement |
| ⬜ White | Empty | Walkable cell not yet explored |

---

## 🧠 Module Responsibilities

| File | Responsibility |
|------|---------------|
| `main.py` | Entry point only — creates the window and starts the app |
| `constants.py` | Single source of truth for all colors, sizes, and state codes |
| `heuristics.py` | Manhattan and Euclidean distance formulas |
| `algorithms.py` | Full GBFS and A\* implementations with path reconstruction |
| `grid.py` | 2D grid state, obstacle toggling, random generation, dynamic spawning |
| `gui_builder.py` | All Tkinter widgets, control panel layout, and color legend |
| `visualizer.py` | Canvas drawing, cell color updates, and search animation |
| `app.py` | Controller — handles all events and connects every module |

---

## 📦 Dependencies

```
Python 3.x — standard library only, no pip installs needed

  tkinter   → GUI window, canvas, widgets
  heapq     → priority queue for search algorithms
  random    → random obstacle generation and dynamic spawning
  math      → Euclidean distance calculation
  time      → execution time measurement in milliseconds
```

---

## 🔬 Algorithms at a Glance

### Greedy Best-First Search
```
f(n) = h(n)
```
Only uses the heuristic. Fast but not guaranteed to find the shortest path.

### A\* Search
```
f(n) = g(n) + h(n)

  g(n) = actual steps walked from start to node n
  h(n) = estimated steps remaining from node n to goal
```
Always finds the shortest path when the heuristic never overestimates.

### Heuristics
```
Manhattan:   h = |row_now - row_goal| + |col_now - col_goal|
Euclidean:   h = sqrt( (row_diff)^2 + (col_diff)^2 )
```
Manhattan is the recommended choice for 4-directional grids.

---

## 📝 License

Created for a university assignment. Free to use for academic and educational purposes.
