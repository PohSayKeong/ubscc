from flask import Flask, request, jsonify
import logging
from routes import app


def calculate_efficiency_dp(monsters):
    n = len(monsters)

    if n == 0:
        return 0
    elif n == 1:
        return max(0, monsters[0] - 1)

    # DP array to store maximum efficiency up to each time frame
    dp = [0] * n

    # Base cases
    dp[0] = max(0, monsters[0] - 1)
    if n > 1:
        dp[1] = max(dp[0], monsters[1] - 1)

    # Fill DP table using recurrence relation
    for i in range(2, n):
        # Option 1: Don't attack at time i, just carry over the previous efficiency
        dp[i] = dp[i - 1]

        # Option 2: Attack at time i, add monsters[i] - 1 and skip the next time frame
        dp[i] = max(dp[i], dp[i - 2] + (monsters[i] - 1))

    # Return the maximum efficiency at the last time frame
    return dp[n - 1]


@app.route("/efficient-hunter-kazuma", methods=["POST"])
def efficient_hunter_kazuma():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    response = []

    for entry in data:
        monsters = entry["monsters"]
        efficiency = calculate_efficiency_dp(monsters)
        response.append({"efficiency": efficiency})

    return jsonify(response)
