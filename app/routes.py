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

        periods = []
        for i in range(len(request.form.getlist('periods[0][day_of_week]'))):
            period = {
                'day_of_week': request.form.get(f'periods[{i}][day_of_week]'),
                'period_number': request.form.get(f'periods[{i}][period_number]'),
                'date': request.form.get(f'periods[{i}][date]'),
                'covering_teacher_id': request.form.get(f'covering_teacher_{i}')
            }
            periods.append(period)

        # Process each period
        for period in periods:
            schedule = Schedule.query.filter_by(
                teacher_id=leave_request.teacher_id,
                day_of_week=period['day_of_week'],
                period_number=period['period_number']
            ).first()

            if schedule:
                cover_assignment = CoverAssignment(
                    absent_teacher_id=leave_request.teacher_id,
                    covering_teacher_id=period['covering_teacher_id'],
                    date=datetime.strptime(period['date'], '%Y-%m-%d').date(),
                    schedule_id=schedule.id
                )
                db.session.add(cover_assignment)

        leave_request.status = 'completed'
        db.session.commit()
        flash('Cover assignment completed successfully.')
        return redirect(url_for('index'))

    leave_request_id = request.args.get('leave_request_id')
    leave_request = get_leave_request_by_id(leave_request_id)

    if not leave_request:
        flash('Leave request not found.')
        return redirect(url_for('index'))

    periods = get_absence_periods(leave_request.start_date, leave_request.end_date, leave_request.teacher_id)
    teachers = get_all_teachers()

    # Find recommended teachers for each period
    for period in periods:
        available_teachers = find_available_teachers([period], leave_request.teacher_id)
        if available_teachers:
            period['recommended_teacher_id'] = available_teachers[0]  # Select the first available teacher

    return render_template('cover_assignments.html', periods=periods, teachers=teachers, leave_request_id=leave_request_id)


# View leave requests
@app.route('/leave-requests')
def view_leave_requests():
    leave_requests = LeaveRequest.query.all()
    return render_template('view_leave_requests.html', leave_requests=leave_requests)


@app.route('/cover-assignments')
def cover_assignments():
    cover_assignments = CoverAssignment.query.all()
    return render_template('cover_assignments.html', cover_assignments=cover_assignments)