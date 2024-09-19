from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.models import Teacher, LeaveRequest, Schedule
from app.helpers import (
    get_leave_request_by_id,
    get_all_teachers,
    validate_dates,
    get_absence_periods,
    find_available_teachers
)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Display all teachers
@app.route('/teachers')
def teachers():
    all_teachers = get_all_teachers()
    return render_template('teachers.html', teachers=all_teachers)

# Leave request route
@app.route('/leave-request', methods=['GET', 'POST'])
def leave_request():
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')
        comment = request.form.get('comment')

        if not (teacher_id and start_date and end_date and reason and comment):
            flash('All fields are required.')
            return redirect(url_for('leave_request'))

        start_date, end_date = validate_dates(start_date, end_date)
        if not start_date or not end_date:
            flash('Invalid date format. Use YYYY-MM-DD.')
            return redirect(url_for('leave_request'))

        leave = LeaveRequest(
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending',
            comment=comment
        )
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted successfully.')
        return redirect(url_for('index'))

    teachers = get_all_teachers()
    return render_template('leave_request.html', teachers=teachers)

# View leave requests
@app.route('/view_leave_requests')
def view_leave_requests():
    pending_requests = LeaveRequest.query.filter_by(status='pending').all()
    other_requests = LeaveRequest.query.filter(LeaveRequest.status != 'pending').all()
    return render_template('view_leave_requests.html', pending_requests=pending_requests, other_requests=other_requests)

# Route to handle accept/decline action
@app.route('/handle_request/<int:request_id>', methods=['POST'])
def handle_request(request_id):
    leave_request = get_leave_request_by_id(request_id)

    if leave_request:
        action = request.form.get('action')
        if action == 'approve':
            leave_request.status = 'approved'
        elif action == 'decline':
            leave_request.status = 'declined'

        db.session.commit()
        flash(f'Leave request {action}d successfully.')
    else:
        flash('Leave request not found.')

    return redirect(url_for('view_leave_requests'))

# Assign cover route
@app.route('/assign-cover', methods=['GET', 'POST'])
def assign_cover():
    if request.method == 'POST':
        # Handle cover assignment logic here
        pass

    # Render cover assignment form
    teachers = get_all_teachers()
    return render_template('assign_cover.html', teachers=teachers)