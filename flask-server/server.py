"""
server.py

This module defines API routes for the Schedule Builder backend. 

It handles:
- Receiving user constraints via POST requests and generating schedules.
- Returning generated schedules via GET requests.

Flask is used as the backend framework.

Endpoints:
- POST /generate_schedule: Accepts constraints and generates a schedule.
- GET /get_schedule/<schedule_id>: Returns a schedule by ID.
- GET /get_courses/<
"""

from flask import Flask

app = Flask(__name__)


# Routes
@app.route("/")
def index():
    return
