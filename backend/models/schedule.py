from . import db

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., "M1 Informatique"
    students_count = db.Column(db.Integer, default=30)
    
    schedules = db.relationship('Schedule', backref='group', lazy=True)
    # students = db.relationship('User', backref='group', lazy=True) # If we link students to groups

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'students_count': self.students_count
        }

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True) # Can be null if provisional
    
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    semester = db.Column(db.Integer, default=1)

    teacher = db.relationship('User', backref='schedules')

    def to_dict(self):
        return {
            'id': self.id,
            'course_name': self.course_name,
            'group_id': self.group_id,
            'teacher_id': self.teacher_id,
            'room_id': self.room_id,
            'day_of_week': self.day_of_week,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'teacher_name': self.teacher.username if self.teacher else None
        }
