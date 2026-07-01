from celery_setup import make_celery
from app import create_app
from models import Application
import csv
import os

flask_app = create_app()
celery = make_celery(flask_app)

@celery.task()
def export_applications_csv(drive_id):
    apps = Application.query.filter_by(drive_id=drive_id).all()
    filename = f"drive_{drive_id}_applications.csv"
    filepath = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Application ID', 'Student Name', 'CGPA', 'Status'])
        for app in apps:
            writer.writerow([app.id, app.student.name, app.student.cgpa, app.status])
            
    print(f"Task Complete! CSV saved to {filepath}")
    return filepath