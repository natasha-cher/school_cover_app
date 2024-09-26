from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField, PasswordField, StringField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class LeaveRequestForm(FlaskForm):
    teacher_id = SelectField('Teacher', validators=[DataRequired()])
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


class CoverAssignmentForm(FlaskForm):
    cover_teacher_id = SelectField('Select Cover Teacher', validators=[DataRequired()])
    submit = SubmitField('Assign Cover')


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



