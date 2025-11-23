# # app/routes.py
# from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
# from flask_login import login_user, logout_user, login_required, current_user
# from .forms import SubjectForm, TeacherForm, LoginForm, PeriodTemplateForm
# from .imports import db
# from .models import (
#     User,  # Added import for User
#     School, Teacher, ClassRoom, EducationLevel, PeriodTemplate,
#     Subject, Room, Timetable  # Using TimetableSlot for timetable entries
# )
# from .utils import json_response

# main_main_bp = Blueprint("main", __name__)

# @main_main_bp.route("/")
# @login_required
# def index():
#     return redirect(url_for('main.admin_admin_dashboard'))

# # @main_main_bp.route("/admin_admin_dashboard")
# # @login_required
# # def admin_admin_dashboard():
# #     return render_template("admin_admin_dashboard.html")

# @main_main_bp.route('/admin')
# @login_required
# def admin_admin_dashboard():
#     schools = School.query.all()
#     teachers = Teacher.query.all()
#     classes = ClassRoom.query.all()

#     school = schools[0] if schools else None

#     return render_template(
#         "admin_admin_dashboard.html",
#         school=school,
#         teachers=teachers,
#         classes=classes
#     )



# @main_main_bp.route("/login", methods=["GET", "POST"])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         u = User.query.filter_by(username=form.username.data).first()
#         if u and u.check_password(form.password.data):
#             login_user(u)
#             flash(f"Welcome back, {u.username}", "success")
#             return redirect(url_for("main.admin_admin_dashboard"))
#         flash("Invalid credentials", "danger")
#     return render_template("login.html", form=form)


# @main_main_bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.login"))


# # Utility serializer helpers

# def serialize_school(s):
#     return {"id": s.id, "name": s.name}

# def serialize_education_level(el):
#     return {"id": el.id, "name": el.name}

# def serialize_teacher(t):
#     return {
#         "id": t.id,
#         "school_id": t.school_id,
#         "first_name": t.first_name,
#         "last_name": t.last_name,
#         "email": t.email,
#         "max_periods_per_day": t.max_periods_per_day,
#         "max_periods_per_week": t.max_periods_per_week,
#         "education_level_id": t.education_level_id
#     }

# def serialize_classroom(c):
#     return {
#         "id": c.id,
#         "school_id": c.school_id,
#         "name": c.name,
#         "size": c.size,
#         "education_level_id": c.education_level_id
#     }

# def serialize_period_template(pt):
#     return {
#         "id": pt.id,
#         "school_id": pt.school_id,
#         "name": pt.name,
#         "days_per_week": pt.days_per_week,
#         "periods_per_day": pt.periods_per_day,
#         "break_after_period": pt.break_after_period
#     }

# def serialize_subject(s):
#     return {
#         "id": s.id,
#         "school_id": s.school_id,
#         "code": s.code,
#         "name": s.name,
#         "subject_type": s.subject_type,
#         "periods_per_week": s.periods_per_week,
#         "education_level_id": s.education_level_id
#     }

# def serialize_room(r):
#     return {
#         "id": r.id,
#         "school_id": r.school_id,
#         "name": r.name,
#         "capacity": r.capacity,
#         "room_type": r.room_type
#     }

# def serialize_timetable_slot(ts):
#     return {
#         "id": ts.id,
#         "class_id": ts.class_id,
#         "teacher_id": ts.teacher_id,
#         "subject_id": ts.subject_id,
#         "room_id": ts.room_id,
#         "day_of_week": ts.day_of_week,
#         "period_index": ts.period_index
#     }

# # -------------------------
# # API ROUTES
# # -------------------------

# @main_main_bp.route("/api/schools", methods=["GET"])
# @login_required
# def api_get_schools():
#     schools = School.query.all()
#     return jsonify([serialize_school(s) for s in schools])

# @main_main_bp.route("/api/education-levels", methods=["GET"])
# @login_required
# def api_get_education_levels():
#     els = EducationLevel.query.all()
#     return jsonify([serialize_education_level(el) for el in els])

