from flask import Blueprint, request, jsonify
from models import db
from models.reservation import Reservation
from datetime import datetime

bp = Blueprint('reservations', __name__, url_prefix='/api/reservations')

@bp.route('/', methods=['POST'])
def create_reservation():
    data = request.get_json()
    
    # Needs validation for date/time format
    try:
        new_res = Reservation(
            teacher_id=data['teacher_id'],
            room_id=data.get('room_id'),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            motif=data.get('motif'),
            status='pending'
        )
        db.session.add(new_res)
        db.session.commit()
        return jsonify(new_res.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/', methods=['GET'])
def get_reservations():
    # Filters: teacher_id, status
    teacher_id = request.args.get('teacher_id')
    status = request.args.get('status')
    
    query = Reservation.query
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if status:
        query = query.filter_by(status=status)
        
    reservations = query.all()
    return jsonify([r.to_dict() for r in reservations])

@bp.route('/<int:id>/status', methods=['PUT'])
def update_status(id):
    reservation = Reservation.query.get_or_404(id)
    data = request.get_json()
    
    # Should check if user is admin here (middleware/decorator)
    status = data.get('status')
    if status in ['approved', 'rejected']:
        reservation.status = status
        db.session.commit()
        return jsonify(reservation.to_dict())
    
    return jsonify({'error': 'Invalid status'}), 400
