from flask import Flask, request, jsonify

from routes import app


def calculate_efficiency(monsters):
    n = len(monsters)
    efficiency = 0
    i = 0

    while i < n:
        # Kazuma prepares to attack only if it's beneficial
        if monsters[i] > 0:
            # Monsters at current time frame (protection cost is equal to monsters in this frame)
            protection_cost = monsters[i]

            # Attack only if Kazuma gains more than the protection cost (defeating all monsters)
            if protection_cost > 1:  # Minimum cost of 1 adventurer (cost >= 1)
                efficiency += (
                    protection_cost - 1
                )  # Earns gold equivalent to (monsters - cost)

            # After attack, move to rear and recover for one time frame (i+1 is skipped)
            i += 2
        else:
            # Move to next time frame if no monsters or no attack
            i += 1

    return efficiency


@app.route("/efficient-hunter-kazuma", methods=["POST"])
def efficient_hunter_kazuma():
    data = request.get_json()
    response = []

    for entry in data:
        monsters = entry["monsters"]
        efficiency = calculate_efficiency(monsters)
        response.append({"efficiency": efficiency})

    return jsonify(response)
