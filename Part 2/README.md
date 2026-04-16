# COMP2090SEF-Project-GPR_72
# Task 2: Maze

## 1. Introduction
We have implemented a **Maze** generator using **Disjoint Set Union (DSU)** and **Randomized Kruskal's Algorithm**, ensuring a fully connected path exists without cycles.

### Chosen Topics:
* **Data Structure**: Disjoint Set Union (Union-Find)
* **Algorithm**: Randomized Kruskal's Algorithm

---

## 2. Data Structure: Disjoint Set Union (DSU)
### Abstract Data Type (ADT)
DSU is a tree-based data structure that tracks elements partitioned into a number of disjoint (non-overlapping) sets.
* **Find**: Identifies which set an element belongs to. Our implementation in `maze.py` uses **Path Compression** to flatten the tree structure, ensuring near-constant time complexity for future queries.
* **Union**: Merges two distinct sets into a single set.

### Application in Project
In `maze.py`, the `DisjointSetDataStructure` class manages the connectivity of maze cells. By treating each cell as an individual set initially, we can determine if two cells are already connected before removing a wall, effectively preventing the creation of loops or isolated areas.

---

## 3. Algorithm: Randomized Kruskal's Algorithm
### Logic & Implementation
While Kruskal's is traditionally used for finding a Minimum Spanning Tree (MST), we adapted it for maze generation:
1.  **Initialize**: All walls are intact, and every cell is its own set.
2.  **Shuffle**: All potential walls are placed in a list and randomized to ensure a unique maze layout every time.
3.  **Process**: For each wall in the randomized list:
    * Check the sets of the two cells divided by the wall using `find`.
    * If they belong to different sets, `union` the sets and remove the wall (set value to 0).
    * If they are already in the same set, keep the wall to avoid cycles.

### Time Complexity Analysis
* **Initialization**: $O(V)$, where $V$ is the total number of cells.
* **Main Loop**: Processes $E$ edges (walls). With Path Compression, the complexity is approximately $O(E \cdot \alpha(V))$, where $\alpha$ is the inverse Ackermann function. For all practical purposes, this is considered $O(1)$ per operation.

---

## 4. User Guide
### How to Run
1.  Ensure the `pygame` library is installed: `pip install pygame`.
2.  Execute the main entry point: `python main.py`.
3.  **Controls**:
    * Use **W, A, S, D** to navigate the blue player square.
    * **Objective**: Reach the red exit square. 

<img width="2876" height="1654" alt="螢幕擷取畫面 2026-04-16 191158" src="https://github.com/user-attachments/assets/24626876-313e-4059-91d2-85ad9b62faaa" />

4. Click on **Search road**:
   * It will show the only path in yellow that can reach the red exit square form the green start square
   * Yellow Path: The current path being explored.
   * Dark Gray: Dead ends identified by the DFS algorithm.
   
<img width="2885" height="1650" alt="螢幕擷取畫面 2026-04-16 191219" src="https://github.com/user-attachments/assets/4e25d49f-4d04-4c1a-b595-43f8e80d384d" />

5. Once the blue player square reach the red exit square. Upon success, the DSU logic will trigger and generate a fresh maze instantly.

---
## 5. Modular Structure
The project is divided into three modules to follow modular programming principles:
   * `main.py`: Handles the GUI, rendering, and user input.
   * `maze.py`: Contains the DSU class and the Kruskal's maze generation logic.
   * `search.py`: Implements the pathfinding generator for non-blocking visualization.

---
## 6. References
* **Maze Generation Theory**: Randomized Kruskal's Algorithm.