# # PERIOD TEMPLATES

# @main_main_bp.route("/api/period-templates", methods=["GET", "POST"])
# @login_required
# def api_period_templates():
#     if request.method == "GET":
#         templates = PeriodTemplate.query.filter_by(school_id=1).order_by(PeriodTemplate.id.desc()).all()
#         return jsonify([serialize_period_template(t) for t in templates])

#     # POST - create new
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     name = data.get("name", "").strip()
#     days_per_week = data.get("days_per_week")
#     periods_per_day = data.get("periods_per_day")
#     break_after_period = data.get("break_after_period")

#     if not name or not isinstance(days_per_week, int) or not isinstance(periods_per_day, int):
#         return jsonify({"error": "Invalid or missing fields"}), 400

#     pt = PeriodTemplate(
#         school_id=1,
#         name=name,
#         days_per_week=days_per_week,
#         periods_per_day=periods_per_day,
#         break_after_period=break_after_period
#     )
#     db.session.add(pt)
#     db.session.commit()
#     return jsonify(serialize_period_template(pt)), 201


# @main_main_bp.route("/api/period-templates/<int:id>", methods=["GET", "PUT", "DELETE"])
# @login_required
# def api_period_template_detail(id):
#     pt = PeriodTemplate.query.get_or_404(id)

#     if request.method == "GET":
#         return jsonify(serialize_period_template(pt))

#     if request.method == "PUT":
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         pt.name = data.get("name", pt.name).strip()
#         pt.days_per_week = data.get("days_per_week", pt.days_per_week)
#         pt.periods_per_day = data.get("periods_per_day", pt.periods_per_day)
#         pt.break_after_period = data.get("break_after_period", pt.break_after_period)
#         db.session.commit()
#         return jsonify(serialize_period_template(pt))

#     if request.method == "DELETE":
#         db.session.delete(pt)
#         db.session.commit()
#         return jsonify({"message": "Period template deleted"}), 200

# # TEACHERS

# @main_main_bp.route("/manage_teachers", methods=["GET", "POST"])
# @login_required
# def manage_teachers():
#     if request.method == "GET":
#         teachers = Teacher.query.all()
#         return jsonify([serialize_teacher(t) for t in teachers])

#     # POST create new
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     first_name = data.get("first_name")
#     last_name = data.get("last_name")
#     email = data.get("email")
#     max_periods_per_day = data.get("max_periods_per_day", 6)
#     max_periods_per_week = data.get("max_periods_per_week", 30)
#     education_level_id = data.get("education_level_id", None)
#     if education_level_id == 0:
#         education_level_id = None

#     if not first_name or not last_name or not email:
#         return jsonify({"error": "Missing required fields"}), 400

#     new_teacher = Teacher(
#         school_id=1,
#         first_name=first_name,
#         last_name=last_name,
#         email=email,
#         max_periods_per_day=max_periods_per_day,
#         max_periods_per_week=max_periods_per_week,
#         education_level_id=education_level_id
#     )
#     db.session.add(new_teacher)
#     db.session.commit()
#     return jsonify(serialize_teacher(new_teacher)), 201

# @main_main_bp.route("/api/teachers/<int:id>", methods=["GET", "PUT", "DELETE"])
# @login_required
# def api_teacher_detail(id):
#     teacher = Teacher.query.get_or_404(id)

#     if request.method == "GET":
#         return jsonify(serialize_teacher(teacher))

#     if request.method == "PUT":
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         teacher.first_name = data.get("first_name", teacher.first_name)
#         teacher.last_name = data.get("last_name", teacher.last_name)
#         teacher.email = data.get("email", teacher.email)
#         teacher.max_periods_per_day = data.get("max_periods_per_day", teacher.max_periods_per_day)
#         teacher.max_periods_per_week = data.get("max_periods_per_week", teacher.max_periods_per_week)
#         education_level_id = data.get("education_level_id", teacher.education_level_id)
#         teacher.education_level_id = None if education_level_id == 0 else education_level_id
#         db.session.commit()
#         return jsonify(serialize_teacher(teacher))

