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
    
    // Set up auto-refresh for real-time data
    setInterval(function() {
        loadDashboardData();
        if (document.getElementById('overview').classList.contains('active')) {
            loadRecentActivities();
        }
        if (document.getElementById('alerts').classList.contains('active')) {
            loadAlerts();
        }
    }, 30000); // Refresh every 30 seconds
    
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
    
    // Load initial recent activities
    loadRecentActivities();
});

// Function to load dashboard overview data
function loadDashboardData() {
    // Fetch statistics
    fetch('/api/dashboard/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
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
}

// Function to load and display recent activities
function loadRecentActivities() {
    // Fetch recent activities with limit parameter
    fetch('/api/dashboard/activities?limit=15')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const activitiesContainer = document.getElementById('recent-activities');
            activitiesContainer.innerHTML = '';
            
            if (data.activities && data.activities.length > 0) {
                // Create the activities list
                const activitiesList = document.createElement('div');
                activitiesList.className = 'activities-list';
                
                data.activities.forEach(activity => {
                    // Format timestamp for better readability
                    const activityDate = new Date(activity.time);
                    const formattedTime = activityDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    const formattedDate = activityDate.toLocaleDateString();
                    
                    // Create activity item with appropriate styling
                    const activityItem = document.createElement('div');
                    activityItem.className = `activity-item activity-${activity.type || 'default'}`;
                    activityItem.dataset.id = activity.id || '';
                    
                    // Create and append the icon based on activity type
                    let icon = '';
                    let typeClass = '';
                    
                    if (activity.type === 'check-in') {
                        icon = '→';
                        typeClass = 'check-in';
                    } else if (activity.type === 'check-out') {
                        icon = '←';
                        typeClass = 'check-out';
                    } else if (activity.type === 'break') {
                        icon = '⏸';
                        typeClass = 'break';
                    } else if (activity.type === 'alert') {
                        icon = '⚠';
                        typeClass = `alert ${activity.details?.severity || ''}`;
                    } else {
                        icon = '•';
                        typeClass = 'default';
                    }
                    
                    activityItem.innerHTML = `
                        <div class="activity-header">
                            <span class="activity-icon ${typeClass}">${icon}</span>
                            <div class="activity-time">
                                <span class="time">${formattedTime}</span>
                                <span class="date">${formattedDate}</span>
                            </div>
                        </div>
                        <div class="activity-content">
                            <p class="activity-description">${activity.description}</p>
                            <p class="activity-detail">${activity.employee_name || ''} ${activity.department ? `(${activity.department})` : ''}</p>
                        </div>
                    `;
                    
                    // Add click event to view details if available
                    if (activity.details) {
                        activityItem.addEventListener('click', function() {
                            showActivityDetails(activity);
                        });
                        activityItem.style.cursor = 'pointer';
                    }
                    
                    activitiesList.appendChild(activityItem);
                });
                
                // Add update time
                const updateInfo = document.createElement('div');
                updateInfo.className = 'update-info';
                updateInfo.innerHTML = `<small>Last updated: ${data.last_updated || new Date().toLocaleString()}</small>`;
                
                // Append to the container
                activitiesContainer.appendChild(activitiesList);
                activitiesContainer.appendChild(updateInfo);
            } else {
                activitiesContainer.innerHTML = '<p class="no-data">No recent activities</p>';
            }
        })
        .catch(error => {
            console.error('Error loading recent activities:', error);
            document.getElementById('recent-activities').innerHTML = 
                '<p class="error-message">Error loading activities. Please try refreshing the page.</p>';
        });
}

// Function to show activity details in a popup
function showActivityDetails(activity) {
    // Create a simple popup with activity details
    const detailsContent = `
        <h3>${activity.description}</h3>
        <p><strong>Time:</strong> ${activity.time}</p>
        <p><strong>Employee:</strong> ${activity.employee_name || 'Unknown'}</p>
        ${activity.department ? `<p><strong>Department:</strong> ${activity.department}</p>` : ''}
        
        <h4>Details:</h4>
        <ul>
            ${Object.entries(activity.details || {}).map(([key, value]) => 
                `<li><strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${value}</li>`
            ).join('')}
        </ul>
    `;
    
    alert(detailsContent.replace(/<[^>]*>/g, '')); // Simple alert for now, replace with modal in production
}

