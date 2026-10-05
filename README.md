# Slitherlink AI Solver — Intelligent Puzzle Resolution

[![Language](https://img.shields.io/badge/Language-Python%203-blue.svg)](https://www.python.org/)
[![Field](https://img.shields.io/badge/Field-Artificial%20Intelligence-purple.svg)]()
[![Method](https://img.shields.io/badge/Search-DFS%20%2B%20MRV%20Heuristic-green.svg)]()
[![Paradigm](https://img.shields.io/badge/Formulation-CSP%20%26%20Arc%20Consistency-orange.svg)]()
[![GUI](https://img.shields.io/badge/UI-Tkinter%20GUI-yellow.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, high-performance automated solver for the NP-complete puzzle **Slitherlink**, developed in Python as part of the **Artificial Intelligence (Inteligência Artificial)** course at **Instituto Superior Técnico (IST), Universidade de Lisboa**.

The solver models the problem as a **Constraint Satisfaction Problem (CSP)** and solves it using an optimized **Backtracking Depth-First Search (DFS)** augmented with static pattern inference, arc consistency, and the **Minimum Remaining Values (MRV)** heuristic.

---

## The Slitherlink Puzzle

Slitherlink is played on a rectangular grid of dots. Some cells in the grid contain numbers from 0 to 3:
* The objective is to connect horizontally and vertically adjacent dots to form a single continuous, non-intersecting loop.
* Each numbered cell must have exactly that number of active edges around its perimeter.
* Cells without numbers can have any number of edges.
* At every grid vertex, the degree must be either `0` (untouched) or `2` (part of the loop). No vertices with degrees `1`, `3`, or `4` are allowed.

---

## Technical Architecture & AI Strategy

### 1. CSP Formulation
* **Variables:** Grid edges (horizontal and vertical), which can take the state of `ACTIVE` (1), `BLOCKED` (0), or `UNKNOWN` (None).
* **Constraints:**
  * **Cell Degree Constraints:** Number of active edges surrounding a cell cannot exceed the target number, and remaining unknown edges must be sufficient to satisfy the number.
  * **Vertex Constraints:** Any grid vertex connected to an active edge must connect to exactly two active edges (degree 2 constraint), preventing branches or dead ends.
  * **Loop Consistency:** The solution must form exactly one single closed cycle covering all active edges (no isolated sub-loops).

### 2. Pre-Search Static Inference & Arc Consistency
Similar to Forward Checking and AC-3, static deduction rules are applied to the initial board to collapse the search space before exploration:
* **Zeros:** A cell with `0` immediately marks all 4 surrounding edges as blocked.
* **Corners & Diagonals:** Common boundary patterns (e.g. adjacent `3`s, corner constraints) propagate deterministic edge placements at near-zero computational cost.

### 3. MRV (Minimum Remaining Values) Heuristic
During search tree expansion, naive branch selection leads to exponential branching factors. The solver enforces the **Fail-First Principle** using the **MRV heuristic**:
* Chooses cells with the minimum number of unassigned edges to branch on first.
* Forces contradictory states to fail early in the tree, drastically pruning invalid search branches before deep exploration.

### 4. Backtracking DFS Engine
* Utilizes Depth-First Search with state immutability / deep copying to maintain pristine backtrack points.
* Memory efficiency: Maintains linear space complexity $\mathcal{O}(d)$ relative to search depth, resolving grids up to 15x15 without memory exhaustion.

---

## Project Structure

```
.
├── slitherlink.py                 # Core AI solver, search logic & problem formulation
├── slitherlink_gui.py             # Interactive Tkinter visual interface
├── search.py                      # Generic AI search algorithms framework
├── utils.py                       # Helper data structures and utilities
├── slitherlink-boards-public/     # Public test benchmark instances (test01 to test09)
├── LICENSE                        # MIT License
└── README.md                      # Project documentation
```

---

## Installation & Requirements

* **Python 3.8+**
* Standard library modules (`tkinter` for the GUI).

On Ubuntu/Debian, ensure Tkinter is installed:
```bash
sudo apt-get install python3-tk
```

---

## Usage

### 1. Command-Line Solver
Run the solver on any input board file piped via standard input:

```bash
# Test on benchmark board 1 (4x4)
python3 slitherlink.py < slitherlink-boards-public/test01.txt

# Test on benchmark board 2 (6x6)
python3 slitherlink.py < slitherlink-boards-public/test02.txt
```

#### Output Format
The solver outputs the solution matrix in 4-digit binary per cell indicating edge states (top, right, bottom, left):
```
0000	0110	1001	1100
0110	1001	0000	0110
1011	0000	0110	1001
1100	0111	1001	0000
```

### 2. Graphical Interface (GUI)
Launch the visual interactive interface:

```bash
python3 slitherlink_gui.py
```

* Load board files directly.
* Visualize the step-by-step resolution of the loop graphically.

---

## Benchmark Results

| Instance | Grid Size | Algorithm | Nodes Expanded | Status |
| :--- | :--- | :--- | :--- | :--- |
| `test01` | 4x4 | DFS + MRV | < 50 | Solved (< 0.1s) |
| `test02` | 6x6 | DFS + MRV | < 200 | Solved (< 0.2s) |
| `test03` | 10x10 | DFS + MRV | ~ 1,500 | Solved (< 1.5s) |

---

## Authors

* **David Vasques** ([@DeastV](https://github.com/DeastV))
* **Leonor Machado** ([@leonormm](https://github.com/leonormm))

*Instituto Superior Técnico — Universidade de Lisboa (2025/2026)*
