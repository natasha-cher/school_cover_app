# app/seed.py

import os
import sys
from datetime import date

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, app
from app.models import User, Department, LeaveRequest, Lesson, TeachingSlot, CoverAssignment


# Define a function to seed the database
def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()  # Optional: Uncomment if you want to clear existing data
        db.create_all()  # Create tables

        # Seed Departments
        departments = [
            Department(name='Mathematics'),
            Department(name='Science'),
            Department(name='Literature'),
            Department(name='History'),
            Department(name='Art')
        ]
        db.session.bulk_save_objects(departments)

        # Seed Users
        users = [
            User(email='admin@example.com', first_name='Admin', last_name='User', role='admin'),
            User(email='teacher1@example.com', first_name='John', last_name='Doe', role='teacher', department_id=1),
            User(email='teacher2@example.com', first_name='Jane', last_name='Smith', role='teacher', department_id=2),
            User(email='teacher3@example.com', first_name='Alice', last_name='Johnson', role='teacher', department_id=3),
            User(email='teacher4@example.com', first_name='Bob', last_name='Williams', role='teacher', department_id=4)
        ]
        for user in users:
            user.set_password('password')  # Set a default password
        db.session.bulk_save_objects(users)

        # Seed Lessons
        lessons = [
            Lesson(name='Algebra', year_group='Year 10', subject='Mathematics'),
            Lesson(name='Biology', year_group='Year 11', subject='Science'),
            Lesson(name='Shakespeare', year_group='Year 12', subject='Literature'),
            Lesson(name='World History', year_group='Year 10', subject='History'),
            Lesson(name='Painting Basics', year_group='Year 11', subject='Art')
        ]
        db.session.bulk_save_objects(lessons)

        # Seed Teaching Slots
        teaching_slots = [
            TeachingSlot(lesson_id=1, teacher_id=2, day_of_week=1, period_number=1),  # Teacher 1 teaches Algebra
            TeachingSlot(lesson_id=2, teacher_id=3, day_of_week=2, period_number=2),  # Teacher 2 teaches Biology
            TeachingSlot(lesson_id=3, teacher_id=4, day_of_week=3, period_number=3),  # Teacher 3 teaches Shakespeare
            TeachingSlot(lesson_id=4, teacher_id=2, day_of_week=4, period_number=1),  # Teacher 1 teaches World History
            TeachingSlot(lesson_id=5, teacher_id=3, day_of_week=5, period_number=2)   # Teacher 2 teaches Painting Basics
        ]
        db.session.bulk_save_objects(teaching_slots)

        # Seed Leave Requests
        leave_requests = [
            LeaveRequest(user_id=2, start_date=date(2024, 10, 15), end_date=date(2024, 10, 17), reason='Family emergency', status='pending'),
            LeaveRequest(user_id=3, start_date=date(2024, 10, 20), end_date=date(2024, 10, 22), reason='Sick leave', status='approved'),
            LeaveRequest(user_id=4, start_date=date(2024, 10, 25), end_date=date(2024, 10, 28), reason='Personal reasons', status='declined')
        ]
        db.session.bulk_save_objects(leave_requests)

        # Seed Cover Assignments
        cover_assignments = [
            CoverAssignment(absent_teacher_id=3, covering_teacher_id=2, date=date(2024, 10, 21), teaching_slot_id=2),
            CoverAssignment(absent_teacher_id=4, covering_teacher_id=3, date=date(2024, 10, 26), teaching_slot_id=3)
        ]
        db.session.bulk_save_objects(cover_assignments)

        # Commit the session
        db.session.commit()
        print("Data seeded successfully.")

if __name__ == '__main__':
    seed_data()