from flask import Flask, request, jsonify
import logging
from routes import app


def calculate_efficiency_dp(monsters):
    n = len(monsters)

    if n == 0:
        return 0
    elif n == 1:
        return 0  # Not enough time to prepare and attack

    # DP array to store the maximum efficiency starting from each time frame
    dp = [0] * (n + 1)

    # Iterate from the end of the time frames to the beginning
    for i in range(n - 2, -1, -1):
        # Option 1: Skip this time frame
        dp[i] = dp[i + 1]

        # Option 2: Prepare circle at i, attack at i+1, and rest at i+2 (if within bounds)
        if i + 1 < n:
            # Kazuma pays for preparation at i and attack at i+1
            profit = (monsters[i + 1]) - monsters[i]
            if i + 2 < n:
                dp[i] = max(dp[i], dp[i + 2] + profit)
            else:
                dp[i] = max(dp[i], profit)

    # Maximum efficiency is stored in dp[0]
    return dp[0]


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
