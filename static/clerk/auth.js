// Clerk Authentication Integration for Flask App

let clerk;
let isInitialized = false;

// Initialize Clerk
async function initializeClerk() {
    if (isInitialized) return;

    try {
        // Wait for Clerk to be available
        if (!window.Clerk) {
            await new Promise((resolve) => {
                const checkClerk = () => {
                    if (window.Clerk) {
                        resolve();
                    } else {
                        setTimeout(checkClerk, 100);
                    }
                };
                checkClerk();
            });
        }

        // Get publishable key from server configuration
        const clerkPubKey = window.CLERK_CONFIG?.publishableKey;

        if (!clerkPubKey) {
            console.error('Clerk publishable key not found. Please check your server configuration.');
            return;
        }

        clerk = new window.Clerk(clerkPubKey);
        await clerk.load({
            signInUrl: '/auth/login',
            signUpUrl: '/auth/signup'
        });

        isInitialized = true;

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
            signIn: () => clerk.openSignIn(),
            signUp: () => clerk.openSignUp(),
            signOut: () => clerk.signOut()
        };

        // Listen for auth state changes
        clerk.addListener(({ user }) => {
            updateAuthUI(user);
            handleAuthChange(user);
        });

        // Initial UI update
        updateAuthUI(clerk.user);

        console.log('Clerk initialized successfully');
    } catch (error) {
        console.error('Failed to initialize Clerk:', error);
    }
}

// Update authentication UI elements
function updateAuthUI(user) {
    const authButtons = document.querySelectorAll('[data-auth-button]');
    const userInfo = document.querySelectorAll('[data-user-info]');
    const protectedContent = document.querySelectorAll('[data-protected]');

    if (user) {
        // User is signed in
        authButtons.forEach(btn => {
            if (btn.dataset.authButton === 'sign-out') {
                btn.style.display = 'inline-block';
                btn.onclick = () => clerk.signOut();
            } else {
                btn.style.display = 'none';
            }
        });

        userInfo.forEach(info => {
            info.textContent = `Hello, ${user.firstName || user.emailAddresses[0]?.emailAddress || 'User'}`;
            info.style.display = 'inline-block';
        });

        // Show/hide protected content based on premium access
        protectedContent.forEach(content => {
            const requiresPremium = content.dataset.protected === 'premium';
            if (requiresPremium && !window.ClerkAuth.hasPremiumAccess()) {
                content.innerHTML = '<div class="alert alert-warning">🔒 Premium content - upgrade to access</div>';
            } else {
                content.style.display = 'block';
            }
        });
    } else {
        // User is not signed in
        authButtons.forEach(btn => {
            if (btn.dataset.authButton === 'sign-in') {
                btn.style.display = 'inline-block';
                btn.onclick = () => clerk.openSignIn();
            } else if (btn.dataset.authButton === 'sign-up') {
                btn.style.display = 'inline-block';
                btn.onclick = () => clerk.openSignUp();
            } else {
                btn.style.display = 'none';
            }
        });

        userInfo.forEach(info => {
            info.style.display = 'none';
        });

        protectedContent.forEach(content => {
            content.innerHTML = '<div class="alert alert-info">🔐 Please sign in to access this content</div>';
        });
    }
}

// Handle authentication state changes
function handleAuthChange(user) {
    if (user) {
        // User signed in - send to backend for session management
        sendAuthToBackend(user);
    } else {
        // User signed out - clear backend session
        fetch('/auth/logout', { method: 'GET' });
    }
}

// Send authentication data to Flask backend
async function sendAuthToBackend(user) {
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
            // Reload page to update server-side authentication state
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            console.error('Auth sync failed');
        }
    } catch (error) {
        console.error('Failed to sync auth with backend:', error);
    }
}

// Protect links that require authentication
function protectLinks() {
    const protectedLinks = document.querySelectorAll('a[href*="/advanced"], a[href*="/intermediate/month"]');

    protectedLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!window.ClerkAuth || !window.ClerkAuth.isSignedIn()) {
                e.preventDefault();
                clerk.openSignIn();
                return false;
            }

            if (!window.ClerkAuth.hasPremiumAccess() && !window.ClerkAuth.isAllowedUser()) {
                e.preventDefault();
                showPaywallModal();
                return false;
            }
        });
    });
}

// Show paywall modal
function showPaywallModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">🔒 Premium Content</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>This content requires a premium subscription to access.</p>
                    <p>Upgrade now to unlock:</p>
                    <ul>
                        <li>✨ Advanced FAANG+ Roadmap</li>
                        <li>🎯 Intermediate Fortune500 Monthly Plans</li>
                        <li>📊 Detailed Progress Tracking</li>
                        <li>💼 Interview Preparation Resources</li>
                    </ul>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Later</button>
                    <button type="button" class="btn btn-primary" onclick="handleUpgrade()">Upgrade Now</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Handle upgrade process
function handleUpgrade() {
    // This is where you'd integrate with your payment system
    alert('Upgrade functionality would be integrated here with Stripe/PayPal etc.');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeClerk();

    // Small delay to ensure Clerk is loaded before protecting links
    setTimeout(protectLinks, 1000);
});

// Re-run protection after page updates
window.addEventListener('load', () => {
    setTimeout(protectLinks, 1500);
});