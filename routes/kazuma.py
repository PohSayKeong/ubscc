from flask import Flask, request, jsonify
import logging
from routes import app


def calculate_max_efficiency(monsters):
    n = len(monsters)
    dp = [0] * (n + 1)  # dp[i] stores the maximum efficiency starting from time i
    max_gold = 0

    # Traverse backwards through the time steps to calculate the best decision at each point
    for i in range(n - 1, -1, -1):
        # If Kazuma prepares a circle at time i, he can attack at any future time j (j > i)
        for j in range(i + 1, n):
            attack_gain = max(
                0, monsters[j] - monsters[i]
            )  # Gain from attacking at time j
            if j + 1 < n:
                dp[i] = max(
                    dp[i], attack_gain + dp[j + 1]
                )  # Include future gains after cooldown
            else:
                dp[i] = max(
                    dp[i], attack_gain
                )  # No future steps after attacking at the last moment
        # If Kazuma does nothing at this time, he just carries forward the next step's efficiency
        dp[i] = max(dp[i], dp[i + 1])

    return dp[0]


@app.route("/efficient-hunter-kazuma", methods=["POST"])
def efficient_hunter_kazuma():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    response = []

    for entry in data:
        monsters = entry["monsters"]
        efficiency = calculate_max_efficiency(monsters)
        response.append({"efficiency": efficiency})

    return jsonify(response)
