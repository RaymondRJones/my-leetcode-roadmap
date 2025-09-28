// Simple Clerk Authentication Integration
let clerk;

async function initializeClerk() {
    // Wait for Clerk to be loaded and initialized by the data attribute
    try {
        // Wait for window.Clerk to be available
        let attempts = 0;
        while (!window.Clerk && attempts < 50) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }

        if (!window.Clerk) {
            console.error("Clerk failed to load");
            setupFallbackMode();
            return;
        }

        // Clerk is automatically initialized with the data attribute, just get the instance
        clerk = window.Clerk;

        // Wait for Clerk to be fully loaded and ready
        await clerk.load();

        // Set up global auth utilities
        window.ClerkAuth = {
            isSignedIn: () => clerk.user !== null,
            getUser: () => clerk.user,
            getToken: async () => {
                if (!clerk.session) return null;
                return await clerk.session.getToken();
            },
            hasPremiumAccess: () => {
                const user = clerk.user;
                if (!user) return false;
                return user.publicMetadata?.premium === true ||
                       user.publicMetadata?.tier === 'premium' ||
                       user.organizationMemberships?.length > 0;
            },
            isAllowedUser: () => {
                const user = clerk.user;
                if (!user) return false;
                const allowedEmails = [
                    'admin@example.com',
                    'raymond@example.com',
                ];
                return allowedEmails.includes(user.primaryEmailAddress?.emailAddress) ||
                       user.publicMetadata?.specialAccess === true;
            },
            signIn: () => {
                if (clerk.loaded) {
                    clerk.openSignIn();
                } else {
                    console.warn('Clerk not ready yet, please try again');
                }
            },
            signUp: () => {
                if (clerk.loaded) {
                    clerk.openSignUp();
                } else {
                    console.warn('Clerk not ready yet, please try again');
                }
            },
            signOut: () => {
                if (clerk.loaded) {
                    clerk.signOut();
                } else {
                    console.warn('Clerk not ready yet, please try again');
                }
            }
        };

        // Update UI based on auth state
        updateAuthUI();

        // Listen for auth state changes
        clerk.addListener(({ user }) => {
            updateAuthUI();
            if (user) {
                sendAuthToBackend(user);
            } else {
                fetch('/auth/logout', { method: 'GET' });
            }
        });

        console.log('Clerk initialized successfully');
    } catch (error) {
        console.error('Failed to initialize Clerk:', error);
        setupFallbackMode();
    }
}

function updateAuthUI() {
    const user = clerk?.user;
    const authButtons = document.querySelectorAll('[data-auth-button]');
    const userInfo = document.querySelectorAll('[data-user-info]');

    if (user) {
        // User is signed in
        authButtons.forEach(btn => {
            if (btn.dataset.authButton === 'sign-out') {
                btn.style.display = 'inline-block';
                btn.onclick = () => window.ClerkAuth.signOut();
            } else {
                btn.style.display = 'none';
            }
        });

        userInfo.forEach(info => {
            info.textContent = `Hello, ${user.firstName || user.emailAddresses[0]?.emailAddress || 'User'}`;
            info.style.display = 'inline-block';
        });
    } else {
        // User is not signed in
        authButtons.forEach(btn => {
            if (btn.dataset.authButton === 'sign-in') {
                btn.style.display = 'inline-block';
                btn.onclick = () => window.ClerkAuth.signIn();
            } else if (btn.dataset.authButton === 'sign-up') {
                btn.style.display = 'inline-block';
                btn.onclick = () => window.ClerkAuth.signUp();
            } else {
                btn.style.display = 'none';
            }
        });

        userInfo.forEach(info => {
            info.style.display = 'none';
        });
    }
}

// Track last synced user to prevent duplicate syncs
let lastSyncedUserId = null;

// Send authentication data to Flask backend
async function sendAuthToBackend(user) {
    // Prevent duplicate syncs for the same user
    if (lastSyncedUserId === user.id) {
        console.log('User already synced, skipping');
        return;
    }

    lastSyncedUserId = user.id;

    try {
        const response = await fetch('/auth/callback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user: {
                    id: user.id,
                    email_addresses: user.emailAddresses,
                    first_name: user.firstName,
                    last_name: user.lastName,
                    public_metadata: user.publicMetadata,
                    organization_memberships: user.organizationMemberships
                }
            })
        });

        if (response.ok) {
            console.log('Auth sync successful');
            // Don't reload - just update UI state
        } else {
            console.error('Auth sync failed');
        }
    } catch (error) {
        console.error('Failed to sync auth with backend:', error);
    }
}

// Fallback mode when Clerk is not available
function setupFallbackMode() {
    console.warn('Running in fallback mode without authentication');

    window.ClerkAuth = {
        isSignedIn: () => false,
        getUser: () => null,
        getToken: async () => null,
        hasPremiumAccess: () => false,
        isAllowedUser: () => false,
        signIn: () => {
            alert('Authentication is not configured. Please set up Clerk keys to enable sign-in.');
        },
        signUp: () => {
            alert('Authentication is not configured. Please set up Clerk keys to enable sign-up.');
        },
        signOut: () => {
            alert('Authentication is not configured.');
        }
    };

    // Hide auth buttons in fallback mode
    const authButtons = document.querySelectorAll('[data-auth-button]');
    authButtons.forEach(btn => {
        btn.style.display = 'none';
    });
}

// Protect premium links
function protectPremiumLinks() {
    const premiumLinks = document.querySelectorAll('a[href*="/complete-list"], a[href*="/advanced"], a[href*="/system-design"], a[href*="/behavioral-guide"]');

    premiumLinks.forEach(link => {
        console.log("HIII", window.ClerkAuth.hasPremiumAccess(), window.ClerkAuth.isAllowedUser())
        link.addEventListener('click', (e) => {
            if (!window.ClerkAuth?.isSignedIn()) {
                e.preventDefault();
                // Redirect non-logged-in users to sales page
                window.location.href = '/landing';
                return false;
            }

            if (!window.ClerkAuth.hasPremiumAccess() && !window.ClerkAuth.isAllowedUser()) {
                e.preventDefault();
                // Redirect to payment page instead of showing modal
                window.open('https://raymond-site.vercel.app/landing', '_blank');
                return false;
            }
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    initializeClerk();

    // Set up link protection after a brief delay
    setTimeout(protectPremiumLinks, 1000);
});