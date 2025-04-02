document.addEventListener('DOMContentLoaded', function() {
    // Navigation tabs functionality
    const navLinks = document.querySelectorAll('.dashboard-nav a');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the section id from data-section attribute
            const sectionId = this.getAttribute('data-section');
            
            // Remove active class from all links and sections
            navLinks.forEach(link => link.parentElement.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked link and corresponding section
            this.parentElement.classList.add('active');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Load dashboard data
    loadDashboardData();
    
    // Set up employee search
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('employee-search');
    
    searchBtn.addEventListener('click', function() {
        searchEmployees(searchInput.value);
    });
    
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchEmployees(searchInput.value);
        }
    });
    
    // Set up alert filters
    const alertSeverityFilter = document.getElementById('alert-severity-filter');
    const alertTimeFilter = document.getElementById('alert-time-filter');
    
    alertSeverityFilter.addEventListener('change', loadAlerts);
    alertTimeFilter.addEventListener('change', loadAlerts);
    
    // Load initial alerts
    loadAlerts();
    
    // Set up report buttons
    document.getElementById('attendance-report-btn').addEventListener('click', function() {
        generateReport('attendance');
    });
    
    document.getElementById('anomaly-report-btn').addEventListener('click', function() {
        generateReport('anomaly');
    });
    
    document.getElementById('hours-report-btn').addEventListener('click', function() {
        generateReport('hours');
    });
});

// Function to load dashboard overview data
function loadDashboardData() {
    // Fetch statistics
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-employees').textContent = data.total_employees || 0;
            document.getElementById('present-today').textContent = data.present_today || 0;
            document.getElementById('on-break').textContent = data.on_break || 0;
            document.getElementById('alerts-today').textContent = data.alerts_today || 0;
            
            // Load charts if data available
            if (data.attendance_trend) {
                renderAttendanceChart(data.attendance_trend);
            }
            
            if (data.alert_types) {
                renderAlertChart(data.alert_types);
            }
        })
        .catch(error => {
            console.error('Error loading dashboard stats:', error);
        });
    
    // Fetch recent activities
    fetch('/api/dashboard/activities')
        .then(response => response.json())
        .then(data => {
            const activitiesContainer = document.getElementById('recent-activities');
            activitiesContainer.innerHTML = '';
            
            if (data.activities && data.activities.length > 0) {
                data.activities.forEach(activity => {
                    const activityItem = document.createElement('div');
                    activityItem.className = 'activity-item';
                    activityItem.innerHTML = `
                        <p><strong>${activity.time}</strong> - ${activity.description}</p>
                    `;
                    activitiesContainer.appendChild(activityItem);
                });
            } else {
                activitiesContainer.innerHTML = '<p>No recent activities</p>';
            }
        })
        .catch(error => {
            console.error('Error loading recent activities:', error);
        });
}

