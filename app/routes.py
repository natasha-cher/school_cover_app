from flask import render_template, redirect, url_for, request, flash, jsonify
from app import app, db
from app.models import LeaveRequest, CoverAssignment, User
from app.forms import LeaveRequestForm, CoverAssignmentForm, SignupForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from app.helpers import (
    get_leave_request_by_id,
    get_all_teachers,
    get_teaching_slots_by_date_range,
    get_available_teachers_for_cover,
)

# Initialize Flask-Login's LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
def index():
    return redirect(url_for('sign_up_options'))


# Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    pending_count = db.session.execute(db.select(LeaveRequest).filter_by(status='pending')).scalar()
    total_teachers = db.session.execute(db.select(User).filter_by(role='teacher')).scalar()

    return render_template('admin_dashboard.html', pending_count=pending_count, total_teachers=total_teachers)


# Teacher Dashboard
@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if not current_user.is_teacher():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    pending_requests = []
    assignments = []
    return render_template('teacher_dashboard.html', pending_requests=pending_requests, assignments=assignments)


# Display all teachers
@app.route('/teachers')
@login_required
def teachers():
    all_teachers = get_all_teachers()
    return render_template('teachers.html', teachers=all_teachers)


# Leave Request Route
@app.route('/leave-request', methods=['GET', 'POST'])
@login_required
def leave_request():
    form = LeaveRequestForm()

    if form.validate_on_submit():
        leave_request = LeaveRequest(
            user_id=form.teacher_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data,
            status='pending',
            comment=form.comment.data
        )
        db.session.add(leave_request)
        db.session.commit()

        flash('Leave request submitted successfully.')
        return redirect(url_for('view_leave_requests'))

    return render_template('leave_request.html', form=form)


# Get Teaching Periods
@app.route('/periods/<int:request_id>')
@login_required
def get_teaching_periods(request_id):
    leave_request = get_leave_request_by_id(request_id)
    if not leave_request:
        return jsonify({'error': 'Leave request not found'}), 404

    periods = get_teaching_slots_by_date_range(
        leave_request.teacher_id,
        leave_request.start_date,
        leave_request.end_date
    )

    period_dict_list = [{'id': period.id, 'lesson_id': period.lesson_id, 'teacher_id': period.teacher_id,
                         'day_of_week': period.day_of_week, 'period_number': period.period_number}
                        for period in periods]

    return jsonify({'periods': period_dict_list})


# View Leave Requests
@app.route('/view_leave_requests')
@login_required
def view_leave_requests():
    pending_requests = db.session.execute(db.select(LeaveRequest).filter_by(status='pending')).scalars().all()
    approved_requests = db.session.execute(db.select(LeaveRequest).filter_by(status='approved')).scalars().all()
    declined_requests = db.session.execute(db.select(LeaveRequest).filter_by(status='declined')).scalars().all()

    return render_template('view_leave_requests.html',
                           pending_requests=pending_requests,
                           approved_requests=approved_requests,
                           declined_requests=declined_requests)


# Handle Leave Request Actions
@app.route('/handle_request/<int:request_id>', methods=['POST'])
@login_required
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


# Assign Cover Route
@app.route('/assign-cover/<int:leave_request_id>', methods=['GET', 'POST'])
@login_required
def assign_cover(leave_request_id):
    leave_request = get_leave_request_by_id(leave_request_id)
    if not leave_request:
        flash('Leave request not found.')
        return redirect(url_for('view_leave_requests'))

    form = CoverAssignmentForm()
    available_teachers = get_available_teachers_for_cover(leave_request)
    form.cover_teacher_id.choices = [(teacher.id, teacher.name) for teacher in available_teachers]

    if form.validate_on_submit():
        # Loop through each teaching slot and assign cover teachers
        for slot in leave_request.teaching_slots:  # Assuming leave_request has related teaching_slots
            cover_teacher_id = request.form.get(f'cover_teacher_{slot.period_number}')
            if cover_teacher_id:
                cover_assignment = CoverAssignment(
                    leave_request_id=leave_request.id,
                    teaching_slot_id=slot.id,
                    cover_teacher_id=cover_teacher_id
                )
                db.session.add(cover_assignment)

        db.session.commit()
        flash('Cover assignments created successfully.')
        return redirect(url_for('view_leave_requests'))

    teaching_slots = get_teaching_slots_by_date_range(
        leave_request.teacher_id, leave_request.start_date, leave_request.end_date
    )

    return render_template('assign_cover.html', leave_request=leave_request,
                           teaching_slots=teaching_slots,
                           available_teachers=available_teachers,
                           form=form)


# View Cover Assignments
@app.route('/cover_assignments')
@login_required
def view_cover_assignments():
    cover_assignments = db.session.execute(db.select(CoverAssignment)).scalars().all()
    return render_template('cover_assignments.html', cover_assignments=cover_assignments)


# Sign Up Options
@app.route('/sign_up_options')
def sign_up_options():
    return render_template('sign_up_options.html')


# Signup Route
@app.route('/signup/<role>', methods=['GET', 'POST'])
def sign_up(role):
    if role not in ['teacher', 'admin']:
        flash('Invalid role specified.')
        return redirect(url_for('sign_up_options'))

    form = SignupForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar()
        if user is None:
            new_user = User(
                email=form.email.data,
                role=role,  # Set the role dynamically
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                department_id=form.department_id.data
            )
            new_user.set_password(form.password.data)  # Make sure to hash the password
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f'Sign up successful. You are now logged in as a {role}.')
            return redirect(url_for('admin_dashboard') if role == 'admin' else url_for('teacher_dashboard'))

        flash('Email already exists. Please use a different email.')

    return render_template('sign_up.html', form=form, role=role)


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard') if current_user.is_admin() else url_for('teacher_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard') if user.is_admin() else url_for('teacher_dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')

    return render_template('login.html', form=form)


# Logout Route
@app.route('/logout')
@login_required
def logout():
    user_email = current_user.email
    logout_user()
    flash('You have been logged out successfully!', 'success')
    app.logger.info(f'User {user_email} logged out.')
    return redirect(url_for('login'))
