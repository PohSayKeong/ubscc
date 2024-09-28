import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p1', methods=['POST'])
def bug_fixer():
    data = request.json
    results = []
    
    for project in data:
        times = project['time']
        prerequisites = project['prerequisites']
        
        n = len(times)
        graph = defaultdict(list)
        indegree = [0] * n
        completion_time = [0] * n
        
        # Build the graph and indegree array
        for a, b in prerequisites:
            graph[a-1].append(b-1)  # Convert to 0-indexed
            indegree[b-1] += 1
        
        # Initialize the completion times
        for i in range(n):
            completion_time[i] = times[i]

        # Topological sort using Kahn's algorithm
        queue = deque()
        
        # Start with projects that have no prerequisites
        for i in range(n):
            if indegree[i] == 0:
                queue.append(i)

        while queue:
            current = queue.popleft()
            
            # Process each dependent project
            for neighbor in graph[current]:
                # Calculate the max completion time for this project
                completion_time[neighbor] = max(completion_time[neighbor], completion_time[current] + times[neighbor])
                indegree[neighbor] -= 1
                
                # If this project now has no more prerequisites, add it to the queue
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        # The minimum hours needed is the maximum completion time across all projects
        results.append(max(completion_time))
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
