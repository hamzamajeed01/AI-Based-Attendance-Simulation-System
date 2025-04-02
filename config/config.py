import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "data", "attendance.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Work hour settings
    NORMAL_WORK_START = '09:00'  # 9 AM
    NORMAL_WORK_END = '17:00'    # 5 PM
    WORK_HOURS_PER_DAY = 8.0
    LUNCH_BREAK_DURATION = 60    # in minutes
    NORMAL_BREAK_DURATION = 15   # in minutes
    
    # Anomaly detection settings
    LATE_THRESHOLD = 30          # minutes
    EARLY_DEPARTURE_THRESHOLD = 30  # minutes
    ABNORMAL_BREAK_THRESHOLD = 1.5  # multiplier of normal break duration
    CONSECUTIVE_ANOMALIES_THRESHOLD = 3  # number of consecutive anomalies before critical alert
    MULTIPLE_SWIPE_THRESHOLD = 3 # number of swipes within short period
    TIME_WINDOW_FOR_MULTIPLE_SWIPES = 5  # minutes
    
    # Alert severity levels
    SEVERITY_LEVELS = {
        'LOW': 'low',
        'MEDIUM': 'medium',
        'HIGH': 'high',
        'CRITICAL': 'critical'
    }
    
    # Alert types
    ALERT_TYPES = {
        'LATE_ARRIVAL': 'Late Arrival',
        'EARLY_DEPARTURE': 'Early Departure',
        'EXTENDED_BREAK': 'Extended Break',
        'MISSING_CHECK_IN': 'Missing Check-in',
        'MISSING_CHECK_OUT': 'Missing Check-out',
        'MULTIPLE_SWIPES': 'Multiple Swipes',
        'UNUSUAL_PATTERN': 'Unusual Pattern',
        'SHORT_WORKDAY': 'Short Workday',
        'CONSECUTIVE_ANOMALIES': 'Consecutive Anomalies'
    } 