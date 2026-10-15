import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from src.maze import load_maze, generate_maze
from src.benchmark import find_position
from src.astar import astar
from src.dijkstra import dijkstra

# cell codes -> colors
EMPTY, WALL, EXPLORED, PATH, START, GOAL, CURRENT = range(7)
COLORS = ["white", "black", "lightskyblue", "limegreen", "orange", "red", "gold"]
CMAP = ListedColormap(COLORS)

ALGORITHMS = {"A*": astar, "Dijkstra": dijkstra}
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


# ----------------------------------------------------------------- helpers
def run(name, maze, start, goal):
    path, expanded = ALGORITHMS[name](maze, start, goal)
    return {"name": name, "path": path or [], "expanded": expanded}


def base_grid(maze):
    return [[WALL if cell == "#" else EMPTY for cell in row] for row in maze]


def build_frame(maze, start, goal, result, n_explored, n_path):
    """Grid state after n_explored nodes searched and n_path path cells drawn."""
    grid = base_grid(maze)
    expanded = result["expanded"]

    for r, c in expanded[:n_explored]:
        grid[r][c] = EXPLORED
    if 0 < n_explored < len(expanded):
        r, c = expanded[n_explored - 1]
        grid[r][c] = CURRENT
    for r, c in result["path"][:n_path]:
        grid[r][c] = PATH

    grid[start[0]][start[1]] = START
    grid[goal[0]][goal[1]] = GOAL
    return grid


def setup_axes(ax, maze, title):
    rows, cols = len(maze), len(maze[0])
    im = ax.imshow(
        np.array(base_grid(maze)), cmap=CMAP, vmin=0, vmax=len(COLORS) - 1,
        interpolation="nearest",
    )
    if rows <= 30 and cols <= 30:  # grid lines make big mazes slow to redraw
        ax.set_xticks([x - 0.5 for x in range(cols + 1)])
        ax.set_yticks([y - 0.5 for y in range(rows + 1)])
        ax.grid(True, color="lightgray", linewidth=0.4)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
    ax.tick_params(length=0, labelbottom=False, labelleft=False)
    ax.set_title(title)
    return im


def make_figure(count):
    """Compact window that fits a laptop screen (~1000x600 for two plots)."""
    fig, axes = plt.subplots(1, count, figsize=(5.2 * count, 6.0), dpi=90)
    if count == 1:
        axes = [axes]
    return fig, axes


