from flask import Flask, request, jsonify
from routes import app

def find_best_path(locations, starting_point, time_limit):
    max_satisfaction = 0
    best_path = []

    # Backtracking function to explore paths
    def backtrack(current_station, current_time, current_satisfaction, visited, path):
        nonlocal max_satisfaction, best_path
        
        # Check if we exceeded the time limit
        if current_time > time_limit:
            return
        
        # If we are back to the starting point with more than one stop, check satisfaction
        if len(path) > 1 and current_station == starting_point:
            if current_satisfaction > max_satisfaction:
                max_satisfaction = current_satisfaction
                best_path = path[:]
            return
        
        # Explore the next stations
        for station, (satisfaction, min_time) in locations.items():
            if station not in visited:
                visited.add(station)
                path.append(station)
                # Recursive call to backtrack with updated parameters
                backtrack(station, current_time + min_time, current_satisfaction + satisfaction, visited, path)
                path.pop()
                visited.remove(station)
    
    # Initialize the backtracking
    visited = set()
    visited.add(starting_point)
    backtrack(starting_point, 0, 0, visited, [starting_point])
    
    return best_path, max_satisfaction

@app.route('/tourist', methods=['POST'])
def tourist():
    data = request.get_json()
    locations = data['locations']
    starting_point = data['startingPoint']
    time_limit = data['timeLimit']
    
    # Find the best path and satisfaction
    path, satisfaction = find_best_path(locations, starting_point, time_limit)
    
    # Format the output
    response = {
        'path': path,
        'satisfaction': satisfaction
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
