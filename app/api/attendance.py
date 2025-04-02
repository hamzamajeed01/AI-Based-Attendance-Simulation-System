from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.models import Employee, AttendanceRecord, Break, Alert, db
from app.utils.helpers import (
    get_current_attendance_record, create_attendance_record,
    record_time_out, start_break, end_break, get_active_break,
    create_alert, check_consecutive_anomalies
)
from app.utils.anomaly_detector import AnomalyDetector
from config.config import Config

attendance_bp = Blueprint('attendance', __name__)
anomaly_detector = AnomalyDetector()

# Keep track of recent swipes to detect multiple swipes
recent_swipes = []

@attendance_bp.route('/swipe', methods=['POST'])
def swipe_card():
    global recent_swipes
    data = request.get_json()
    
    if not data or 'rfid_tag' not in data:
        return jsonify({'error': 'RFID tag is required'}), 400
    
    rfid_tag = data['rfid_tag']
    current_time = datetime.now()
    
    # Find the employee by RFID tag
    employee = Employee.query.filter_by(rfid_tag=rfid_tag).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Check for multiple swipes
    recent_swipes.append({
        'employee_id': employee.id,
        'timestamp': current_time
    })
    
    # Keep only recent swipes
    recent_swipes = [s for s in recent_swipes 
                    if (current_time - s['timestamp']).total_seconds() / 60 <= Config.TIME_WINDOW_FOR_MULTIPLE_SWIPES]
    
    # Check for multiple swipes anomaly
    multiple_swipes_alert = anomaly_detector.detect_multiple_swipes(
        employee.id, current_time, recent_swipes
    )
    
    if multiple_swipes_alert:
        create_alert(employee.id, multiple_swipes_alert)
    
    # Get or create today's attendance record
    current_date = current_time.date()
    record = get_current_attendance_record(employee.id, current_date)
    
    # New actions based on current state
    if not record:
        # First check-in of the day
        record = create_attendance_record(employee.id, current_time)
        return jsonify({
            'message': f'Check-in recorded for {employee.name}',
            'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'checked_in'
        }), 201
    
    if not record.time_out:
        # Employee already checked in
        active_break = get_active_break(record)
        
        if active_break:
            # End an active break
            end_break(active_break, current_time)
            return jsonify({
                'message': f'Break ended for {employee.name}',
                'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'break_ended',
                'break_duration': f'{active_break.duration:.2f} minutes'
            }), 200
        else:
            # Either checking out or starting a break
            if data.get('action') == 'break':
                # Start a break
                break_record = start_break(record, current_time)
                return jsonify({
                    'message': f'Break started for {employee.name}',
                    'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'break_started'
                }), 200
            else:
                # Check out
                record_time_out(record, current_time)
                
                # Detect anomalies and create alerts
                anomalies = anomaly_detector.detect_anomalies(record)
                if anomalies:
                    record.is_anomaly = True
                    db.session.commit()
                    
                    for anomaly in anomalies:
                        create_alert(employee.id, anomaly)
                    
                    # Check for consecutive anomalies
                    if check_consecutive_anomalies(employee.id):
                        consecutive_alert = {
                            'type': Config.ALERT_TYPES['CONSECUTIVE_ANOMALIES'],
                            'severity': Config.SEVERITY_LEVELS['CRITICAL'],
                            'description': f'Employee has shown {Config.CONSECUTIVE_ANOMALIES_THRESHOLD} or more anomalies in the past week.'
                        }
                        create_alert(employee.id, consecutive_alert)
                
                return jsonify({
                    'message': f'Check-out recorded for {employee.name}',
                    'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'checked_out',
                    'total_hours': f'{record.total_hours:.2f} hours'
                }), 200
    else:
        # Employee already checked out
        return jsonify({
            'message': f'{employee.name} already checked out today',
            'time': record.time_out.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'already_checked_out'
        }), 400

@attendance_bp.route('/attendance/<employee_id>', methods=['GET'])
def get_employee_attendance(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Optional date filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AttendanceRecord.query.filter_by(employee_id=employee.id)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(AttendanceRecord.date >= start_date)
        except ValueError:
            pass
            
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(AttendanceRecord.date <= end_date)
        except ValueError:
            pass
    
    records = query.order_by(AttendanceRecord.date.desc()).all()
    
    return jsonify({
        'employee': employee.serialize(),
        'records': [record.serialize() for record in records]
    }), 200

@attendance_bp.route('/alerts', methods=['GET'])
def get_alerts():
    # Optional employee and severity filtering
    employee_id = request.args.get('employee_id')
    severity = request.args.get('severity')
    
    query = Alert.query
    
    if employee_id:
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        if employee:
            query = query.filter_by(employee_id=employee.id)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.timestamp.desc()).all()
    
    return jsonify({
        'alerts': [alert.serialize() for alert in alerts]
    }), 200

@attendance_bp.route('/train-model', methods=['POST'])
def train_anomaly_model():
    records = AttendanceRecord.query.all()
    
    if anomaly_detector.train_model(records):
        return jsonify({'message': 'Anomaly detection model trained successfully'}), 200
    else:
        return jsonify({'error': 'Not enough data to train the model'}), 400 