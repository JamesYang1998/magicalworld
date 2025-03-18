// API integration module for backend communication
const API_BASE_URL = 'https://kol-backend-uemmyzlr.fly.dev';

// Authentication API functions
async function login(username, password) {
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
    localStorage.setItem('auth_token', data.access_token);
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

async function register(userData) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

// KOL profile API functions
async function getKolProfile() {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.log('No authentication token found, checking localStorage');
      // Try to get from localStorage
      const localProfile = localStorage.getItem('kol_profile');
      if (localProfile) {
        return JSON.parse(localProfile);
      }
      return null;
    }
    
    const response = await fetch(`${API_BASE_URL}/kol-profiles/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        // Try to get from localStorage as fallback
        const localProfile = localStorage.getItem('kol_profile');
        if (localProfile) {
          return JSON.parse(localProfile);
        }
        return null; // Profile not found
      }
      throw new Error('Failed to fetch profile');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get profile error:', error);
    // Try to get from localStorage as fallback
    const localProfile = localStorage.getItem('kol_profile');
    if (localProfile) {
      return JSON.parse(localProfile);
    }
    return null;
  }
}

async function saveKolProfile(profileData) {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.log('No authentication token found, falling back to localStorage');
      // Save to localStorage as fallback
      localStorage.setItem('kol_profile', JSON.stringify(profileData));
      return { success: true, message: 'Profile saved to localStorage', data: profileData };
    }
    
    // Check if profile exists
    let method = 'POST';
    let url = `${API_BASE_URL}/kol-profiles`;
    
    try {
      const profile = await getKolProfile();
      if (profile) {
        method = 'PUT';
        url = `${API_BASE_URL}/kol-profiles/me`;
      }
    } catch (error) {
      // Profile doesn't exist, use POST
    }
    
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(profileData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to save profile to API');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Save profile error:', error);
    // Save to localStorage as fallback on any error
    localStorage.setItem('kol_profile', JSON.stringify(profileData));
    return { success: true, message: 'Profile saved to localStorage', data: profileData };
  }
}

// Task API functions
async function getTasks() {
  try {
    const token = localStorage.getItem('auth_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'GET',
      headers: headers,
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get tasks error:', error);
    // Return sample tasks if API fails
    return getSampleTasks();
  }
}

async function createTask(taskData) {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(taskData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create task');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Create task error:', error);
    // Store in localStorage as fallback if API fails
    const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
    taskData.id = tasks.length + 1;
    tasks.push(taskData);
    localStorage.setItem('tasks', JSON.stringify(tasks));
    return taskData;
  }
}

// Twitter verification API functions
async function verifyTwitter() {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      // Save current URL to return after login
      localStorage.setItem('return_after_login', window.location.href);
      // Redirect to login page with return URL parameter
      window.location.href = 'index.html#/login?return_url=' + encodeURIComponent(window.location.href);
      return { redirected: true, message: '请先登录再验证Twitter账户' };
    }
    
    // Redirect to Twitter authorization page
    window.location.href = `${API_BASE_URL}/twitter/authorize`;
    return true;
  } catch (error) {
    console.error('Twitter verification error:', error);
    // Return user-friendly error message
    return { error: true, message: '验证Twitter时出错，请稍后再试' };
  }
}

async function verifyTwitterLink(platformLink) {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/twitter/verify-link`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ platform_link: platformLink }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to verify Twitter link');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Twitter link verification error:', error);
    throw error;
  }
}

// Submission API functions
async function createSubmission(submissionData) {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/submissions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(submissionData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create submission');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Create submission error:', error);
    throw error;
  }
}

// Helper functions
function getSampleTasks() {
  return [
    {
      id: 1,
      title: "Sonic Twitter Campaign",
      description: "Promote the new Sonic game on Twitter with engaging content.",
      requirements: "Create a tweet highlighting the game's new features and include the hashtag #SonicSpeed.",
      platform: "Twitter",
      platform_requirements: "At least 5,000 followers",
      commission: 400,
      word_count: 280,
      status: "open"
    },
    {
      id: 2,
      title: "Crypto Exchange Instagram Post",
      description: "Create an Instagram post about our new crypto exchange features.",
      requirements: "Post should include a screenshot of the exchange UI and mention the low fees.",
      platform: "Instagram",
      platform_requirements: "At least 10,000 followers",
      commission: 600,
      word_count: 100,
      status: "open"
    },
    {
      id: 3,
      title: "NFT Collection YouTube Review",
      description: "Create a detailed review of our new NFT collection.",
      requirements: "Video should be at least 5 minutes long and showcase at least 5 different NFTs.",
      platform: "YouTube",
      platform_requirements: "At least 20,000 subscribers",
      commission: 1000,
      word_count: 0,
      status: "open"
    }
  ];
}

// Helper function to get profile from localStorage
function getProfileFromLocalStorage() {
  const profileData = localStorage.getItem('kol_profile');
  return profileData ? JSON.parse(profileData) : null;
}

// Twitter analysis API functions
async function getTwitterAnalysis(profileId) {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/kol-profiles/${profileId}/twitter-analysis`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to get Twitter analysis');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting Twitter analysis:', error);
    return null;
  }
}


// Export API functions
window.api = {
  login,
  register,
  getKolProfile,
  saveKolProfile,
  getTasks,
  createTask,
  verifyTwitter,
  verifyTwitterLink,
  createSubmission,
  getSampleTasks,
  getProfileFromLocalStorage,
  getTwitterAnalysis
};
