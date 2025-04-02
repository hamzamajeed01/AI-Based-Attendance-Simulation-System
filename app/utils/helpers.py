from datetime import datetime, timedelta
from app.models.models import Employee, AttendanceRecord, Break, Alert, db
from config.config import Config

def calculate_work_hours(time_in, time_out, breaks):
    if not time_in or not time_out:
        return None
        
    total_break_duration = 0
    for break_record in breaks:
        if break_record.duration:
            total_break_duration += break_record.duration
            
    total_seconds = (time_out - time_in).total_seconds()
    total_hours = total_seconds / 3600 - (total_break_duration / 60)
    
    return max(0, total_hours)

def calculate_break_duration(start_time, end_time):
    if not start_time or not end_time:
        return None
        
    duration_seconds = (end_time - start_time).total_seconds()
    return duration_seconds / 60  # Convert to minutes

def get_current_attendance_record(employee_id, current_date):
    return AttendanceRecord.query.filter_by(
        employee_id=employee_id,
        date=current_date
    ).first()

def create_attendance_record(employee_id, current_time):
    record = AttendanceRecord(
        employee_id=employee_id,
        date=current_time.date(),
        time_in=current_time
    )
    db.session.add(record)
    db.session.commit()
    return record

def record_time_out(record, current_time):
    record.time_out = current_time
    record.total_hours = calculate_work_hours(record.time_in, current_time, record.breaks)
    db.session.commit()
    return record

def start_break(record, current_time):
    break_record = Break(
        attendance_record_id=record.id,
        start_time=current_time
    )
    db.session.add(break_record)
    db.session.commit()
    return break_record

def end_break(break_record, current_time):
    break_record.end_time = current_time
    break_record.duration = calculate_break_duration(break_record.start_time, current_time)
    db.session.commit()
    return break_record

def get_active_break(record):
    return Break.query.filter_by(
        attendance_record_id=record.id,
        end_time=None
    ).first()

def create_alert(employee_id, alert_info):
    alert = Alert(
        employee_id=employee_id,
        alert_type=alert_info['type'],
        severity=alert_info['severity'],
        description=alert_info['description']
    )
    db.session.add(alert)
    db.session.commit()
    return alert

def check_consecutive_anomalies(employee_id, days=7):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    records = AttendanceRecord.query.filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date >= start_date,
        AttendanceRecord.date <= end_date,
        AttendanceRecord.is_anomaly == True
    ).order_by(AttendanceRecord.date.desc()).all()
    
    if len(records) >= Config.CONSECUTIVE_ANOMALIES_THRESHOLD:
        return True
    return False

def generate_random_attendance_data(employee, date, normal=True):
    from random import randint, choice, random
    
    # Base times
    normal_start = datetime.strptime(Config.NORMAL_WORK_START, '%H:%M').time()
    normal_end = datetime.strptime(Config.NORMAL_WORK_END, '%H:%M').time()
    
    if normal:
        # Normal behavior - arrive around 9AM, leave around 5PM
        time_in_variance = randint(-10, 15)  # -10 to +15 minutes
        time_out_variance = randint(-15, 20)  # -15 to +20 minutes
    else:
        # Anomalous behavior - significantly early/late
        time_in_variance = choice([randint(-60, -30), randint(30, 90)])
        time_out_variance = choice([randint(-90, -45), randint(45, 120)])
    
    time_in = datetime.combine(date, normal_start) + timedelta(minutes=time_in_variance)
    time_out = datetime.combine(date, normal_end) + timedelta(minutes=time_out_variance)
    
    # Create the attendance record
    record = AttendanceRecord(
        employee_id=employee.id,
        date=date,
        time_in=time_in,
        time_out=time_out
    )
    db.session.add(record)
    db.session.flush()
    
    # Add breaks
    num_breaks = randint(1, 3) if normal else randint(3, 5)
    
    for _ in range(num_breaks):
        # Create a break sometime between check-in and check-out
        time_range = (time_out - time_in).total_seconds() / 60  # in minutes
        break_start_minutes = randint(60, int(time_range - 60))  # Start break after 1h of work, end at least 1h before leaving
        break_start = time_in + timedelta(minutes=break_start_minutes)
        
        if normal:
            break_duration = randint(10, 20) if random() < 0.7 else Config.LUNCH_BREAK_DURATION
        else:
            break_duration = randint(25, 90)  # Longer breaks for anomalous behavior
            
        break_end = break_start + timedelta(minutes=break_duration)
        
        break_record = Break(
            attendance_record_id=record.id,
            start_time=break_start,
            end_time=break_end,
            duration=break_duration
        )
        db.session.add(break_record)
    
    # Calculate total hours
    db.session.flush()
    record.total_hours = calculate_work_hours(record.time_in, record.time_out, record.breaks)
    
    return record 