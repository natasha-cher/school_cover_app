from flask import render_template, redirect, url_for, request, flash, jsonify
from app import app, db
from app.models import LeaveRequest, CoverAssignment, Teacher, User
from app.forms import LeaveRequestForm, CoverAssignmentForm, SignupForm
from flask_login import login_user
from app.helpers import (
    get_leave_request_by_id,
    get_all_teachers,
    validate_dates,
    get_teaching_slots_by_date_range,
    get_available_teachers_for_cover,
)


# Home route
@app.route('/')
def index():
    pending_count = LeaveRequest.query.filter_by(status='pending').count()
    total_teachers = Teacher.query.count()
    return render_template('index.html', pending_count=pending_count, total_teachers=total_teachers)


# Display all teachers
@app.route('/teachers')
def teachers():
    all_teachers = get_all_teachers()
    return render_template('teachers.html', teachers=all_teachers)


@app.route('/leave-request', methods=['GET', 'POST'])
def leave_request():
    teachers = get_all_teachers()
    form = LeaveRequestForm()

    # Populate the teacher choices for the form
    form.teacher_id.choices = [(teacher.id, teacher.name) for teacher in teachers]

    if form.validate_on_submit():
        # Get data from the validated form
        teacher_id = form.teacher_id.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        reason = form.reason.data
        comment = form.comment.data

        # Create the leave request
        leave_request = LeaveRequest(
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending',
            comment=comment
        )
        db.session.add(leave_request)
        db.session.commit()

        flash('Leave request submitted successfully.')
        return redirect(url_for('view_leave_requests'))

    return render_template('leave_request.html', teachers=teachers, form=form)


@app.route('/periods/<int:request_id>')
def get_teaching_periods(request_id):
    leave_request = get_leave_request_by_id(request_id)
    if not leave_request:
        return jsonify({'error': 'Leave request not found'}), 404
    periods = get_teaching_slots_by_date_range(
        leave_request.teacher_id,
        leave_request.start_date,
        leave_request.end_date
    )
    period_dict_list = []
    for period in periods:
        period_dict_list.append({
            'id': period.id,
            'lesson_id': period.lesson_id,
            'teacher_id': period.teacher_id,
            'day_of_week': period.day_of_week,
            'period_number': period.period_number
        })

    # Return the periods as JSON
    return jsonify({'periods': period_dict_list})


# View leave requests
@app.route('/view_leave_requests')
def view_leave_requests():
    pending_requests = LeaveRequest.query.filter_by(status='pending').all()
    approved_requests = LeaveRequest.query.filter_by(status='approved').all()
    declined_requests = LeaveRequest.query.filter_by(status='declined').all()
    return render_template('view_leave_requests.html', pending_requests=pending_requests, approved_requests=approved_requests, declined_requests=declined_requests)


# Handle accept/decline action
@app.route('/handle_request/<int:request_id>', methods=['POST'])
def handle_request(request_id):
    leave_request = get_leave_request_by_id(request_id)
    action = request.form.get('action')

    if leave_request and action in ['approve', 'decline']:
        leave_request.status = 'approved' if action == 'approve' else 'declined'
        db.session.commit()
        flash(f'Leave request {action}d successfully.')
    else:
        flash('Leave request not found or invalid action.')

    return redirect(url_for('view_leave_requests'))


# Assign cover route
@app.route('/assign-cover/<int:leave_request_id>', methods=['GET', 'POST'])
def assign_cover(leave_request_id):
    # Retrieve the leave request by its ID
    leave_request = get_leave_request_by_id(leave_request_id)
    if not leave_request:
        flash('Leave request not found.')
        return redirect(url_for('view_leave_requests'))

    # Initialize the form
    form = CoverAssignmentForm()

    # Fetch available teachers for cover assignments
    available_teachers = get_available_teachers_for_cover(leave_request)

    # Set choices for the cover teacher select field
    form.cover_teacher_id.choices = [(teacher.id, teacher.name) for teacher in available_teachers]

    if request.method == 'POST':
        # Validate and process the form submission
        if form.validate_on_submit():
            # Loop through each teaching slot and assign cover teachers
            for slot in leave_request.teaching_slots:  # Assuming leave_request has related teaching_slots
                cover_teacher_id = request.form.get(f'cover_teacher_{slot.period_number}')
                if cover_teacher_id:
                    # Logic to create or update the cover assignment in the database
                    cover_assignment = CoverAssignment(
                        leave_request_id=leave_request.id,
                        teaching_slot_id=slot.id,
                        cover_teacher_id=cover_teacher_id
                    )
                    db.session.add(cover_assignment)

            # Commit all cover assignments to the database
            db.session.commit()

            flash('Cover assignments created successfully.')
            return redirect(url_for('view_leave_requests'))

    # Get teaching slots for the specific leave request
    teaching_slots = get_teaching_slots_by_date_range(
        leave_request.teacher_id, leave_request.start_date, leave_request.end_date
    )

    return render_template('assign_cover.html', leave_request=leave_request,
                           teaching_slots=teaching_slots, available_teachers=available_teachers, form=form)


@app.route('/cover_assignments')
def view_cover_assignments():
    cover_assignments = CoverAssignment.query.all()
    return render_template('cover_assignments.html', cover_assignments=cover_assignments)


@app.route('/sign_up_options')
def sign_up_options():
    return render_template('sign_up_options.html')


@app.route('/signup/<role>', methods=['GET', 'POST'])
def sign_up(role):
    if role not in ['teacher', 'admin']:
        flash('Invalid role specified.')
        return redirect(url_for('sign_up_options'))

    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            new_user = User(email=form.email.data, role=role)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash(f'Sign up successful. You are logged in as a {role}.')
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('teacher_dashboard'))
        else:
            flash('Email already exists. Please use a different email.')
    return render_template('sign_up.html', form=form, role=role)
