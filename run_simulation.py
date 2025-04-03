import os
import sys
import json
import random
import time
import requests
from datetime import datetime, timedelta
import argparse
# Import from app_main to avoid confusion with the app package
from app_main import app, create_app
from app.models.models import Employee, AttendanceRecord, Break, Alert, db
from app.utils.helpers import generate_random_attendance_data, get_active_break

# Sample employee data for seeding the database
SAMPLE_EMPLOYEES = [
    {
        'employee_id': 'EMP001',
        'rfid_tag': '5F3C7A9E1B',
        'name': 'John Smith',
        'department': 'Engineering',
        'position': 'Software Developer'
    },
    {
        'employee_id': 'EMP002',
        'rfid_tag': '8D2E6F4A1C',
        'name': 'Emily Johnson',
        'department': 'Marketing',
        'position': 'Marketing Manager'
    },
    {
        'employee_id': 'EMP003',
        'rfid_tag': '3A7B9C2D1E',
        'name': 'Michael Brown',
        'department': 'Finance',
        'position': 'Financial Analyst'
    },
    {
        'employee_id': 'EMP004',
        'rfid_tag': '6E1D8F5A2C',
        'name': 'Sarah Davis',
        'department': 'Human Resources',
        'position': 'HR Specialist'
    },
    {
        'employee_id': 'EMP005',
        'rfid_tag': '9C4B7E2A1F',
        'name': 'David Wilson',
        'department': 'Operations',
        'position': 'Operations Manager'
    },
    {
        'employee_id': 'EMP006',
        'rfid_tag': '2D8E5F1A9C',
        'name': 'Jessica Taylor',
        'department': 'Engineering',
        'position': 'QA Engineer'
    },
    {
        'employee_id': 'EMP007',
        'rfid_tag': '7B3A1F8E2D',
        'name': 'Daniel Martinez',
        'department': 'Sales',
        'position': 'Sales Representative'
    },
    {
        'employee_id': 'EMP008',
        'rfid_tag': '4F9E2C7B1A',
        'name': 'Elizabeth Anderson',
        'department': 'Engineering',
        'position': 'DevOps Engineer'
    },
    {
        'employee_id': 'EMP009',
        'rfid_tag': '1A5C8F3E7D',
        'name': 'Christopher Thomas',
        'department': 'Customer Support',
        'position': 'Support Specialist'
    },
    {
        'employee_id': 'EMP010',
        'rfid_tag': '8E2A6C1D9F',
        'name': 'Amanda White',
        'department': 'Product',
        'position': 'Product Manager'
    }
]

def seed_database():
    """Seed the database with sample employee data"""
    print("Seeding database with sample employees...")
    
    # Create a new app instance using the imported create_app function
    flask_app = create_app()
    with flask_app.app_context():
        # Check if we already have employees
        if Employee.query.count() > 0:
            print("Database already seeded with employees.")
            return
            
        # Add sample employees
        for employee_data in SAMPLE_EMPLOYEES:
            employee = Employee(**employee_data)
            db.session.add(employee)
            
        db.session.commit()
        print(f"Successfully added {len(SAMPLE_EMPLOYEES)} employees.")

def generate_historical_data(days_back=30):
    """Generate historical attendance data for specified number of days"""
    print(f"Generating historical attendance data for the past {days_back} days...")
    
    # Create a new app instance using the imported create_app function
    flask_app = create_app()
    with flask_app.app_context():
        # Get all employees
        employees = Employee.query.all()
        
        if not employees:
            print("No employees found in database. Run seed_database first.")
            return
            
        # Generate data for each day
        end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=days_back-1)
        
        # Clear existing historical data in this range
        AttendanceRecord.query.filter(
            AttendanceRecord.date >= start_date,
            AttendanceRecord.date <= end_date
        ).delete()
        db.session.commit()
        
        # Generate new data
        print(f"Generating attendance data from {start_date} to {end_date}...")
        
        total_records = 0
        current_date = start_date
        
        while current_date <= end_date:
            print(f"Generating data for {current_date}...")
            day_records = 0
            
            for employee in employees:
                # Randomly skip some employees (weekends, vacations, etc.)
                if random.random() < 0.2:  # 20% chance of absence
                    continue
                    
                # Randomly determine if this will be an anomalous day (10% chance)
                is_anomaly = random.random() < 0.1
                
                # Generate attendance record
                record = generate_random_attendance_data(employee, current_date, not is_anomaly)
                
                # Mark as anomaly if applicable
                if is_anomaly:
                    record.is_anomaly = True
                
                db.session.add(record)
                day_records += 1
                
            db.session.commit()
            total_records += day_records
            print(f"  Added {day_records} records for {current_date}")
            
            current_date += timedelta(days=1)
            
        print(f"Successfully generated {total_records} historical attendance records.")
        
        # Train the anomaly detection model
        print("Training anomaly detection model on historical data...")
        requests.post('http://localhost:5000/api/train-model')

