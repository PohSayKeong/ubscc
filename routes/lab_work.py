import json
import logging
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

@app.route('/lab_work', methods=['POST'])
def lab_work():
    data = request.get_json()
    logging.info("Data received for evaluation: {}".format(data))
    
    if not isinstance(data, list):
        logging.error("Invalid input format: Expected a list of test cases.")
        return jsonify({"error": "Invalid input format"}), 400
    
    results = []
    
    for idx, test_case in enumerate(data):
        test_case_results = {}
        
        try:
            logging.info(f"Processing test case {idx + 1}")
            labs = parse_labs(test_case)
            logging.info(f"Labs initialized: {labs}")
        except Exception as e:
            logging.error(f"Failed to parse test case {idx + 1}: {str(e)}")
            return jsonify({"error": f"Failed to parse test case {idx + 1}: {str(e)}"}), 400

        analysis_counts = {lab_id: 0 for lab_id in labs}
        
        # Run for 10,000 days
        for day in range(1, 10001):
            try:
                process_day(labs, analysis_counts)
            except Exception as e:
                logging.error(f"Error processing day {day} for test case {idx + 1}: {str(e)}")
                return jsonify({"error": f"Error processing day {day} for test case {idx + 1}: {str(e)}"}), 500
            
            if day % 1000 == 0:
                logging.info(f"Logging results for day {day} in test case {idx + 1}")
                test_case_results[str(day)] = [analysis_counts[lab_id] for lab_id in sorted(analysis_counts)]
        
        results.append(test_case_results)
    
    logging.info(f"Final result: {results}")
    return jsonify(results)

def parse_labs(test_case):
    labs = {}
    lines = test_case.strip().split("\n")
    if len(lines) < 2:
        raise ValueError("Invalid test case format: too few lines")
    
    for line in lines[2:]:  # Skip the header
        try:
            lab_id, counts, increment, condition = parse_line(line)
            labs[int(lab_id)] = {
                "counts": list(map(int, counts.split())),
                "increment": increment,
                "condition": list(map(int, condition.split())),
            }
        except Exception as e:
            raise ValueError(f"Failed to parse line '{line}': {str(e)}")
    return labs

def parse_line(line):
    parts = line.split("|")
    lab_id = parts[1].strip()          # First column is the lab ID
    counts = parts[2].strip()          # Second column is the cell counts
    increment = parts[3].strip()       # Third column is the increment rule
    condition = parts[4].strip()       # Fourth column is the condition
    
    return lab_id, counts, increment, condition

def process_day(labs, analysis_counts):
    # Create a new list for each lab to avoid multiple appends
    new_counts = {lab_id: [] for lab_id in labs}
    
    for lab_id, lab_data in labs.items():
        current_counts = lab_data['counts']
        increment_func = create_increment_function(lab_data['increment'])

        for count in current_counts:
            new_count = increment_func(count)
            
            # Check condition
            divisible_by, pass_if_true, pass_if_false = lab_data['condition']
            pass_to = pass_if_true if new_count % divisible_by == 0 else pass_if_false
            
            new_counts[pass_to].append(new_count)

        # Update analysis counts
        analysis_counts[lab_id] += len(current_counts)
    
    # Update labs for the next day
    for lab_id in new_counts:
        labs[lab_id]['counts'] = new_counts[lab_id]

def create_increment_function(increment):
    """ Create a function for the increment operation to avoid repeated parsing. """
    if '*' in increment:
        factor = increment.split('*')[-1].strip()
        if factor == "count":
            return lambda x: x * x  # Use x * x directly
        else:
            factor = int(factor)
            return lambda x: x * factor
    elif '+' in increment:
        add_value = increment.split('+')[-1].strip()
        if add_value == "count":
            return lambda x: x + x  # Use x + x directly
        else:
            add_value = int(add_value)
            return lambda x: x + add_value
    else:
        raise ValueError(f"Invalid increment format: {increment}")
