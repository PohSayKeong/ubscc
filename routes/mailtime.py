import logging
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz
from routes import app

logger = logging.getLogger(__name__)

def calculate_response_time(email1, email2):
    sent_time1 = datetime.fromisoformat(email1['timeSent']).replace(tzinfo=pytz.UTC)
    sent_time2 = datetime.fromisoformat(email2['timeSent']).replace(tzinfo=pytz.UTC)
    
    # Calculate the total seconds between the two timestamps
    return int((sent_time2 - sent_time1).total_seconds())

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
        response_time = calculate_response_time(email1, email2)
        
        if user_name in response_times:
            response_times[user_name].append(response_time)
        else:
            response_times[user_name] = [response_time]
    
    # Calculate average response times per user
    average_times = {user: round(sum(times) / len(times)) for user, times in response_times.items()}
    
    return jsonify(average_times)

if __name__ == '__main__':
    app.run(debug=True)