// Function to render attendance trend chart
function renderAttendanceChart(data) {
    const ctx = document.getElementById('attendance-chart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Present',
                data: data.present,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.3,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Function to render alert types chart
function renderAlertChart(data) {
    const ctx = document.getElementById('alert-chart').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#3498db', // Low
                    '#f39c12', // Medium
                    '#e74c3c', // High
                    '#c0392b'  // Critical
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Function to search employees
function searchEmployees(query) {
    if (!query.trim()) {
        return;
    }
    
    fetch(`/api/employees/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('employee-results');
            resultsContainer.innerHTML = '';
            
            if (data.employees && data.employees.length > 0) {
                data.employees.forEach(employee => {
                    const employeeCard = document.createElement('div');
                    employeeCard.className = 'employee-card';
                    employeeCard.innerHTML = `
                        <h3>${employee.name}</h3>
                        <p>ID: ${employee.employee_id}</p>
                        <p>Department: ${employee.department}</p>
                        <p>Position: ${employee.position}</p>
                    `;
                    
                    employeeCard.addEventListener('click', function() {
                        viewEmployeeDetails(employee.employee_id);
                    });
                    
                    resultsContainer.appendChild(employeeCard);
                });
            } else {
                resultsContainer.innerHTML = '<p>No employees found</p>';
            }
        })
        .catch(error => {
            console.error('Error searching employees:', error);
        });
}

// Function to view employee details
function viewEmployeeDetails(employeeId) {
    fetch(`/api/employees/${employeeId}`)
        .then(response => response.json())
        .then(data => {
            const detailsContainer = document.getElementById('employee-details');
            
            if (data.employee) {
                const employee = data.employee;
                
                detailsContainer.innerHTML = `
                    <h3>${employee.name}</h3>
                    <div class="employee-info">
                        <p><strong>Employee ID:</strong> ${employee.employee_id}</p>
                        <p><strong>Department:</strong> ${employee.department}</p>
                        <p><strong>Position:</strong> ${employee.position}</p>
                        <p><strong>Join Date:</strong> ${employee.join_date}</p>
                    </div>
                    <div class="employee-actions">
                        <button class="view-attendance-btn" data-employee-id="${employee.employee_id}">View Attendance</button>
                        <button class="view-alerts-btn" data-employee-id="${employee.employee_id}">View Alerts</button>
                    </div>
                `;
                
                detailsContainer.classList.add('active');
                
                // Add event listeners to buttons
                const viewAttendanceBtn = detailsContainer.querySelector('.view-attendance-btn');
                const viewAlertsBtn = detailsContainer.querySelector('.view-alerts-btn');
                
                viewAttendanceBtn.addEventListener('click', function() {
                    const employeeId = this.getAttribute('data-employee-id');
                    viewEmployeeAttendance(employeeId);
                });
                
                viewAlertsBtn.addEventListener('click', function() {
                    const employeeId = this.getAttribute('data-employee-id');
                    document.getElementById('alert-severity-filter').value = '';
                    document.getElementById('alert-time-filter').value = 'all';
                    
                    // Switch to alerts tab and filter by this employee
                    document.querySelector('.dashboard-nav a[data-section="alerts"]').click();
                    loadAlerts(employeeId);
                });
            } else {
                detailsContainer.innerHTML = '<p>Employee details not found</p>';
                detailsContainer.classList.add('active');
            }
        })
        .catch(error => {
            console.error('Error loading employee details:', error);
        });
}

// Function to view employee attendance
function viewEmployeeAttendance(employeeId) {
    fetch(`/api/attendance/${employeeId}`)
        .then(response => response.json())
        .then(data => {
            const detailsContainer = document.getElementById('employee-details');
            
            if (data.records && data.records.length > 0) {
                let attendanceHTML = `
                    <h3>Attendance Records for ${data.employee.name}</h3>
                    <div class="attendance-records">
                        <table class="attendance-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Time In</th>
                                    <th>Time Out</th>
                                    <th>Hours Worked</th>
                                    <th>Breaks</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                data.records.forEach(record => {
                    const breakCount = record.breaks ? record.breaks.length : 0;
                    const status = record.is_anomaly ? 
                        '<span class="status-anomaly">Anomaly</span>' : 
                        '<span class="status-normal">Normal</span>';
                    
                    attendanceHTML += `
                        <tr>
                            <td>${record.date}</td>
                            <td>${record.time_in || 'N/A'}</td>
                            <td>${record.time_out || 'N/A'}</td>
                            <td>${record.total_hours ? record.total_hours.toFixed(2) : 'N/A'}</td>
                            <td>${breakCount}</td>
                            <td>${status}</td>
                        </tr>
                    `;
                });
                
                attendanceHTML += `
                            </tbody>
                        </table>
                    </div>
                    <button class="back-btn">Back to Employee Details</button>
                `;
                
                detailsContainer.innerHTML = attendanceHTML;
                
                // Add event listener to back button
                detailsContainer.querySelector('.back-btn').addEventListener('click', function() {
                    viewEmployeeDetails(employeeId);
                });
            } else {
                detailsContainer.innerHTML = `
                    <h3>No Attendance Records</h3>
                    <p>No attendance records found for this employee.</p>
                    <button class="back-btn">Back to Employee Details</button>
                `;
                
                detailsContainer.querySelector('.back-btn').addEventListener('click', function() {
                    viewEmployeeDetails(employeeId);
                });
            }
        })
        .catch(error => {
            console.error('Error loading employee attendance:', error);
        });
}

// Function to load alerts
function loadAlerts(employeeId = null) {
    const severity = document.getElementById('alert-severity-filter').value;
    const timeFilter = document.getElementById('alert-time-filter').value;
    
    let url = '/api/alerts?';
    
    if (employeeId) {
        url += `employee_id=${employeeId}&`;
    }
    
    if (severity) {
        url += `severity=${severity}&`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const alertsContainer = document.getElementById('alerts-list');
            alertsContainer.innerHTML = '';
            
            if (data.alerts && data.alerts.length > 0) {
                // Filter by time if needed
                let filteredAlerts = data.alerts;
                
                if (timeFilter !== 'all') {
                    const now = new Date();
                    let startDate = new Date();
                    
                    if (timeFilter === 'today') {
                        startDate.setHours(0, 0, 0, 0);
                    } else if (timeFilter === 'week') {
                        startDate.setDate(now.getDate() - 7);
                    } else if (timeFilter === 'month') {
                        startDate.setMonth(now.getMonth() - 1);
                    }
                    
                    filteredAlerts = data.alerts.filter(alert => {
                        const alertDate = new Date(alert.timestamp);
                        return alertDate >= startDate;
                    });
                }
                
                filteredAlerts.forEach(alert => {
                    const alertItem = document.createElement('div');
                    alertItem.className = `alert-item ${alert.severity}`;
                    
                    alertItem.innerHTML = `
                        <h3>
                            ${alert.alert_type}
                            <span class="alert-severity ${alert.severity}">${alert.severity.toUpperCase()}</span>
                        </h3>
                        <p>${alert.description}</p>
                        <p class="alert-timestamp">
                            <small>${alert.timestamp}</small>
                        </p>
                    `;
                    
                    alertsContainer.appendChild(alertItem);
                });
            } else {
                alertsContainer.innerHTML = '<p>No alerts found</p>';
            }
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
        });
}

// Function to generate reports
function generateReport(reportType) {
    let reportHTML = '';
    const reportResult = document.getElementById('report-result');
    
    // In a real application, this would fetch data from the server
    // For this demo, we'll just show a placeholder
    
    switch (reportType) {
        case 'attendance':
            reportHTML = `
                <h3>Attendance Report</h3>
                <p>Generated on ${new Date().toLocaleString()}</p>
                <div class="report-placeholder">
                    <p>This is a placeholder for the attendance report. In a real application, this would display detailed attendance data.</p>
                </div>
            `;
            break;
            
        case 'anomaly':
            reportHTML = `
                <h3>Anomaly Report</h3>
                <p>Generated on ${new Date().toLocaleString()}</p>
                <div class="report-placeholder">
                    <p>This is a placeholder for the anomaly report. In a real application, this would display detailed anomaly detection data.</p>
                </div>
            `;
            break;
            
        case 'hours':
            reportHTML = `
                <h3>Work Hours Report</h3>
                <p>Generated on ${new Date().toLocaleString()}</p>
                <div class="report-placeholder">
                    <p>This is a placeholder for the work hours report. In a real application, this would display detailed working hours data.</p>
                </div>
            `;
            break;
    }
    
    reportResult.innerHTML = reportHTML;
    reportResult.classList.add('active');
} 