from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(10), unique=True, nullable=False)
    rfid_tag = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    attendance_records = db.relationship('AttendanceRecord', backref='employee', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'rfid_tag': self.rfid_tag,
            'name': self.name,
            'department': self.department,
            'position': self.position,
            'join_date': self.join_date.strftime('%Y-%m-%d')
        }

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time_in = db.Column(db.DateTime, nullable=True)
    time_out = db.Column(db.DateTime, nullable=True)
    breaks = db.relationship('Break', backref='attendance_record', lazy=True)
    total_hours = db.Column(db.Float, nullable=True)
    is_anomaly = db.Column(db.Boolean, default=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'time_in': self.time_in.strftime('%H:%M:%S') if self.time_in else None,
            'time_out': self.time_out.strftime('%H:%M:%S') if self.time_out else None,
            'total_hours': self.total_hours,
            'is_anomaly': self.is_anomaly,
            'breaks': [brk.serialize() for brk in self.breaks]
        }

class Break(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendance_record_id = db.Column(db.Integer, db.ForeignKey('attendance_record.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Float, nullable=True)  # in minutes
    
    def serialize(self):
        return {
            'id': self.id,
            'start_time': self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M:%S') if self.end_time else None,
            'duration': self.duration
        }

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    description = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'alert_type': self.alert_type,
            'severity': self.severity,
            'description': self.description,
            'is_resolved': self.is_resolved
        } 