from flask import Flask, request, jsonify
import logging
from routes import app

cache = {}


def calculate_new_colony(current_colony, weight):
    n = len(current_colony)
    new_colony = [0] * (2 * n - 1)  # Preallocate size for performance

    # Fill the new colony
    for i in range(n - 1):
        first = current_colony[i]
        second = current_colony[i + 1]

        # Calculate the signature
        if (first, second, weight) in cache:
            digit = cache[(first, second, weight)]
        else:
            if first == second:
                signature = 0
            elif first > second:
                signature = first - second
            else:
                signature = 10 - (second - first)

            digit = (weight + signature) % 10
            cache[(first, second, weight)] = digit
        # Calculate the new digit and append in place
        new_colony[2 * i] = first
        new_colony[2 * i + 1] = digit

    new_colony[-1] = current_colony[-1]  # Add the last digit

    return new_colony


def weights(colony, generations):
    current_colony = list(map(int, colony))
    for i in range(generations):
        weight = sum(current_colony) % 10  # Modular arithmetic to keep weight small
        logging.info(f"Generation {i}, Weight: {weight}")
        new_colony = calculate_new_colony(current_colony, weight)

        # Early termination if colony stabilizes
        if new_colony == current_colony:
            break

        current_colony = new_colony

    final_weight = sum(current_colony)
    return final_weight


@app.route("/digitalcolony", methods=["POST"])
def digitalcolony():
    data = request.json
    results = []

    for entry in data:
        generations = entry["generations"]
        colony = entry["colony"]
        weight = weights(colony, generations)
        results.append(str(weight))
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
