
global grid
global visited

def bfs(starting_positions):
    # using a deque to pop from the left, as this leads to higher performance vs a array
    queue = deque()
    for position in starting_positions:
        for direction in ["left", "right", "up", "down"]:
            queue.append((position, direction))
            visited[(position, direction)] = True

    # notice how we must move in each direction for each starting position
    while queue:
        position, direction = queue.popleft(0)

        # if we have visited all directions, we can mark the position as owned
        visited[(position, direction)] = True
        if all(visited[(position, direction)] for direction in ["left", "right", "up", "down"]):
            grid[position].mark_as_owned()

        if direction == "left":
            new_position = (position[0] - 1, position[1])
        elif direction == "right":
            new_position = (position[0] + 1, position[1])
        elif direction == "up":
            new_position = (position[0], position[1] - 1)
        elif direction == "down":
            new_position = (position[0], position[1] + 1)

        # if we have visited this position before, or we are out of bounds, we skip
        if (new_position, direction) in visited or out_of_bounds(new_position):
            continue

        # otherwise, we add the new position to the queue
        queue.append((new_position, direction))

    # now we have terminated our search, where the grid was modified in place

### Clarification
# The cells will be visited once per every direction.
# The cell is only marked as owned if all directions are visited.
# The grid is a 2D array, and is a circular grid.
# A 2D array will represent the grid
# The cell will immediately mark itself as owned when all directions are visited.
# We will not handle territory conflicts, as the intersection of paths will lead to a death.