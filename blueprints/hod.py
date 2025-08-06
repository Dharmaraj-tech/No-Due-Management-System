from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import User, Subject, StaffSubject, NoDueStatus, FinalApproval, Class, db
from functools import wraps

hod_bp = Blueprint('hod', __name__)

def hod_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'hod':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@hod_bp.route('/dashboard')
@hod_required
def dashboard():
    return render_template('hod_dashboard.html')

@hod_bp.route('/api/department-students')
@hod_required
def get_department_students():
    hod = User.query.get(session['user_id'])
    students = User.query.filter_by(
        role='student',
        department=hod.department
    ).all()
    
    students_data = []
    for student in students:
        # Get subject approval count
        total_subjects = Subject.query.filter_by(
            department=student.department,
            semester=student.semester
        ).count()
        
        approved_subjects = NoDueStatus.query.filter_by(
            student_id=student.id,
            status='approved'
        ).count()
        
        # Get final approval status
        final_approval = FinalApproval.query.filter_by(student_id=student.id).first()
        
        students_data.append({
            'id': student.id,
            'name': student.name,
            'roll_number': student.roll_number,
            'class_section': student.class_section,
            'year': student.year,
            'semester': student.semester,
            'approved_subjects': approved_subjects,
            'total_subjects': total_subjects,
            'final_status': final_approval.status if final_approval else 'not_requested',
            'final_remarks': final_approval.remarks if final_approval else None
        })
    
    return jsonify(students_data)

@hod_bp.route('/api/final-approve', methods=['POST'])
@hod_required
def final_approve():
    data = request.get_json()
    student_id = data.get('student_id')
    action = data.get('action')  # approve or reject
    remarks = data.get('remarks', '')
    
    final_approval = FinalApproval.query.filter_by(student_id=student_id).first()
    if not final_approval:
        return jsonify({
            'success': False,
            'message': 'No final approval request found'
        }), 404
    
    final_approval.status = 'approved' if action == 'approve' else 'rejected'
    final_approval.approved_by = session['user_id']
    final_approval.remarks = remarks
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Final approval {action}d successfully'
    })

@hod_bp.route('/api/staff')
@hod_required
def get_staff():
    hod = User.query.get(session['user_id'])
    staff = User.query.filter_by(
        role='staff',
        department=hod.department
    ).all()
    
    staff_data = []
    for member in staff:
        assignments = StaffSubject.query.filter_by(staff_id=member.id).all()
        advised_classes = Class.query.filter_by(class_advisor_id=member.id).all()
        staff_data.append({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'assignments': len(assignments),
            'advised_classes': len(advised_classes)
        })
    
    return jsonify(staff_data)

@hod_bp.route('/api/subjects')
@hod_required
def get_subjects():
    hod = User.query.get(session['user_id'])
    subjects = Subject.query.filter_by(department=hod.department).all()
    
    subjects_data = []
    for subject in subjects:
        class_info = Class.query.get(subject.class_id) if subject.class_id else None
        subjects_data.append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
            'semester': subject.semester,
            'credits': subject.credits,
            'class_name': class_info.name if class_info else 'Not assigned'
        })
    
    return jsonify(subjects_data)

@hod_bp.route('/api/classes')
@hod_required
def get_classes():
    hod = User.query.get(session['user_id'])
    classes = Class.query.filter_by(department=hod.department).all()
    
    classes_data = []
    for cls in classes:
        advisor = User.query.get(cls.class_advisor_id) if cls.class_advisor_id else None
        subject_count = Subject.query.filter_by(class_id=cls.id).count()
        
        classes_data.append({
            'id': cls.id,
            'name': cls.name,
            'year': cls.year,
            'semester': cls.semester,
            'section': cls.section,
            'advisor_name': advisor.name if advisor else 'Not assigned',
            'advisor_id': cls.class_advisor_id,
            'subject_count': subject_count
        })
    
    return jsonify(classes_data)

@hod_bp.route('/api/create-class', methods=['POST'])
@hod_required
def create_class():
    data = request.get_json()
    hod = User.query.get(session['user_id'])
    
    # Check if class already exists
    existing = Class.query.filter_by(
        department=hod.department,
        year=data.get('year'),
        semester=data.get('semester'),
        section=data.get('section')
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'message': 'Class already exists'
        }), 400
    
    new_class = Class(
        name=data.get('name'),
        department=hod.department,
        year=data.get('year'),
        semester=data.get('semester'),
        section=data.get('section')
    )
    
    db.session.add(new_class)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Class created successfully'
    })

@hod_bp.route('/api/create-subject', methods=['POST'])
@hod_required
def create_subject():
    data = request.get_json()
    hod = User.query.get(session['user_id'])
    
    # Check if subject code already exists
    existing = Subject.query.filter_by(
        code=data.get('code'),
        department=hod.department
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'message': 'Subject code already exists'
        }), 400
    
    new_subject = Subject(
        name=data.get('name'),
        code=data.get('code'),
        department=hod.department,
        semester=data.get('semester'),
        credits=data.get('credits', 3),
        class_id=data.get('class_id') if data.get('class_id') else None
    )
    
    db.session.add(new_subject)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Subject created successfully'
    })

@hod_bp.route('/api/assign-class-advisor', methods=['POST'])
@hod_required
def assign_class_advisor():
    data = request.get_json()
    class_id = data.get('class_id')
    staff_id = data.get('staff_id')
    
    class_obj = Class.query.get_or_404(class_id)
    staff = User.query.get_or_404(staff_id)
    
    if staff.role != 'staff':
        return jsonify({
            'success': False,
            'message': 'Selected user is not a staff member'
        }), 400
    
    class_obj.class_advisor_id = staff_id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Class advisor assigned successfully'
    })

@hod_bp.route('/api/assign-subject', methods=['POST'])
@hod_required
def assign_subject():
    data = request.get_json()
    staff_id = data.get('staff_id')
    subject_id = data.get('subject_id')
    class_id = data.get('class_id')
    
    # Check if assignment already exists
    existing = StaffSubject.query.filter_by(
        staff_id=staff_id,
        subject_id=subject_id,
        class_id=class_id
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'message': 'Assignment already exists'
        }), 400
    
    assignment = StaffSubject(
        staff_id=staff_id,
        subject_id=subject_id,
        class_id=class_id
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Subject assigned successfully'
    })
