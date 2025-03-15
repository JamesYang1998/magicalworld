// Admin API Integration Module

// API Base URL
const API_BASE_URL = 'https://kol-backend-uemmyzlr.fly.dev';

// Authentication functions
async function adminLogin(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }
        
        const data = await response.json();
        localStorage.setItem('admin_token', data.access_token);
        return data;
    } catch (error) {
        console.error('Admin login error:', error);
        throw error;
    }
}

// User management functions
async function getAllUsers() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Get users error:', error);
        // Return mock data if API fails
        return getMockUsers();
    }
}

// KOL profile management functions
async function getAllKolProfiles() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/kol-profiles`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch KOL profiles');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Get KOL profiles error:', error);
        // Return mock data if API fails
        return getMockKolProfiles();
    }
}

// Task management functions
async function getAllTasks() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/tasks`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch tasks');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Get tasks error:', error);
        // Return mock data if API fails
        return getMockTasks();
    }
}

// Submission management functions
async function getAllSubmissions() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/submissions`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch submissions');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Get submissions error:', error);
        // Return mock data if API fails
        return getMockSubmissions();
    }
}

// Export functions
async function exportKolProfiles() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/export/kol-profiles`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to export KOL profiles');
        }
        
        // Create a download link for the Excel file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'kol_profiles.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return true;
    } catch (error) {
        console.error('Export KOL profiles error:', error);
        return false;
    }
}

async function exportTasks() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/export/tasks`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to export tasks');
        }
        
        // Create a download link for the Excel file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tasks.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return true;
    } catch (error) {
        console.error('Export tasks error:', error);
        return false;
    }
}

async function exportSubmissions() {
    try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch(`${API_BASE_URL}/admin/export/submissions`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error('Failed to export submissions');
        }
        
        // Create a download link for the Excel file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'submissions.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return true;
    } catch (error) {
        console.error('Export submissions error:', error);
        return false;
    }
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

// Export API functions
window.adminApi = {
    login: adminLogin,
    users: {
        getAll: getAllUsers
    },
    kolProfiles: {
        getAll: getAllKolProfiles,
        export: exportKolProfiles
    },
    tasks: {
        getAll: getAllTasks,
        export: exportTasks
    },
    submissions: {
        getAll: getAllSubmissions,
        export: exportSubmissions
    }
};
