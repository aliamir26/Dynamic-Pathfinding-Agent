# 🧭 Dynamic Pathfinding Agent

A Python + Tkinter GUI implementing **Greedy Best-First Search** and **A\*** on a dynamic grid with real-time obstacle spawning and re-planning.

---

## 📁 Project Structure

```
dynamic-pathfinding-agent/
│
├── main.py                    ← RUN THIS FILE
│
├── modules/
│   ├── __init__.py            ← Makes 'modules' a Python package
│   ├── constants.py           ← All shared colors, sizes, state codes
│   ├── heuristics.py          ← Manhattan + Euclidean distance formulas
│   ├── algorithms.py          ← GBFS and A* search logic
│   ├── grid.py                ← Grid state management
│   ├── gui_builder.py         ← Tkinter widget layout
│   ├── app.py                 ← Main controller (connects everything)
│   └── visualizer.py          ← Canvas drawing and animation
│
└── README.md
```

---

## 🚀 How to Run

```bash
# No installations needed — uses Python standard library only!
python main.py
```

> On Linux if Tkinter is missing:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## 🎮 Usage Guide

| Step | Action |
|------|--------|
| 1 | Set grid Rows × Cols → click **Apply Grid Size** |
| 2 | Click **Generate Random Map** or click cells to draw walls |
| 3 | Select **Algorithm** (A\* or Greedy BFS) |
| 4 | Select **Heuristic** (Manhattan or Euclidean) |
| 5 | Toggle **Dynamic Mode** if you want live obstacle spawning |
| 6 | Click **▶ Start Search** |
| 7 | Watch the agent find its path! |

---

## 🧠 Module Responsibilities

| File | Does What |
|------|-----------|
| `main.py` | Entry point only — creates window, starts app |
| `constants.py` | Single source of truth for all values |
| `heuristics.py` | h(n) formulas — Manhattan, Euclidean |
| `algorithms.py` | GBFS `f=h(n)` and A\* `f=g(n)+h(n)` |
| `grid.py` | 2D grid state, obstacle logic, dynamic spawning |
| `gui_builder.py` | All Tkinter widgets and layout |
| `visualizer.py` | Canvas drawing, animation, agent movement |
| `app.py` | Controller: connects all modules, handles events |

---

## 📦 Dependencies

```
Python 3.x  (standard library only)
  ├── tkinter   — GUI
  ├── heapq     — priority queue for search
  ├── random    — random obstacle generation
  ├── math      — Euclidean distance
  └── time      — execution time measurement
```

---

## 🎨 Color Legend

| Color | Meaning |
|-------|---------|
| 🟠 Orange | Start node |
| 🟣 Purple | Goal node |
| 🟡 Yellow | Frontier (open list) |
| 🔵 Blue | Visited (explored) |
| 🟢 Green | Final path |
| ⬛ Black | Obstacle / Wall |
| 🔴 Red | Agent (live position) |