#     if request.method == "DELETE":
#         try:
#             db.session.delete(teacher)
#             db.session.commit()
#             return jsonify({"message": "Teacher deleted"})
#         except Exception:
#             db.session.rollback()
#             return jsonify({"error": "Error deleting teacher"}), 500

# # SUBJECTS

# @main_main_bp.route("/manage_subjects", methods=["GET", "POST"])
# @login_required
# def manage_subjects():
#     if request.method == "GET":
#         subjects = Subject.query.filter_by(school_id=1).all()
#         return jsonify([serialize_subject(s) for s in subjects])

#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     code = data.get("code")
#     name = data.get("name")
#     subject_type = data.get("subject_type")
#     periods_per_week = data.get("periods_per_week")

#     if not code or not name or not subject_type or periods_per_week is None:
#         return jsonify({"error": "Missing required fields"}), 400

#     new_subject = Subject(
#         school_id=1,
#         code=code,
#         name=name,
#         subject_type=subject_type,
#         periods_per_week=periods_per_week
#     )
#     db.session.add(new_subject)
#     db.session.commit()
#     return jsonify(serialize_subject(new_subject)), 201

# @main_main_bp.route("/api/subjects/<int:id>", methods=["GET", "PUT", "DELETE"])
# @login_required
# def api_subject_detail(id):
#     subject = Subject.query.get_or_404(id)

#     if request.method == "GET":
#         return jsonify(serialize_subject(subject))

#     if request.method == "PUT":
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         subject.code = data.get("code", subject.code)
#         subject.name = data.get("name", subject.name)
#         subject.subject_type = data.get("subject_type", subject.subject_type)
#         subject.periods_per_week = data.get("periods_per_week", subject.periods_per_week)
#         db.session.commit()
#         return jsonify(serialize_subject(subject))

#     if request.method == "DELETE":
#         db.session.delete(subject)
#         db.session.commit()
#         return jsonify({"message": "Subject deleted"}), 200

# # ROOMS

# @main_main_bp.route("/manage_rooms", methods=["GET", "POST"])
# @login_required
# def manage_rooms():
#     if request.method == "GET":
#         rooms = Room.query.all()
#         return jsonify([serialize_room(r) for r in rooms])

#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     name = data.get("name")
#     capacity = data.get("capacity")
#     room_type = data.get("room_type")

#     if not name or capacity is None or not room_type:
#         return jsonify({"error": "Missing required fields"}), 400

#     new_room = Room(
#         school_id=1,
#         name=name,
#         capacity=capacity,
#         room_type=room_type
#     )
#     db.session.add(new_room)
#     db.session.commit()
#     return jsonify(serialize_room(new_room)), 201

# @main_main_bp.route("/api/rooms/<int:id>", methods=["GET", "PUT", "DELETE"])
# @login_required
# def api_room_detail(id):
#     room = Room.query.get_or_404(id)

#     if request.method == "GET":
#         return jsonify(serialize_room(room))

#     if request.method == "PUT":
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         room.name = data.get("name", room.name)
#         room.capacity = data.get("capacity", room.capacity)
#         room.room_type = data.get("room_type", room.room_type)
#         db.session.commit()
#         return jsonify(serialize_room(room))

#     if request.method == "DELETE":
#         db.session.delete(room)
#         db.session.commit()
#         return jsonify({"message": "Room deleted"}), 200

# # CLASSES

# @main_main_bp.route("/manage_classes", methods=["GET", "POST"])
# @login_required
# def manage_classes():
#     if request.method == "GET":
#         classes = ClassRoom.query.all()
#         return jsonify([serialize_classroom(c) for c in classes])

#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     name = data.get("name")
#     size = data.get("size")
#     education_level_id = data.get("education_level_id")

#     if not name or size is None or education_level_id is None:
#         return jsonify({"error": "Missing required fields"}), 400

