from models.schedule import Schedule
from models.unavailable import Unavailable
from sqlalchemy import or_

class ConflictDetector:
    @staticmethod
    def is_slot_available(date, start_time, end_time, teacher_id=None, room_id=None, group_id=None):
        """
        Check if the time slot is available for the given entities.
        Returns True if available, False otherwise.
        """
        # 1. Check Teacher Availability (Unavailable table)
        if teacher_id:
            # Check explicit unavailability
            # Assuming 'date' provides day of week. 
            # In a real app, we need to handle specific dates vs recurring weekly slots.
            # Simplified: Check recurring weekly unavailability based on day name.
            day_name = date.strftime('%A')
            
            unavailable = Unavailable.query.filter_by(teacher_id=teacher_id, day_of_week=day_name).filter(
                or_(
                    (Unavailable.start_time <= start_time) & (Unavailable.end_time > start_time),
                    (Unavailable.start_time < end_time) & (Unavailable.end_time >= end_time)
                )
            ).first()
            if unavailable:
                return False

            # Check existing schedules for teacher
            conflict = Schedule.query.filter_by(teacher_id=teacher_id, day_of_week=day_name).filter(
               or_(
                    (Schedule.start_time <= start_time) & (Schedule.end_time > start_time),
                    (Schedule.start_time < end_time) & (Schedule.end_time >= end_time)
               ) 
            ).first()
            if conflict:
                return False

        # 2. Check Room Availability
        if room_id:
            day_name = date.strftime('%A')
            conflict = Schedule.query.filter_by(room_id=room_id, day_of_week=day_name).filter(
               or_(
                    (Schedule.start_time <= start_time) & (Schedule.end_time > start_time),
                    (Schedule.start_time < end_time) & (Schedule.end_time >= end_time)
               ) 
            ).first()
            if conflict:
                return False
        
        # 3. Check Group Availability
        if group_id:
            day_name = date.strftime('%A')
            conflict = Schedule.query.filter_by(group_id=group_id, day_of_week=day_name).filter(
               or_(
                    (Schedule.start_time <= start_time) & (Schedule.end_time > start_time),
                    (Schedule.start_time < end_time) & (Schedule.end_time >= end_time)
               ) 
            ).first()
            if conflict:
                return False

        return True
