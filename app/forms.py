from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField, PasswordField, StringField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User
from flask_login import current_user


# Leave Request Form
class LeaveRequestForm(FlaskForm):
    teacher_name = StringField('Teacher Name', validators=[DataRequired()], render_kw={'readonly': True})
    teacher_id = HiddenField('Teacher ID')  # Hidden field to store the teacher's ID

    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    reason = SelectField('Select Reason', choices=[
        ('', '-- Select Reason --'),
        ('Personal', 'Personal'),
        ('Illness', 'Illness'),
        ('Professional Development', 'Professional Development'),
        ('Field Trip', 'Field Trip')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Leave Request')

    # Set teacher name and ID based on the logged-in user
    def set_teacher_info(self):
        self.teacher_name.data = current_user.name  # Display the current user's name
        self.teacher_id.data = current_user.id  # Store the current user's ID


# Cover Assignment Form
class CoverAssignmentForm(FlaskForm):
    cover_teacher_id = SelectField('Select Cover Teacher', validators=[DataRequired()])
    submit = SubmitField('Assign Cover')

    # Set choices for cover teachers
    def set_cover_teacher_choices(self):
        self.cover_teacher_id.choices = [(teacher.id, teacher.email) for teacher in
                                         User.query.filter_by(role='teacher').all()]


# Sign Up Form
class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=100, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    department = StringField('Department', validators=[DataRequired(), Length(min=2, max=100)])  # New field
    submit = SubmitField('Sign Up')

    # Custom validator to check if the email already exists
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please choose a different one.')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')