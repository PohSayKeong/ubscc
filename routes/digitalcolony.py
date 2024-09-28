from flask import Flask, request, jsonify

from routes import app

def calculate_new_colony(current_colony, weight):
    n = len(current_colony)
    new_colony = []
    
    for i in range(n - 1):
        first = current_colony[i]
        second = current_colony[i + 1]

        # Calculate the signature
        if first == second:
            signature = 0
        elif first > second:
            signature = first - second
        else:
            signature = 10 - (second - first)

        new_digit = (weight + signature) % 10
        new_colony.append(first)
        new_colony.append(new_digit)

    new_colony.append(current_colony[-1])  # Add the last digit
    return new_colony

def weights(colony, generations, chunk_size=500):
    current_colony = list(map(int, colony))
    
    for _ in range(generations):
        weight = sum(current_colony)
        new_colony = []

        # Process in chunks
        for start in range(0, len(current_colony), chunk_size):
            end = min(start + chunk_size, len(current_colony))
            chunk = current_colony[start:end]
            new_chunk = calculate_new_colony(chunk, weight)
            new_colony.extend(new_chunk)

        current_colony = new_colony
    
    final_weight = sum(current_colony)
    return final_weight

@app.route('/digitalcolony', methods=['POST'])
def digitalcolony():
    data = request.json
    results = []
    
    for entry in data:
        generations = entry['generations']
        colony = entry['colony']
        weight = weights(colony, generations)
        results.append(str(weight))
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)