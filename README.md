# Attendance Simulation System

A comprehensive Flask-based RFID attendance system simulation that tracks employee check-ins/outs, breaks, working hours, and includes advanced anomaly detection capabilities with real-time dashboard visualization.

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
- **Alert Resolution System**: Ability to mark alerts as resolved with tracking

### Interactive Dashboard
- **Real-time Overview**: Dashboard with current attendance statistics that auto-refreshes
- **Visual Analytics**: Charts and graphs for attendance trends and anomaly distribution
- **Employee Management**: Search, view, and manage employee information
- **Alert Monitoring**: View, filter, resolve, and manage alerts by severity and time period
- **Reporting Tools**: Generate attendance, anomaly, and work hour reports
- **Recent Activities Feed**: Live-updating feed of check-ins, check-outs, breaks, and alerts
- **Navigation Tabs**: Easy navigation between dashboard sections (Overview, Employees, Alerts, Reports)
- **Test Alert Generation**: Built-in functionality to generate sample alerts for testing

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
- **Auto-refresh**: Real-time data updates using JavaScript polling

### Data Models
- **Employee**: Stores employee information and RFID tag identifiers
- **AttendanceRecord**: Tracks daily attendance with time stamps
- **Break**: Records break periods within attendance records
- **Alert**: Stores anomaly detection results with severity indicators and resolution status

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
- **Historical Data Generation**: Creates realistic attendance history with configurable days
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
│   │   │   └── styles.css  # Main stylesheet
│   │   └── js/
│   │       └── dashboard.js # Dashboard functionality
│   └── templates/          # HTML templates
│       ├── admin/
│       ├── dashboard.html  # Main dashboard template
│       └── index.html
├── config/                 # Configuration files
│   └── config.py           # App configuration
├── data/                   # SQLite database and other data
├── app.py                  # Main application entry point
├── app_main.py             # Flask server initialization
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

## Dashboard Features

### Overview Section
- **Key Statistics**: Total employees, present today, on break, alerts today
- **Attendance Chart**: 7-day trend of attendance records
- **Alert Type Distribution**: Doughnut chart showing alert distribution by severity
- **Recent Activities**: Real-time feed of latest attendance activities with visual indicators
  - Check-ins (→)
  - Check-outs (←)
  - Breaks (⏸)
  - Alerts (⚠)

### Employees Section
- **Search Functionality**: Find employees by name, ID, or department
- **Employee Cards**: Visual display of employee information
- **Detailed View**: Click to see employee details including:
  - Personal information
  - Department and position
  - Join date
- **Attendance Records**: View detailed attendance history for each employee
- **Alert History**: View alerts associated with specific employees

### Alerts Section
- **Filter System**: Filter alerts by:
  - Severity (low, medium, high, critical)
  - Time period (today, this week, this month, all)
  - Employee
- **Alert Table**: Detailed view of all alerts with:
  - Timestamp
  - Employee information
  - Alert type and description
  - Severity (color-coded)
  - Status (active or resolved)
- **Actions**: View alert details or mark alerts as resolved
- **Test Alert Generation**: Generate sample alerts for testing the system

### Reports Section
- **Attendance Reports**: Overview of attendance patterns
- **Anomaly Reports**: Summary of detected anomalies
- **Hours Reports**: Analysis of working hours

## Usage Instructions

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv myenv
   ```
3. Activate the virtual environment:
   - Windows: `myenv\Scripts\activate`
   - Unix/MacOS: `source myenv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask application (in one terminal):
   ```bash
   python app_main.py
   ```
   This will start the server at http://localhost:5000

2. Access the dashboard:
   - Open your browser and go to http://localhost:5000/dashboard

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

#### All-in-One Quick Setup

To seed the database, generate 5 days of historical data, and simulate a day:
```bash
python run_simulation.py --seed --historical --days 5 --simulate
```

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
- `GET /api/dashboard/alerts`: Get alerts with filtering options
- `POST /api/dashboard/create-alert`: Create a test alert for demonstration
- `POST /api/dashboard/alerts/<alert_id>/resolve`: Mark an alert as resolved

## Recent Updates and Fixes

- **Auto-Refresh Mechanism**: Dashboard now auto-refreshes every 30 seconds to show real-time data
- **Enhanced Activities Display**: Improved visual representation of recent activities with color-coding and icons
- **Alert Generation Tool**: Added functionality to generate sample alerts for testing
- **Alert Resolution System**: Implemented system to mark alerts as resolved
- **Improved UI**: Enhanced stylesheets for better visual hierarchy and user experience
- **Fixed Issues**:
  - Resolved circular import issues between app modules
  - Fixed database column naming inconsistency between `resolved` and `is_resolved`
  - Corrected API endpoint responses to ensure proper data formatting
  - Fixed port configuration to consistently use port 5000 across all components

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
- Email/SMS notifications for critical alerts
- Integration with HR systems
- Advanced analytics and predictive modeling
- Shift management and scheduling
- Vacation and time-off tracking 