from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.models import Teacher, LeaveRequest, CoverAssignment, TeachingSchedule
from datetime import datetime


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)


@app.route('/leave-request', methods=['GET', 'POST'])
def leave_request():
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        date = request.form.get('date')
        reason = request.form.get('reason')

        leave = LeaveRequest(teacher_id=teacher_id, date=datetime.strptime(date, '%Y-%m-%d'), reason=reason)
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted successfully.')
        return redirect(url_for('index'))

    teachers = Teacher.query.all()
    return render_template('leave_request.html', teachers=teachers)


@app.route('/assign-cover')
def assign_cover():
    # Logic for assigning cover work goes here
    return render_template('cover_assignments.html')