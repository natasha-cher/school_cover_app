from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from app import db, app
from app.models import LeaveRequest, CoverAssignment, User
from app.forms import LeaveRequestForm, CoverAssignmentForm, SignupForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from app.helpers import (
    get_all_teachers,
    get_teaching_slots_by_date_range,
    get_available_teachers_for_slot
)
from datetime import timedelta

main = Blueprint('main', __name__)

# Initialize Flask-Login's LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


# Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    pending_count = db.session.execute(
        db.select(LeaveRequest).filter_by(status='pending').with_only_columns(db.func.count())
    ).scalar()

    total_teachers = db.session.execute(
        db.select(User).filter_by(role='teacher').with_only_columns(db.func.count())
    ).scalar()

    return render_template('admin_dashboard.html', pending_count=pending_count, total_teachers=total_teachers)


# Teacher Dashboard
@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if not current_user.is_teacher():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

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
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data,
            status='pending',
            comment=form.comment.data
        )
        try:
            db.session.add(leave_request)
            db.session.commit()
            flash('Leave request submitted successfully.')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your leave request. Please try again.')

        return redirect(url_for('view_leave_requests'))
    return render_template('leave_request.html', form=form)


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
    if not current_user.is_admin():
        flash('You do not have permission to handle leave requests.', 'danger')
        return redirect(url_for('view_leave_requests'))

    leave_request = LeaveRequest.query.get_or_404(request_id)
    action = request.form.get('action')
    valid_actions = ['approve', 'decline']
    if action in valid_actions:
        leave_request.status = 'approved' if action == 'approve' else 'declined'
        db.session.commit()
        flash(f'Leave request {action}d successfully.', 'success')
    else:
        flash('Invalid action. Please try again.', 'danger')

    return redirect(url_for('view_leave_requests'))


from datetime import datetime


@app.route('/fetch-slots', methods=['POST'])
@login_required
def fetch_slots():
    data = request.json
    teacher_id = data.get('teacher_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    # Convert string dates to datetime.date objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    slots_to_cover = get_teaching_slots_by_date_range(
        teacher_id, start_date, end_date
    )

    all_teachers = get_all_teachers()
    slot_teacher_mapping = {
        slot.id: {
            'lesson': slot.lesson.name,
            'period': slot.period_number,
            'teachers': [
                {'id': teacher.id, 'name': teacher.full_name}
                for teacher in get_available_teachers_for_slot(slot, all_teachers)
            ]
        }
        for slot in slots_to_cover
    }
    return jsonify(slot_teacher_mapping)


# Assign Cover Route
@app.route('/assign-cover/<int:leave_request_id>', methods=['GET', 'POST'])
@login_required
def assign_cover(leave_request_id):
    form = CoverAssignmentForm()
    leave_request = LeaveRequest.query.get_or_404(leave_request_id)

    if form.validate_on_submit():
        for slot_id, teacher_id in request.form.items():
            if slot_id.startswith('slot_'):
                cover_assignment = CoverAssignment(
                    absent_teacher_id=leave_request.requesting_user.id,
                    covering_teacher_id=int(teacher_id),
                    teaching_slot_id=int(slot_id.split('_')[1]),
                )
                db.session.add(cover_assignment)
        db.session.commit()
        flash("Cover assignments created successfully.", "success")
        return redirect(url_for('leave_request_detail', leave_request_id=leave_request.id))
    return render_template('assign_cover.html', form=form, leave_request=leave_request)


# View Cover Assignments
@app.route('/cover_assignments')
@login_required
def view_cover_assignments():
    cover_assignments = db.session.execute(db.select(CoverAssignment)).scalars().all()
    return render_template('cover_assignments.html', cover_assignments=cover_assignments)


# Sign Up Options
@app.route('/sign_up_options')
def sign_up_options():
    return render_template('index.html')


# Signup Route
@app.route('/signup/<role>', methods=['GET', 'POST'])
def sign_up(role):
    if role not in ['teacher', 'admin']:
        flash('Invalid role specified.')
        return redirect(url_for('sign_up_options'))

    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = db.one_or_404(db.select(User).filter_by(email=form.email.data),
                                 description="User with this email does not exist.")
        except:
            user = None  # Proceed with user creation if the user is not found

        if user is None:
            new_user = User(
                email=form.email.data,
                role=role,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                department_id=form.department_id.data
            )
            new_user.set_password(form.password.data)
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
        user = db.first_or_404(db.select(User).filter_by(email=form.email.data),
                               description="Invalid email or password.")
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
