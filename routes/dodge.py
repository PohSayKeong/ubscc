import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

@app.route('/dodge', methods=['POST'])
def dodge():
    data = request.json
    map_text = data.get('map', '')
    instructions = []

    # Parse the map into a 2D array
    grid = [list(line) for line in map_text.splitlines()]
    player_position = None
    bullets = []

    # Locate the player and bullets
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == '*':
                player_position = (r, c)
            elif grid[r][c] in 'udlr':
                bullets.append((r, c, grid[r][c]))

    if not player_position:
        return jsonify({"instructions": None})

    # Possible moves
    moves = {
        'u': (-1, 0),  # Up
        'd': (1, 0),   # Down
        'l': (0, -1),  # Left
        'r': (0, 1)    # Right
    }

    # Create a set of bullet positions after potential player moves
    bullet_positions = set()
    for br, bc, direction in bullets:
        if direction == 'u':
            bullet_positions.add((br - 1, bc))  # Bullet moves up
        elif direction == 'd':
            bullet_positions.add((br + 1, bc))  # Bullet moves down
        elif direction == 'l':
            bullet_positions.add((br, bc - 1))  # Bullet moves left
        elif direction == 'r':
            bullet_positions.add((br, bc + 1))  # Bullet moves right

    # Check valid moves and avoid moves towards bullets
    for move_key, (dr, dc) in moves.items():
        new_r = player_position[0] + dr
        new_c = player_position[1] + dc
        # Check if the new position is within bounds and not a bullet position
        if is_within_bounds(new_r, new_c, grid):
            if (new_r, new_c) not in bullet_positions:  # Ensure move is safe
                instructions.append(move_key)

    # If there are valid instructions, return the first valid one; otherwise, return null
    if instructions:
        return jsonify({"instructions": [instructions[0]]})
    else:
        return jsonify({"instructions": None})

def is_within_bounds(row, col, grid):
    return 0 <= row < len(grid) and 0 <= col < len(grid[0])

if __name__ == '__main__':
    app.run(debug=True)
