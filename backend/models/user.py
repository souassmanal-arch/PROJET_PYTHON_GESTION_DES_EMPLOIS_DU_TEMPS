from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'teacher', 'student'
    
    # Relationships
    # For teachers: unavailabilities, reservations
    unavailabilities = db.relationship('Unavailable', backref='teacher', lazy=True)
    reservations = db.relationship('Reservation', backref='teacher', lazy=True)
    
    # For students: could link to group if needed
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'group_id': self.group_id
        }
