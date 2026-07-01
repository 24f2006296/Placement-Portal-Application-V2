from flask import Flask
from config import Config
from models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from cache import cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)       
    JWTManager(app)        
    CORS(app)              
    cache.init_app(app)
    
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    from routes.company import company_bp
    app.register_blueprint(company_bp, url_prefix='/api/company')
    
    from routes.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/api/student')

    with app.app_context():
        db.create_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)