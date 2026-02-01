from app import create_app, db
from models.user import User
import os
from werkzeug.security import generate_password_hash

try:
    app = create_app()
    with app.app_context():
        # Check tables
        tables = db.metadata.tables.keys()
        print(f"Tables found: {list(tables)}")
        
        # Check if database file exists
        if os.path.exists('university.db'):
            print("university.db exists.")
        else:
            print("university.db created by create_all().")

        # Create a test user
        if not User.query.filter_by(username='admin').first():
            u = User(username='admin', email='admin@test.com', role='admin', password_hash=generate_password_hash('admin123'))
            db.session.add(u)
            db.session.commit()
            print("Created admin user.")
        else:
            print("Admin user already exists.")
            
    print("Verification Succeeded!")
except Exception as e:
    print(f"Verification Failed: {e}")
