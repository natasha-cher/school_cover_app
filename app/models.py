# models.py
from app import db
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

    # Relationship: A teacher can have multiple leave requests
    requests = db.relationship('LeaveRequest', backref='teacher', lazy=True)

    # Relationship: A teacher can have multiple TeachingSlots
    teaching_slots = db.relationship('TeachingSlot', backref='teacher', lazy=True)


class Lesson(db.Model):
    __tablename__ = 'lesson'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year_group = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

    # Relationship: A lesson can have many TeachingSlots
    TeachingSlots = db.relationship('TeachingSlot', backref='lesson', lazy=True)


class TeachingSlot(db.Model):
    __tablename__ = 'TeachingSlot'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
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
    teaching_slot_id = db.Column(db.Integer, db.ForeignKey('TeachingSlot.id'), nullable=False)

    # Relationships to access teachers easily
    absent_teacher = db.relationship('Teacher', foreign_keys=[absent_teacher_id], backref='absences')
    covering_teacher = db.relationship('Teacher', foreign_keys=[covering_teacher_id], backref='covers')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Method to set a password, which hashes it
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to verify the password by comparing hashes
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login required methods (inherited from UserMixin)
    @property
    def is_active(self):
        # You can add logic to check if a user is active, or just return True
        return True

    @property
    def is_authenticated(self):
        # Always return True, as this is handled by Flask-Login
        return True

    @property
    def is_anonymous(self):
        # Anonymous users are not authenticated, so return False
        return False

    def get_id(self):
        # Flask-Login requires a method that returns the user's ID as a string
        return str(self.id)

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'