def add_legend(fig):
    handles = [
        Patch(facecolor="orange", label="Start"),
        Patch(facecolor="red", label="Goal"),
        Patch(facecolor="lightskyblue", label="Explored"),
        Patch(facecolor="gold", label="Currently expanding"),
        Patch(facecolor="limegreen", label="Final path"),
        Patch(facecolor="black", label="Wall"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=8)


# ------------------------------------------------------------ static views
def show_static(maze, start, goal, names, save_name):
    results = [run(n, maze, start, goal) for n in names]

    fig, axes = make_figure(len(results))

    for ax, res in zip(axes, results):
        steps = len(res["path"]) - 1 if res["path"] else "no path"
        im = setup_axes(
            ax, maze,
            f"{res['name']} | expanded: {len(res['expanded'])} | path: {steps}",
        )
        im.set_data(
            build_frame(maze, start, goal, res, len(res["expanded"]), len(res["path"]))
        )

    add_legend(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{save_name}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.show()


# ------------------------------------------------------------- live views
def build_animation(maze, start, goal, names, speed=2, interval=50):
    """speed = nodes revealed per frame. Same speed for every algorithm, so a
    algorithm that expands fewer nodes finishes sooner (a fair race)."""
    results = [run(n, maze, start, goal) for n in names]

    fig, axes = make_figure(len(results))
    images = [setup_axes(ax, maze, res["name"]) for ax, res in zip(axes, results)]
    add_legend(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    explore_frames = [math.ceil(len(r["expanded"]) / speed) for r in results]
    total_frames = max(
        ef + len(r["path"]) for ef, r in zip(explore_frames, results)
    ) + 25  # hold the final picture for a moment

    # one grid per algorithm, updated incrementally (much faster than rebuilding)
    grids = [np.array(base_grid(maze)) for _ in results]
    applied = [{"n": 0, "p": 0} for _ in results]

    def advance(grid, res, state, n, p):
        expanded, path = res["expanded"], res["path"]
        if state["n"] > 0 and state["n"] <= len(expanded):
            r, c = expanded[state["n"] - 1]
            grid[r, c] = EXPLORED  # previous "current" becomes plain explored
        for r, c in expanded[state["n"]:n]:
            grid[r, c] = EXPLORED
        if 0 < n < len(expanded):
            r, c = expanded[n - 1]
            grid[r, c] = CURRENT
        for r, c in path[state["p"]:p]:
            grid[r, c] = PATH
        grid[start[0], start[1]] = START
        grid[goal[0], goal[1]] = GOAL
        state["n"], state["p"] = n, p

    def update(frame):
        for ax, im, res, ef, grid, state in zip(
            axes, images, results, explore_frames, grids, applied
        ):
            n = min(frame * speed, len(res["expanded"]))
            p = min(max(0, frame - ef), len(res["path"]))
            advance(grid, res, state, n, p)
            im.set_data(grid)

            if n < len(res["expanded"]):
                ax.set_title(f"{res['name']} | searching... expanded: {n}")
            else:
                steps = len(res["path"]) - 1 if res["path"] else "no path"
                done = p >= len(res["path"])
                ax.set_title(
                    f"{res['name']} | "
                    f"{'DONE' if done else 'drawing path'} | "
                    f"expanded: {n} | path: {steps}"
                )
        return images + [ax.title for ax in axes]

    anim = FuncAnimation(
        fig, update, frames=total_frames, interval=interval, repeat=False, blit=True
    )
    return fig, anim


def show_live(maze, start, goal, names, speed):
    fig, anim = build_animation(maze, start, goal, names, speed=speed)
    try:
        fig.canvas.manager.window.wm_geometry("+60+40")  # keep window on screen (TkAgg)
    except Exception:
        pass
    plt.show()  # keep `anim` alive until the window is closed
    return anim


# ------------------------------------------------------------------- menu
def ask(prompt, valid, default=None):
    while True:
        text = input(prompt).strip()
        if not text and default is not None:
            return default
        if text in valid:
            return text
        print(f"  Please enter one of: {', '.join(valid)}")


def ask_int(prompt, default, low, high):
    while True:
        text = input(prompt).strip()
        if not text:
            return default
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print(f"  Enter a number between {low} and {high} (or press Enter for {default}).")


def choose_maze():
    print("\nWhich maze?")
    print("  1) Random maze (new one every time)")
    print("  2) Sample maze from mazes/sample_maze.txt (small 5x5)")
    choice = ask("Choice [1]: ", {"1", "2"}, default="1")

    if choice == "2":
        return load_maze()

    size = ask_int("Maze size (10-60) [25]: ", 25, 10, 60)
    import random
    return generate_maze(rows=size, cols=size, seed=random.randrange(10**6))


def main():
    maze = choose_maze()

    while True:
        print("\nWhat do you want to see?")
        print("  1) Static  - A* only")
        print("  2) Static  - Dijkstra only")
        print("  3) Static  - A* vs Dijkstra side by side")
        print("  4) LIVE    - A* only")
        print("  5) LIVE    - Dijkstra only")
        print("  6) LIVE    - A* vs Dijkstra race")
        print("  7) New maze")
        print("  0) Quit")
        choice = ask("Choice: ", {"0", "1", "2", "3", "4", "5", "6", "7"})

        if choice == "0":
            print("Bye!")
            return
        if choice == "7":
            maze = choose_maze()
            continue

        start = find_position(maze, "S")
        goal = find_position(maze, "G")

        modes = {
            "1": (["A*"], "astar"),
            "2": (["Dijkstra"], "dijkstra"),
            "3": (["A*", "Dijkstra"], "comparison"),
            "4": (["A*"], None),
            "5": (["Dijkstra"], None),
            "6": (["A*", "Dijkstra"], None),
        }
        names, save_name = modes[choice]

        if save_name:
            show_static(maze, start, goal, names, save_name)
        else:
            auto = min(10, max(2, len(maze) * len(maze[0]) // 250))
            speed = ask_int(
                f"Speed - nodes per frame, 1=slow 10=fast [{auto}]: ", auto, 1, 10
            )
            print("Close the window to return to the menu.")
            show_live(maze, start, goal, names, speed)


if __name__ == "__main__":
    main()