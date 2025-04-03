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
    # Get recent check-ins, check-outs, breaks, and alerts with more detail
    from flask import request
    
    # Get limit parameter (default to 10)
    limit = request.args.get('limit', 10, type=int)
    
    # Get hours parameter (default to 24 - show last 24 hours)
    hours = request.args.get('hours', 24, type=int)
    
    # Calculate the time threshold
    time_threshold = datetime.now() - timedelta(hours=hours)
    today = datetime.now().date()
    activities = []
    
    # Recent check-ins with more details
    recent_checkins = AttendanceRecord.query.filter(
        AttendanceRecord.time_in >= time_threshold
    ).order_by(AttendanceRecord.time_in.desc()).limit(limit).all()
    
    for record in recent_checkins:
        employee = Employee.query.get(record.employee_id)
        if employee:
            time_str = record.time_in.strftime('%Y-%m-%d %H:%M:%S')
            activities.append({
                'id': f"checkin_{record.id}",
                'time': time_str,
                'timestamp': record.time_in.timestamp(),
                'type': 'check-in',
                'employee_id': employee.employee_id,
                'employee_name': employee.name,
                'department': employee.department,
                'description': f'{employee.name} checked in',
                'details': {
                    'time': record.time_in.strftime('%H:%M:%S'),
                    'date': record.date.strftime('%Y-%m-%d')
                }
            })
    
    # Recent check-outs with more details
    recent_checkouts = AttendanceRecord.query.filter(
        AttendanceRecord.time_out >= time_threshold
    ).order_by(AttendanceRecord.time_out.desc()).limit(limit).all()
    
    for record in recent_checkouts:
        employee = Employee.query.get(record.employee_id)
        if employee and record.time_out:
            time_str = record.time_out.strftime('%Y-%m-%d %H:%M:%S')
            hours_worked = record.total_hours if record.total_hours else 0
            activities.append({
                'id': f"checkout_{record.id}",
                'time': time_str,
                'timestamp': record.time_out.timestamp(),
                'type': 'check-out',
                'employee_id': employee.employee_id,
                'employee_name': employee.name,
                'department': employee.department,
                'description': f'{employee.name} checked out',
                'details': {
                    'time': record.time_out.strftime('%H:%M:%S'),
                    'date': record.date.strftime('%Y-%m-%d'),
                    'hours_worked': f"{hours_worked:.2f} hours"
                }
            })
    
    # Recent breaks
    recent_breaks = Break.query.join(
        AttendanceRecord, Break.attendance_record_id == AttendanceRecord.id
    ).filter(
        Break.start_time >= time_threshold
    ).order_by(Break.start_time.desc()).limit(limit).all()
    
    for break_record in recent_breaks:
        attendance = AttendanceRecord.query.get(break_record.attendance_record_id)
        employee = Employee.query.get(attendance.employee_id) if attendance else None
        
        if employee and break_record.start_time:
            time_str = break_record.start_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Break status
            if break_record.end_time:
                status = "ended"
                duration = break_record.duration or 0
                detail = f"Duration: {duration:.0f} minutes"
            else:
                status = "started"
                detail = "Currently on break"
                
            activities.append({
                'id': f"break_{break_record.id}",
                'time': time_str,
                'timestamp': break_record.start_time.timestamp(),
                'type': 'break',
                'employee_id': employee.employee_id,
                'employee_name': employee.name,
                'department': employee.department,
                'description': f'{employee.name} {status} break',
                'details': {
                    'time': break_record.start_time.strftime('%H:%M:%S'),
                    'date': attendance.date.strftime('%Y-%m-%d'),
                    'status': status,
                    'detail': detail
                }
            })
    
    # Recent alerts with more details
    recent_alerts = Alert.query.filter(
        Alert.timestamp >= time_threshold
    ).order_by(Alert.timestamp.desc()).limit(limit).all()
    
    for alert in recent_alerts:
        employee = Employee.query.get(alert.employee_id)
        if employee:
            time_str = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            activities.append({
                'id': f"alert_{alert.id}",
                'time': time_str,
                'timestamp': alert.timestamp.timestamp(),
                'type': 'alert',
                'employee_id': employee.employee_id,
                'employee_name': employee.name,
                'department': employee.department,
                'description': f'Alert: {alert.alert_type} for {employee.name}',
                'details': {
                    'time': alert.timestamp.strftime('%H:%M:%S'),
                    'date': alert.timestamp.strftime('%Y-%m-%d'),
                    'severity': alert.severity,
                    'alert_type': alert.alert_type,
                    'description': alert.description,
                    'resolved': 'Yes' if alert.is_resolved else 'No'
                }
            })
    
    # Sort activities by time, most recent first
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Limit to requested number
    activities = activities[:limit]
    
    return jsonify({
        'activities': activities,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

@dashboard_bp.route('/alerts', methods=['GET'])
def get_alerts():
    from flask import request
    from datetime import datetime, timedelta
    
    # Get query parameters
    employee_id = request.args.get('employee_id')
    severity = request.args.get('severity')
    time_filter = request.args.get('time_filter', 'all')
    
    # Base query
    query = Alert.query
    
    # Apply filters
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
        
    if severity:
        query = query.filter_by(severity=severity)
    
    # Apply time filter
    if time_filter != 'all':
        now = datetime.now()
        if time_filter == 'today':
            start_date = datetime.combine(now.date(), datetime.min.time())
            query = query.filter(Alert.timestamp >= start_date)
        elif time_filter == 'week':
            start_date = now - timedelta(days=7)
            query = query.filter(Alert.timestamp >= start_date)
        elif time_filter == 'month':
            start_date = now - timedelta(days=30)
            query = query.filter(Alert.timestamp >= start_date)
    
    # Execute query and get results
    alerts = query.order_by(Alert.timestamp.desc()).all()
    
    # Format results
    result = []
    for alert in alerts:
        employee = Employee.query.get(alert.employee_id)
        result.append({
            'id': alert.id,
            'employee_id': alert.employee_id,
            'employee_name': employee.name if employee else 'Unknown',
            'timestamp': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'alert_type': alert.alert_type,
            'description': alert.description,
            'severity': alert.severity,
            'resolved': alert.is_resolved
        })
    
    return jsonify({
        'alerts': result
    }), 200

@dashboard_bp.route('/create-alert', methods=['POST'])
def create_test_alert():
    """Create a test alert for demonstration purposes"""
    from flask import request
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'alert_type', 'description', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create the alert
        alert = Alert(
            employee_id=data['employee_id'],
            alert_type=data['alert_type'],
            description=data['description'],
            severity=data['severity'],
            timestamp=datetime.now(),
            is_resolved=False
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'message': 'Alert created successfully',
            'alert_id': alert.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Mark an alert as resolved"""
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
            
        alert.is_resolved = True
        db.session.commit()
        
        return jsonify({
            'message': 'Alert marked as resolved',
            'alert_id': alert.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 