def simulate_day():
    """Simulate a full day of attendance activities"""
    print("Starting full day attendance simulation...")
    
    # Create a new app instance using the imported create_app function
    flask_app = create_app()
    with flask_app.app_context():
        # Get all employees
        employees = Employee.query.all()
        
        if not employees:
            print("No employees found in database. Run seed_database first.")
            return
            
        # Today's date
        today = datetime.now().date()
        
        # Clear any existing records for today
        AttendanceRecord.query.filter_by(date=today).delete()
        db.session.commit()
        
        # Simulate morning check-ins (8:30 AM - 9:30 AM)
        print("Simulating morning check-ins...")
        base_time = datetime.combine(today, datetime.strptime("08:30", "%H:%M").time())
        
        for employee in employees:
            # Some employees might be absent
            if random.random() < 0.1:  # 10% chance of absence
                continue
                
            # Random check-in time between 8:30 and 9:30
            minutes_offset = random.randint(0, 60)
            check_in_time = base_time + timedelta(minutes=minutes_offset)
            
            # Multiple swipes for some employees
            swipe_count = random.choices([1, 2, 3, 4], weights=[0.7, 0.2, 0.05, 0.05])[0]
            
            for i in range(swipe_count):
                # Small time difference between swipes
                swipe_time = check_in_time + timedelta(seconds=random.randint(0, 30))
                
                data = {
                    'rfid_tag': employee.rfid_tag
                }
                
                try:
                    response = requests.post('http://localhost:5000/api/attendance/swipe', json=data)
                    print(f"  {swipe_time.strftime('%H:%M:%S')} - {employee.name} swiped in: {response.status_code}")
                    time.sleep(0.5)  # Small delay between API calls
                except Exception as e:
                    print(f"  Error during check-in for {employee.name}: {str(e)}")
        
        # Simulate morning breaks (10:30 AM - 11:30 AM)
        print("Simulating morning breaks...")
        base_time = datetime.combine(today, datetime.strptime("10:30", "%H:%M").time())
        
        # Get employees who checked in
        records = AttendanceRecord.query.filter_by(date=today).all()
        for record in records:
            # Not all employees take morning breaks
            if random.random() < 0.3:  # 70% take morning breaks
                continue
                
            employee = Employee.query.get(record.employee_id)
            
            # Random break time between 10:30 and 11:30
            minutes_offset = random.randint(0, 60)
            break_time = base_time + timedelta(minutes=minutes_offset)
            
            data = {
                'rfid_tag': employee.rfid_tag,
                'action': 'break'
            }
            
            try:
                response = requests.post('http://localhost:5000/api/attendance/swipe', json=data)
                print(f"  {break_time.strftime('%H:%M:%S')} - {employee.name} started break: {response.status_code}")
                time.sleep(0.5)  # Small delay between API calls
                
                # End break after 10-20 minutes
                break_duration = random.randint(10, 20)
                end_break_time = break_time + timedelta(minutes=break_duration)
                
                # Simulate time passing
                print(f"  (Waiting for {break_duration} minutes of break time...)")
                time.sleep(2)  # Just a short delay for simulation
                
                # End break
                response = requests.post('http://localhost:5000/api/attendance/swipe', json={'rfid_tag': employee.rfid_tag})
                print(f"  {end_break_time.strftime('%H:%M:%S')} - {employee.name} ended break: {response.status_code}")
                
            except Exception as e:
                print(f"  Error during break for {employee.name}: {str(e)}")
        
        # Simulate lunch breaks (12:00 PM - 1:30 PM)
        print("Simulating lunch breaks...")
        base_time = datetime.combine(today, datetime.strptime("12:00", "%H:%M").time())
        
        # Get employees who checked in
        records = AttendanceRecord.query.filter_by(date=today).all()
        for record in records:
            # Almost all employees take lunch
            if random.random() < 0.1:  # 90% take lunch
                continue
                
            employee = Employee.query.get(record.employee_id)
            
            # Random lunch time between 12:00 and 1:30
            minutes_offset = random.randint(0, 90)
            lunch_time = base_time + timedelta(minutes=minutes_offset)
            
            data = {
                'rfid_tag': employee.rfid_tag,
                'action': 'break'
            }
            
            try:
                response = requests.post('http://localhost:5000/api/attendance/swipe', json=data)
                print(f"  {lunch_time.strftime('%H:%M:%S')} - {employee.name} started lunch: {response.status_code}")
                time.sleep(0.5)  # Small delay between API calls
                
                # End lunch after 30-60 minutes
                lunch_duration = random.randint(30, 60)
                end_lunch_time = lunch_time + timedelta(minutes=lunch_duration)
                
                # Simulate time passing
                print(f"  (Waiting for {lunch_duration} minutes of lunch time...)")
                time.sleep(2)  # Just a short delay for simulation
                
                # End lunch
                response = requests.post('http://localhost:5000/api/attendance/swipe', json={'rfid_tag': employee.rfid_tag})
                print(f"  {end_lunch_time.strftime('%H:%M:%S')} - {employee.name} ended lunch: {response.status_code}")
                
            except Exception as e:
                print(f"  Error during lunch for {employee.name}: {str(e)}")
        
        # Simulate afternoon breaks (3:00 PM - 4:00 PM)
        print("Simulating afternoon breaks...")
        base_time = datetime.combine(today, datetime.strptime("15:00", "%H:%M").time())
        
        # Get employees who checked in
        records = AttendanceRecord.query.filter_by(date=today).all()
        for record in records:
            # Not all employees take afternoon breaks
            if random.random() < 0.4:  # 60% take afternoon breaks
                continue
                
            employee = Employee.query.get(record.employee_id)
            
            # Random break time between 3:00 and 4:00
            minutes_offset = random.randint(0, 60)
            break_time = base_time + timedelta(minutes=minutes_offset)
            
            data = {
                'rfid_tag': employee.rfid_tag,
                'action': 'break'
            }
            
            try:
                response = requests.post('http://localhost:5000/api/attendance/swipe', json=data)
                print(f"  {break_time.strftime('%H:%M:%S')} - {employee.name} started break: {response.status_code}")
                time.sleep(0.5)  # Small delay between API calls
                
                # End break after 10-20 minutes
                break_duration = random.randint(10, 20)
                end_break_time = break_time + timedelta(minutes=break_duration)
                
                # Simulate time passing
                print(f"  (Waiting for {break_duration} minutes of break time...)")
                time.sleep(2)  # Just a short delay for simulation
                
                # End break
                response = requests.post('http://localhost:5000/api/attendance/swipe', json={'rfid_tag': employee.rfid_tag})
                print(f"  {end_break_time.strftime('%H:%M:%S')} - {employee.name} ended break: {response.status_code}")
                
            except Exception as e:
                print(f"  Error during break for {employee.name}: {str(e)}")
        
        # Simulate evening check-outs (5:00 PM - 6:30 PM)
        print("Simulating evening check-outs...")
        base_time = datetime.combine(today, datetime.strptime("17:00", "%H:%M").time())
        
        # Get employees who checked in
        records = AttendanceRecord.query.filter_by(date=today).all()
        for record in records:
            employee = Employee.query.get(record.employee_id)
            
            # Random check-out time between 5:00 and 6:30
            minutes_offset = random.randint(0, 90)
            check_out_time = base_time + timedelta(minutes=minutes_offset)
            
            # Add some anomalies - very early departure
            if random.random() < 0.05:  # 5% chance of early departure
                check_out_time = datetime.combine(today, datetime.strptime("14:30", "%H:%M").time())
                check_out_time += timedelta(minutes=random.randint(0, 60))
            
            # Add some anomalies - very late departure
            if random.random() < 0.05:  # 5% chance of late departure
                check_out_time = datetime.combine(today, datetime.strptime("19:00", "%H:%M").time())
                check_out_time += timedelta(minutes=random.randint(0, 120))
                
            # Multiple swipes for some employees
            swipe_count = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
            
            for i in range(swipe_count):
                # Small time difference between swipes
                swipe_time = check_out_time + timedelta(seconds=random.randint(0, 30))
                
                try:
                    response = requests.post('http://localhost:5000/api/attendance/swipe', json={'rfid_tag': employee.rfid_tag})
                    print(f"  {swipe_time.strftime('%H:%M:%S')} - {employee.name} swiped out: {response.status_code}")
                    time.sleep(0.5)  # Small delay between API calls
                except Exception as e:
                    print(f"  Error during check-out for {employee.name}: {str(e)}")
        
        print("Simulation of full day completed!")

