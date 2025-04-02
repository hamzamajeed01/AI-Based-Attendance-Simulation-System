from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from app.models.models import Employee, AttendanceRecord, Break, Alert, db
from sqlalchemy import func, desc

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    # Get current date
    today = datetime.now().date()
    
    # Get total employees count
    total_employees = Employee.query.count()
    
    # Get present today count (employees who have checked in today)
    present_today = AttendanceRecord.query.filter_by(date=today).count()
    
    # Get employees currently on break
    on_break_count = db.session.query(AttendanceRecord, Break).join(
        Break, AttendanceRecord.id == Break.attendance_record_id
    ).filter(
        AttendanceRecord.date == today,
        Break.end_time == None
    ).count()
    
    # Get alerts today count
    alerts_today = Alert.query.filter(
        func.date(Alert.timestamp) == today
    ).count()
    
    # Get attendance trend for the past 7 days
    attendance_trend = get_attendance_trend(7)
    
    # Get alert types distribution
    alert_types = get_alert_types_distribution()
    
    return jsonify({
        'total_employees': total_employees,
        'present_today': present_today,
        'on_break': on_break_count,
        'alerts_today': alerts_today,
        'attendance_trend': attendance_trend,
        'alert_types': alert_types
    }), 200

@dashboard_bp.route('/activities', methods=['GET'])
def get_recent_activities():
    # Get recent check-ins, check-outs, and alerts
    today = datetime.now().date()
    activities = []
    
    # Recent check-ins
    recent_checkins = AttendanceRecord.query.filter(
        AttendanceRecord.date >= today - timedelta(days=1),
        AttendanceRecord.time_in != None
    ).order_by(AttendanceRecord.time_in.desc()).limit(5).all()
    
    for record in recent_checkins:
        employee = Employee.query.get(record.employee_id)
        activities.append({
            'time': record.time_in.strftime('%Y-%m-%d %H:%M:%S'),
            'description': f'{employee.name} checked in'
        })
    
    # Recent check-outs
    recent_checkouts = AttendanceRecord.query.filter(
        AttendanceRecord.date >= today - timedelta(days=1),
        AttendanceRecord.time_out != None
    ).order_by(AttendanceRecord.time_out.desc()).limit(5).all()
    
    for record in recent_checkouts:
        employee = Employee.query.get(record.employee_id)
        activities.append({
            'time': record.time_out.strftime('%Y-%m-%d %H:%M:%S'),
            'description': f'{employee.name} checked out'
        })
    
    # Recent alerts
    recent_alerts = Alert.query.filter(
        Alert.timestamp >= datetime.now() - timedelta(days=1)
    ).order_by(Alert.timestamp.desc()).limit(5).all()
    
    for alert in recent_alerts:
        employee = Employee.query.get(alert.employee_id)
        activities.append({
            'time': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'description': f'Alert for {employee.name}: {alert.alert_type}'
        })
    
    # Sort activities by time, most recent first
    activities.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M:%S'), reverse=True)
    
    return jsonify({
        'activities': activities[:10]  # Return top 10 activities
    }), 200

def get_attendance_trend(days):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    dates = []
    present_counts = []
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        count = AttendanceRecord.query.filter_by(date=current_date).count()
        present_counts.append(count)
        current_date += timedelta(days=1)
    
    return {
        'dates': dates,
        'present': present_counts
    }

def get_alert_types_distribution():
    # Count alerts for each severity level
    low_count = Alert.query.filter_by(severity='low').count()
    medium_count = Alert.query.filter_by(severity='medium').count()
    high_count = Alert.query.filter_by(severity='high').count()
    critical_count = Alert.query.filter_by(severity='critical').count()
    
    return {
        'Low': low_count,
        'Medium': medium_count,
        'High': high_count,
        'Critical': critical_count
    } 