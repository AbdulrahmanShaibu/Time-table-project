# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, SelectField, BooleanField, TimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")

class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[Optional()])
    role = SelectField("Role", choices=[("admin", "Admin"), ("scheduler", "Scheduler")], validators=[DataRequired()])
    school_id = SelectField("School", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class TeacherForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Last name", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=255)])
    qualification = SelectField(
        "Qualification",
        choices=[('Nursery', 'Nursery'), ('Lower primary', 'Lower primary'), ('Upper primary', 'Upper primary'), ('Secondary', 'Secondary')],
        validators=[DataRequired()]
    )
    max_periods_per_day = IntegerField("Max periods/day", validators=[Optional(), NumberRange(min=1)])
    max_periods_per_week = IntegerField("Max periods/week", validators=[Optional(), NumberRange(min=1)])
    school_id = SelectField("School", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

class SchoolForm(FlaskForm):
    name = StringField("School name", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Save")

class EducationLevelForm(FlaskForm):
    name = StringField("Level name", validators=[DataRequired(), Length(max=100)])
    level_type = SelectField(
        "Level type",
        choices=[('nursery', 'Nursery'), ('lower_primary', 'Lower Primary'), ('upper_primary', 'Upper Primary'), ('secondary', 'Secondary')],
        validators=[DataRequired()]
    )
    school_id = SelectField("School", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class ClassForm(FlaskForm):
    name = StringField("Class name", validators=[DataRequired(), Length(max=50)])
    education_level_id = SelectField("Education Level", coerce=int, validators=[DataRequired()])
    assigned_teacher_id = SelectField("Assigned Teacher", coerce=int, validators=[Optional()])
    school_id = SelectField("School", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class SubjectForm(FlaskForm):
    code = StringField("Code", validators=[DataRequired(), Length(max=10)])
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    subject_type = SelectField(
        "Subject Type",
        choices=[('core', 'Core'), ('elective', 'Elective'), ('practical', 'Practical'), ('lab', 'Lab')],
        validators=[DataRequired()]
    )
    school_id = SelectField("School", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class SubjectLevelAssignmentForm(FlaskForm):
    subject_id = SelectField("Subject", coerce=int, validators=[DataRequired()])
    education_level_id = SelectField("Education Level", coerce=int, validators=[DataRequired()])
    periods_per_week = IntegerField("Periods per Week", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Save")

class TeacherSubjectQualificationForm(FlaskForm):
    teacher_id = SelectField("Teacher", coerce=int, validators=[DataRequired()])
    subject_id = SelectField("Subject", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

class ClassSubjectAssignmentForm(FlaskForm):
    class_id = SelectField("Class", coerce=int, validators=[DataRequired()])
    subject_id = SelectField("Subject", coerce=int, validators=[DataRequired()])
    teacher_id = SelectField("Teacher", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

class RoomForm(FlaskForm):
    name = StringField("Room Name", validators=[DataRequired(), Length(max=50)])
    capacity = IntegerField("Capacity", validators=[Optional(), NumberRange(min=0)])
    school_id = SelectField("School", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class PeriodTemplateForm(FlaskForm):
    name = StringField("Template name", validators=[DataRequired(), Length(max=100)])
    start_time = TimeField("Start time", validators=[DataRequired()])
    end_time = TimeField("End time", validators=[DataRequired()])
    submit = SubmitField("Save")

class TimetableEntryForm(FlaskForm):
    class_subject_assignment_id = SelectField("Class Subject Assignment", coerce=int, validators=[DataRequired()])
    room_id = SelectField("Room", coerce=int, validators=[DataRequired()])
    day_of_week = SelectField("Day of Week", choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'), ('Friday','Friday')], validators=[DataRequired()])
    start_time = TimeField("Start time", validators=[DataRequired()])
    end_time = TimeField("End time", validators=[DataRequired()])
    submit = SubmitField("Save")
