// Admin Dashboard JavaScript

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        window.location.href = 'admin-login.html';
    }
    
    // Display admin username
    const adminUsername = document.getElementById('admin-username');
    if (adminUsername) {
        adminUsername.textContent = localStorage.getItem('admin_username') || 'Admin';
    }
}

// Handle logout
function setupLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_username');
            window.location.href = 'admin-login.html';
        });
    }
}

// Tab switching functionality
function setupTabs() {
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabLinks.forEach(tab => {
                tab.classList.remove('border-blue-500', 'text-blue-600');
                tab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
            });
            
            // Add active class to clicked tab
            this.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
            this.classList.add('border-blue-500', 'text-blue-600');
            
            // Hide all tab contents
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // Show selected tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

// Load sample data for users table
function loadUsersData() {
    const usersTableBody = document.getElementById('users-table-body');
    if (!usersTableBody) return;
    
    // Sample user data
    const users = [
        {
            id: 1,
            username: 'admin',
            email: 'admin@acfspark.com',
            role: 'admin',
            created_at: '2025-03-10 08:00:00'
        },
        {
            id: 2,
            username: 'kol_user1',
            email: 'kol1@example.com',
            role: 'kol',
            created_at: '2025-03-10 09:15:00'
        },
        {
            id: 3,
            username: 'kol_user2',
            email: 'kol2@example.com',
            role: 'kol',
            created_at: '2025-03-11 14:45:00'
        },
        {
            id: 4,
            username: 'publisher1',
            email: 'publisher1@example.com',
            role: 'publisher',
            created_at: '2025-03-10 10:30:00'
        }
    ];
    
    // Clear existing data
    usersTableBody.innerHTML = '';
    
    // Add users to table
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.username}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.email}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.role}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.created_at}</td>
        `;
        usersTableBody.appendChild(row);
    });
}

// Load sample data for KOL profiles table
function loadKolProfilesData() {
    const kolProfilesTableBody = document.getElementById('kol-profiles-table-body');
    if (!kolProfilesTableBody) return;
    
    // Sample KOL profile data
    const kolProfiles = [
        {
            id: 1,
            user: 'kol_user1',
            platform: 'Twitter',
            followers: 5280,
            focus_area: 'Meme',
            price: 400,
            verified: true
        },
        {
            id: 2,
            user: 'kol_user2',
            platform: 'Instagram',
            followers: 12500,
            focus_area: 'Investment',
            price: 600,
            verified: false
        }
    ];
    
    // Clear existing data
    kolProfilesTableBody.innerHTML = '';
    
    // Add KOL profiles to table
    kolProfiles.forEach(profile => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${profile.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${profile.user}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${profile.platform}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${profile.followers}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${profile.focus_area}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${profile.price} USDT</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${profile.verified ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    ${profile.verified ? 'Yes' : 'No'}
                </span>
            </td>
        `;
        kolProfilesTableBody.appendChild(row);
    });
}

