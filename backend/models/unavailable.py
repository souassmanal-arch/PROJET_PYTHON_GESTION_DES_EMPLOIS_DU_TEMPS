from . import db

class Unavailable(db.Model):
    __tablename__ = 'unavailabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # Monday, Tuesday...
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'day_of_week': self.day_of_week,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'reason': self.reason
        }
