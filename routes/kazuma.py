from flask import Flask, request, jsonify
import logging
from routes import app


def calculate_max_efficiency(monsters):
    dp = {}

    def dfs(i, charged):
        if i >= len(monsters):
            return 0
        if (i, charged) in dp:
            return dp[(i, charged)]

        if charged:
            ans = max(dfs(i + 2, False) + monsters[i], dfs(i + 1, True))
        else:
            ans = max(dfs(i + 1, False), dfs(i + 1, True) - monsters[i])

        dp[(i, charged)] = ans
        return ans

    return dfs(0, False)


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