def interactive_mode():
    """Simulate individual employee actions interactively"""
    print("Interactive simulation mode started.")
    print("This mode allows you to manually simulate RFID card swipes.")
    
    # Create a new app instance using the imported create_app function
    flask_app = create_app()
    with flask_app.app_context():
        # Get all employees for reference
        employees = Employee.query.all()
        
        if not employees:
            print("No employees found in database. Run seed_database first.")
            return
            
        # Print employee list
        print("\nAvailable employees:")
        for i, emp in enumerate(employees):
            print(f"{i+1}. {emp.name} (ID: {emp.employee_id}, RFID: {emp.rfid_tag})")
        
        # Interactive session
        while True:
            print("\n=== Interactive Mode ===")
            print("1. Swipe card (check-in/out)")
            print("2. Swipe card for break")
            print("3. List all employees")
            print("4. View today's attendance")
            print("5. Exit interactive mode")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                emp_id = input("Enter employee number (or RFID tag): ")
                
                # Find employee
                employee = None
                try:
                    # Check if input is an index
                    if emp_id.isdigit() and 1 <= int(emp_id) <= len(employees):
                        employee = employees[int(emp_id) - 1]
                    else:
                        # Check if input is an RFID tag
                        employee = next((e for e in employees if e.rfid_tag == emp_id), None)
                        
                    if not employee:
                        print("Employee not found. Please try again.")
                        continue
                        
                    print(f"Selected employee: {employee.name}")
                    
                    # Send swipe request
                    data = {'rfid_tag': employee.rfid_tag}
                    response = requests.post('http://localhost:5000/api/attendance/swipe', json=data)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"SUCCESS: {response.json()['message']}")
                    else:
                        print(f"ERROR: {response.json()['error'] if 'error' in response.json() else 'Unknown error'}")
                        
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    
            elif choice == "2":
                emp_id = input("Enter employee number (or RFID tag): ")
                
                # Find employee
                employee = None
                try:
                    # Check if input is an index
                    if emp_id.isdigit() and 1 <= int(emp_id) <= len(employees):
                        employee = employees[int(emp_id) - 1]
                    else:
                        # Check if input is an RFID tag
                        employee = next((e for e in employees if e.rfid_tag == emp_id), None)
                        
                    if not employee:
                        print("Employee not found. Please try again.")
                        continue
                        
                    print(f"Selected employee: {employee.name}")
                    
                    # Send swipe request for break
                    data = {'rfid_tag': employee.rfid_tag, 'action': 'break'}
                    response = requests.post('http://localhost:5000/api/attendance/swipe', json=data)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"SUCCESS: {response.json()['message']}")
                    else:
                        print(f"ERROR: {response.json()['error'] if 'error' in response.json() else 'Unknown error'}")
                        
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    
            elif choice == "3":
                print("\nEmployees:")
                for i, emp in enumerate(employees):
                    print(f"{i+1}. {emp.name} (ID: {emp.employee_id}, RFID: {emp.rfid_tag})")
                    
            elif choice == "4":
                today = datetime.now().date()
                print(f"\nToday's attendance ({today}):")
                
                records = AttendanceRecord.query.filter_by(date=today).all()
                
                if not records:
                    print("No attendance records for today.")
                else:
                    for record in records:
                        employee = Employee.query.get(record.employee_id)
                        status = "Checked in"
                        if record.time_out:
                            status = f"Checked out (worked {record.total_hours:.2f} hours)"
                        elif get_active_break(record):
                            status = "On break"
                            
                        print(f"- {employee.name}: {status}")
                        
                        if record.breaks:
                            break_count = len(record.breaks)
                            total_break_time = sum([b.duration or 0 for b in record.breaks if b.duration])
                            print(f"  Breaks: {break_count} (Total: {total_break_time:.0f} minutes)")
                            
            elif choice == "5":
                print("Exiting interactive mode.")
                return
                
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Attendance System Simulation')
    parser.add_argument('--seed', action='store_true', help='Seed the database with sample employees')
    parser.add_argument('--historical', action='store_true', help='Generate historical attendance data')
    parser.add_argument('--days', type=int, default=30, help='Number of historical days to generate (default: 30)')
    parser.add_argument('--simulate', action='store_true', help='Simulate a full day of attendance activities')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode for manual simulation')
    
    # No need to start Flask server as it's running in a separate terminal
    print("Connecting to Flask server running on port 5000...")
    time.sleep(1)
    
    args = parser.parse_args()
    
    if args.seed:
        seed_database()
        
    if args.historical:
        generate_historical_data(args.days)
        
    if args.simulate:
        simulate_day()
        
    if args.interactive:
        interactive_mode()
        
    # If no arguments, show help
    if not (args.seed or args.historical or args.simulate or args.interactive):
        parser.print_help()
        print("\nExample usage:")
        print("  python run_simulation.py --seed")
        print("  python run_simulation.py --historical --days 14")
        print("  python run_simulation.py --simulate")
        print("  python run_simulation.py --interactive") 