// Twitter OAuth Integration Mock Implementation

// Mock Twitter user data
const mockTwitterData = {
  username: 'kol_user123',
  followers_count: 5280,
  verified: true,
  profile_image: 'https://pbs.twimg.com/profile_images/default_profile.png',
  tweets: [
    {
      id: '1234567890',
      text: 'Excited to join the ACF Engine platform, looking forward to collaborating with brands! #KOL #DigitalMarketing',
      created_at: '2025-03-10T12:30:00Z',
      likes: 42,
      retweets: 12
    },
    {
      id: '1234567891',
      text: 'Just completed a cryptocurrency project promotion with great results! #Crypto #Marketing',
      created_at: '2025-03-05T09:15:00Z',
      likes: 38,
      retweets: 8
    },
    {
      id: '1234567892',
      text: 'Sharing some social media marketing tips, hope they help everyone! #SocialMedia #Tips',
      created_at: '2025-02-28T15:45:00Z',
      likes: 56,
      retweets: 23
    }
  ]
};

// Function to handle Twitter verification
function handleTwitterVerification() {
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

// Function to update profile with Twitter data
function updateProfileWithTwitterData() {
  // Get stored Twitter data
  const twitterData = JSON.parse(localStorage.getItem('twitter_auth_data'));
  
  if (!twitterData) return;
  
  // Update follower count field
  const followerCountInput = document.querySelector('input[placeholder="Example: 5000"]');
  if (followerCountInput) {
    followerCountInput.value = twitterData.followers_count;
  }
  
  // Update verify button to show verified status
  const verifyButton = document.querySelector('button.btn-standard:contains("verify")');
  if (verifyButton) {
    verifyButton.innerHTML = '✓ Verified';
    verifyButton.classList.add('bg-green-600');
    verifyButton.disabled = true;
  }
  
  // Show success message
  showNotification('Twitter account verified successfully!', 'success');
}

// Function to show notification
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${type === 'success' ? 'bg-green-500' : 'bg-blue-500'} text-white`;
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
  if (urlParams.get('twitter_auth') === 'success') {
    updateProfileWithTwitterData();
  }
}

// Export functions for use in main application
window.twitterAuth = {
  handleVerification: handleTwitterVerification,
  checkAuthSuccess: checkTwitterAuthSuccess
};
