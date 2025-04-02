from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html') 