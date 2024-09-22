from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

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