from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .imports import db


# ============================
# USER MODEL
# ============================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum('admin', 'scheduler', name='user_roles'), default='admin')
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ============================
# SCHOOL MODEL
# ============================
class School(db.Model):
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    education_levels = db.relationship("EducationLevel", back_populates="school", cascade="all, delete-orphan")
    subjects = db.relationship("Subject", back_populates="school", cascade="all, delete-orphan")
    teachers = db.relationship("Teacher", back_populates="school", cascade="all, delete-orphan")
    classes = db.relationship("ClassRoom", back_populates="school", cascade="all, delete-orphan")
    rooms = db.relationship("Room", back_populates="school", cascade="all, delete-orphan")


# ============================
# EDUCATION LEVEL
# ============================
class EducationLevel(db.Model):
    __tablename__ = "education_levels"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level_type = db.Column(db.Enum('nursery', 'lower_primary', 'upper_primary', 'secondary', name='level_types'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    school = db.relationship("School", back_populates="education_levels")
    subjects_levels = db.relationship("SubjectLevelAssignment", back_populates="education_level", cascade="all, delete-orphan")
    classes = db.relationship("ClassRoom", back_populates="education_level", cascade="all, delete-orphan")


# ============================
# SUBJECT MODEL
# ============================
class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    subject_type = db.Column(db.Enum('core', 'elective', 'practical', 'lab', name='subject_types'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    school = db.relationship("School", back_populates="subjects")
    subject_levels = db.relationship("SubjectLevelAssignment", back_populates="subject", cascade="all, delete-orphan")
    teacher_qualifications = db.relationship("TeacherSubjectQualification", back_populates="subject", cascade="all, delete-orphan")
    class_subject_assignments = db.relationship("ClassSubjectAssignment", back_populates="subject", cascade="all, delete-orphan")


# ============================
# SUBJECT ↔ EDUCATION LEVEL
# ============================
class SubjectLevelAssignment(db.Model):
    __tablename__ = "subject_level_assignments"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    education_level_id = db.Column(db.Integer, db.ForeignKey("education_levels.id", ondelete="CASCADE"), nullable=False)
    periods_per_week = db.Column(db.Integer, nullable=False)

    subject = db.relationship("Subject", back_populates="subject_levels")
    education_level = db.relationship("EducationLevel", back_populates="subjects_levels")


# ============================
# TEACHER MODEL
# ============================
class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    qualification = db.Column(db.Enum('Nursery', 'Lower primary', 'Upper primary', 'Secondary', name='teacher_qualification'), nullable=False)
    max_periods_per_day = db.Column(db.Integer, default=6)
    max_periods_per_week = db.Column(db.Integer, default=30)

    school = db.relationship("School", back_populates="teachers")
    teacher_subject_qualifications = db.relationship("TeacherSubjectQualification", back_populates="teacher", cascade="all, delete-orphan")
    class_subject_assignments = db.relationship("ClassSubjectAssignment", back_populates="teacher", cascade="all, delete-orphan")
    assigned_classes = db.relationship("ClassRoom", back_populates="assigned_teacher")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ============================
# TEACHER ↔ SUBJECT QUALIFICATION
# ============================
class TeacherSubjectQualification(db.Model):
    __tablename__ = "teacher_subject_qualifications"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    teacher = db.relationship("Teacher", back_populates="teacher_subject_qualifications")
    subject = db.relationship("Subject", back_populates="teacher_qualifications")


# ============================
# CLASS MODEL
# ============================
class ClassRoom(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    education_level_id = db.Column(db.Integer, db.ForeignKey("education_levels.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    assigned_teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)

    school = db.relationship("School", back_populates="classes")
    education_level = db.relationship("EducationLevel", back_populates="classes")
    assigned_teacher = db.relationship("Teacher", back_populates="assigned_classes")
    class_subject_assignments = db.relationship("ClassSubjectAssignment", back_populates="classroom", cascade="all, delete-orphan")


# ============================
# ROOM MODEL
# ============================
class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer)

    school = db.relationship("School", back_populates="rooms")
    timetables = db.relationship("Timetable", back_populates="room", cascade="all, delete-orphan")


# ============================
# CLASS ↔ SUBJECT ↔ TEACHER
# ============================
class ClassSubjectAssignment(db.Model):
    __tablename__ = "class_subject_assignments"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    classroom = db.relationship("ClassRoom", back_populates="class_subject_assignments")
    subject = db.relationship("Subject", back_populates="class_subject_assignments")
    teacher = db.relationship("Teacher", back_populates="class_subject_assignments")
    timetables = db.relationship("Timetable", back_populates="class_subject_assignment", cascade="all, delete-orphan")


# ============================
# TIMETABLE MODEL
# ============================
class Timetable(db.Model):
    __tablename__ = "timetables"

    id = db.Column(db.Integer, primary_key=True)
    class_subject_assignment_id = db.Column(db.Integer, db.ForeignKey("class_subject_assignments.id", ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    day_of_week = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', name='days_of_week'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    class_subject_assignment = db.relationship("ClassSubjectAssignment", back_populates="timetables")
    room = db.relationship("Room", back_populates="timetables")


# ============================
# PERIOD TEMPLATE
# ============================
class PeriodTemplate(db.Model):
    __tablename__ = "period_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
