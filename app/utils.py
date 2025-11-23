# app/utils.py
from flask import current_app
from datetime import datetime
import json

def json_response(data, status=200):
    from flask import jsonify
    return jsonify(data), status

def now_ts():
    return int(datetime.utcnow().timestamp())

def chunkify(iterable, size):
    """Yield successive chunks from iterable (helper)."""
    it = iter(iterable)
    while True:
        chunk = []
        for _ in range(size):
            try:
                chunk.append(next(it))
            except StopIteration:
                break
        if not chunk:
            break
        yield chunk

from .models import Timetable

def validate_assignment(classroom, teacher, subject, room, day, period):

    # 1. Teacher conflict
    if Timetable.query.filter_by(
        teacher_id=teacher.id,
        day_of_week=day,
        period_index=period
    ).first():
        return "Teacher already has a class at this time."

    # 2. Room conflict
    if Timetable.query.filter_by(
        room_id=room.id,
        day_of_week=day,
        period_index=period
    ).first():
        return "Room is already occupied."

    # 3. Class conflict
    if Timetable.query.filter_by(
        class_id=classroom.id,
        day_of_week=day,
        period_index=period
    ).first():
        return "Class already has a subject assigned at this time."

    return None
