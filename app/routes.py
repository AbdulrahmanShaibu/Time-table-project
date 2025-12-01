
# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from datetime import time
from .models import User, School, Teacher, EducationLevel, ClassRoom, Subject, SubjectLevelAssignment, TeacherSubjectQualification, ClassSubjectAssignment, Room, Timetable, PeriodTemplate
from .forms import (
    LoginForm, UserForm, SchoolForm, TeacherForm, EducationLevelForm, ClassForm,
    SubjectForm, SubjectLevelAssignmentForm, TeacherSubjectQualificationForm,
    ClassSubjectAssignmentForm, RoomForm, PeriodTemplateForm,TimetableEntryForm
)
from .imports import db
from flask import send_file
from io import BytesIO

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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

# @main_bp.route('/')
# @login_required
# def admin_dashboard():
#     school = School.query.first()   # or get current user's school
#     return render_template('admin_dashboard.html', school=school)

@main_bp.route('/')
@login_required
def admin_dashboard():
    school = School.query.first()   # or get current user's school
    weekly_days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    weekly_load = [5, 7, 6, 8, 7]

    classes = [c.name for c in ClassRoom.query.all()]
    
    # Count subjects per class (assuming a relationship ClassRoom.subjects)
    subjects_count = []
    for c in ClassRoom.query.all():
        if hasattr(c, 'subjects'):
            subjects_count.append(c.subjects.count())
        else:
            subjects_count.append(0)  # fallback if no relationship

    subject_names = [s.name for s in Subject.query.all()]
    
    # Count teachers per subject (assuming Subject.teachers relationship)
    teachers_per_subject = []
    for s in Subject.query.all():
        if hasattr(s, 'teachers'):
            teachers_per_subject.append(s.teachers.count())
        else:
            teachers_per_subject.append(0)

    # Total counts
    total_teachers = Teacher.query.count()
    total_subjects = Subject.query.count()
    total_classes = ClassRoom.query.count()
    total_periods = Timetable.query.count()

    return render_template('admin_dashboard.html',
                           total_teachers=total_teachers,
                           total_subjects=total_subjects,
                           total_classes=total_classes,
                           total_periods=total_periods,
                           weekly_days=weekly_days,
                           weekly_load=weekly_load,
                           classes=classes,
                           subjects_count=subjects_count,
                           subject_names=subject_names,
                           teachers_per_subject=teachers_per_subject)


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
            max_periods_per_day=form.max_periods_per_day.data if form.max_periods_per_day.data else 6,
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

@main_bp.route('/teachers/download_all_pdf', methods=['GET'])
@login_required
def download_all_teachers_pdf():

    from io import BytesIO
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from flask import current_app, send_file
    import os

    teachers = Teacher.query.all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    # ----------------------------------------------------------
    # 1. Insert Logo (Centered)
    # ----------------------------------------------------------
    logo_path = os.path.join(current_app.root_path, "static", "images", "realistic-school.png")

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 8))

    # ----------------------------------------------------------
    # 2. Add Title
    # ----------------------------------------------------------
    title = Paragraph("<b>All Teachers – Professional Report</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # ----------------------------------------------------------
    # 3. Prepare Table Data
    # ----------------------------------------------------------
    data = [["ID", "Name", "Email", "Qualification", "School", "Max/Day", "Max/Week"]]

    for t in teachers:
        data.append([
            t.id,
            f"{t.first_name} {t.last_name}",
            t.email,
            t.qualification,
            t.school.name if t.school else "N/A",
            t.max_periods_per_day,
            t.max_periods_per_week
        ])

    # ----------------------------------------------------------
    # 4. Table Styling (Academic Look)
    # ----------------------------------------------------------
    table = Table(data, repeatRows=1)

    # Academic color palette (soft blue + grey)
    header_color = colors.HexColor("#1E3A8A")      # deep academic blue
    header_text = colors.white
    row_alt_1 = colors.HexColor("#EDF2F7")         # light grey/blue
    row_alt_2 = colors.white

    style = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), header_text),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Body cells
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

        # Table grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]

    # Alternating row colors
    for i in range(1, len(data)):
        bg = row_alt_1 if i % 2 == 0 else row_alt_2
        style.append(('BACKGROUND', (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style))

    elements.append(table)

    # ----------------------------------------------------------
    # 5. Build PDF
    # ----------------------------------------------------------
    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="all_teachers.pdf",
        mimetype="application/pdf"
    )

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
            code=form.code.data.strip(),
            name=form.name.data.strip(),
            subject_type=form.subject_type.data.strip().lower(),
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
        subject.code = form.code.data.strip()
        subject.name = form.name.data.strip()
        subject.subject_type = form.subject_type.data.strip().lower()
        subject.school_id = form.school_id.data

        db.session.commit()
        flash("Subject updated successfully", "success")
        return redirect(url_for('main.manage_subjects'))

    return render_template('subjects/add_edit.html', form=form, action="Update")


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

