from flask import Flask
from flask_cors import CORS
from config import Config
from models import db

# Import Blueprints
from routes.auth import bp as auth_bp
from routes.rooms import bp as rooms_bp
from routes.reservations import bp as reservations_bp
from routes.schedules import bp as schedules_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(schedules_bp)
    
    from routes.users import bp as users_bp
    app.register_blueprint(users_bp)
    
    from routes.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp)
    
    from routes.frontend import bp as frontend_bp
    app.register_blueprint(frontend_bp)
    
    app.secret_key = 'super-secret-key-123'

    
    with app.app_context():
        from models import user, room, schedule, reservation, unavailable, notification
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    print("Server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

