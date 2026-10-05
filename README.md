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

### 2. Board Pre-Processing & Inference
Before tree search expansion, the solver applies deterministic deductions directly to reduce state permutations:
* **Zero-Cell Suppression:** Cells with target `0` immediately flag all 4 incident edges as blocked (`BLOCKED`).
* **Boundary Validation:** Boundary and corner edges are verified against adjacent cell limits to prune invalid states early.

### 3. Search Engine & Consistency Checks
* **Tree Search Formulation:** Formulated on top of the search framework (`depth_first_tree_search`), exploring assignments to grid edges.
* **Vertex Degree Enforcing:** Validates that no explored vertex exceeds degree 2 or becomes a dead-end with degree 1 during search expansion (`is_ok_active`, `is_ok_blocked`).
* **Single Closed Loop Validation:** `traverse_loop` walks active edges from the first connected vertex to ensure the final state forms exactly one unbroken cycle matching the required cell numbers.

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

## Benchmark Instances

The repository includes a suite of test boards in `slitherlink-boards-public/`:
* `test01.txt` (4x4 introductory board)
* `test02.txt` (6x6 intermediate board)
* `test03.txt` to `test09.txt` (varying grid sizes and constraint distributions)

Run any board file directly through the solver pipeline:
```bash
python3 slitherlink.py < slitherlink-boards-public/test01.txt
```

---

## Authors & Acknowledgments

* **David Vasques** ([@DeastV](https://github.com/DeastV))
* **Leonor Machado** ([@leonormm](https://github.com/leonormm))

Collaborative group project developed for Inteligência Artificial at Instituto Superior Técnico, Universidade de Lisboa.

*Course-Provided Resources:* The generic search harness (`search.py`), data structures (`utils.py`), and test benchmark boards (`slitherlink-boards-public/`) were provided by the Inteligência Artificial teaching staff. The MIT License applies to the Slitherlink CSP formulation, domain consistency checks, cycle traversal logic, and the interactive Tkinter GUI (`slitherlink_gui.py`).
