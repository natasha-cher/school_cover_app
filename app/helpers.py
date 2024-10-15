from datetime import timedelta
from app.models import User, TeachingSlot
from app import db


def get_all_teachers():
    return db.session.execute(db.select(User).filter_by(role='teacher')).scalars().all()


def get_teaching_slots_by_date_range(teacher_id, start_date, end_date):
    teaching_slots = []
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
        daily_teaching_slots = db.session.execute(
            db.select(TeachingSlot).filter(
                TeachingSlot.teacher_id == teacher_id,
                TeachingSlot.day_of_week == day_of_week
            )
        ).scalars().all()

        teaching_slots.extend(daily_teaching_slots)
        current_date += timedelta(days=1)

    return teaching_slots


def get_available_teachers_for_slot(slot, all_teachers):
    available_teachers = []

    for teacher in all_teachers:
        conflicting_slot = db.session.execute(
            db.select(TeachingSlot).filter(
                TeachingSlot.teacher_id == teacher.id,
                TeachingSlot.date == slot.date,
                TeachingSlot.start_time < slot.end_time,  # Slot overlap check
                TeachingSlot.end_time > slot.start_time  # Slot overlap check
            )
        ).scalars().first()

        if not conflicting_slot:
            available_teachers.append(teacher)

    return available_teachers


