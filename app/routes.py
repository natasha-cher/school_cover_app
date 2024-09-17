from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.models import Teacher, LeaveRequest, CoverAssignment, Schedule
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


@app.route('/assign-cover', methods=['GET', 'POST'])
def assign_cover():
    if request.method == 'POST':
        leave_request_id = request.form.get('leave_request_id')
        leave_request = get_leave_request_by_id(leave_request_id)

        if not leave_request:
            flash('Leave request not found.')
            return redirect(url_for('assign_cover'))

        periods_needed = get_absence_periods(leave_request.start_date, leave_request.end_date, leave_request.teacher_id)
        available_teachers = find_available_teachers(periods_needed, leave_request.teacher_id)

        if not available_teachers:
            flash('No available teachers for the specified periods.')
            return redirect(url_for('assign_cover'))

        # Assign cover assignments for each period
        for period in periods_needed:
            for teacher_id in available_teachers:
                cover_assignment = CoverAssignment(
                    absent_teacher_id=leave_request.teacher_id,
                    covering_teacher_id=teacher_id,
                    start_date=leave_request.start_date,
                    end_date=leave_request.end_date,
                    schedule_id=None  # Assign a valid schedule_id later
                )

                db.session.add(cover_assignment)

        db.session.commit()
        flash('Cover assignments created successfully.')
        return redirect(url_for('index'))

    leave_requests = LeaveRequest.query.filter_by(status='pending').all()
    teachers = get_all_teachers()
    return render_template('cover_assignments.html', leave_requests=leave_requests, teachers=teachers)


# View leave requests
@app.route('/leave-requests')
def view_leave_requests():
    leave_requests = LeaveRequest.query.all()
    return render_template('view_leave_requests.html', leave_requests=leave_requests)


@app.route('/cover-assignments')
def cover_assignments():
    cover_assignments = CoverAssignment.query.all()
    return render_template('cover_assignments.html', cover_assignments=cover_assignments)