from flask import Blueprint, jsonify
from models.user import User
from models.schedule import Group

bp = Blueprint('users', __name__, url_prefix='/api/data')

@bp.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = User.query.filter_by(role='teacher').all()
    return jsonify([t.to_dict() for t in teachers])

@bp.route('/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    return jsonify([g.to_dict() for g in groups])
