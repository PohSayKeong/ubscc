import logging
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz
from routes import app

logger = logging.getLogger(__name__)

# Helper function to calculate time within working hours, skipping weekends and after-hours
def calculate_working_time(start_time, end_time, user):
    tz = pytz.timezone(user['officeHours']['timeZone'])
    local_start = start_time.astimezone(tz)
    local_end = end_time.astimezone(tz)

    total_seconds = 0
    work_start = user['officeHours']['start']
    work_end = user['officeHours']['end']

    while local_start < local_end:
        # Move to the next working day if outside working hours
        if local_start.hour >= work_end:  # If current time is after working hours
            local_start += timedelta(days=1)
            local_start = local_start.replace(hour=work_start, minute=0, second=0, microsecond=0)
        elif local_start.hour < work_start:  # If current time is before working hours
            local_start = local_start.replace(hour=work_start, minute=0, second=0, microsecond=0)

        # Skip weekends
        while local_start.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            local_start += timedelta(days=1)
            local_start = local_start.replace(hour=work_start, minute=0, second=0, microsecond=0)

        # Calculate time until the end of the working day or the response time
        next_work_end = local_start.replace(hour=work_end, minute=0, second=0, microsecond=0)
        
        if local_end < next_work_end:  # If the end time is before the workday ends
            total_seconds += (local_end - local_start).total_seconds()
            break
        else:  # If the end time is after the workday ends, add time until the end of the working day
            total_seconds += (next_work_end - local_start).total_seconds()
            local_start = next_work_end

    return total_seconds

# Calculate the response time in seconds
def calculate_response_time(email1, email2, users):
    sender1 = next(u for u in users if u['name'] == email1['sender'])
    receiver1 = next(u for u in users if u['name'] == email1['receiver'])
    
    sent_time1 = datetime.fromisoformat(email1['timeSent']).replace(tzinfo=pytz.UTC)
    sent_time2 = datetime.fromisoformat(email2['timeSent']).replace(tzinfo=pytz.UTC)

    # Calculate the time within working hours for the receiver of email2
    return calculate_working_time(sent_time1, sent_time2, receiver1)

@app.route('/mailtime', methods=['POST'])
def mailtime():
    data = request.json
    emails = data['emails']
    users = data['users']
    
    response_times = {}
    
    # Sort emails based on subject and time
    emails.sort(key=lambda x: x['timeSent'])
    
    for i in range(1, len(emails)):
        email1 = emails[i - 1]
        email2 = emails[i]
        
        # Calculate response time for the sender of email2
        user_name = email2['sender']
        response_time = calculate_response_time(email1, email2, users)
        
        if user_name in response_times:
            response_times[user_name].append(response_time)
        else:
            response_times[user_name] = [response_time]
    
    # Calculate average response times per user
    average_times = {user: round(sum(times) / len(times)) for user, times in response_times.items()}
    
    return jsonify(average_times)

if __name__ == '__main__':
    app.run(debug=True)
