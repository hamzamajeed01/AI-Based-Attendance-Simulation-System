# Attendance Simulation System

A comprehensive Flask-based RFID attendance system simulation that tracks employee check-ins/outs, breaks, working hours, and includes advanced anomaly detection capabilities.

## Overview

This system simulates an RFID-based employee attendance tracking system using Flask as the backend framework and SQLite as the database. It implements a full-featured attendance management solution with real-time tracking, anomaly detection, and an administrative dashboard for monitoring and analytics.

The simulation allows for generating historical attendance data, simulating a full day of attendance activities, and provides an interactive mode for manual testing, all without requiring actual RFID hardware.

## Key Features

### Core Attendance Tracking
- **RFID-based Authentication**: Simulates RFID card scanning for employee identification
- **Time Tracking**: Records precise check-in and check-out times
- **Break Management**: Tracks break starts, ends, and durations
- **Working Hours Calculation**: Automatically computes total working hours with break deductions
- **Historical Data**: Maintains complete attendance history for reporting and analysis

### Advanced Anomaly Detection
- **Machine Learning Integration**: Uses Isolation Forest algorithm to detect unusual patterns
- **Rule-based Detection**: Identifies common attendance anomalies through predefined rules
- **Multiple Anomaly Types**: Detects various anomalies including:
  - Late arrivals and early departures
  - Extended or excessive breaks
  - Short workdays (insufficient hours)
  - Missing check-ins or check-outs
  - Multiple card swipes in short periods
  - Pattern-based anomalies using historical data analysis
- **Severity Classification**: Categorizes alerts by severity level (low, medium, high, critical)
- **Consecutive Anomaly Detection**: Escalates severity for repeated anomalous behavior

### Admin Dashboard
- **Real-time Overview**: Dashboard with current attendance statistics
- **Visual Analytics**: Charts and graphs for attendance trends and anomaly distribution
- **Employee Management**: Search, view, and manage employee information
- **Alert Monitoring**: View and filter alerts by severity and time period
- **Reporting Tools**: Generate attendance, anomaly, and work hour reports

### Simulation Capabilities
- **Dummy Data Generation**: Creates realistic employee profiles for testing
- **Historical Data Simulation**: Generates past attendance records with normal and anomalous patterns
- **Full Day Simulation**: Automates a complete day of check-ins, breaks, and check-outs
- **Interactive Mode**: Allows manual simulation of attendance activities
- **Anomaly Injection**: Randomly introduces anomalies to test detection capabilities

## Technical Implementation

### Architecture
- **Backend**: Flask-based RESTful API architecture
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript with Chart.js for visualizations
- **API Design**: RESTful endpoints for attendance, employees, alerts, and dashboard data

### Data Models
- **Employee**: Stores employee information and RFID tag identifiers
- **AttendanceRecord**: Tracks daily attendance with time stamps
- **Break**: Records break periods within attendance records
- **Alert**: Stores anomaly detection results with severity indicators

### Anomaly Detection System
The system employs a two-pronged approach to anomaly detection:

1. **Rule-based Detection**:
   - Predefined rules for common attendance violations
   - Configurable thresholds for late arrivals, early departures, etc.
   - Real-time detection during check-in/out events

2. **Machine Learning Detection**:
   - Isolation Forest algorithm for unsupervised anomaly detection
   - Feature extraction from attendance patterns
   - Training on historical data to establish normal behavior baselines
   - Detection of complex or subtle anomalies that rules might miss

### Simulation Engine
The simulation engine provides several modes:

- **Seed Database**: Creates initial employee data for testing
- **Historical Data Generation**: Creates realistic attendance history
- **Day Simulation**: Simulates a full day with various attendance events
- **Interactive Mode**: Allows manual triggering of attendance events

## Project Structure

