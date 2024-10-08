from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField, PasswordField, StringField, HiddenField, \
    BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User, Department
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
        self.teacher_name.data = current_user.name
        self.teacher_id.data = current_user.id


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
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=100, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])

    # Department select field with a default choice
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()],
                                choices=[(0, '-- Select Department --')])  # Add default choice

    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        # Populate department choices
        self.department_id.choices += [(dept.id, dept.name) for dept in Department.query.all()]

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
