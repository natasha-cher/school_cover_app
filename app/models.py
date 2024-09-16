# models.py
from app import db


class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=True)

    # Relationship: A teacher can have multiple leave requests
    requests = db.relationship('LeaveRequest', backref='teacher', lazy=True)

    # Relationship: A teacher can have multiple schedules
    schedules = db.relationship('Schedule', backref='teacher', lazy=True)


class Class(db.Model):
    __tablename__ = 'class'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year_group = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

    # Relationship: A class can have many schedules
    schedules = db.relationship('Schedule', backref='class', lazy=True)


class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    period_number = db.Column(db.Integer, nullable=False)


class LeaveRequest(db.Model):
    __tablename__ = 'leave_request'

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.Text, nullable=True)

    # Foreign key
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)


class CoverAssignment(db.Model):
    __tablename__ = 'cover_assignment'

    id = db.Column(db.Integer, primary_key=True)

    absent_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    covering_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Foreign key
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)

    # Relationships to access teachers easily
    absent_teacher = db.relationship('Teacher', foreign_keys=[absent_teacher_id], backref='absences')
    covering_teacher = db.relationship('Teacher', foreign_keys=[covering_teacher_id], backref='covers')