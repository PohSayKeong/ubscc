import logging
from flask import Flask, request, jsonify
from collections import deque
from routes import app


# Bullet movements map: u, d, r, l
directions = {"u": (-1, 0), "d": (1, 0), "r": (0, 1), "l": (0, -1)}


# Function to move bullets on the grid
def move_bullets(grid):
    rows, cols = len(grid), len(grid[0])
    new_grid = [["." for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if isinstance(grid[r][c], set):  # If multiple bullets in the cell
                for bullet in grid[r][c]:
                    dr, dc = directions[bullet]
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < rows and 0 <= new_c < cols:
                        if new_grid[new_r][new_c] == ".":
                            new_grid[new_r][new_c] = set()
                        new_grid[new_r][new_c].add(bullet)
            elif grid[r][c] in directions:  # Single bullet
                dr, dc = directions[grid[r][c]]
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r < rows and 0 <= new_c < cols:
                    if new_grid[new_r][new_c] == ".":
                        new_grid[new_r][new_c] = set()
                    new_grid[new_r][new_c].add(grid[r][c])

    # Convert sets to single values where applicable for output consistency
    for r in range(rows):
        for c in range(cols):
            if isinstance(new_grid[r][c], set):
                if len(new_grid[r][c]) == 1:
                    new_grid[r][c] = list(new_grid[r][c])[0]

    return new_grid


# Function to convert grid to hashable format for visited set
def grid_to_hashable(grid):
    hashable_grid = []
    for row in grid:
        hashable_row = []
        for cell in row:
            if isinstance(cell, set):
                hashable_row.append(frozenset(cell))
            else:
                hashable_row.append(cell)
        hashable_grid.append(tuple(hashable_row))
    return tuple(hashable_grid)


# Function to find all valid moves from current player position
def get_valid_moves(curr_grid, next_grid, pos):
    r, c = pos
    rows, cols = len(curr_grid), len(curr_grid[0])
    possible_moves = {
        "u": (r - 1, c),
        "d": (r + 1, c),
        "l": (r, c - 1),
        "r": (r, c + 1),
    }

    valid_moves = []
    for direction, (new_r, new_c) in possible_moves.items():
        if (
            0 <= new_r < rows
            and 0 <= new_c < cols
            and next_grid[new_r][new_c] == "."
            and curr_grid[new_r][new_c] == "."
        ):
            valid_moves.append((direction, (new_r, new_c)))

    return valid_moves


# BFS to explore all possible states
def bfs_simulation(grid, player_pos):
    rows, cols = len(grid), len(grid[0])

    # Queue for BFS (stores current grid, player position, and list of moves)
    queue = deque([(grid, player_pos, [])])

    visited = set()  # To track visited states (hashable grid + player position)

    while queue:
        curr_grid, (pr, pc), moves = queue.popleft()

        # Check if there are no more bullets left
        if not any(
            isinstance(curr_grid[r][c], set) or curr_grid[r][c] in directions
            for r in range(rows)
            for c in range(cols)
        ):
            return moves  # All bullets dodged, return the sequence of moves

        # Convert the current grid to a hashable format for state tracking
        hashable_grid = grid_to_hashable(curr_grid)
        state_key = (hashable_grid, pr, pc)

        # Skip this state if it has been visited before
        if state_key in visited:
            continue
        visited.add(state_key)

        # Move the bullets to the next step
        # logging.info(f"Current grid: {curr_grid}")
        next_grid = move_bullets(curr_grid)
        # logging.info(f"Next grid: {next_grid}")

        # Check if next grid has no bullets, return the sequence of moves
        if not any(
            isinstance(next_grid[r][c], set) or next_grid[r][c] in directions
            for r in range(rows)
            for c in range(cols)
        ):
            return moves

        # Get all valid moves for the player
        # logging.info(f"Player position: {pr, pc}")
        valid_moves = get_valid_moves(curr_grid, next_grid, (pr, pc))
        # logging.info(f"Valid moves: {valid_moves}")

        for direction, new_pos in valid_moves:
            queue.append((next_grid, new_pos, moves + [direction]))

    return None  # No solution found, player cannot dodge all bullets


# POST endpoint to handle dodging logic
@app.route("/dodge", methods=["POST"])
def dodge():
    data = request.data
    logging.info("data sent for evaluation {}".format(data))
    grid = [[x for x in line.decode("utf-8")] for line in data.splitlines()]

    # Find player position
    player_pos = None
    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char == "*":
                player_pos = (r, c)

    if not player_pos:
        return jsonify({"instructions": None})

    # Prepare grid: convert bullet symbols into sets where multiple bullets might land
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] in directions:
                grid[r][c] = {grid[r][c]}

    # Run BFS simulation to find the optimal sequence of moves
    result = bfs_simulation(grid, player_pos)

    if result is None:
        return jsonify({"instructions": None})
    else:
        return jsonify({"instructions": result})
