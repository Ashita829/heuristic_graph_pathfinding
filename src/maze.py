import random
from collections import deque
from pathlib import Path

WALL = "#"
EMPTY = "."
START = "S"
GOAL = "G"


def load_maze(name="sample_maze.txt"):
    maze_file = Path(__file__).resolve().parent.parent / "mazes" / name

    with open(maze_file, "r", encoding="utf-8") as file:
        maze = [list(line.strip()) for line in file if line.strip()]
    return maze


def _solvable(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    seen, queue = {start}, deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return True
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != WALL and (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append((nr, nc))
    return False


def generate_maze(rows=25, cols=25, wall_density=0.25, seed=7):
    """Random open grid with scattered walls. Start top-left, goal bottom-right.
    Open areas let A*'s heuristic actually prune the search."""
    rng = random.Random(seed)
    start, goal = (0, 0), (rows - 1, cols - 1)
    while True:
        maze = [
            [WALL if rng.random() < wall_density else EMPTY for _ in range(cols)]
            for _ in range(rows)
        ]
        maze[start[0]][start[1]] = START
        maze[goal[0]][goal[1]] = GOAL
        if _solvable(maze, start, goal):
            return maze


def print_maze(maze):
    for row in maze:
        print(" ".join(row))


if __name__ == "__main__":
    print_maze(load_maze())