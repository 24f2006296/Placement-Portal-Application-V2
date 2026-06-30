from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User, Student, Company

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists!"}), 400
        
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    
    if role == 'student':
        new_student = Student(user_id=new_user.id, name=data.get('name'), cgpa=data.get('cgpa'))
        db.session.add(new_student)
    elif role == 'company':
        new_company = Company(user_id=new_user.id, company_name=data.get('company_name'))
        db.session.add(new_company)
        
    db.session.commit()
    return jsonify({"message": "Registration successful!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and check_password_hash(user.password, data.get('password')):
        if user.is_blacklisted:
            return jsonify({"error": "Your account has been blacklisted by the Admin."}), 403
        
        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        return jsonify({"message": "Login successful!", "token": access_token, "role": user.role}), 200
    return jsonify({"error": "Wrong email or password!"}), 401


        