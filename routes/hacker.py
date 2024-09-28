import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)


@app.route("/coolcodehack", methods=["POST"])
def hacker():
    return json.dumps({"username": "username", "password": "password"})
