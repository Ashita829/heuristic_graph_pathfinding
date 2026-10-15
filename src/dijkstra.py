import heapq


def dijkstra(maze, start, goal):
    rows, cols = len(maze), len(maze[0])

    priority_queue = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}
    expanded_nodes = []

    while priority_queue:
        current_cost, current = heapq.heappop(priority_queue)

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

            new_cost = current_cost + 1

            if new_cost < cost_so_far.get(neighbor, float("inf")):
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current

                heapq.heappush(
                    priority_queue,
                    (new_cost, neighbor),
                )

    return None, expanded_nodes
