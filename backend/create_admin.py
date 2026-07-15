
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def create_super_admin():
    # Create a mini-version of our Flask app
    app = create_app()
    
   
    with app.app_context():
        existing_admin = User.query.filter_by(email="admin@sanjivni.com").first()
        
        if existing_admin:
            print("Admin already exists! You can log in with admin@sanjivni.com")
            return

        # 3. Create the new Admin User
        print("Creating Super Admin account...")
        admin_password = generate_password_hash("admin123") # Change this in real life!
        
        admin_user = User(
            email="admin@sanjivni.com",
            password=admin_password,
            role="admin"
        )
        
        # 4. Save to Database
        db.session.add(admin_user)
        db.session.commit()
        
        print("Success! Admin account created.")
        print("Email: admin@sanjivni.com")
        print("Password: admin123")

if __name__ == "__main__":
    create_super_admin()