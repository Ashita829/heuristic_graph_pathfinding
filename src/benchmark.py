import csv
import time
from pathlib import Path

from src.maze import load_maze, generate_maze
from src.astar import astar
from src.dijkstra import dijkstra


def find_position(maze, symbol):
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == symbol:
                return (r, c)

    raise ValueError(f"Symbol {symbol} not found in maze")


def run_algorithm(name, algorithm, maze, start, goal):
    start_time = time.perf_counter()
    path, expanded_nodes = algorithm(maze, start, goal)
    runtime = time.perf_counter() - start_time

    steps = len(path) - 1 if path else None

    return {
        "name": name,
        "path": path,
        "steps": steps,
        "expanded": len(expanded_nodes),
        "explored_nodes": expanded_nodes,
        "runtime": runtime,
    }


def main():
    maze = generate_maze()  # swap for load_maze() to use mazes/sample_maze.txt

    start = find_position(maze, "S")
    goal = find_position(maze, "G")

    results = [
        run_algorithm("A*", astar, maze, start, goal),
        run_algorithm("Dijkstra", dijkstra, maze, start, goal),
    ]

    print("ALGORITHM COMPARISON")
    print("-" * 65)
    print(f"{'Algorithm':<12} {'Steps':<10} {'Expanded':<12} {'Runtime (s)'}")
    print("-" * 65)

    for result in results:
        steps_text = (
            str(result["steps"])
            if result["steps"] is not None
            else "No path"
        )

        print(
            f"{result['name']:<12} "
            f"{steps_text:<10} "
            f"{result['expanded']:<12} "
            f"{result['runtime']:.6f}"
        )

    results_dir = Path(__file__).resolve().parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    csv_file = results_dir / "benchmark_results.csv"

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Algorithm",
            "Path Length",
            "Expanded Nodes",
            "Runtime Seconds",
        ])

        for result in results:
            writer.writerow([
                result["name"],
                result["steps"],
                result["expanded"],
                f"{result['runtime']:.8f}",
            ])

    print(f"\nResults saved to: {csv_file}")

    print("\nPATH VISUALIZATIONS")

    for result in results:
        print(f"\n{result['name']}:")
        display_maze = [row[:] for row in maze]

        for r, c in result["explored_nodes"]:
            if display_maze[r][c] not in ("S", "G"):
                display_maze[r][c] = "E"

        if result["path"]:
            for r, c in result["path"]:
                if display_maze[r][c] not in ("S", "G"):
                    display_maze[r][c] = "*"

        for row in display_maze:
            print(" ".join(row))

    print("\nLegend: E = explored node, * = final path")


if __name__ == "__main__":
    main()