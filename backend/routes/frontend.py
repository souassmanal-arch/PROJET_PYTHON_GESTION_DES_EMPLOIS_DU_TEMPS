from flask import Blueprint, render_template

bp = Blueprint('frontend', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@bp.route('/teacher_dashboard')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@bp.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')