```
attendance-system/
├── app/                    # Main application code
│   ├── api/                # API routes
│   │   ├── attendance.py   # Attendance APIs
│   │   ├── dashboard.py    # Dashboard data APIs
│   │   ├── employees.py    # Employee management APIs
│   │   └── web.py          # Web routes
│   ├── models/             # Database models
│   │   └── models.py       # All data models
│   ├── utils/              # Utility functions
│   │   ├── anomaly_detector.py  # Anomaly detection logic
│   │   └── helpers.py      # Helper functions
│   ├── static/             # Static files (CSS, JS)
│   │   ├── css/
│   │   └── js/
│   └── templates/          # HTML templates
│       ├── admin/
│       └── index.html
├── config/                 # Configuration files
│   └── config.py           # App configuration
├── data/                   # SQLite database and other data
├── app.py                  # Main application entry point
├── run_simulation.py       # Script to run automated simulations
└── requirements.txt        # Project dependencies
```

## Anomaly Detection Details

The anomaly detection system works in several layers:

### Layer 1: Direct Rules
- Late arrivals (configurable threshold)
- Early departures (configurable threshold)
- Missing check-ins or check-outs
- Extended breaks (configurable threshold)
- Short workdays (less than expected hours)

### Layer 2: Pattern Analysis
- Multiple card swipes in short periods
- Sequence anomalies in check-in/out patterns

### Layer 3: Machine Learning
- Isolation Forest algorithm for detecting outliers
- Features used:
  - Time-in (converted to minutes)
  - Time-out (converted to minutes)
  - Break duration totals
  - Work duration
  - Number of breaks taken
- The model is trained on historical data to learn normal patterns
- New attendance records are compared against this model

### Layer 4: Consecutive Anomaly Detection
- Tracks repeated anomalies over time
- Escalates severity for persistent offenders
- Creates critical alerts after configurable threshold is reached

## Usage Instructions

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```
   This will start the server at http://localhost:5000

2. Access the admin dashboard:
   - Open your browser and go to http://localhost:5000/admin

### Running Simulations

The application includes a simulation script that can generate data and simulate attendance activities.

#### Seeding the Database

To create initial employee data:
```bash
python run_simulation.py --seed
```

#### Generating Historical Data

To generate attendance history for a specified number of days:
```bash
python run_simulation.py --historical --days 30
```

#### Simulating a Full Day

To simulate a full day of attendance activities:
```bash
python run_simulation.py --simulate
```

#### Interactive Mode

For manual simulation of attendance activities:
```bash
python run_simulation.py --interactive
```

## Configuration

Key settings can be adjusted in `config/config.py`:

- Work hour expectations (normal start/end times, break durations)
- Anomaly detection thresholds (late threshold, early departure threshold, etc.)
- Alert severity levels
- Database settings

## API Endpoints

The system provides several API endpoints:

### Attendance APIs
- `POST /api/attendance/swipe`: Record attendance event (check-in, check-out, break)
- `GET /api/attendance/<employee_id>`: Get attendance records for an employee
- `GET /api/alerts`: Get attendance anomaly alerts with optional filters
- `POST /api/train-model`: Train the anomaly detection model

### Employee APIs
- `GET /api/employees/`: Get all employees
- `GET /api/employees/<employee_id>`: Get specific employee
- `POST /api/employees/`: Add a new employee
- `PUT /api/employees/<employee_id>`: Update employee information
- `DELETE /api/employees/<employee_id>`: Delete an employee
- `GET /api/employees/search`: Search for employees

### Dashboard APIs
- `GET /api/dashboard/stats`: Get dashboard statistics
- `GET /api/dashboard/activities`: Get recent attendance activities

## Security Considerations

In a production environment, the following security enhancements would be recommended:

- Implement proper authentication and authorization
- Add HTTPS to secure API communications
- Implement rate limiting on API endpoints
- Add input validation for all user inputs
- Set up proper database backup and recovery processes

## Future Enhancements

Potential areas for expansion:

- Mobile application for remote attendance tracking
- Integration with actual RFID hardware
- Face recognition as an additional authentication method
- Advanced analytics for workforce management
- Integration with HR systems
- Email/SMS notifications for anomalies
- Geolocation verification for attendance events

## License

[MIT License](LICENSE)

## Acknowledgments

- Flask framework
- SQLAlchemy ORM
- Scikit-learn for machine learning algorithms
- Chart.js for dashboard visualizations 