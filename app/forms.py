from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo


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


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


