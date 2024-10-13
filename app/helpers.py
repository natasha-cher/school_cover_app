from app.models import LeaveRequest, TeachingSlot, User
from app import db


def get_all_teachers():
    return db.session.execute(db.select(User).filter_by(role='teacher')).scalars().all()


def get_teaching_slots_by_date_range(start_date, end_date):
    teaching_slots = db.session.execute(
        db.select(TeachingSlot).filter(
            TeachingSlot.date >= start_date,
            TeachingSlot.date <= end_date
        )
    ).scalars().all()

    return teaching_slots


def get_available_teachers_for_cover(leave_request):
    """Finds available teachers to cover for a leave request."""
    start_date = leave_request.start_date
    end_date = leave_request.end_date
    available_teachers = []

    all_teachers = get_all_teachers()
    teaching_slots = get_teaching_slots_by_date_range(start_date, end_date)
    occupied_teacher_ids = {slot.teacher_id for slot in teaching_slots}
    available_teachers = [teacher for teacher in all_teachers if teacher.id not in occupied_teacher_ids]

    return available_teachers
