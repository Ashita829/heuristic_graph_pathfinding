
import heapq


def heuristic(a, b):
    """Manhattan distance between two grid cells."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze, start, goal):
    rows, cols = len(maze), len(maze[0])

    priority_queue = [(heuristic(start, goal), 0, start)]
    came_from = {}
    cost_so_far = {start: 0}
    expanded_nodes = []

    while priority_queue:
        _, current_cost, current = heapq.heappop(priority_queue)

        if current_cost != cost_so_far.get(current):
            continue

        expanded_nodes.append(current)

        if current == goal:
            path = []

            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path, expanded_nodes

        r, c = current

        for nr, nc in [
            (r - 1, c),
            (r + 1, c),
            (r, c - 1),
            (r, c + 1),
        ]:
            neighbor = (nr, nc)

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue

            if maze[nr][nc] == "#":
                continue

            new_cost = cost_so_far[current] + 1

            if new_cost < cost_so_far.get(neighbor, float("inf")):
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current

                priority = new_cost + heuristic(neighbor, goal)

                heapq.heappush(
                    priority_queue,
                    (priority, new_cost, neighbor),
                )

    return None, expanded_nodes