# @main_bp.route('/timetables')
# @login_required
# def list_timetables():
#     timetables = Timetable.query.order_by(Timetable.day_of_week, Timetable.start_time).all()
#     return render_template('timetables/list.html', timetables=timetables)

from collections import defaultdict
from datetime import time

@main_bp.route('/timetables')
@login_required
def list_timetables():
    from sqlalchemy.orm import joinedload

    timetables = (
        Timetable.query
        .options(
            joinedload(Timetable.class_subject_assignment).joinedload(ClassSubjectAssignment.classroom),
            joinedload(Timetable.class_subject_assignment).joinedload(ClassSubjectAssignment.subject),
            joinedload(Timetable.class_subject_assignment).joinedload(ClassSubjectAssignment.teacher),
            joinedload(Timetable.room)
        )
        .order_by(Timetable.day_of_week, Timetable.start_time)
        .all()
    )

    timetable_dict = defaultdict(list)
    for t in timetables:
        timetable_dict[(t.day_of_week, t.start_time)].append(t)

    period_times = {
        1: time(8, 0),
        2: time(8, 40),
        3: time(9, 20),
        4: time(10, 0),
        5: time(10, 40),
        6: time(11, 20),
        7: time(12, 0),
        8: time(12, 40),
        9: time(13, 20),
        10: time(14, 0),
    }

    return render_template('timetables/list.html', timetable_dict=timetable_dict, period_times=period_times)


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



# counting logic
from flask import jsonify

@main_bp.route('/api/counts')
@login_required
def get_counts():
    total_teachers = Teacher.query.count()
    total_subjects = Subject.query.count()
    total_classes = ClassRoom.query.count()
    total_periods = Timetable.query.count()

    return jsonify({
        "total_teachers": total_teachers,
        "total_subjects": total_subjects,
        "total_classes": total_classes,
        "total_periods": total_periods,
    })

@main_bp.route('/admin/overview')
@login_required
def admin_overview():
    total_teachers = Teacher.query.count()
    total_subjects = Subject.query.count()
    total_classes = ClassRoom.query.count()
    total_periods = Timetable.query.count()

    # Prepare data for charts (mock or query real data as needed)
    weekly_days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    weekly_load = [5, 7, 6, 8, 7]  # Example data for weekly allocation load

    classes = [c.name for c in ClassRoom.query.all()]
    subjects_count = []
    for c in ClassRoom.query.all():
        count = c.subjects.count() if hasattr(c, 'subjects') else 3  # Example fallback
        subjects_count.append(count)

    subject_names = [s.name for s in Subject.query.all()]
    teachers_per_subject = []
    for s in Subject.query.all():
        count = s.teachers.count() if hasattr(s, 'teachers') else 2  # Example fallback
        teachers_per_subject.append(count)

    return render_template('admin_dashboard.html',
                           total_teachers=total_teachers,
                           total_subjects=total_subjects,
                           total_classes=total_classes,
                           total_periods=total_periods,
                           weekly_days=weekly_days,
                           weekly_load=weekly_load,
                           classes=classes,
                           subjects_count=subjects_count,
                           subject_names=subject_names,
                           teachers_per_subject=teachers_per_subject)

