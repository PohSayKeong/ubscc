import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)

# Directions mapping
directions = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1)
}

def parse_board(board_str):
    return [list(board_str[i:i+4]) for i in range(0, 20, 4)]

def board_to_string(board):
    return ''.join(''.join(row) for row in board)

def can_move(board, block, direction):
    delta_row, delta_col = directions[direction]
    block_positions = [(r, c) for r in range(4) for c in range(5) if board[r][c] == block]

    # Check if all parts of the block can move in the specified direction
    for r, c in block_positions:
        new_r = r + delta_row
        new_c = c + delta_col
        
        # Check if the new position is within bounds and is empty
        if not (0 <= new_r < 4 and 0 <= new_c < 5 and (board[new_r][new_c] == '@' or board[new_r][new_c] == block)):
            return False
    return True

def move_block(board, block, direction):
    delta_row, delta_col = directions[direction]
    block_positions = [(r, c) for r in range(4) for c in range(5) if board[r][c] == block]

    for r, c in block_positions:
        board[r][c] = '@'  # Clear the old position

    for r, c in block_positions:
        new_r = r + delta_row
        new_c = c + delta_col
        board[new_r][new_c] = block  # Place the block in the new position

def process_board(board_str, moves_str):
    board = parse_board(board_str)

    for i in range(0, len(moves_str), 2):
        block = moves_str[i]
        direction = moves_str[i+1]
        
        # Only try to move if the block exists in the board
        if any(block in row for row in board) and can_move(board, block, direction):
            move_block(board, block, direction)

    return board_to_string(board)

@app.route('/klotski', methods=['POST'])
def klotski():
    data = request.json
    results = []
    
    for item in data:
        board = item['board']
        moves = item['moves']
        result_board = process_board(board, moves)
        results.append(result_board)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
