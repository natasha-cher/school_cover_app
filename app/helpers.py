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