#     new_class = ClassRoom(
#         school_id=1,
#         name=name,
#         size=size,
#         education_level_id=education_level_id
#     )
#     db.session.add(new_class)
#     db.session.commit()
#     return jsonify(serialize_classroom(new_class)), 201

# @main_main_bp.route("/api/classes/<int:id>", methods=["GET", "PUT", "DELETE"])
# @login_required
# def api_class_detail(id):
#     classroom = ClassRoom.query.get_or_404(id)

#     if request.method == "GET":
#         return jsonify(serialize_classroom(classroom))

#     if request.method == "PUT":
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         classroom.name = data.get("name", classroom.name)
#         classroom.size = data.get("size", classroom.size)
#         classroom.education_level_id = data.get("education_level_id", classroom.education_level_id)
#         db.session.commit()
#         return jsonify(serialize_classroom(classroom))

#     if request.method == "DELETE":
#         db.session.delete(classroom)
#         db.session.commit()
#         return jsonify({"message": "Class deleted"}), 200

# # TIMETABLE SLOTS

# @main_main_bp.route("/api/timetable/class/<int:class_id>", methods=["GET"])
# @login_required
# def api_timetable_class(class_id):
#     slots = Timetable.query.filter_by(class_id=class_id).all()
#     return jsonify([serialize_timetable_slot(s) for s in slots])

# @main_main_bp.route("/api/timetable/teacher/<int:teacher_id>", methods=["GET"])
# @login_required
# def api_timetable_teacher(teacher_id):
#     slots = Timetable.query.filter_by(teacher_id=teacher_id).all()
#     return jsonify([serialize_timetable_slot(s) for s in slots])

# # VALIDATE ASSIGNMENT (example endpoint)

# @main_main_bp.route("/api/validate-assignment", methods=["POST"])
# @login_required
# def api_validate_assignment():
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     try:
#         classroom = ClassRoom.query.get(data["class_id"])
#         teacher = Teacher.query.get(data["teacher_id"])
#         subject = Subject.query.get(data["subject_id"])
#         room = Room.query.get(data["room_id"])
#         day = data["day_of_week"]
#         period = data["period_index"]
#     except KeyError:
#         return jsonify({"error": "Missing required keys"}), 400

#     if not all([classroom, teacher, subject, room]):
#         return jsonify({"error": "Invalid class/teacher/subject/room ID"}), 404

#     # Make sure you have a validate_assignment function defined somewhere
#     error = validate_assignment(classroom, teacher, subject, room, day, period)
#     if error:
#         return jsonify({"valid": False, "error": error}), 200
#     return jsonify({"valid": True, "message": "Assignment valid"}), 200



# @main_main_bp.route("/manage_classsubjects")
# @login_required
# def manage_classsubjects():
#     return render_template("manage_classsubjects.html")

# @main_main_bp.route("/manage_period_templates")
# @login_required
# def manage_period_templates():
#     return render_template("manage_period_templates.html")

# @main_main_bp.route("/admin_generate")
# @login_required
# def admin_generate():
#     return render_template("admin_generate.html")







# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from datetime import time
from .models import User, School, Teacher, EducationLevel, ClassRoom, Subject, SubjectLevelAssignment, TeacherSubjectQualification, ClassSubjectAssignment, Room, Timetable, PeriodTemplate
from .forms import (
    LoginForm, UserForm, SchoolForm, TeacherForm, EducationLevelForm, ClassForm,
    SubjectForm, SubjectLevelAssignmentForm, TeacherSubjectQualificationForm,
    ClassSubjectAssignmentForm, RoomForm, PeriodTemplateForm
)
from .imports import db

main_bp = Blueprint("main", __name__)

# LOGIN/LOGOUT ROUTES

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.admin_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/')
@login_required
def admin_dashboard():
    school = School.query.first()   # or get current user's school
    return render_template('admin_dashboard.html', school=school)

