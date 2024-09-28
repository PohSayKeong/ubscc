import logging
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz
from routes import app
from collections import defaultdict


# Helper function to extract the root subject
def get_root_subject(subject):
    return subject.split("RE: ")[-1].strip()


def calculate_response_time(email1, email2, tz1, tz2):
    # 2024-01-12T15:00:00+01:00
    time1 = datetime.fromisoformat(email1["timeSent"])
    time2 = datetime.fromisoformat(email2["timeSent"])
    logging.info(f"time1: {time1}, time2: {time2}")
    logging.info(f"tz1: {tz1}, tz2: {tz2}")

    # Convert time2 to time1's timezone
    time2 = time2.astimezone(tz1)
    logging.info(f"time2 converted to tz1: {time2}")

    return (time2 - time1).total_seconds()


@app.route("/mailtime", methods=["POST"])
def mailtime():
    data = request.json
    logging.info("data sent for evaluation {}".format(data))
    emails = data["emails"]
    users_info = data["users"]
    users = {user["name"]: user["officeHours"]["timeZone"] for user in users_info}

    # Group emails by thread
    threads = defaultdict(list)

    for email in emails:
        root_subject = get_root_subject(email["subject"])
        threads[root_subject].append(email)

    response_times = defaultdict(list)

    # Calculate response times for each email in the thread
    for thread in threads.values():
        thread.sort(key=lambda x: x["timeSent"])
        for i in range(1, len(thread)):
            email1 = thread[i - 1]
            email2 = thread[i]
            tz1 = pytz.timezone(users[email1["sender"]])
            tz2 = pytz.timezone(users[email2["sender"]])

            # Calculate response time for the sender of email2
            user_name = email2["sender"]
            response_time = calculate_response_time(email1, email2, tz1, tz2)
            logging.info(
                f"Response time from {email1['sender']} to {email2['sender']}: {response_time} seconds"
            )

            response_times[user_name].append(response_time)

    # Calculate average response times per user
    average_times = {
        user: round(sum(times) / len(times)) for user, times in response_times.items()
    }

    return jsonify({"response": average_times})


if __name__ == "__main__":
    app.run(debug=True)