@main_bp.route('/manage_class_subject_assignment')
@login_required
def manage_class_subject_assignment():
     class_subject_assignments = (
        ClassSubjectAssignment.query
        .options(
            joinedload(ClassSubjectAssignment.classroom),
            joinedload(ClassSubjectAssignment.subject),
            joinedload(ClassSubjectAssignment.teacher)
        )
        .all()
    )

     return render_template(
        'manage_class_subject_assignment.html',
        class_subject_assignments=class_subject_assignments
    )


# @main_bp.route('/add_teacher_class_subject', methods=['GET', 'POST'])
# @login_required
# def add_teacher_class_subject():
#     classes = ClassRoom.query.all()
#     subjects = Subject.query.all()
#     teachers = Teacher.query.all()

#     if request.method == 'POST':
#         class_id = request.form['class_id']
#         subject_id = request.form['subject_id']
#         teacher_id = request.form['teacher_id']

#         new_assignment = ClassSubjectAssignment(
#             class_id=class_id,
#             subject_id=subject_id,
#             teacher_id=teacher_id
#         )
#         db.session.add(new_assignment)
#         db.session.commit()

#         flash('Assignment created successfully', 'success')
#         return redirect(url_for('main.manage_class_subject_assignment'))

#     return render_template(
#         'add_teacher_class_subject.html',
#         classes=classes,
#         subjects=subjects,
#         teachers=teachers
#     )

@main_bp.route("/add_teacher_class_subject", methods=["GET", "POST"])
def add_teacher_class_subject():
    form = ClassSubjectAssignmentForm()
    # populate select fields
    classes = ClassRoom.query.order_by(ClassRoom.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    teachers = Teacher.query.order_by(Teacher.first_name).all()

    form.class_id.choices = [(c.id, c.name) for c in classes]
    form.subject_id.choices = [(s.id, f"{s.name} ({s.code})") for s in subjects]
    form.teacher_id.choices = [(t.id, t.full_name) for t in teachers]

    if form.validate_on_submit():
        # prevent duplicates: same class + subject
        existing = ClassSubjectAssignment.query.filter_by(class_id=form.class_id.data, subject_id=form.subject_id.data).first()
        if existing:
            flash("That class already has this subject assigned. Edit the existing assignment instead.", "warning")
            return redirect(url_for("main.manage_class_subject_assignment"))

        assignment = ClassSubjectAssignment(
            class_id=form.class_id.data,
            subject_id=form.subject_id.data,
            teacher_id=form.teacher_id.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment added.", "success")
        return redirect(url_for("main.manage_class_subject_assignment"))

    return render_template("assignment_form.html", form=form, title="Add Assignment")


@main_bp.route('/edit-class-subject-assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_class_subject_assignment(assignment_id):
    assignment = ClassSubjectAssignment.query.get_or_404(assignment_id)

    classes = ClassRoom.query.all()
    subjects = Subject.query.all()
    teachers = Teacher.query.all()

    if request.method == "POST":
        assignment.class_id = request.form['class_id']
        assignment.subject_id = request.form['subject_id']
        assignment.teacher_id = request.form['teacher_id']

        db.session.commit()
        flash("Assignment updated successfully!", "success")
        return redirect(url_for('main.list_class_subject_assignments'))

    return render_template('edit_class_subject_assignment.html',
                           assignment=assignment,
                           classes=classes,
                           subjects=subjects,
                           teachers=teachers)


@main_bp.route('/delete-class-subject-assignment/<int:assignment_id>', methods=['POST'])
@login_required
def delete_class_subject_assignment(assignment_id):
    assignment = ClassSubjectAssignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()

    flash("Assignment deleted!", "success")
    return redirect(url_for('main.list_class_subject_assignments'))

from sqlalchemy.orm import joinedload
@main_bp.route('/class-subject-assignments')
@login_required
def list_class_subject_assignments():
    # assignments = ClassSubjectAssignment.query.all()
     # load relationships to prevent N+1 queries
    assignments = (
        ClassSubjectAssignment.query
        .options(
            joinedload(ClassSubjectAssignment.classroom),
            joinedload(ClassSubjectAssignment.subject),
            joinedload(ClassSubjectAssignment.teacher)
        )
        .order_by(ClassSubjectAssignment.id)
        .all()
    )
    return render_template('list_class_subject_assignments.html',
                           class_subject_assignments=assignments)