// Load sample data for tasks table
function loadTasksData() {
    const tasksTableBody = document.getElementById('tasks-table-body');
    if (!tasksTableBody) return;
    
    // Sample task data
    const tasks = [
        {
            id: 1,
            title: 'Sonic Twitter Campaign',
            platform: 'Twitter',
            commission: 400,
            requirements: 'At least 5,000 followers',
            status: 'open',
            created_at: '2025-03-10 08:30:00'
        },
        {
            id: 2,
            title: 'Crypto Exchange Instagram Post',
            platform: 'Instagram',
            commission: 600,
            requirements: 'At least 10,000 followers',
            status: 'open',
            created_at: '2025-03-11 14:15:00'
        }
    ];
    
    // Clear existing data
    tasksTableBody.innerHTML = '';
    
    // Add tasks to table
    tasks.forEach(task => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${task.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${task.title}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${task.platform}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${task.commission} USDT</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${task.requirements}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    ${task.status}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${task.created_at}</td>
        `;
        tasksTableBody.appendChild(row);
    });
}

// Load sample data for submissions table
function loadSubmissionsData() {
    const submissionsTableBody = document.getElementById('submissions-table-body');
    if (!submissionsTableBody) return;
    
    // Sample submission data
    const submissions = [
        {
            id: 1,
            task: 'Sonic Twitter Campaign',
            kol: 'kol_user1',
            content_link: 'https://twitter.com/kol_user1/status/1234567890',
            status: 'pending',
            submitted_at: '2025-03-12 10:45:00'
        }
    ];
    
    // Clear existing data
    submissionsTableBody.innerHTML = '';
    
    // Add submissions to table
    submissions.forEach(submission => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${submission.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${submission.task}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${submission.kol}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <a href="${submission.content_link}" target="_blank" class="text-blue-600 hover:text-blue-800">View Content</a>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                    ${submission.status}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${submission.submitted_at}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button class="px-2 py-1 bg-green-500 text-white rounded mr-2 hover:bg-green-600">Approve</button>
                <button class="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600">Reject</button>
            </td>
        `;
        submissionsTableBody.appendChild(row);
    });
    
    // Add event listeners to action buttons
    const approveButtons = document.querySelectorAll('.bg-green-500');
    const rejectButtons = document.querySelectorAll('.bg-red-500');
    
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Submission approved! Payment will be processed.');
            const statusCell = this.parentElement.parentElement.querySelector('td:nth-child(5) span');
            statusCell.textContent = 'approved';
            statusCell.classList.remove('bg-yellow-100', 'text-yellow-800');
            statusCell.classList.add('bg-green-100', 'text-green-800');
        });
    });
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Submission rejected! KOL will be notified.');
            const statusCell = this.parentElement.parentElement.querySelector('td:nth-child(5) span');
            statusCell.textContent = 'rejected';
            statusCell.classList.remove('bg-yellow-100', 'text-yellow-800');
            statusCell.classList.add('bg-red-100', 'text-red-800');
        });
    });
}

