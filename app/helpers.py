from app import db
from app.models import Teacher, LeaveRequest, Schedule
from datetime import datetime


def get_teacher_by_id(teacher_id):
    return Teacher.query.get(teacher_id)


def get_leave_request_by_id(leave_request_id):
    return LeaveRequest.query.get(leave_request_id)


def get_schedules_for_teacher(teacher_id):
    return Schedule.query.filter_by(teacher_id=teacher_id).all()


def get_all_teachers():
    return Teacher.query.all()


def validate_dates(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        return start_date, end_date
    except ValueError:
        return None, None


def get_absence_periods(start_date, end_date, teacher_id):
    schedules = Schedule.query.join(LeaveRequest).filter(
        LeaveRequest.teacher_id == teacher_id,
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date
    ).all()

    periods_needed = [
        {
            'day_of_week': schedule.day_of_week,
            'period_number': schedule.period_number
        }
        for schedule in schedules
    ]

    return periods_needed


def find_available_teachers(periods_needed, excluded_teacher_id):
    free_teachers = []

    for period in periods_needed:
        # Find teachers who do not have a schedule in the specified period
        available_teachers = Schedule.query.filter(
            Schedule.day_of_week == period['day_of_week'],
            Schedule.period_number == period['period_number']
        ).filter(Schedule.teacher_id != excluded_teacher_id).all()

        # Filter out teachers who are already assigned for the period
        available_teacher_ids = {teacher.teacher_id for teacher in available_teachers}

        for teacher_id in available_teacher_ids:
            if teacher_id not in [t.id for t in free_teachers]:
                free_teachers.append(teacher_id)

    return free_teachers

