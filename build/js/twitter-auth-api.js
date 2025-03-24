// Twitter OAuth Integration with Backend API

// Function to handle Twitter verification using backend API
async function handleTwitterVerification() {
  try {
    // Check if API is available
    if (window.api && typeof window.api.verifyTwitter === 'function') {
      // Use the backend API for verification
      await window.api.verifyTwitter();
    } else {
      // Fallback to mock implementation
      // Open Twitter authorization page in a new window
      const authWindow = window.open('twitter-auth.html', 'TwitterAuth', 'width=600,height=600');
      
      // Listen for messages from the auth window
      window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'twitter_auth_success') {
          // Close the auth window
          authWindow.close();
          
          // Update the UI with Twitter data
          updateProfileWithTwitterData();
        }
      }, false);
    }
  } catch (error) {
    console.error('Twitter verification error:', error);
    showNotification('Twitter verification failed, please try again.', 'error');
  }
}

// Function to update profile with Twitter data
async function updateProfileWithTwitterData() {
  try {
    // Try to get profile from backend API
    if (window.api && typeof window.api.getKolProfile === 'function') {
      const profile = await window.api.getKolProfile();
      if (profile) {
        // Update follower count field
        const followerCountInput = document.querySelector('input[placeholder="Example: 5000"]');
        if (followerCountInput) {
          followerCountInput.value = profile.followers_count;
        }
        
        // Update verify button to show verified status
        const verifyButton = document.getElementById('verify-twitter-btn');
        if (verifyButton) {
          verifyButton.innerHTML = '✓ Verified';
          verifyButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
          verifyButton.classList.add('verified');
          verifyButton.disabled = true;
        }
        
        // Show success message
        showNotification('Twitter account verified successfully!', 'success');
      }
    } else {
      // Fallback to localStorage
      const twitterData = JSON.parse(localStorage.getItem('twitter_auth_data'));
      
      if (!twitterData) return;
      
      // Update follower count field
      const followerCountInput = document.querySelector('input[placeholder="Example: 5000"]');
      if (followerCountInput) {
        followerCountInput.value = twitterData.followers_count;
      }
      
      // Update verify button to show verified status
      const verifyButton = document.getElementById('verify-twitter-btn');
      if (verifyButton) {
        verifyButton.innerHTML = '✓ Verified';
        verifyButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        verifyButton.classList.add('verified');
        verifyButton.disabled = true;
      }
      
      // Show success message
      showNotification('Twitter account verified successfully!', 'success');
    }
  } catch (error) {
    console.error('Error updating profile with Twitter data:', error);
  }
}

// Function to show notification
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

// Check for Twitter auth success parameter in URL
function checkTwitterAuthSuccess() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('twitter_auth') === 'success' || urlParams.get('twitter_verified') === 'true') {
    updateProfileWithTwitterData();
  }
}

// Export functions for use in main application
window.twitterAuth = {
  handleVerification: handleTwitterVerification,
  checkAuthSuccess: checkTwitterAuthSuccess,
  showNotification: showNotification
};
