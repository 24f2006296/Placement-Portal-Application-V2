
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from models import db, Student, Drive, Application
from utils import student_required
from datetime import datetime 
from cache import cache

student_bp = Blueprint('student', __name__)

#  View & Update Student Profile ---
@student_bp.route('/profile', methods=['GET', 'PUT'])
@student_required()
def handle_profile():
    student = Student.query.filter_by(user_id=get_jwt_identity()).first()
    if not student:
        return jsonify({"error": "Profile not found!"}), 404

    if request.method == 'GET':
        return jsonify({
            "name": student.name,
            "cgpa": student.cgpa,
            "education": student.education,
            "skills": student.skills,
            "experience": student.experience,
            "resume_link": student.resume_link
        }), 200

    # If PUT request (Updating profile)
    data = request.get_json()
    student.name = data.get('name', student.name)
    student.cgpa = data.get('cgpa', student.cgpa)
    student.education = data.get('education', student.education)
    student.skills = data.get('skills', student.skills)
    student.experience = data.get('experience', student.experience)
    student.resume_link = data.get('resume_link', student.resume_link)
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully!"}), 200


#  Smart Job Board (Hides closed/expired & Allows Search) ---
@student_bp.route('/drives', methods=['GET'])
@student_required()
@cache.cached(timeout=120, query_string=True) 
def get_available_drives():
    search_query = request.args.get('q', '')
    
    query = Drive.query.filter_by(status='approved', is_closed=False)
    
    if search_query:
        from models import Company 
        query = query.join(Company).filter(
            db.or_(
                Drive.title.ilike(f'%{search_query}%'),
                Drive.skills.ilike(f'%{search_query}%'),
                Company.company_name.ilike(f'%{search_query}%')
            )
        )
        
    drives = query.all()
    current_time = datetime.utcnow()
    
    drives_list = []
    for drive in drives:
        # CHECK: If there is a deadline AND it has already passed, skip this job!
        if drive.deadline and drive.deadline < current_time:
            continue
            
        drives_list.append({
            "id": drive.id,
            "company_name": drive.company.company_name,
            "title": drive.title,
            "package": drive.package,
            "eligibility_cgpa": drive.eligibility_cgpa,
            "skills": drive.skills,
            "experience": drive.experience,
            "benefits": drive.benefits,
            "deadline": drive.deadline.strftime('%Y-%m-%d %H:%M') if drive.deadline else None
        })
        
    return jsonify(drives_list), 200


# Apply for Job ---
@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@student_required()
def apply_for_job(drive_id):
    student = Student.query.filter_by(user_id=get_jwt_identity()).first()
    drive = Drive.query.get(drive_id)
    
    if not drive or drive.status != 'approved' or drive.is_closed:
        return jsonify({"error": "Drive is not available!"}), 404
    if drive.deadline and drive.deadline < datetime.utcnow():
        return jsonify({"error": "The deadline for this job has passed!"}), 400
        
    if student.cgpa < drive.eligibility_cgpa:
        return jsonify({"error": "Your CGPA is too low to apply."}), 400
        
    if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
        return jsonify({"error": "You have already applied!"}), 400
        
    new_application = Application(student_id=student.id, drive_id=drive.id, status='applied')
    db.session.add(new_application)
    db.session.commit()
    return jsonify({"message": "Successfully applied for the job!"}), 201


# My Application History (Track Status) ---
@student_bp.route('/applications', methods=['GET'])
@student_required()
def get_my_applications():
    student = Student.query.filter_by(user_id=get_jwt_identity()).first()
    applications = Application.query.filter_by(student_id=student.id).all()
    
    app_list = []
    for app in applications:
        app_list.append({
            "application_id": app.id,
            "drive_id": app.drive_id,
            "company_name": app.drive.company.company_name,
            "job_title": app.drive.title,
            "status": app.status,
            "applied_on": app.applied_on.strftime('%Y-%m-%d'),
            "feedback": app.feedback,
            "interview_date": app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else None,
            "offer_letter": app.offer_letter
        })
        
    return jsonify(app_list), 200

# Trigger Asynchronous CSV Export
@student_bp.route('/export', methods=['POST'])
@student_required()
def trigger_export():
    from tasks import export_student_csv

    student = Student.query.filter_by(user_id=get_jwt_identity()).first()
    task = export_student_csv.delay(student.id)
    return jsonify({"message": "Export started in the background!", "task_id": task.id}), 202

# Check Task Status
@student_bp.route('/export/status/<string:task_id>', methods=['GET'])
@student_required()
def check_export_status(task_id):
    from tasks import celery
    
    task = celery.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return jsonify({"status": "Completed", "file": task.result}), 200
    return jsonify({"status": task.state}), 200

# Csv export file download Route
@student_bp.route('/download/<path:filepath>', methods=['GET'])
def download_csv(filepath):
    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found!"}), 404