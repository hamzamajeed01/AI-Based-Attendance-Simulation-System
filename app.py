from flask import Flask
from app.models.models import db
from app.api.attendance import attendance_bp
from app.api.employees import employees_bp
from app.api.dashboard import dashboard_bp
from app.api.web import web_bp
from config.config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__,
                static_folder='app/static',
                template_folder='app/templates')
    
    app.config.from_object(config_class)
    
    # Ensure data directory exists
    os.makedirs(os.path.join(config_class.BASE_DIR, 'data'), exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(web_bp, url_prefix='/')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 