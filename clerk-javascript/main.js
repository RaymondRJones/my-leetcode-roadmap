import Clerk from '@clerk/clerk-js';

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const clerk = new Clerk(clerkPubKey);
await clerk.load();

// Export clerk for use in other parts of the app
window.clerk = clerk;

// Auth utilities for the main Flask app
window.ClerkAuth = {
  // Check if user is signed in
  isSignedIn: () => {
    return clerk.user !== null;
  },

  // Get user data
  getUser: () => {
    return clerk.user;
  },

  // Get session token for API calls
  getToken: async () => {
    if (!clerk.session) return null;
    return await clerk.session.getToken();
  },

  // Check if user has premium access (customize logic as needed)
  hasPremiumAccess: () => {
    const user = clerk.user;
    if (!user) return false;

    // Check for premium subscription or specific permissions
    // This is where you'd implement your paywall logic
    return user.publicMetadata?.premium === true ||
           user.publicMetadata?.tier === 'premium' ||
           user.organizationMemberships?.length > 0;
  },

  // Check if user is in allowed list
  isAllowedUser: () => {
    const user = clerk.user;
    if (!user) return false;

    // Check if user email is in allowed list (you can customize this)
    const allowedEmails = [
      'admin@example.com',
      // Add more allowed emails here
    ];

    return allowedEmails.includes(user.primaryEmailAddress?.emailAddress) ||
           user.publicMetadata?.specialAccess === true;
  },

  // Sign in
  signIn: () => {
    clerk.openSignIn();
  },

  // Sign up
  signUp: () => {
    clerk.openSignUp();
  },

  // Sign out
  signOut: () => {
    clerk.signOut();
  }
};

// Initialize UI components
clerk.addListener(({ user }) => {
  // Update UI when auth state changes
  updateAuthUI(user);
});

function updateAuthUI(user) {
  // Update any auth-related UI elements
  const authButtons = document.querySelectorAll('[data-auth-button]');
  const userInfo = document.querySelectorAll('[data-user-info]');
  const protectedContent = document.querySelectorAll('[data-protected]');

  if (user) {
    // User is signed in
    authButtons.forEach(btn => {
      if (btn.dataset.authButton === 'sign-out') {
        btn.style.display = 'inline-block';
        btn.textContent = 'Sign Out';
        btn.onclick = () => clerk.signOut();
      } else {
        btn.style.display = 'none';
      }
    });

    userInfo.forEach(info => {
      info.textContent = user.firstName || user.emailAddresses[0]?.emailAddress || 'User';
      info.style.display = 'inline-block';
    });

    // Show/hide protected content based on premium access
    protectedContent.forEach(content => {
      const requiresPremium = content.dataset.protected === 'premium';
      if (requiresPremium && !window.ClerkAuth.hasPremiumAccess()) {
        content.style.display = 'none';
      } else {
        content.style.display = 'block';
      }
    });
  } else {
    // User is not signed in
    authButtons.forEach(btn => {
      if (btn.dataset.authButton === 'sign-in') {
        btn.style.display = 'inline-block';
        btn.textContent = 'Sign In';
        btn.onclick = () => clerk.openSignIn();
      } else if (btn.dataset.authButton === 'sign-up') {
        btn.style.display = 'inline-block';
        btn.textContent = 'Sign Up';
        btn.onclick = () => clerk.openSignUp();
      } else {
        btn.style.display = 'none';
      }
    });

    userInfo.forEach(info => {
      info.style.display = 'none';
    });

    protectedContent.forEach(content => {
      content.style.display = 'none';
    });
  }
}

// Initial UI update
updateAuthUI(clerk.user);
