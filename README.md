# School Cover App

A web-based application designed to streamline the assignment of cover work for teachers based on their schedules and workloads. This application aims to simplify the management of teacher absences and ensure equitable coverage within a school.

## Current Status

This project is currently a work in progress. Future enhancements will include automating cover assignments to guarantee fair distribution based on teachers’ workloads for the day. Additionally, plans are underway to generate reports concerning teacher absences.

## Features

- **User Management**: Admin and teacher roles with separate dashboards.
- **Teacher Leave Requests**: Submit, view, and manage leave requests with an approval workflow.
- **Cover Assignments**: Automated assignment of covering teachers for absent staff.
- **Dashboards**: Dedicated dashboards for teachers and admins to monitor activities.

## Tech Stack

- **Backend**: Flask, SQLAlchemy (ORM),WTForms
- **Frontend**: HTML/CSS, Bootstrap, Jinja templates
- **Authentication**: Flask-Login
- **Database**: SQLite or PostgreSQL

## Database Schema

The database consists of the following tables:

- **User**: Stores user information (email, password hash, role, department).
- **Department**: Contains department names and relationships with users.
- **Lesson**: Holds lesson details (year group, subject).
- **TeachingSlot**: Links lessons to teachers and includes scheduling information.
- **LeaveRequest**: Manages leave requests, statuses, and comments.
- **CoverAssignment**: Connects absent teachers with their covering teachers.

## Usage

- **Admin Login**: Access the admin dashboard to manage teachers and leave requests.
- **Teachers**: Submit leave requests and view cover assignments.
- **Assign Cover**: Admins can assign teachers to cover absences through the app’s interface.

## Main Routes Overview

- **/admin_dashboard**: Admin overview of pending requests and teacher statistics.
- **/teacher_dashboard**: Dashboard for teachers to track assignments and requests.
- **/leave-request**: Submit leave requests.
- **/assign-cover/<leave_request_id>**: Assign covering teachers for a leave request.

## Installation

1. **Clone the repository**:
   
   ```bash
   git clone https://github.com/natasha-cher/school_cover_app
   cd school_cover_app
2. **Create a virtual environment****:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt

4. **Initialize the database**:

   ```bash
   flask db upgrade

5. **Run the app**:

   ```bash
   flask run 


## Seeding the Database

To populate the database with initial data, you can use the provided seed file. This file is located in the seeds.py within the project app directory.  Command to run the seed file:
python -m app.seed

## Contributions 
Contributions are welcome! If you would like to contribute, please follow these steps:

- Fork the repository.
- Create a new branch (git checkout -b feature/YourFeature).
- Make your changes and commit them (git commit -m 'Add some feature').
- Push to the branch (git push origin feature/YourFeature).
- Open a pull request with a detailed description of your changes.

Please ensure your code follows the project’s coding conventions and includes appropriate tests.