# @main_bp.route("/admin/dashboard")
# def admin_dashboard():
#     return render_template(
#         "admin_dashboard.html",
#         total_teachers=Teacher.query.count(),
#         total_subjects=Subject.query.count(),
#         total_classes=Class.query.count(),
#         total_periods=PeriodTemplate.query.count(),

#         weekly_days=["Mon","Tue","Wed","Thu","Fri"],
#         weekly_load=[20,18,22,21,17],

#         classes=["Std 1","Std 2","Std 3","Std 4","Std 5","Std 6","Std 7"],
#         subjects_count=[7, 8, 8, 9, 9, 10, 12],

#         subject_names=["Math","English","Science","Islamic","Kiswahili"],
#         teachers_per_subject=[4, 5, 3, 6, 4]
#     )

# SCHOOL CRUD
@main_bp.route('/schools')
@login_required
def list_schools():
    schools = School.query.all()
    return render_template('schools/list.html', schools=schools)

@main_bp.route('/schools/add', methods=['GET', 'POST'])
@login_required
def add_school():
    form = SchoolForm()
    if form.validate_on_submit():
        school = School(name=form.name.data)
        db.session.add(school)
        db.session.commit()
        flash("School added successfully", "success")
        return redirect(url_for('main.list_schools'))
    return render_template('schools/add_edit.html', form=form, action="Add")

@main_bp.route('/schools/edit/<int:school_id>', methods=['GET', 'POST'])
@login_required
def edit_school(school_id):
    school = School.query.get_or_404(school_id)
    form = SchoolForm(obj=school)
    if form.validate_on_submit():
        school.name = form.name.data
        db.session.commit()
        flash("School updated successfully", "success")
        return redirect(url_for('main.list_schools'))
    return render_template('schools/add_edit.html', form=form, action="Edit")

@main_bp.route('/schools/delete/<int:school_id>', methods=['POST'])
@login_required
def delete_school(school_id):
    school = School.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    flash("School deleted", "success")
    return redirect(url_for('main.list_schools'))


# TEACHER CRUD
@main_bp.route('/manage_teachers')
@login_required
def manage_teachers():
    teachers = Teacher.query.all()
    return render_template('manage_teachers.html', teachers=teachers)