// Initialize charts
function initCharts() {
    // Platform distribution chart
    const platformChartCtx = document.getElementById('platform-chart');
    if (platformChartCtx) {
        new Chart(platformChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Twitter', 'Instagram', 'YouTube', 'TikTok'],
                datasets: [{
                    data: [45, 30, 15, 10],
                    backgroundColor: [
                        '#3b82f6',
                        '#ef4444',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Task status chart
    const taskStatusChartCtx = document.getElementById('task-status-chart');
    if (taskStatusChartCtx) {
        new Chart(taskStatusChartCtx, {
            type: 'bar',
            data: {
                labels: ['Open', 'In Progress', 'Completed'],
                datasets: [{
                    label: 'Tasks',
                    data: [2, 0, 0],
                    backgroundColor: '#3b82f6',
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Setup export buttons
function setupExportButtons() {
    const exportButtons = [
        document.getElementById('export-users-btn'),
        document.getElementById('export-kol-profiles-btn'),
        document.getElementById('export-tasks-btn'),
        document.getElementById('export-submissions-btn')
    ];
    
    exportButtons.forEach(button => {
        if (button) {
            button.addEventListener('click', function() {
                // In a real implementation, this would call the backend API
                // For now, just show a notification
                const notification = document.createElement('div');
                notification.className = 'fixed top-4 right-4 p-4 rounded-lg shadow-lg bg-green-500 text-white';
                notification.textContent = 'Excel file generated and downloaded!';
                document.body.appendChild(notification);
                
                // Remove notification after 3 seconds
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            });
        }
    });
}

// Initialize admin dashboard
function initAdminDashboard() {
    checkAuth();
    setupLogout();
    setupTabs();
    loadUsersData();
    loadKolProfilesData();
    loadTasksData();
    loadSubmissionsData();
    initCharts();
    setupExportButtons();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAdminDashboard);
            const statusCell = this.parentElement.parentElement.querySelector('td:nth-child(5) span');
            statusCell.textContent = 'rejected';
            statusCell.classList.remove('bg-yellow-100', 'text-yellow-800');
            statusCell.classList.add('bg-red-100', 'text-red-800');
            
            // Remove action buttons
            this.parentElement.innerHTML = '';
        });
    });
}

// Helper functions
function getStatusClass(status) {
    switch (status) {
        case 'open':
            return 'bg-green-100 text-green-800';
        case 'in_progress':
            return 'bg-blue-100 text-blue-800';
        case 'completed':
            return 'bg-purple-100 text-purple-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

function getSubmissionStatusClass(status) {
    switch (status) {
        case 'pending':
            return 'bg-yellow-100 text-yellow-800';
        case 'approved':
            return 'bg-green-100 text-green-800';
        case 'rejected':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

// Update task status chart
function updateTaskStatusChart(tasks) {
    const taskStatusChartCtx = document.getElementById('task-status-chart');
    if (!taskStatusChartCtx) return;
    
    // Count tasks by status
    const statusCounts = {
        open: 0,
        in_progress: 0,
        completed: 0
    };
    
    tasks.forEach(task => {
        if (statusCounts.hasOwnProperty(task.status)) {
            statusCounts[task.status]++;
        } else {
            statusCounts.open++;
        }
    });
    
    // Update chart
    const taskStatusChart = Chart.getChart(taskStatusChartCtx);
    if (taskStatusChart) {
        taskStatusChart.data.datasets[0].data = [
            statusCounts.open,
            statusCounts.in_progress,
            statusCounts.completed
        ];
        taskStatusChart.update();
    }
}

// Initialize charts
function initCharts() {
    // Platform distribution chart
    const platformChartCtx = document.getElementById('platform-chart');
    if (platformChartCtx) {
        new Chart(platformChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Twitter', 'Instagram', 'YouTube', 'TikTok'],
                datasets: [{
                    data: [45, 30, 15, 10],
                    backgroundColor: [
                        '#3b82f6',
                        '#ef4444',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Task status chart
    const taskStatusChartCtx = document.getElementById('task-status-chart');
    if (taskStatusChartCtx) {
        new Chart(taskStatusChartCtx, {
            type: 'bar',
            data: {
                labels: ['Open', 'In Progress', 'Completed'],
                datasets: [{
                    label: 'Tasks',
                    data: [2, 0, 0],
                    backgroundColor: '#3b82f6',
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Setup export buttons
function setupExportButtons() {
    // Export users button
    const exportUsersBtn = document.getElementById('export-users-btn');
    if (exportUsersBtn) {
        exportUsersBtn.addEventListener('click', async function() {
            try {
                if (window.adminApi && typeof window.adminApi.users.export === 'function') {
                    const success = await window.adminApi.users.export();
                    if (success) {
                        showNotification('Users exported successfully!', 'success');
                    } else {
                        throw new Error('Export failed');
                    }
                } else {
                    // Mock export
                    showNotification('Excel file generated and downloaded!', 'success');
                }
            } catch (error) {
                console.error('Export users error:', error);
                showNotification('Failed to export users', 'error');
            }
        });
    }
    
    // Export KOL profiles button
    const exportKolProfilesBtn = document.getElementById('export-kol-profiles-btn');
    if (exportKolProfilesBtn) {
        exportKolProfilesBtn.addEventListener('click', async function() {
            try {
                if (window.adminApi && typeof window.adminApi.kolProfiles.export === 'function') {
                    const success = await window.adminApi.kolProfiles.export();
                    if (success) {
                        showNotification('KOL profiles exported successfully!', 'success');
                    } else {
                        throw new Error('Export failed');
                    }
                } else {
                    // Mock export
                    showNotification('Excel file generated and downloaded!', 'success');
                }
            } catch (error) {
                console.error('Export KOL profiles error:', error);
                showNotification('Failed to export KOL profiles', 'error');
            }
        });
    }
    
    // Export tasks button
    const exportTasksBtn = document.getElementById('export-tasks-btn');
    if (exportTasksBtn) {
        exportTasksBtn.addEventListener('click', async function() {
            try {
                if (window.adminApi && typeof window.adminApi.tasks.export === 'function') {
                    const success = await window.adminApi.tasks.export();
                    if (success) {
                        showNotification('Tasks exported successfully!', 'success');
                    } else {
                        throw new Error('Export failed');
                    }
                } else {
                    // Mock export
                    showNotification('Excel file generated and downloaded!', 'success');
                }
            } catch (error) {
                console.error('Export tasks error:', error);
                showNotification('Failed to export tasks', 'error');
            }
        });
    }
    
    // Export submissions button
    const exportSubmissionsBtn = document.getElementById('export-submissions-btn');
    if (exportSubmissionsBtn) {
        exportSubmissionsBtn.addEventListener('click', async function() {
            try {
                if (window.adminApi && typeof window.adminApi.submissions.export === 'function') {
                    const success = await window.adminApi.submissions.export();
                    if (success) {
                        showNotification('Submissions exported successfully!', 'success');
                    } else {
                        throw new Error('Export failed');
                    }
                } else {
                    // Mock export
                    showNotification('Excel file generated and downloaded!', 'success');
                }
            } catch (error) {
                console.error('Export submissions error:', error);
                showNotification('Failed to export submissions', 'error');
            }
        });
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'} text-white`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Mock data functions (fallback if API fails)
function getMockUsers() {
    return [
        {
            id: 1,
            username: 'admin',
            email: 'admin@acfspark.com',
            role: 'admin',
            created_at: '2025-03-10 08:00:00'
        },
        {
            id: 2,
            username: 'kol_user1',
            email: 'kol1@example.com',
            role: 'kol',
            created_at: '2025-03-10 09:15:00'
        },
        {
            id: 3,
            username: 'kol_user2',
            email: 'kol2@example.com',
            role: 'kol',
            created_at: '2025-03-11 14:45:00'
        },
        {
            id: 4,
            username: 'publisher1',
            email: 'publisher1@example.com',
            role: 'publisher',
            created_at: '2025-03-10 10:30:00'
        }
    ];
}

function getMockKolProfiles() {
    return [
        {
            id: 1,
            user_id: 2,
            user: {
                username: 'kol_user1'
            },
            platform: 'Twitter',
            platform_link: 'https://twitter.com/kol_user1',
            followers_count: 5280,
            focus_area: 'Meme',
            price_per_post: 400,
            wallet_address: '0x1234567890abcdef',
            twitter_verified: true,
            created_at: '2025-03-10 09:30:00',
            updated_at: '2025-03-10 09:30:00'
        },
        {
            id: 2,
            user_id: 3,
            user: {
                username: 'kol_user2'
            },
            platform: 'Instagram',
            platform_link: 'https://instagram.com/kol_user2',
            followers_count: 12500,
            focus_area: 'Investment',
            price_per_post: 600,
            wallet_address: '0xabcdef1234567890',
            twitter_verified: false,
            created_at: '2025-03-11 14:50:00',
            updated_at: '2025-03-11 14:50:00'
        }
    ];
}

function getMockTasks() {
    return [
        {
            id: 1,
            title: 'Sonic Twitter Campaign',
            description: 'Promote the new Sonic game on Twitter with engaging content.',
            requirements: 'Create a tweet highlighting the game\'s new features and include the hashtag #SonicSpeed.',
            platform: 'Twitter',
            platform_requirements: 'At least 5,000 followers',
            commission: 400,
            word_count: 280,
            status: 'open',
            created_at: '2025-03-10 08:30:00',
            updated_at: '2025-03-10 08:30:00'
        },
        {
            id: 2,
            title: 'Crypto Exchange Instagram Post',
            description: 'Create an Instagram post about our new crypto exchange features.',
            requirements: 'Post should include a screenshot of the exchange UI and mention the low fees.',
            platform: 'Instagram',
            platform_requirements: 'At least 10,000 followers',
            commission: 600,
            word_count: 100,
            status: 'open',
            created_at: '2025-03-11 14:15:00',
            updated_at: '2025-03-11 14:15:00'
        }
    ];
}

function getMockSubmissions() {
    return [
        {
            id: 1,
            task_id: 1,
            task: {
                title: 'Sonic Twitter Campaign'
            },
            kol_id: 1,
            kol: {
                user: {
                    username: 'kol_user1'
                }
            },
            content_link: 'https://twitter.com/kol_user1/status/1234567890',
            comments: 'Created an engaging tweet with the required hashtag.',
            status: 'pending',
            created_at: '2025-03-12 10:45:00',
            updated_at: '2025-03-12 10:45:00'
        }
    ];
}

// Initialize admin dashboard
function initAdminDashboard() {
    checkAuth();
    setupLogout();
    setupTabs();
    loadUsersData();
    loadKolProfilesData();
    loadTasksData();
    loadSubmissionsData();
    initCharts();
    setupExportButtons();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAdminDashboard);
