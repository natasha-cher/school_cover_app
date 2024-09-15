from app import db


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.String(64))
    total_weekly_hours = db.Column(db.Integer, default=0)
    cover_history = db.Column(db.Integer, default=0)
    schedules = db.relationship('TeachingSchedule', backref='teacher', lazy=True)


class TeachingSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day_of_week = db.Column(db.String(10))
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_free_period = db.Column(db.Boolean, default=False)


class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')


class CoverAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    absent_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    covering_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)