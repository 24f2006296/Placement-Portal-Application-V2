from celery_setup import make_celery
from app import create_app
from models import Application, Student, User, Company, Drive 
import csv
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart # for HTML emails

flask_app = create_app()
celery = make_celery(flask_app)

# ... (Keep export_applications_csv and send_interview_reminders tasks here) ...

# Monthly Report Task 
@celery.task(name="tasks.send_monthly_reports")
def send_monthly_reports():
    print("Starting monthly report generation...")
    
    # 1. Get all approved companies
    approved_companies = Company.query.filter_by(status='approved').all()
    reports_sent = 0
    current_month = datetime.utcnow().strftime("%B %Y") # e.g., "August 2026"
    
    for company in approved_companies:
        # 2. Calculate Statistics
        drives = Drive.query.filter_by(company_id=company.id).all()
        total_drives = len(drives)
        
        if total_drives == 0:
            continue # Skip companies that haven't posted any jobs
            
        applications = []
        for drive in drives:
            applications.extend(Application.query.filter_by(drive_id=drive.id).all())
            
        total_applicants = len(applications)
        total_interviews = len([a for a in applications if a.status in ['interview', 'offer', 'placed']])
        total_placed = len([a for a in applications if a.status == 'placed'])
        
        # 3. Create the HTML Report
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <h2 style="color: #2c5364;">Placement Report - {current_month}</h2>
                <p>Hello <strong>{company.company_name}</strong>,</p>
                <p>Here is your automated monthly hiring summary from the Sanjivni Placement Portal.</p>
                
                <table style="width: 100%; max-width: 600px; border-collapse: collapse; margin-top: 20px;">
                    <tr style="background-color: #f8f9fa; border-bottom: 2px solid #ddd;">
                        <th style="padding: 10px; text-align: left;">Metric</th>
                        <th style="padding: 10px; text-align: left;">Count</th>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Total Job Postings</td>
                        <td style="padding: 10px;"><strong>{total_drives}</strong></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Total Applications Received</td>
                        <td style="padding: 10px;"><strong>{total_applicants}</strong></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Candidates Interviewed</td>
                        <td style="padding: 10px;"><strong>{total_interviews}</strong></td>
                    </tr>
                    <tr style="background-color: #e9f7ef; border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;"><strong>Total Students Hired</strong></td>
                        <td style="padding: 10px; color: #28a745;"><strong>{total_placed}</strong></td>
                    </tr>
                </table>
                
                <p style="margin-top: 30px; font-size: 0.9em; color: #777;">
                    Log in to your dashboard to manage open positions and schedule more interviews.<br>
                    - The Placement Portal Team
                </p>
            </body>
        </html>
        """
        
        # 4. Send Email
        company_email = company.user.email
        subject = f"Your Monthly Hiring Report - {current_month}"
        
        send_email(company_email, subject, html_content, is_html=True)
        reports_sent += 1
        
    print(f"Finished generating reports. Sent {reports_sent} emails.")
    return f"Sent {reports_sent} reports."


# Upgraded Helper Function: Send Email ---
def send_email(to_email, subject, body, is_html=False):
    sender = flask_app.config.get('SENDER_EMAIL')
    password = flask_app.config.get('SENDER_PASSWORD')
    
    # If testing without credentials
    if sender == "your_email@gmail.com":
        print(f"\n[MOCK EMAIL to {to_email}]")
        print(f"Subject: {subject}")
        if is_html:
            print("(Contains HTML Document)")
        else:
            print(f"Body:\n{body}")
        print("-" * 30 + "\n")
        return
        
    try:
        # Check if we should render HTML or Plain Text
        if is_html:
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(body, 'html'))
        else:
            msg = MIMEText(body, 'plain')
            
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email
        
        server = smtplib.SMTP(flask_app.config.get('SMTP_SERVER'), flask_app.config.get('SMTP_PORT'))
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Student CSV Export Task ---
@celery.task(name="tasks.export_student_csv")
def export_student_csv(student_id):
    student = Student.query.get(student_id)
    applications = Application.query.filter_by(student_id=student.id).all()
    
    filename = f"student_{student.id}_history.csv"
    filepath = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Company Name', 'Job Title', 'Applied On', 'Status', 'Interview Date', 'Feedback'])
        for app in applications:
            interview = app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else 'N/A'
            applied = app.applied_on.strftime('%Y-%m-%d')
            writer.writerow([app.drive.company.company_name, app.drive.title, applied, app.status, interview, app.feedback or 'N/A'])
            
    print(f"Task Complete! Student CSV saved to {filepath}")
    return filepath

# Company CSV Export Task ---
@celery.task(name="tasks.export_company_csv")
def export_company_csv(company_id):
    drives = Drive.query.filter_by(company_id=company_id).all()
    
    filename = f"company_{company_id}_placements.csv"
    filepath = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Job Title', 'Student Name', 'CGPA', 'Applied On', 'Status'])
        for drive in drives:
            for app in drive.applications:
                applied = app.applied_on.strftime('%Y-%m-%d')
                writer.writerow([drive.title, app.student.name, app.student.cgpa, applied, app.status])
                
    print(f"Task Complete! Company CSV saved to {filepath}")
    return filepath