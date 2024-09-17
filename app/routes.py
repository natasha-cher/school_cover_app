from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.models import Teacher, LeaveRequest, CoverAssignment, Schedule
from app.helpers import get_leave_request_by_id, get_schedules_for_teacher, get_all_teachers, validate_dates
from datetime import datetime


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
        covering_teacher_id = request.form.get('covering_teacher_id')

        leave_request = get_leave_request_by_id(leave_request_id)
        if not leave_request:
            flash('Leave request not found.')
            return redirect(url_for('assign_cover'))

        # Ensure covering_teacher_id is not the same as absent_teacher_id
        if covering_teacher_id == str(leave_request.teacher_id):
            flash('Covering teacher cannot be the same as the absent teacher.')
            return redirect(url_for('assign_cover'))

        # Fetch all schedules for the absent teacher
        absent_teacher_schedules = get_schedules_for_teacher(leave_request.teacher_id)
        if not absent_teacher_schedules:
            flash('No schedule found for the absent teacher.')
            return redirect(url_for('assign_cover'))

        # Fetch or create schedules for the covering teacher
        covering_teacher_schedules = get_schedules_for_teacher(covering_teacher_id)
        if not covering_teacher_schedules:
            flash('No schedule found for the covering teacher.')
            return redirect(url_for('assign_cover'))

        # Create cover assignments
        for schedule in absent_teacher_schedules:
            cover_assignment = CoverAssignment(
                absent_teacher_id=leave_request.teacher_id,
                covering_teacher_id=covering_teacher_id,
                date=datetime.today().date(),
                schedule_id=schedule.id
            )
            db.session.add(cover_assignment)

            # Update the covering teacher's schedule (e.g., create new entries)
            covering_teacher_schedule = Schedule(
                lesson_id=schedule.lesson_id,
                teacher_id=covering_teacher_id,
                day_of_week=schedule.day_of_week,
                period_number=schedule.period_number
            )
            db.session.add(covering_teacher_schedule)

        # Update the leave request status to completed
        leave_request.status = 'completed'
        db.session.add(leave_request)

        # Commit the transaction
        db.session.commit()
        flash('Cover assignment completed and leave request status updated.')
        return redirect(url_for('index'))

    leave_requests = LeaveRequest.query.filter_by(status='pending').all()
    teachers = get_all_teachers()
    return render_template('cover_assignments.html', leave_requests=leave_requests, teachers=teachers)


# View leave requests
@app.route('/leave-requests')
def view_leave_requests():
    leave_requests = LeaveRequest.query.all()
    return render_template('view_leave_requests.html', leave_requests=leave_requests)
