# app/seed.py

import os
import sys
from datetime import date, timedelta
from random import choice

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

        # Seed Users - One admin and nine teachers with real names
        users = [
            User(email='admin@example.com', first_name='Admin', last_name='User', role='admin'),
            User(email='jane.doe@example.com', first_name='Jane', last_name='Doe', role='teacher', department_id=1),
            # Mathematics
            User(email='john.doe@example.com', first_name='John', last_name='Doe', role='teacher', department_id=2),
            # Science
            User(email='alice.johnson@example.com', first_name='Alice', last_name='Johnson', role='teacher',
                 department_id=3),  # Literature
            User(email='bob.williams@example.com', first_name='Bob', last_name='Williams', role='teacher',
                 department_id=4),  # History
            User(email='mary.brown@example.com', first_name='Mary', last_name='Brown', role='teacher', department_id=5),
            # Art
            User(email='david.smith@example.com', first_name='David', last_name='Smith', role='teacher',
                 department_id=1),  # Mathematics
            User(email='susan.clark@example.com', first_name='Susan', last_name='Clark', role='teacher',
                 department_id=2),  # Science
            User(email='michael.evans@example.com', first_name='Michael', last_name='Evans', role='teacher',
                 department_id=3),  # Literature
            User(email='linda.martin@example.com', first_name='Linda', last_name='Martin', role='teacher',
                 department_id=4)  # History
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
            Lesson(name='Painting Basics', year_group='Year 11', subject='Art'),
            Lesson(name='Physics', year_group='Year 11', subject='Science'),
            Lesson(name='Chemistry', year_group='Year 10', subject='Science'),
            Lesson(name='English Literature', year_group='Year 12', subject='Literature'),
            Lesson(name='Art History', year_group='Year 11', subject='Art'),
            Lesson(name='Geometry', year_group='Year 10', subject='Mathematics')
        ]
        db.session.bulk_save_objects(lessons)

        # Seed Leave Requests
        leave_requests = []
        for user_id in range(2, 11):  # Assuming user IDs 2-10
            start_date = date.today() + timedelta(days=choice(range(1, 30)))
            end_date = start_date + timedelta(days=choice(range(1, 5)))  # Random end date within 4 days
            reason = choice(['Family emergency', 'Sick leave', 'Personal reasons', 'Vacation'])
            status = choice(['pending', 'approved', 'declined'])
            leave_requests.append(
                LeaveRequest(user_id=user_id, start_date=start_date, end_date=end_date, reason=reason, status=status))
        db.session.bulk_save_objects(leave_requests)

        # Seed Teaching Slots
        teaching_slots = []
        for teacher_id in range(2, 11):  # Skip admin (id 1)
            for _ in range(20):  # Each teacher gets 20 teaching slots
                lesson_id = choice(range(1, 11))  # Choose a lesson randomly
                day_of_week = choice(range(1, 6))  # Random day of the week (1-5)
                period_number = choice(range(1, 7))  # Random period number (1-6)
                teaching_slots.append(TeachingSlot(lesson_id=lesson_id, teacher_id=teacher_id, day_of_week=day_of_week,
                                                   period_number=period_number))

        db.session.bulk_save_objects(teaching_slots)

        # Commit the session
        db.session.commit()
        print("Data seeded successfully.")


if __name__ == '__main__':
    seed_data()