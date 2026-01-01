// Simple Clerk Authentication Integration
let clerk;
let isClerkReady = false;
let authCheckInProgress = false;

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
                return user.publicMetadata?.has_premium === true ||
                       user.publicMetadata?.premium === true ||
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

        // Mark Clerk as ready
        isClerkReady = true;
        authCheckInProgress = false;

        // Update UI based on auth state
        updateAuthUI();
        updateNavigationAccess();

        // Listen for auth state changes
        clerk.addListener(({ user }) => {
            updateAuthUI();
            updateNavigationAccess();
            if (user) {
                sendAuthToBackend(user);
            } else {
                fetch('/auth/logout', { method: 'GET' });
            }
        });

        console.log('Clerk initialized successfully');
    } catch (error) {
        console.error('Failed to initialize Clerk:', error);
        isClerkReady = true; // Mark as ready to avoid infinite loading
        authCheckInProgress = false;
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

// Update navigation access based on authentication status
function updateNavigationAccess() {
    if (!isClerkReady) return;

    const premiumNavLinks = document.querySelectorAll('a[href="/advanced"], a[href="/complete-list"], a[href="/system-design"], a[href="/behavioral-guide"]');
    const isSignedIn = window.ClerkAuth?.isSignedIn();
    const hasPremium = window.ClerkAuth?.hasPremiumAccess();
    const isAllowed = window.ClerkAuth?.isAllowedUser();

    premiumNavLinks.forEach(link => {
        // Remove any existing classes and handlers
        link.classList.remove('nav-disabled', 'nav-premium-required');
        link.removeAttribute('data-original-href');

        if (!isSignedIn) {
            // User not signed in - disable and redirect to landing
            link.classList.add('nav-disabled');
            link.setAttribute('data-original-href', link.href);
            link.href = '/landing';
            link.title = 'Sign in required';

            // Add visual indicator
            link.style.opacity = '0.6';
            link.style.pointerEvents = 'none';
        } else if (!hasPremium && !isAllowed) {
            // User signed in but no premium access
            link.classList.add('nav-premium-required');
            link.setAttribute('data-original-href', link.href);
            link.href = 'https://raymond-site.vercel.app/leetcode-roadmap';
            link.setAttribute('target', '_blank');
            link.title = 'Premium access required';

            // Add visual indicator
            link.style.opacity = '0.7';
            const icon = link.querySelector('.material-icons');
            if (icon) {
                icon.style.color = 'var(--md-warning)';
            }
        } else {
            // User has access - restore normal functionality
            const originalHref = link.getAttribute('data-original-href');
            if (originalHref) {
                link.href = originalHref;
                link.removeAttribute('data-original-href');
            }
            link.removeAttribute('target');
            link.title = '';
            link.style.opacity = '1';
            link.style.pointerEvents = 'auto';

            const icon = link.querySelector('.material-icons');
            if (icon) {
                icon.style.color = '';
            }
        }
    });
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
                    private_metadata: user.privateMetadata,
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

    isClerkReady = true;
    authCheckInProgress = false;

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

    // Update navigation access (will disable premium links)
    updateNavigationAccess();

    // Hide auth buttons in fallback mode
    const authButtons = document.querySelectorAll('[data-auth-button]');
    authButtons.forEach(btn => {
        btn.style.display = 'none';
    });
}

// Enhanced premium link protection with immediate blocking
function protectPremiumLinks() {
    const premiumLinks = document.querySelectorAll('a[href*="/guides"], a[href*="/complete-list"], a[href*="/advanced"], a[href*="/system-design"], a[href*="/behavioral-guide"]');
    const intermediateMonthLinks = document.querySelectorAll('a[href*="/intermediate/month/Month%202"], a[href*="/intermediate/month/Month 2"], a[href*="/intermediate/month/Month%203"], a[href*="/intermediate/month/Month 3"]');

    premiumLinks.forEach(link => {

        // Remove any existing click handlers
        link.replaceWith(link.cloneNode(true));
        const newLink = document.querySelector(`a[href="${link.href}"]`);

        newLink.addEventListener('click', (e) => {
            // Block all clicks if Clerk isn't ready yet
            if (!isClerkReady || authCheckInProgress) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Blocking access - authentication still loading');
                return false;
            }

            if (!window.ClerkAuth?.isSignedIn()) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Blocking access - user not signed in');
                window.location.href = '/landing';
                return false;
            }

            if (!window.ClerkAuth.hasPremiumAccess() && !window.ClerkAuth.isAllowedUser()) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Blocking access - no premium access');
                window.open('https://raymond-site.vercel.app/leetcode-roadmap', '_blank');
                return false;
            }

            console.log('Allowing access - user has permissions');
        });
    });

    // Protect Month 2 and Month 3 intermediate links
    intermediateMonthLinks.forEach(link => {
        // Remove any existing click handlers
        link.replaceWith(link.cloneNode(true));
        const newLink = document.querySelector(`a[href="${link.href}"]`);

        newLink.addEventListener('click', (e) => {
            // Block all clicks if Clerk isn't ready yet
            if (!isClerkReady || authCheckInProgress) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Blocking access - authentication still loading');
                return false;
            }

            if (!window.ClerkAuth?.isSignedIn()) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Blocking access - user not signed in');
                window.location.href = '/landing';
                return false;
            }

            if (!window.ClerkAuth.hasPremiumAccess() && !window.ClerkAuth.isAllowedUser()) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Blocking access - no premium access');
                window.open('https://raymond-site.vercel.app/leetcode-roadmap', '_blank');
                return false;
            }

            console.log('Allowing access - user has permissions');
        });
    });
}

// Immediate protection for all links - runs before Clerk loads
function immediateProtection() {
    authCheckInProgress = true;

    // Block ALL premium links immediately
    const allPremiumLinks = document.querySelectorAll('a[href*="/complete-list"], a[href*="/advanced"], a[href*="/system-design"], a[href*="/behavioral-guide"]');
    const intermediateMonthLinks = document.querySelectorAll('a[href*="/intermediate/month/Month%202"], a[href*="/intermediate/month/Month 2"], a[href*="/intermediate/month/Month%203"], a[href*="/intermediate/month/Month 3"]');

    allPremiumLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!isClerkReady) {
                e.preventDefault();
                e.stopPropagation();
                console.log('SECURITY: Blocked access attempt before authentication ready');
                return false;
            }
        }, { capture: true }); // Use capture to catch events early
    });

    // Block Month 2 and Month 3 intermediate links immediately
    intermediateMonthLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!isClerkReady) {
                e.preventDefault();
                e.stopPropagation();
                console.log('SECURITY: Blocked access attempt before authentication ready');
                return false;
            }
        }, { capture: true }); // Use capture to catch events early
    });
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    // Apply immediate protection before Clerk loads
    immediateProtection();

    // Initialize Clerk authentication
    initializeClerk();

    // Set up comprehensive link protection
    setTimeout(protectPremiumLinks, 100);
});

// Also run immediate protection as early as possible
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', immediateProtection);
} else {
    immediateProtection();
}