from flask import Blueprint, jsonify, request
from models import db, Company, Drive
from utils import admin_required
from tasks import export_applications_csv
from models import db, Company, Drive, Student, Application, User
from cache import cache

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@admin_required()
def get_dashboard_stats():
    # Let the database do the math quickly!
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()
    
    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "total_applications": total_applications
    }), 200


# Search Companies 
@admin_bp.route('/companies/search', methods=['GET'])
@admin_required()
@cache.cached(timeout=120, query_string=True) # Expiry Policy: 120 seconds
def search_companies():
    # Grab the search query from the URL (default is empty string)
    search_query = request.args.get('q', '') 
    
    # Search the database!
    companies = Company.query.filter(
        db.or_(
            Company.company_name.ilike(f'%{search_query}%')
        )
    ).all()
    
    result = []
    for comp in companies:
        result.append({
            "id": comp.id,
            "user_id": comp.user_id, # We need this for blacklisting!
            "company_name": comp.company_name,
            "industry": comp.industry,
            "status": comp.status,
            "is_blacklisted": comp.user.is_blacklisted # Magic thread to User table
        })
        
    return jsonify(result), 200


# Search Students (by name)
@admin_bp.route('/students/search', methods=['GET'])
@admin_required()
@cache.cached(timeout=120, query_string=True) # Expiry Policy: 120 seconds
def search_students():
    search_query = request.args.get('q', '')
    
    students = Student.query.filter(
        db.or_(
            Student.name.ilike(f'%{search_query}%')
        )
    ).all()
    
    result = []
    for student in students:
        result.append({
            "id": student.id,
            "user_id": student.user_id, # We need this for blacklisting!
            "name": student.name,
            "cgpa": student.cgpa,
            "contact": student.contact,
            "is_blacklisted": student.user.is_blacklisted
        })
        
    return jsonify(result), 200



@admin_bp.route('/users/<int:user_id>/blacklist', methods=['PUT'])
@admin_required()
def toggle_blacklist(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found!"}), 404
        
    # Flip the switch! If it's True, make it False. If it's False, make it True.
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()

    # REFRESH POLICY: Clear the Redis cache instantly so searches reflect the ban!
    cache.clear()
    
    action = "Blacklisted" if user.is_blacklisted else "Un-blacklisted"
    return jsonify({"message": f"User successfully {action}!"}), 200


@admin_bp.route('/companies/pending', methods=['GET'])
@admin_required()
def get_pending_companies():
    companies = Company.query.filter_by(status='pending').all()
    company_list = [{"id": c.id, "company_name": c.company_name, "status": c.status} for c in companies]
    return jsonify(company_list), 200

@admin_bp.route('/companies/<int:company_id>/<string:action>', methods=['PUT'])
@admin_required()
def handle_company(company_id, action):
    company = Company.query.get(company_id)
    if not company or action not in ['approve', 'reject']:
        return jsonify({"error": "Invalid request!"}), 400
    company.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    return jsonify({"message": f"Company {company.status}!"}), 200


# View a student's full profile and application history
@admin_bp.route('/students/<int:student_id>/history', methods=['GET'])
@admin_required()
def get_student_history(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found!"}), 404
        
    # Get all applications for this student
    applications = Application.query.filter_by(student_id=student.id).all()
    
    app_history = []
    for app in applications:
        app_history.append({
            "job_title": app.drive.title,
            "company_name": app.drive.company.company_name,
            "status": app.status,
            "applied_on": app.applied_on.strftime('%Y-%m-%d'),
            "interview_date": app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else None,
            "feedback": app.feedback
        })
        
    return jsonify({
        "profile": {
            "name": student.name,
            "cgpa": student.cgpa,
            "skills": student.skills,
            "resume_link": student.resume_link
        },
        "applications": app_history
    }), 200


@admin_bp.route('/drives/pending', methods=['GET'])
@admin_required()
def get_pending_drives():
    drives = Drive.query.filter_by(status='pending').all()
    drive_list = [{"id": d.id, "company_name": d.company.company_name, "title": d.title, "package": d.package, "eligibility_cgpa": d.eligibility_cgpa} for d in drives]
    return jsonify(drive_list), 200

@admin_bp.route('/drives/approved', methods=['GET'])
@admin_required()
def get_approved_drives():
    drives = Drive.query.filter_by(status='approved').all()
    drive_list = [{"id": d.id, "company_name": d.company.company_name, "title": d.title, "package": d.package} for d in drives]
    return jsonify(drive_list), 200

@admin_bp.route('/drives/<int:drive_id>/<string:action>', methods=['PUT'])
@admin_required()
def handle_drive(drive_id, action):
    drive = Drive.query.get(drive_id)
    if not drive or action not in ['approve', 'reject']:
        return jsonify({"error": "Invalid request!"}), 400
    drive.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    # REFRESH POLICY: Clear the cache so students can see the newly approved job!
    cache.clear()
    return jsonify({"message": f"Drive {drive.status}!"}), 200

@admin_bp.route('/drives/<int:drive_id>/export', methods=['POST'])
@admin_required()
def trigger_csv_export(drive_id):
    if not Drive.query.get(drive_id):
        return jsonify({"error": "Drive not found!"}), 404
    task = export_applications_csv.delay(drive_id)
    return jsonify({"message": "CSV export has started!", "task_id": task.id}), 202

