from app.models import Teacher, LeaveRequest, TeachingSlot
from datetime import datetime, timedelta


def get_all_teachers():
    return Teacher.query.all()


def validate_dates(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        return start_date, end_date
    except ValueError:
        return None, None


def get_leave_request_by_id(leave_request_id):
    return LeaveRequest.query.get(leave_request_id)


def get_teaching_slots_by_date_range(teacher_id, start_date, end_date):
    teaching_slots = []
    current_date = start_date

    while current_date <= end_date:
        day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
        daily_teaching_slots = TeachingSlot.query.filter_by(teacher_id=teacher_id, day_of_week=day_of_week).all()

        teaching_slots.extend(daily_teaching_slots)

        current_date += timedelta(days=1)

    return teaching_slots


def get_available_teachers_for_cover(leave_request):
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
