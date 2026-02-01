from flask import Blueprint, request, jsonify
from models import db
from models.schedule import Schedule, Group
from services.ai_scheduler import AIScheduler
from datetime import datetime, date, timedelta

bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

@bp.route('/', methods=['GET'])
def get_schedules():
    group_id = request.args.get('group_id')
    teacher_id = request.args.get('teacher_id')
    room_id = request.args.get('room_id')
    
    query = Schedule.query
    if group_id:
        query = query.filter_by(group_id=group_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if room_id:
        query = query.filter_by(room_id=room_id)
        
    schedules = query.all()
    return jsonify([s.to_dict() for s in schedules])

@bp.route('/generate', methods=['POST'])
def generate_schedule():
    # Admin only
    scheduler = AIScheduler()
    
    # In a real app, we would fetch parsing constraints from body or DB
    # For now, we fetch all groups and run logic
    groups = Group.query.all()
    
    # Demo: Mock requirements if not provided
    # Format: {group_id: [('Calculus', teacher_id, 4), ...]}
    requirements = request.get_json().get('requirements', {})
    
    # Convert keys to int if JSON sent strings
    requirements = {int(k): v for k, v in requirements.items()}
    
    # Start date
    start_date_str = request.get_json().get('start_date', '2024-09-02') # A Monday
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    result = scheduler.generate_schedule(groups, requirements, start_date)
    
    if result.get('status') == 'success':
        return jsonify(result), 201
    else:
        return jsonify(result), 500
