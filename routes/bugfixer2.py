import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)


def max_bugsfixed(bugseq):
    # Sort the bugs by their escalation limits
    bugseq.sort(key=lambda x: x[1])

    # Initialize dp array, where dp[i] is the minimum time to fix i bugs
    n = len(bugseq)
    dp = [float("inf")] * (n + 1)  # dp[i] holds the minimum time to complete i bugs
    dp[0] = 0  # 0 bugs take 0 time

    # Process each bug
    for difficulty, limit in bugseq:
        # Traverse dp array in reverse to prevent overwriting during update
        for i in range(n - 1, -1, -1):
            # If we can add this bug to the i-th solution without exceeding the limit
            if dp[i] + difficulty <= limit:
                dp[i + 1] = min(dp[i + 1], dp[i] + difficulty)

    # The result is the maximum number of bugs that can be fixed
    for i in range(n, -1, -1):
        if dp[i] != float("inf"):
            return i
    return 0


@app.route("/bugfixer/p2", methods=["POST"])
def max_bugs():
    data = request.json
    results = []

    for bug_info in data:
        bugseq = bug_info["bugseq"]
        results.append(max_bugsfixed(bugseq))

    return jsonify(results)
