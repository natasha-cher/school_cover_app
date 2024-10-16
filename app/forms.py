from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, HiddenField,
    SelectField, DateField, TextAreaField, FieldList, FormField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User, Department
from flask_login import current_user

# Leave Request Form
class LeaveRequestForm(FlaskForm):
    teacher_name = StringField('Teacher Name', render_kw={'readonly': True})
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
        self.teacher_name.data = f"{current_user.first_name} {current_user.last_name}"
        self.teacher_id.data = current_user.id


# Slot Form: Stores slot ID and selected covering teacher
class SlotForm(FlaskForm):
    slot_id = HiddenField('Slot ID')  # Hidden field to store the slot ID
    covering_teacher = SelectField('Select Cover Teacher', coerce=int, validators=[DataRequired()])


# Cover Assignment Form: Contains multiple SlotForms in a FieldList
class CoverAssignmentForm(FlaskForm):
    slots = FieldList(FormField(SlotForm), min_entries=0)
    submit = SubmitField('Assign Cover')

    def set_slot_choices(self, slot_teacher_mapping):
        for slot_form in self.slots:
            slot_id = int(slot_form.slot_id.data)
            if slot_id in slot_teacher_mapping:
                teachers = slot_teacher_mapping[slot_id]
                slot_form.covering_teacher.choices = [
                    (teacher['id'], teacher['name']) for teacher in teachers
                ]
            else:
                slot_form.covering_teacher.choices = []

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
    department_id = SelectField('Department', coerce=int, choices=[(0, '-- Select Department --')])

    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        # Populate department choices
        departments = Department.query.all()
        self.department_id.choices += [(dept.id, dept.name) for dept in departments]

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
