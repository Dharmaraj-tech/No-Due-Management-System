# No-Due-Management-System
Manages academic completion in the Institution

✅ No Due Clearance System - College Web Application
This is a web-based No Due Clearance Management System for colleges. It simplifies and digitizes the no-due process, allowing students to request clearance and staff/HODs to approve or reject those requests based on marks and assignment submissions.

🌐 Project Overview
This system is designed for three main roles:

🎓 Student

👩‍🏫 Staff (Subject Incharge)

🧑‍💼 HOD (Head of Department)

Students submit marks and assignment data. Subject staff verify and approve each subject's no due. The HOD has the power to view all class-wise, subject-wise data and give final clearance.

🏗️ Features by Role
🎓 Student
Register with: Name, Department, Year, Semester, Class (e.g., A/B)

View subject-wise no due status

Enter:

Subject marks

Assignment 1, 2, 3 marks per subject

Total marks

View staff approvals

Request final clearance once all subjects are approved

👨‍🏫 Staff
Login by Name, Department, Class, and allocated Subject(s)

View list of students under their subject & class

Verify:

Marks entered

Assignment data

Approve/Reject subject-wise no due per student

Comments (optional) for rejection

🧑‍💼 HOD
Login as HOD of a department

Create and manage:

Multiple classes

Add subjects

Assign multiple staff per subject

View:

Subject-wise clearance status

Student-wise clearance data

Approve final no-due requests

Dashboard shows:

Number of students per class

Subjects in each class

Number of no dues cleared/pending

🗃️ Database Design (Sample Tables)
students: id, name, department, year, semester, class

subjects: id, name, class_id

classes: id, name (e.g., A/B), year, semester, department

staffs: id, name, department, subject_id, class_id

marks: student_id, subject_id, mark, assignment1, assignment2, assignment3, total

no_due_requests: student_id, subject_id, status (pending/approved/rejected)

final_clearance: student_id, status

🧰 Tech Stack
Layer	Tech
Frontend	HTML, CSS, JavaScript
Backend	Python (Flask or FastAPI)
Database	SQLite / PostgreSQL
Deployment	Vercel (Frontend), Render / Railway (Backend)