@main_bp.route('/teachers/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    # populate school choices
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        teacher = Teacher(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            qualification=form.qualification.data,
            max_periods_per_day=form.max_periods_per_day.data or 6,
            max_periods_per_week=form.max_periods_per_week.data or 30,
            school_id=form.school_id.data
        )
        db.session.add(teacher)
        db.session.commit()
        flash("Teacher added successfully", "success")
        return redirect(url_for('main.manage_teachers'))
    return render_template('teachers/add_edit.html', form=form, action="Add")

@main_bp.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm(obj=teacher)
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.email = form.email.data
        teacher.qualification = form.qualification.data
        teacher.max_periods_per_day = form.max_periods_per_day.data or 6
        teacher.max_periods_per_week = form.max_periods_per_week.data or 30
        teacher.school_id = form.school_id.data
        db.session.commit()
        flash("Teacher updated successfully", "success")
        return redirect(url_for('main.manage_teachers'))
    return render_template('teachers/add_edit.html', form=form, action="Edit")

@main_bp.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash("Teacher deleted", "success")
    return redirect(url_for('main.manage_teachers'))


# CLASS CRUD
@main_bp.route('/manage_classes')
@login_required
def manage_classes():
    classes = ClassRoom.query.all()
    return render_template('manage_classes.html', classes=classes)

@main_bp.route('/classes/add', methods=['GET', 'POST'])
@login_required
def add_class():
    form = ClassForm()
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    form.education_level_id.choices = [(el.id, el.name) for el in EducationLevel.query.order_by(EducationLevel.name).all()]
    form.assigned_teacher_id.choices = [(0, 'None')] + [(t.id, t.full_name) for t in Teacher.query.order_by(Teacher.first_name).all()]
    if form.validate_on_submit():
        assigned_teacher_id = form.assigned_teacher_id.data if form.assigned_teacher_id.data != 0 else None
        classroom = ClassRoom(
            name=form.name.data,
            school_id=form.school_id.data,
            education_level_id=form.education_level_id.data,
            assigned_teacher_id=assigned_teacher_id
        )
        db.session.add(classroom)
        db.session.commit()
        flash("Class added successfully", "success")
        return redirect(url_for('main.manage_classes'))
    return render_template('classes/add_edit.html', form=form, action="Add")

@main_bp.route('/classes/edit/<int:class_id>', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    classroom = ClassRoom.query.get_or_404(class_id)
    form = ClassForm(obj=classroom)
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    form.education_level_id.choices = [(el.id, el.name) for el in EducationLevel.query.order_by(EducationLevel.name).all()]
    form.assigned_teacher_id.choices = [(0, 'None')] + [(t.id, t.full_name) for t in Teacher.query.order_by(Teacher.first_name).all()]
    if form.validate_on_submit():
        assigned_teacher_id = form.assigned_teacher_id.data if form.assigned_teacher_id.data != 0 else None
        classroom.name = form.name.data
        classroom.school_id = form.school_id.data
        classroom.education_level_id = form.education_level_id.data
        classroom.assigned_teacher_id = assigned_teacher_id
        db.session.commit()
        flash("Class updated successfully", "success")
        return redirect(url_for('main.manage_classes'))
    return render_template('classes/add_edit.html', form=form, action="Edit")

@main_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    classroom = ClassRoom.query.get_or_404(class_id)
    db.session.delete(classroom)
    db.session.commit()
    flash("Class deleted", "success")
    return redirect(url_for('main.manage_classes'))


# SUBJECT CRUD
@main_bp.route('/manage_subjects')
@login_required
def manage_subjects():
    subjects = Subject.query.all()
    return render_template('manage_subjects.html', subjects=subjects)

@main_bp.route('/subjects/add', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        subject = Subject(
            code=form.code.data,
            name=form.name.data,
            subject_type=form.subject_type.data.lower(),
            periods_per_week=form.periods_per_week.data,
            school_id=form.school_id.data
        )
        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully", "success")
        return redirect(url_for('main.manage_subjects'))
    return render_template('subjects/add_edit.html', form=form, action="Add")

@main_bp.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        subject.code = form.code.data
        subject.name = form.name.data
        subject.subject_type = form.subject_type.data.lower()
        subject.periods_per_week = form.periods_per_week.data
        subject.school_id = form.school_id.data
        db.session.commit()
        flash("Subject updated successfully", "success")
        return redirect(url_for('main.manage_subjects'))
    return render_template('subjects/add_edit.html', form=form, action="Edit")

@main_bp.route('/subjects/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted", "success")
    return redirect(url_for('main.manage_subjects'))


# ROOM CRUD
@main_bp.route('/manage_rooms')
@login_required
def manage_rooms():
    rooms = Room.query.all()
    return render_template('manage_rooms.html', rooms=rooms)

@main_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    form = RoomForm()
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        room = Room(
            name=form.name.data,
            capacity=form.capacity.data,
            school_id=form.school_id.data
        )
        db.session.add(room)
        db.session.commit()
        flash("Room added successfully", "success")
        return redirect(url_for('main.manage_rooms'))
    return render_template('rooms/add_edit.html', form=form, action="Add")

@main_bp.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        room.name = form.name.data
        room.capacity = form.capacity.data
        room.school_id = form.school_id.data
        db.session.commit()
        flash("Room updated successfully", "success")
        return redirect(url_for('main.manage_rooms'))
    return render_template('rooms/add_edit.html', form=form, action="Edit")

@main_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted", "success")
    return redirect(url_for('main.manage_rooms'))


# PERIOD TEMPLATE CRUD
@main_bp.route('/manage_period_templates')
@login_required
def manage_period_templates():
    templates = PeriodTemplate.query.all()
    return render_template('period_templates/list.html', templates=templates)

@main_bp.route('/period-templates')
@login_required
def list_period_templates():
    templates = PeriodTemplate.query.all()
    return render_template('manage_period_templates.html', templates=templates)

@main_bp.route('/period_templates/add', methods=['GET', 'POST'])
@login_required
def add_period_template():
    form = PeriodTemplateForm()
    if form.validate_on_submit():
        template = PeriodTemplate(
            name=form.name.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        db.session.add(template)
        db.session.commit()
        flash("Period template added successfully", "success")
        return redirect(url_for('main.manage_period_templates'))
    return render_template('period_templates/add_edit.html', form=form, action="Add")

@main_bp.route('/period_templates/edit/<int:template_id>', methods=['GET', 'POST'])
@login_required
def edit_period_template(template_id):
    template = PeriodTemplate.query.get_or_404(template_id)
    form = PeriodTemplateForm(obj=template)
    if form.validate_on_submit():
        template.name = form.name.data
        template.start_time = form.start_time.data
        template.end_time = form.end_time.data
        db.session.commit()
        flash("Period template updated", "success")
        return redirect(url_for('main.manage_period_templates'))
    return render_template('period_templates/add_edit.html', form=form, action="Edit")

@main_bp.route('/period_templates/delete/<int:template_id>', methods=['POST'])
@login_required
def delete_period_template(template_id):
    template = PeriodTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash("Period template deleted", "success")
    return redirect(url_for('main.manage_period_templates'))

@main_bp.route('/timetables')
@login_required
def list_timetables():
    timetables = Timetable.query.order_by(Timetable.day_of_week, Timetable.start_time).all()
    return render_template('timetables/list.html', timetables=timetables)

@main_bp.route('/timetables/add', methods=['GET', 'POST'])
@login_required
def add_timetable():
    form = TimetableEntryForm()
    # populate choices
    form.class_subject_assignment_id.choices = [
        (csa.id, f"{csa.classroom.name} - {csa.subject.name} - {csa.teacher.full_name}") for csa in ClassSubjectAssignment.query.all()
    ]
    form.room_id.choices = [(r.id, r.name) for r in Room.query.all()]

    if form.validate_on_submit():
        timetable_entry = Timetable(
            class_subject_assignment_id=form.class_subject_assignment_id.data,
            room_id=form.room_id.data,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        db.session.add(timetable_entry)
        db.session.commit()
        flash("Timetable entry added", "success")
        return redirect(url_for('main.list_timetables'))

    return render_template('timetables/add_edit.html', form=form, action="Add")


@main_bp.route('/timetables/edit/<int:timetable_id>', methods=['GET', 'POST'])
@login_required
def edit_timetable(timetable_id):
    timetable = Timetable.query.get_or_404(timetable_id)
    form = TimetableEntryForm(obj=timetable)
    form.class_subject_assignment_id.choices = [
        (csa.id, f"{csa.classroom.name} - {csa.subject.name} - {csa.teacher.full_name}") for csa in ClassSubjectAssignment.query.all()
    ]
    form.room_id.choices = [(r.id, r.name) for r in Room.query.all()]

    if form.validate_on_submit():
        timetable.class_subject_assignment_id = form.class_subject_assignment_id.data
        timetable.room_id = form.room_id.data
        timetable.day_of_week = form.day_of_week.data
        timetable.start_time = form.start_time.data
        timetable.end_time = form.end_time.data
        db.session.commit()
        flash("Timetable entry updated", "success")
        return redirect(url_for('main.list_timetables'))
    return render_template('timetables/add_edit.html', form=form, action="Edit")

@main_bp.route('/timetables/delete/<int:timetable_id>', methods=['POST'])
@login_required
def delete_timetable(timetable_id):
    timetable = Timetable.query.get_or_404(timetable_id)
    db.session.delete(timetable)
    db.session.commit()
    flash("Timetable entry deleted", "success")
    return redirect(url_for('main.list_timetables'))


