from app import create_app, db
from models.user import User
from models.room import Room
from models.schedule import Group, Schedule
from models.reservation import Reservation
from models.notification import Notification
from werkzeug.security import generate_password_hash
from datetime import date, time, timedelta, datetime
import random

app = create_app()

with app.app_context():
    print("Refreshing database with 'BZAF' real data...")
    db.drop_all()
    db.create_all()

    # 1. Users
    print("Creating users...")
    admin = User(username='Administrateur', email='admin@univ.ma', role='admin', password_hash=generate_password_hash('admin123'))
    
    teachers = [
        User(username='Pr. Mohammed Alami', email='alami@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Fatima Benjelloun', email='benjelloun@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Hassan Idrissi', email='idrissi@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Karim Tazi', email='tazi@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Sara Berrada', email='berrada@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Oussama El Fassi', email='elfassi@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Houda Mernissi', email='mernissi@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Nabil Chraibi', email='chraibi@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Meryem El Amrani', email='elamrani@univ.ma', role='teacher', password_hash=generate_password_hash('pass123')),
        User(username='Pr. Yacine Bouzid', email='bouzid@univ.ma', role='teacher', password_hash=generate_password_hash('pass123'))
    ]

    students = [
        User(username='Ahmed Amrani', email='ahmed@student.ma', role='student', password_hash=generate_password_hash('stud123')),
        User(username='Salma Bennani', email='salma@student.ma', role='student', password_hash=generate_password_hash('stud123')),
        User(username='Youssef Mansouri', email='youssef@student.ma', role='student', password_hash=generate_password_hash('stud123'))
    ]
    
    db.session.add(admin)
    db.session.add_all(teachers)
    db.session.add_all(students)
    db.session.commit()

    # 2. Rooms
    print("Creating rooms...")
    rooms_data = [
        ('Amphi A', 300, 'Amphitheater', 'Projector, Mic, Sound System, AC'),
        ('Amphi B', 250, 'Amphitheater', 'Projector, Mic'),
        ('Amphi C', 200, 'Amphitheater', 'Projector'),
        ('Amphi D', 200, 'Amphitheater', 'Smart Board'),
        ('Salle 1', 40, 'Classroom', 'Whiteboard, TV'),
        ('Salle 2', 40, 'Classroom', 'Whiteboard'),
        ('Salle 3', 40, 'Classroom', 'Whiteboard'),
        ('Salle 4', 40, 'Classroom', 'Projector'),
        ('Salle 5', 30, 'Classroom', 'Whiteboard'),
        ('Salle 6', 30, 'Classroom', 'Whiteboard'),
        ('Lab Info 1', 25, 'Lab', '25 PCs, Projector'),
        ('Lab Info 2', 25, 'Lab', '25 PCs'),
        ('Lab Reseau', 20, 'Lab', 'Cisco Routers, PCs'),
        ('Lab Electronique', 20, 'Lab', 'Oscilloscopes, Kits'),
    ]
    
    rooms = []
    for r in rooms_data:
        room = Room(name=r[0], capacity=r[1], type=r[2], equipment=r[3])
        rooms.append(room)
    
    db.session.add_all(rooms)
    db.session.commit()

    # 3. Groups
    print("Creating groups...")
    groups = [
        Group(name='Génie Informatique 1', students_count=32),
        Group(name='Génie Informatique 2', students_count=28),
        Group(name='Génie Industriel 1', students_count=35),
        Group(name='Big Data & AI', students_count=24),
        Group(name='Cyber Security', students_count=20),
    ]
    db.session.add_all(groups)
    db.session.commit()

    # Assign student to groups
    students[0].group_id = groups[0].id # Ahmed -> GI1
    students[1].group_id = groups[3].id # Salma -> Big Data
    students[2].group_id = groups[4].id
    db.session.commit()

    # 4. Schedules (MASSIVE DATA)
    print("Creating massive schedules...")
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    courses = [
        'Algorithmique Avancée', 'Base de Données', 'Architecture des Ordinateurs', 'Programmation Python',
        'Machine Learning', 'Probabilités et Stats', 'Cloud Computing', 'Anglais Technique',
        'Management de Projet', 'Systèmes d\'Exploitation', 'Réseaux Informatiques', 'Java JEE',
        'Analyse de Données', 'Deep Learning', 'Soft Skills', 'Droit de l\'Info'
    ]
    
    # Helper to randomize
    def get_random_room(type_filter=None):
        if type_filter:
            candidates = [r for r in rooms if r.type == type_filter]
            return random.choice(candidates) if candidates else rooms[0]
        return random.choice(rooms)

    def get_random_teacher():
        return random.choice(teachers)

    schedules = []
    
    # Generate FULL week for Group 1 (Ahmed)
    # Mon-Sat, Morning and Afternoon
    schedule_templates = [
        ('Monday', '08:30', '10:00', 'Monday', '10:15', '11:45', 'Monday', '14:30', '16:00'),
        ('Tuesday', '08:30', '10:00', 'Tuesday', '10:15', '11:45', 'Tuesday', '16:15', '17:45'),
        ('Wednesday', '08:30', '10:00', 'Wednesday', '10:15', '11:45'), # Half day
        ('Thursday', '08:30', '10:00', 'Thursday', '10:15', '11:45', 'Thursday', '14:30', '16:00'),
        ('Friday', '08:30', '11:30', 'Friday', '15:00', '17:00'),
        ('Saturday', '09:00', '12:00')
    ]

    # For each group, filling the week
    for grp in groups:
        for day_slots in schedule_templates:
            # Process slots triples (Day, Start, End) * N
            # Simplified manual loop for control
            if len(day_slots) >= 3:
                schedules.append({
                    'course': random.choice(courses), 'day': day_slots[0], 'start': day_slots[1], 'end': day_slots[2], 'grp': grp,
                    'room': get_random_room(), 'teacher': get_random_teacher()
                })
            if len(day_slots) >= 6:
                schedules.append({
                    'course': random.choice(courses), 'day': day_slots[3], 'start': day_slots[4], 'end': day_slots[5], 'grp': grp,
                    'room': get_random_room(), 'teacher': get_random_teacher()
                })
            if len(day_slots) >= 9:
                 schedules.append({
                    'course': random.choice(courses), 'day': day_slots[6], 'start': day_slots[7], 'end': day_slots[8], 'grp': grp,
                    'room': get_random_room(), 'teacher': get_random_teacher()
                })

    for s in schedules:
        t_start = time(int(s['start'].split(':')[0]), int(s['start'].split(':')[1]))
        t_end = time(int(s['end'].split(':')[0]), int(s['end'].split(':')[1]))
        
        new_s = Schedule(
            course_name=s['course'],
            day_of_week=s['day'],
            start_time=t_start,
            end_time=t_end,
            room_id=s['room'].id,
            teacher_id=s['teacher'].id,
            group_id=s['grp'].id
        )
        db.session.add(new_s)
    
    db.session.commit()

    # 5. Reservations (Dense)
    print("Creating BZAF reservations...")
    for _ in range(20):
        t = random.choice(teachers)
        r = random.choice(rooms)
        d = date.today() + timedelta(days=random.randint(0, 7))
        status = random.choice(['pending', 'approved', 'rejected'])
        res = Reservation(teacher_id=t.id, room_id=r.id, date=d, start_time=time(14,0), end_time=time(16,0), motif='Event/Class', status=status)
        db.session.add(res)
    db.session.commit()

    # 6. Notifications (BZAF)
    print("Creating BZAF notifications...")
    notif_templates = [
        ("Schedule Update", "Your class 'Python' has been moved to Amphi B.", "warning"),
        ("New Reservation", "Room 101 confirmed for Tuesday.", "success"),
        ("Exam Alert", "Final exams schedule will be posted soon.", "info"),
        ("System Maintenance", "Server will be down on Sunday night.", "danger"),
        ("Welcome", "Welcome to the new academic year 2026/2027.", "info"),
        ("Urgent", "Please submit grades by Friday.", "danger"),
        ("Room Change", "Lab 2 is currently under maintenance.", "warning"),
        ("Event", "Hackathon registration is open!", "success")
    ]
    
    # Add notifications for all users
    all_users = [admin] + teachers + students
    for u in all_users:
        # Give each user 5-8 notifications
        for _ in range(random.randint(5, 12)):
            templ = random.choice(notif_templates)
            n = Notification(user_id=u.id, title=templ[0], message=templ[1], type=templ[2], created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 100)))
            db.session.add(n)
            
    db.session.commit()

    print("Success: Data Volume maxed out.")