// Function to render attendance trend chart
function renderAttendanceChart(data) {
    const ctx = document.getElementById('attendance-chart').getContext('2d');
    
    // Destroy existing chart if it exists to prevent conflicts
    if (window.attendanceChart) {
        window.attendanceChart.destroy();
    }
    
    window.attendanceChart = new Chart(ctx, {
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
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
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
    
    // Destroy existing chart if it exists to prevent conflicts
    if (window.alertChart) {
        window.alertChart.destroy();
    }
    
    window.alertChart = new Chart(ctx, {
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
                    position: 'right',
                    labels: {
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
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
    
    // Construct API URL with query parameters
    let url = '/api/dashboard/alerts?';
    
    if (employeeId) {
        url += `employee_id=${employeeId}&`;
    }
    
    if (severity) {
        url += `severity=${severity}&`;
    }
    
    url += `time_filter=${timeFilter}`;
    
    // Show loading state
    const alertsContainer = document.getElementById('alerts-list');
    alertsContainer.innerHTML = '<div class="loading">Loading alerts...</div>';
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            alertsContainer.innerHTML = '';
            
            if (data.alerts && data.alerts.length > 0) {
                // Create alerts table
                const alertsTable = document.createElement('table');
                alertsTable.className = 'alerts-table';
                
                // Create table header
                const tableHeader = document.createElement('thead');
                tableHeader.innerHTML = `
                    <tr>
                        <th>Time</th>
                        <th>Employee</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                `;
                alertsTable.appendChild(tableHeader);
                
                // Create table body
                const tableBody = document.createElement('tbody');
                
                data.alerts.forEach(alert => {
                    const alertRow = document.createElement('tr');
                    alertRow.className = `alert-row ${alert.severity}`;
                    
                    // Format date for better readability
                    const alertDate = new Date(alert.timestamp);
                    const formattedDate = alertDate.toLocaleString();
                    
                    // Status badge
                    const statusBadge = alert.is_resolved ? 
                        '<span class="status-badge resolved">Resolved</span>' : 
                        '<span class="status-badge active">Active</span>';
                    
                    // Action buttons
                    const actionButtons = alert.is_resolved ?
                        '<button class="btn-view" onclick="viewAlertDetails(' + alert.id + ')">View</button>' :
                        '<button class="btn-view" onclick="viewAlertDetails(' + alert.id + ')">View</button>' +
                        '<button class="btn-resolve" onclick="resolveAlert(' + alert.id + ')">Resolve</button>';
                    
                    alertRow.innerHTML = `
                        <td>${formattedDate}</td>
                        <td>${alert.employee_name}</td>
                        <td>${alert.alert_type}</td>
                        <td>${alert.description}</td>
                        <td><span class="alert-severity ${alert.severity}">${alert.severity.toUpperCase()}</span></td>
                        <td>${statusBadge}</td>
                        <td class="action-buttons">${actionButtons}</td>
                    `;
                    
                    tableBody.appendChild(alertRow);
                });
                
                alertsTable.appendChild(tableBody);
                alertsContainer.appendChild(alertsTable);
            } else {
                // If no alerts found, show message with option to generate alerts
                const noAlertsDiv = document.createElement('div');
                noAlertsDiv.className = 'no-alerts';
                noAlertsDiv.innerHTML = `
                    <p>No alerts found matching the selected filters.</p>
                    <p>Try changing the severity or time filter.</p>
                    <button id="generate-sample-alerts" class="btn">Generate Sample Alerts for Testing</button>
                `;
                alertsContainer.appendChild(noAlertsDiv);
                
                // Add event listener to generate sample alerts
                document.getElementById('generate-sample-alerts').addEventListener('click', function() {
                    generateSampleAlerts();
                });
            }
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
            alertsContainer.innerHTML = `
                <div class="error-message">
                    <p>An error occurred while loading alerts.</p>
                    <p>Please try again later or contact support if the problem persists.</p>
                    <button id="generate-sample-alerts" class="btn">Generate Sample Alerts for Testing</button>
                </div>
            `;
            
            // Add event listener to generate sample alerts
            document.getElementById('generate-sample-alerts').addEventListener('click', function() {
                generateSampleAlerts();
            });
        });
}

// Function to generate sample alerts for testing
function generateSampleAlerts() {
    // Show loading state
    const alertsContainer = document.getElementById('alerts-list');
    alertsContainer.innerHTML = '<div class="loading">Generating sample alerts...</div>';
    
    // Get employees
    fetch('/api/employees')
        .then(response => response.json())
        .then(data => {
            if (data.employees && data.employees.length > 0) {
                // Make API calls to generate alerts
                const promises = [];
                
                // Generate different types of alerts
                const alertTypes = [
                    { type: 'Excessive Break', severity: 'medium' },
                    { type: 'Late Check-in', severity: 'low' },
                    { type: 'Early Departure', severity: 'medium' },
                    { type: 'Multiple Check-ins', severity: 'low' },
                    { type: 'Missing Check-out', severity: 'high' },
                    { type: 'Unauthorized Access', severity: 'critical' }
                ];
                
                // Use first 3 employees for sample alerts
                const sampleEmployees = data.employees.slice(0, 3);
                
                sampleEmployees.forEach(employee => {
                    // Generate 2 random alerts for each employee
                    for (let i = 0; i < 2; i++) {
                        const randomAlert = alertTypes[Math.floor(Math.random() * alertTypes.length)];
                        
                        // Create random description
                        const description = `${randomAlert.type} detected for ${employee.name} on ${new Date().toLocaleDateString()}`;
                        
                        const alertData = {
                            employee_id: employee.employee_id,
                            alert_type: randomAlert.type,
                            description: description,
                            severity: randomAlert.severity,
                            timestamp: new Date().toISOString()
                        };
                        
                        // Make API call to create alert
                        promises.push(
                            fetch('/api/dashboard/create-alert', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(alertData)
                            })
                        );
                    }
                });
                
                // Wait for all API calls to complete
                Promise.all(promises)
                    .then(() => {
                        // Reload alerts after generation
                        loadAlerts();
                    })
                    .catch(error => {
                        console.error('Error generating alerts:', error);
                        alertsContainer.innerHTML = '<div class="error-message">Error generating sample alerts.</div>';
                    });
            } else {
                alertsContainer.innerHTML = '<div class="error-message">No employees found to generate alerts for.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading employees:', error);
            alertsContainer.innerHTML = '<div class="error-message">Error loading employees.</div>';
        });
}

// Function to view alert details
function viewAlertDetails(alertId) {
    // In a real application, this would fetch detailed alert data
    // For now, just show a demo alert
    alert(`Viewing details for alert ID: ${alertId}`);
}

// Function to resolve an alert
function resolveAlert(alertId) {
    // In a real application, this would send a request to mark the alert as resolved
    if (confirm('Are you sure you want to mark this alert as resolved?')) {
        fetch(`/api/dashboard/alerts/${alertId}/resolve`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                alert(`Alert ID ${alertId} has been marked as resolved.`);
                // Reload alerts to refresh the list
                loadAlerts();
            } else {
                alert('Error resolving alert. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error resolving alert:', error);
            alert('Error resolving alert. Please try again.');
        });
    }
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