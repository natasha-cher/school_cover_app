from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin', 'teacher'
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

    # Relationship: A user can have multiple leave requests
    leave_requests = db.relationship('LeaveRequest', backref='user', lazy=True)

    # Method to set a password, which hashes it
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to verify the password by comparing hashes
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login required methods (inherited from UserMixin)
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

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship: A department can have multiple users (teachers)
    teachers = db.relationship('User', backref='department', lazy=True)


class Lesson(db.Model):
    __tablename__ = 'lesson'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year_group = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

    # Relationship: A lesson can have many teaching slots
    teaching_slots = db.relationship('TeachingSlot', backref='lesson', lazy=True)


class TeachingSlot(db.Model):
    __tablename__ = 'teaching_slot'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Referring to User

    day_of_week = db.Column(db.Integer, nullable=False)
    period_number = db.Column(db.Integer, nullable=False)

    # Relationship back to the user
    teacher = db.relationship('User', backref='teaching_slots')


class LeaveRequest(db.Model):
    __tablename__ = 'leave_request'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)  # e.g., 'pending', 'approved', 'declined'
    comment = db.Column(db.Text, nullable=True)

    # Relationship to the User model
    user = db.relationship('User', backref='leave_requests')


class CoverAssignment(db.Model):
    __tablename__ = 'cover_assignment'

    id = db.Column(db.Integer, primary_key=True)
    absent_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    covering_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    teaching_slot_id = db.Column(db.Integer, db.ForeignKey('teaching_slot.id'), nullable=False)

    # Relationships for cover assignments
    absent_teacher = db.relationship('User', foreign_keys=[absent_teacher_id], backref='absences')
    covering_teacher = db.relationship('User', foreign_keys=[covering_teacher_id], backref='covers')