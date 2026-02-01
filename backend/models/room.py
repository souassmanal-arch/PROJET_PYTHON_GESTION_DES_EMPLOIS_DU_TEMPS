from . import db

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50))  # 'Amphitheater', 'Classroom', 'Lab'
    equipment = db.Column(db.String(200))  # Comma-separated list e.g. "Projector,PC"
    
    reservations = db.relationship('Reservation', backref='room', lazy=True)
    schedules = db.relationship('Schedule', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'type': self.type,
            'equipment': self.equipment
        }
