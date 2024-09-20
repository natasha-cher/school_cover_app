from flask import render_template, redirect, url_for, request, flash, jsonify
from app import app, db
from app.models import Teacher, LeaveRequest, TeachingSlot, CoverAssignment
from app.helpers import (
    get_leave_request_by_id,
    get_all_teachers,
    validate_dates,
    get_teaching_slots_by_date_range,
    get_available_teachers_for_cover,
)
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
        return redirect(url_for('index'))

    teachers = get_all_teachers()
    return render_template('leave_request.html', teachers=teachers)


# View leave requests
@app.route('/view_leave_requests')
def view_leave_requests():
    pending_requests = LeaveRequest.query.filter_by(status='pending').all()
    other_requests = LeaveRequest.query.filter(LeaveRequest.status != 'pending').all()
    return render_template('view_leave_requests.html', pending_requests=pending_requests, other_requests=other_requests)


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
    leave_request = get_leave_request_by_id(leave_request_id)
    if not leave_request:
        flash('Leave request not found.')
        return redirect(url_for('view_leave_requests'))

    if request.method == 'POST':
        cover_assignments = []
        periods = get_teaching_slots_by_date_range(leave_request.teacher_id, leave_request.start_date,
                                                   leave_request.end_date)

        for period in periods:
            cover_teacher_id = request.form.get(f'cover_teacher_{period["period_number"]}')
            if cover_teacher_id:
                cover_assignment = CoverAssignment(
                    absent_teacher_id=leave_request.teacher_id,
                    covering_teacher_id=cover_teacher_id,
                    date=period['date'],
                    teaching_slot_id=period['id']
                )
                cover_assignments.append(cover_assignment)

        if cover_assignments:
            db.session.bulk_save_objects(cover_assignments)
            db.session.commit()
            flash('Cover assignments created successfully.')
        else:
            flash('No cover assignments were made. Please select teachers for the periods.')

        return redirect(url_for('view_leave_requests'))

    # Fetch available teachers for the dropdown
    available_teachers = get_available_teachers_for_cover(leave_request)

    # Logic to display periods needing cover
    periods = get_teaching_slots_by_date_range(leave_request.teacher_id, leave_request.start_date,
                                               leave_request.end_date)

    return render_template('assign_cover.html', leave_request=leave_request, periods=periods,
                           available_teachers=available_teachers)


# Get teaching slots for leave request
@app.route('/get_teaching_slots', methods=['POST'])
def get_teaching_slots_for_teacher():
    data = request.get_json()
    teacher_id = data['teacher_id']
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

    teaching_slots = get_teaching_slots_by_date_range(teacher_id, start_date, end_date)
    return jsonify({'teaching_slots': teaching_slots})


@app.route('/view_cover_assignments')
def view_cover_assignments():
    cover_assignments = CoverAssignment.query.all()  # Fetch all cover assignments
    return render_template('view_cover_assignments.html', cover_assignments=cover_assignments)
