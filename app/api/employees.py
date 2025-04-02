from flask import Blueprint, request, jsonify
from app.models.models import Employee, db

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/', methods=['GET'])
def get_all_employees():
    employees = Employee.query.all()
    return jsonify({
        'employees': [employee.serialize() for employee in employees]
    }), 200

@employees_bp.route('/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
        
    return jsonify({
        'employee': employee.serialize()
    }), 200

@employees_bp.route('/', methods=['POST'])
def add_employee():
    data = request.get_json()
    
    required_fields = ['employee_id', 'rfid_tag', 'name', 'department', 'position']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check for duplicate employee_id or rfid_tag
    if Employee.query.filter_by(employee_id=data['employee_id']).first():
        return jsonify({'error': 'Employee ID already exists'}), 400
        
    if Employee.query.filter_by(rfid_tag=data['rfid_tag']).first():
        return jsonify({'error': 'RFID tag already exists'}), 400
    
    employee = Employee(
        employee_id=data['employee_id'],
        rfid_tag=data['rfid_tag'],
        name=data['name'],
        department=data['department'],
        position=data['position']
    )
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify({
        'message': 'Employee added successfully',
        'employee': employee.serialize()
    }), 201

@employees_bp.route('/<employee_id>', methods=['PUT'])
def update_employee(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    data = request.get_json()
    
    # Check for duplicate rfid_tag if being updated
    if 'rfid_tag' in data and data['rfid_tag'] != employee.rfid_tag:
        if Employee.query.filter_by(rfid_tag=data['rfid_tag']).first():
            return jsonify({'error': 'RFID tag already exists'}), 400
    
    # Update fields
    for field in ['rfid_tag', 'name', 'department', 'position']:
        if field in data:
            setattr(employee, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Employee updated successfully',
        'employee': employee.serialize()
    }), 200

@employees_bp.route('/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    db.session.delete(employee)
    db.session.commit()
    
    return jsonify({
        'message': 'Employee deleted successfully'
    }), 200

@employees_bp.route('/search', methods=['GET'])
def search_employees():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    employees = Employee.query.filter(
        (Employee.name.ilike(f'%{query}%')) |
        (Employee.employee_id.ilike(f'%{query}%')) |
        (Employee.department.ilike(f'%{query}%')) |
        (Employee.position.ilike(f'%{query}%'))
    ).all()
    
    return jsonify({
        'employees': [employee.serialize() for employee in employees]
    }), 200 