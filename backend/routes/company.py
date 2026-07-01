
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db, Company, Drive, Application
from utils import company_required
from datetime import datetime
from tasks import export_company_csv, celery

company_bp = Blueprint('company', __name__)

# Create a new Placement Drive 
@company_bp.route('/drives', methods=['POST'])
@company_required()
def create_drive():
    data = request.get_json()
    company = Company.query.filter_by(user_id=get_jwt_identity()['id']).first()
    
    if company.status != 'approved':
        return jsonify({"error": "Your account is not approved by the Admin yet!"}), 403
        
    # Convert string deadline to Python DateTime object
    deadline_obj = None
    if data.get('deadline'):
        try:
            # HTML datetime-local inputs send data in this format: YYYY-MM-DDTHH:MM
            deadline_obj = datetime.strptime(data.get('deadline'), '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({"error": "Invalid date format!"}), 400

    new_drive = Drive(
        company_id=company.id,
        title=data.get('title'),
        package=data.get('package'),
        eligibility_cgpa=data.get('eligibility_cgpa'),
        skills=data.get('skills'),
        experience=data.get('experience'),
        benefits=data.get('benefits'),
        deadline=deadline_obj
    )
    
    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"message": "Placement Drive created successfully!"}), 201


# View all drives created by this company
@company_bp.route('/drives', methods=['GET'])
@company_required()
def get_my_drives():
    company = Company.query.filter_by(user_id=get_jwt_identity()['id']).first()
    drives = Drive.query.filter_by(company_id=company.id).all()
    
    drives_list = []
    for drive in drives:
        drives_list.append({
            "id": drive.id,
            "title": drive.title,
            "package": drive.package,
            "status": drive.status,
            "is_closed": drive.is_closed, # Tell frontend if it's closed
            "deadline": drive.deadline.strftime('%Y-%m-%d %H:%M') if drive.deadline else None
        })
    return jsonify(drives_list), 200


# TO manually Close a Job Posting 
@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@company_required()
def close_drive(drive_id):
    company = Company.query.filter_by(user_id=get_jwt_identity()['id']).first()
    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first()
    
    if not drive:
        return jsonify({"error": "Drive not found!"}), 404
        
    drive.is_closed = True
    db.session.commit()
    return jsonify({"message": "Job posting has been closed!"}), 200


# View students who applied to a specific drive
@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@company_required()
def get_drive_applications(drive_id):
    company = Company.query.filter_by(user_id=get_jwt_identity()['id']).first()
    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({"error": "Drive not found!"}), 404
        
    applications = Application.query.filter_by(drive_id=drive_id).all()
    
    app_list = []
    for app in applications:
        app_list.append({
            "application_id": app.id,
            "student_name": app.student.name,
            "student_cgpa": app.student.cgpa,
            "resume_link": app.student.resume_link, # Give the company the resume!
            "status": app.status,
            "feedback": app.feedback,
            "interview_date": app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else None
        })
    return jsonify(app_list), 200


# Update an application status 
@company_bp.route('/applications/<int:application_id>/<string:action>', methods=['PUT'])
@company_required()
def update_application_status(application_id, action):
    # --- UPDATED TO MATCH YOUR EXACT REQUIREMENTS ---
    allowed_actions = ['shortlisted', 'interview', 'offer', 'rejected', 'placed']
    
    if action not in allowed_actions:
        return jsonify({"error": "Invalid action!"}), 400
        
    company = Company.query.filter_by(user_id=get_jwt_identity()['id']).first()
    application = Application.query.get(application_id)
    
    if not application or application.drive.company_id != company.id:
        return jsonify({"error": "Not allowed!"}), 403
        
    data = request.get_json(silent=True) or {}
    application.status = action
    
    if data.get('feedback'):
        application.feedback = data.get('feedback')
        
    # We can schedule an interview during the 'shortlisted' or 'interview' phase
    if action in ['shortlisted', 'interview'] and data.get('interview_date'):
        try:
            application.interview_date = datetime.strptime(data.get('interview_date'), '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({"error": "Invalid interview date format!"}), 400
            
    db.session.commit()
    return jsonify({"message": f"Student has been successfully updated to {action}!"}), 200

# Trigger Asynchronous CSV Export
@company_bp.route('/export', methods=['POST'])
@company_required()
def trigger_export():
    company = Company.query.filter_by(user_id=get_jwt_identity()['id']).first()
    task = export_company_csv.delay(company.id)
    return jsonify({"message": "Export started in the background!", "task_id": task.id}), 202

# Check Task Status
@company_bp.route('/export/status/<string:task_id>', methods=['GET'])
@company_required()
def check_export_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return jsonify({"status": "Completed", "file": task.result}), 200
    return jsonify({"status": task.state}), 200