import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p2', methods=['POST'])
def max_bugs_fixed():
    data = request.json
    results = []

    for bug_info in data:
        bugseq = bug_info['bugseq']
        
        # Sort bugs by their limits, and by difficulty if limits are the same
        bugseq.sort(key=lambda x: (x[1], x[0]))  # Sort by limit first

        current_time = 0
        count = 0
        
        for difficulty, limit in bugseq:
            if current_time + difficulty <= limit:
                current_time += difficulty  # Update current time
                count += 1  # Increment the count of bugs fixed

        results.append(count)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)