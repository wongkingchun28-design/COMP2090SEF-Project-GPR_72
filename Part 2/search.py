def search_road(maze_data, start, end):
    stack = [start]
    visited = {start}
    path = [start]
    dead_ends = set()

    while stack:
        current = stack[-1]
        if current == end:
            yield path, dead_ends, True 
            return

        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if maze_data.get(neighbor) == 0 and neighbor not in visited:
                neighbors.append(neighbor)

        if neighbors:
            next_node = neighbors[0]
            visited.add(next_node)
            stack.append(next_node)
            path.append(next_node)
        else:
            dead_node = stack.pop()
            dead_ends.add(dead_node)
            path.pop()

        yield path, dead_ends, False
    yield path, dead_ends, False
