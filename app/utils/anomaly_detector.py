import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from datetime import datetime, time
from config.config import Config

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.trained = False
        
    def train_model(self, attendance_records):
        if not attendance_records or len(attendance_records) < 10:
            return False
            
        features = self._extract_features(attendance_records)
        if len(features) > 0:
            self.model.fit(features)
            self.trained = True
            return True
        return False
    
    def _extract_features(self, attendance_records):
        features = []
        
        for record in attendance_records:
            if record.time_in and record.time_out:
                time_in_minutes = self._time_to_minutes(record.time_in.time())
                time_out_minutes = self._time_to_minutes(record.time_out.time())
                total_breaks_duration = sum([b.duration or 0 for b in record.breaks])
                work_duration = record.total_hours * 60 if record.total_hours else 0
                
                features.append([
                    time_in_minutes,
                    time_out_minutes,
                    total_breaks_duration,
                    work_duration,
                    len(record.breaks)
                ])
                
        return np.array(features) if features else np.array([])
    
    def _time_to_minutes(self, t):
        return t.hour * 60 + t.minute
    
    def detect_anomalies(self, record):
        anomalies = []
        
        # Check if time_in exists
        if not record.time_in:
            anomalies.append({
                'type': Config.ALERT_TYPES['MISSING_CHECK_IN'],
                'severity': Config.SEVERITY_LEVELS['HIGH'],
                'description': 'Missing check-in record detected.'
            })
            return anomalies
            
        # Check for late arrival
        normal_start = datetime.strptime(Config.NORMAL_WORK_START, '%H:%M').time()
        normal_start_dt = datetime.combine(record.date, normal_start)
        if record.time_in > normal_start_dt + timedelta(minutes=Config.LATE_THRESHOLD):
            minutes_late = (record.time_in - normal_start_dt).total_seconds() / 60
            anomalies.append({
                'type': Config.ALERT_TYPES['LATE_ARRIVAL'],
                'severity': Config.SEVERITY_LEVELS['MEDIUM'],
                'description': f'Late arrival detected. Employee arrived {int(minutes_late)} minutes late.'
            })
            
        # Check for early departure if time_out exists
        if record.time_out:
            normal_end = datetime.strptime(Config.NORMAL_WORK_END, '%H:%M').time()
            normal_end_dt = datetime.combine(record.date, normal_end)
            if record.time_out < normal_end_dt - timedelta(minutes=Config.EARLY_DEPARTURE_THRESHOLD):
                minutes_early = (normal_end_dt - record.time_out).total_seconds() / 60
                anomalies.append({
                    'type': Config.ALERT_TYPES['EARLY_DEPARTURE'],
                    'severity': Config.SEVERITY_LEVELS['MEDIUM'],
                    'description': f'Early departure detected. Employee left {int(minutes_early)} minutes early.'
                })
        else:
            anomalies.append({
                'type': Config.ALERT_TYPES['MISSING_CHECK_OUT'],
                'severity': Config.SEVERITY_LEVELS['MEDIUM'],
                'description': 'Missing check-out record detected.'
            })
            
        # Check for extended breaks
        for break_record in record.breaks:
            if break_record.duration and break_record.duration > Config.NORMAL_BREAK_DURATION * Config.ABNORMAL_BREAK_THRESHOLD:
                excess_minutes = break_record.duration - Config.NORMAL_BREAK_DURATION
                anomalies.append({
                    'type': Config.ALERT_TYPES['EXTENDED_BREAK'],
                    'severity': Config.SEVERITY_LEVELS['LOW'],
                    'description': f'Extended break detected. Break was {int(excess_minutes)} minutes longer than usual.'
                })
                
        # Check for short workday
        if record.total_hours and record.total_hours < Config.WORK_HOURS_PER_DAY * 0.75:
            anomalies.append({
                'type': Config.ALERT_TYPES['SHORT_WORKDAY'],
                'severity': Config.SEVERITY_LEVELS['MEDIUM'],
                'description': f'Short workday detected. Employee worked only {record.total_hours:.2f} hours.'
            })
            
        # Use machine learning model for unusual pattern detection if trained
        if self.trained and record.time_in and record.time_out:
            features = self._extract_features([record])
            if len(features) > 0:
                prediction = self.model.predict(features)
                if prediction[0] == -1:  # -1 indicates anomaly
                    anomalies.append({
                        'type': Config.ALERT_TYPES['UNUSUAL_PATTERN'],
                        'severity': Config.SEVERITY_LEVELS['HIGH'],
                        'description': 'Unusual attendance pattern detected by machine learning model.'
                    })
                    
        return anomalies
        
    def detect_multiple_swipes(self, employee_id, timestamp, recent_swipes):
        relevant_swipes = [s for s in recent_swipes 
                           if s['employee_id'] == employee_id 
                           and (timestamp - s['timestamp']).total_seconds() / 60 <= Config.TIME_WINDOW_FOR_MULTIPLE_SWIPES]
        
        if len(relevant_swipes) >= Config.MULTIPLE_SWIPE_THRESHOLD:
            return {
                'type': Config.ALERT_TYPES['MULTIPLE_SWIPES'],
                'severity': Config.SEVERITY_LEVELS['HIGH'],
                'description': f'Multiple card swipes detected within {Config.TIME_WINDOW_FOR_MULTIPLE_SWIPES} minutes.'
            }
        return None 