from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------- User Model ------------------
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin', 'teacher'
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

    # Relationships
    leave_requests = db.relationship('LeaveRequest', back_populates='requesting_user', lazy='dynamic')
    teaching_slots = db.relationship('TeachingSlot', back_populates='teacher', lazy=True)

    # Password Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login Required Properties and Methods
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Role Helper Methods
    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    # Property for Full Name
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ---------------- Department Model ------------------
class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    teachers = db.relationship('User', backref='department', lazy='dynamic')


# ---------------- Lesson Model ------------------
class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key=True)
    year_group = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

    teaching_slots = db.relationship('TeachingSlot', back_populates='lesson', lazy=True)


# ---------------- TeachingSlot Model ------------------
class TeachingSlot(db.Model):
    __tablename__ = 'teaching_slot'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_request_id = db.Column(db.Integer, db.ForeignKey('leave_request.id', ondelete='SET NULL'), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)
    period_number = db.Column(db.Integer, nullable=False)

    lesson = db.relationship('Lesson', back_populates='teaching_slots')
    teacher = db.relationship('User', back_populates='teaching_slots')
    leave_request = db.relationship('LeaveRequest', back_populates='teaching_slots')


# ---------------- LeaveRequest Model ------------------
class LeaveRequest(db.Model):
    __tablename__ = 'leave_request'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)  # 'pending', 'approved', 'declined'
    comment = db.Column(db.Text, nullable=True)

    requesting_user = db.relationship('User', back_populates='leave_requests')
    teaching_slots = db.relationship('TeachingSlot', back_populates='leave_request', lazy=True)


# ---------------- CoverAssignment Model ------------------
class CoverAssignment(db.Model):
    __tablename__ = 'cover_assignment'
    id = db.Column(db.Integer, primary_key=True)
    absent_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    covering_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teaching_slot_id = db.Column(db.Integer, db.ForeignKey('teaching_slot.id'), nullable=False)

    absent_teacher = db.relationship('User', foreign_keys=[absent_teacher_id], backref='absences')
    covering_teacher = db.relationship('User', foreign_keys=[covering_teacher_id], backref='covers')
    teaching_slot = db.relationship('TeachingSlot', backref='cover_assignment')

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
