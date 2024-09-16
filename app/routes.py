from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.models import Teacher, LeaveRequest, CoverAssignment, Schedule, Lesson
from datetime import datetime


# Home route
@app.route('/')
def index():
    return render_template('index.html')


# Display all teachers
@app.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)


# Leave request route
@app.route('/leave-request', methods=['GET', 'POST'])
def leave_request():
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')
        comment = request.form.get('comment')

        if not (teacher_id and start_date and end_date and reason):
            flash('All fields are required.')
            return redirect(url_for('leave_request'))

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format.')
            return redirect(url_for('leave_request'))

        leave = LeaveRequest(
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending',  # Default status
            comment=comment  # Store the comment
        )
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted successfully.')
        return redirect(url_for('index'))

    teachers = Teacher.query.all()
    return render_template('leave_request.html', teachers=teachers)


# Assign cover route
@app.route('/assign-cover', methods=['GET', 'POST'])
def assign_cover():
    if request.method == 'POST':
        leave_request_id = request.form.get('leave_request_id')
        covering_teacher_id = request.form.get('covering_teacher_id')

        leave_request = LeaveRequest.query.get(leave_request_id)
        if not leave_request:
            flash('Leave request not found.')
            return redirect(url_for('assign_cover'))

        schedule = Schedule.query.filter_by(teacher_id=leave_request.teacher_id).first()
        if not schedule:
            flash('No schedule found for the absent teacher.')
            return redirect(url_for('assign_cover'))

        cover_assignment = CoverAssignment(
            absent_teacher_id=leave_request.teacher_id,
            covering_teacher_id=covering_teacher_id,
            date=datetime.today().date(),  # or a specific date if required
            schedule_id=schedule.id
        )
        db.session.add(cover_assignment)
        db.session.commit()
        flash('Cover assignment completed successfully.')
        return redirect(url_for('index'))

    leave_requests = LeaveRequest.query.filter_by(status='pending').all()
    teachers = Teacher.query.all()
    return render_template('cover_assignments.html', leave_requests=leave_requests, teachers=teachers)


# View leave requests
@app.route('/leave-requests')
def view_leave_requests():
    leave_requests = LeaveRequest.query.all()
    return render_template('view_leave_requests.html', leave_requests=leave_requests)
