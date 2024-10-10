from app.models import LeaveRequest, TeachingSlot, User
from datetime import datetime, timedelta
from app import db


def get_all_teachers():
    """Fetches all teachers from the database using the newer query syntax."""
    # Using newer syntax with db.session.execute and db.select
    return db.session.execute(db.select(User).filter_by(role='teacher')).scalars().all()


def get_leave_request_by_id(leave_request_id):
    """Fetches a leave request by its ID."""
    # Using db.get for primary key lookups
    return db.session.get(LeaveRequest, leave_request_id)


def get_teaching_slots_by_date_range(teacher_id, start_date, end_date):
    """Fetches teaching slots for a specific teacher within a date range."""
    teaching_slots = []
    current_date = start_date

    while current_date <= end_date:
        day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
        # Use newer syntax for querying teaching slots by day of week and teacher_id
        daily_teaching_slots = db.session.execute(
            db.select(TeachingSlot).filter_by(teacher_id=teacher_id, day_of_week=day_of_week)
        ).scalars().all()
        teaching_slots.extend(daily_teaching_slots)
        current_date += timedelta(days=1)

    return teaching_slots


def get_available_teachers_for_cover(leave_request):
    """Finds available teachers to cover for a leave request."""
    start_date = leave_request.start_date
    end_date = leave_request.end_date
    available_teachers = []

    all_teachers = get_all_teachers()

    # Check each teacher for availability during the leave period
    for teacher in all_teachers:
        teaching_slots = get_teaching_slots_by_date_range(teacher.id, start_date, end_date)
        if not teaching_slots:
            available_teachers.append(teacher)

    return available_teachers
