import logging
from flask import Flask, request, jsonify
from routes import app

logger = logging.getLogger(__name__)

@app.route('/taxi-driver', methods=['POST'])
def taxi_driver():
    data = request.get_json()
    
    # Extract the necessary data
    taxi_info = data['challengeInput']['taxiInfo']
    station_info = data['challengeInput']['taxiStationInfo']
    start_time = data['challengeInput']['startTime']
    end_time = data['challengeInput']['endTime']

    taxi_lo_location = None
    for taxi in taxi_info:
        if taxi['taxiId'] == 0:  # Taxi Lo's ID is always 0
            taxi_lo_location = taxi['taxiLocation']
            break

    # Dictionary to map station names to their customer queues
    station_customers = {station['taxiStation']: station['customers'] for station in station_info}
    
    # Variables to track Taxi Lo's journey
    path = []
    customers_picked = []
    total_profit = 0
    
    # Helper to convert time string to minutes for easy calculations
    def time_to_minutes(time_str):
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    # Time limit in minutes
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    total_shift_duration = end_minutes - start_minutes
    
    # Simulate Taxi Lo's journey
    current_time = 0  # Start at 0 minutes from shift start
    while current_time < total_shift_duration:
        path.append(taxi_lo_location)
        
        # Find the best customer at the current station
        customers_at_station = station_customers[taxi_lo_location]
        if customers_at_station:
            best_customer = max(customers_at_station, key=lambda c: c['fee'])
            customers_picked.append(best_customer['customerId'])
            total_profit += best_customer['fee']
            
            # Move Taxi Lo to the customer's destination
            taxi_lo_location = best_customer['destination']
            
            # Remove the customer from the queue
            station_customers[taxi_lo_location].remove(best_customer)
        else:
            # No customers left, Taxi Lo waits at the current station
            break
        
        # Increase time by 1 hour for the next station move
        current_time += 60
    
    # Return the results
    return jsonify({
        'path': path,
        'customers': customers_picked,
        'profit': total_profit
    })

if __name__ == '__main__':
    app.run(debug=True)
