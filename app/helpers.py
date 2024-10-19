from datetime import timedelta
from app.models import User, TeachingSlot, LeaveRequest, CoverAssignment
from app import db
from app.forms import SlotForm


def get_all_teachers():
    return db.session.execute(db.select(User).filter_by(role='teacher')).scalars().all()


def get_leave_request(request_id):
    return LeaveRequest.query.get_or_404(request_id)


def get_teaching_slots_by_date_range(teacher_id, start_date, end_date):
    teaching_slots = []

    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        day_of_week = single_date.weekday()  # 0 = Monday, 6 = Sunday

        daily_teaching_slots = TeachingSlot.query.filter_by(
            teacher_id=teacher_id,
            day_of_week=day_of_week
        ).all()

        teaching_slots.extend(daily_teaching_slots)

    return teaching_slots


def get_available_teachers_for_slot(slot, all_teachers, leave_request):
    available_teachers = []

    for teacher in all_teachers:
        if teacher.id == leave_request.requesting_user.id:
            continue

        conflicting_slot = TeachingSlot.query.filter_by(
            teacher_id=teacher.id,
            day_of_week=slot.day_of_week,
            period_number=slot.period_number
        ).first()

        if not conflicting_slot:
            available_teachers.append(teacher)

    return available_teachers


def get_slot_teacher_mapping(leave_request):
    teaching_slots = get_teaching_slots_by_date_range(
        leave_request.requesting_user.id,
        leave_request.start_date,
        leave_request.end_date
    )
    all_teachers = get_all_teachers()
    slot_teacher_mapping = {}

    for slot in teaching_slots:
        available_teachers = get_available_teachers_for_slot(slot, all_teachers, leave_request)
        slot_teacher_mapping[slot.id] = [
            {
                "id": teacher.id,
                "name": teacher.full_name
            }
            for teacher in available_teachers
        ]

    return slot_teacher_mapping


def populate_slot_forms(form, slot_teacher_mapping):
    for slot_id, teachers in slot_teacher_mapping.items():
        slot_form = SlotForm()
        slot_form.slot_id.data = slot_id
        slot_form.covering_teacher.choices = [(teacher['id'], teacher['name']) for teacher in teachers]
        form.slots.append_entry(slot_form)


def get_slot_details(teaching_slots, slot_teacher_mapping):
    return [
        {
            'subject': slot.lesson.subject,
            'year_group': slot.lesson.year_group,
        }
        for slot in teaching_slots if slot.id in slot_teacher_mapping
    ]


def save_cover_assignments(form, leave_request):
    for slot_form in form.slots:
        slot_id = slot_form.slot_id.data
        covering_teacher_id = slot_form.covering_teacher.data

        if covering_teacher_id:
            cover_assignment = CoverAssignment(
                absent_teacher_id=leave_request.requesting_user.id,
                covering_teacher_id=covering_teacher_id,
                teaching_slot_id=slot_id
            )
            db.session.add(cover_assignment)

    db.session.commit()
