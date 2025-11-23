# app/api.py
import time
from flask import Blueprint, request, current_app, jsonify
from .imports import db
from .models import Timetable, Subject, ClassRoom, Teacher, Room, Subject, School, PeriodTemplate
from .utils import json_response

api_bp = Blueprint("api", __name__)

@api_bp.route("/generate", methods=["POST"])
def generate():
    """
    Trigger timetable generation for a school.
    JSON body:
      { "school_id": 1, "period_template_id": 1, "overwrite": true }
    """
    data = request.get_json() or {}
    school_id = int(data.get("school_id", 1))
    period_template_id = data.get("period_template_id")
    overwrite = bool(data.get("overwrite", True))

    start = time.time()
    gen = TimetableGenerator(school_id=school_id)
    try:
        result = gen.run(period_template_id=period_template_id, overwrite=overwrite)
        duration = int(time.time() - start)
        # audit
        gr = GeneratorRun(school_id=school_id, status="success" if result["success"] else "partial",
                          message=result["message"], duration_seconds=duration)
        db.session.add(gr)
        db.session.commit()
        return json_response({"ok": True, "result": result})
    except Exception as e:
        duration = int(time.time() - start)
        gr = GeneratorRun(school_id=school_id, status="failed", message=str(e), duration_seconds=duration)
        db.session.add(gr)
        db.session.commit()
        return json_response({"ok": False, "error": str(e)}, status=500)

@api_bp.route("/timetable/class/<int:class_id>", methods=["GET"])
def api_timetable_class(class_id):
    slots = TimetableSlot.query.filter_by(class_id=class_id).all()
    out = []
    for s in slots:
        out.append({
            "day": s.day_of_week,
            "period": s.period_index,
            "teacher_id": s.teacher_id,
            "subject_id": s.subject_id,
            "room_id": s.room_id
        })
    return jsonify(out)
