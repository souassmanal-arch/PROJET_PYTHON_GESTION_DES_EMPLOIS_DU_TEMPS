from models import db
from models.schedule import Schedule
from services.room_optimizer import RoomOptimizer
from services.conflict_detector import ConflictDetector
from datetime import time, date, timedelta

class AIScheduler:
    def __init__(self):
        pass

    def generate_schedule(self, groups, courses_per_group, semester_start_date):
        """
        Simple heuristic scheduler.
        :param groups: List of Group objects
        :param courses_per_group: Dictionary {group_id: [(course_name, teacher_id, hours_needed), ...]}
        :param semester_start_date: Start date of the week to generate for
        """
        generated_count = 0
        errors = []

        # Time slots definition (e.g., 8-10, 10-12, 14-16, 16-18)
        time_slots = [
            (time(8, 0), time(10, 0)),
            (time(10, 0), time(12, 0)),
            (time(14, 0), time(16, 0)),
            (time(16, 0), time(18, 0))
        ]
        
        # Days of week (0=Monday, 4=Friday)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for group in groups:
            courses = courses_per_group.get(group.id, [])
            for course_name, teacher_id, hours in courses:
                # Try to schedule 'hours' sessions. Assuming 2h slots.
                sessions_needed = hours // 2 
                
                for _ in range(sessions_needed):
                    scheduled = False
                    # Greedy search for slots
                    for day_idx, day_name in enumerate(days):
                        if scheduled: break
                        
                        # Calculate actual date if needed, but we store day_name in DB as per model
                        # For conflict check we need a specific date if we check against one-off reservations
                        # asking logic to be simple for now
                        current_date = semester_start_date + timedelta(days=day_idx)

                        for start, end in time_slots:
                            # Check basic availability for Teacher and Group
                            if not ConflictDetector.is_slot_available(current_date, start, end, teacher_id=teacher_id, group_id=group.id):
                                continue

                            # Find room
                            room = RoomOptimizer.find_best_room(
                                capacity_needed=group.students_count,
                                date=current_date,
                                start_time=start,
                                end_time=end,
                                equipment_needed=[] # Simplified
                            )

                            if room:
                                # Book it
                                new_schedule = Schedule(
                                    course_name=course_name,
                                    group_id=group.id,
                                    teacher_id=teacher_id,
                                    room_id=room.id,
                                    day_of_week=day_name,
                                    start_time=start,
                                    end_time=end
                                )
                                db.session.add(new_schedule)
                                scheduled = True
                                generated_count += 1
                                break
                    
                    if not scheduled:
                        errors.append(f"Could not schedule {course_name} for Group {group.name}")
        
        try:
            db.session.commit()
            return {"status": "success", "generated": generated_count, "errors": errors}
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
