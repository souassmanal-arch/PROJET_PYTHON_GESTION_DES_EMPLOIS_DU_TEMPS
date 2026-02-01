from models.room import Room
from services.conflict_detector import ConflictDetector

class RoomOptimizer:
    @staticmethod
    def find_best_room(capacity_needed, date, start_time, end_time, equipment_needed=None):
        """
        Find the best available room matching criteria.
        Returns a Room object or None.
        """
        # exclude rooms valid conflict
        
        # 1. Filter by capacity and equipment
        rooms_query = Room.query.filter(Room.capacity >= capacity_needed)
        
        if equipment_needed:
            # Simple check: assumes equipment_needed is a list or string
            # In a real app, this would be more complex relationship query
            for item in equipment_needed:
                rooms_query = rooms_query.filter(Room.equipment.contains(item))
        
        candidates = rooms_query.order_by(Room.capacity.asc()).all() # Get smallest fitting rooms first
        
        # 2. Check availability
        for room in candidates:
            if ConflictDetector.is_slot_available(date, start_time, end_time, room_id=room.id):
                return room
                
        return None
