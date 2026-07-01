from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    student_profile = db.relationship('Student', backref='user', uselist=False)
    company_profile = db.relationship('Company', backref='user', uselist=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    resume_link = db.Column(db.String(255), nullable=True)
    applications = db.relationship('Application', backref='student', lazy=True)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    drives = db.relationship('Drive', backref='company', lazy=True)

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    package = db.Column(db.String(50), nullable=False)
    eligibility_cgpa = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    skills = db.Column(db.String(255), nullable=True) # e.g., "Python, VueJS"
    experience = db.Column(db.String(50), nullable=True) # e.g., "Fresher" or "1-2 Years"
    benefits = db.Column(db.String(255), nullable=True) # e.g., "Health Insurance"
    deadline = db.Column(db.DateTime, nullable=True) # When the job expires
    is_closed = db.Column(db.Boolean, default=False)
    applications = db.relationship('Application', backref='drive', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    status = db.Column(db.String(20), default='applied')
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.String(255), nullable=True) # "feedback for students [resume, missing skills]."
    interview_date = db.Column(db.DateTime, nullable=True)