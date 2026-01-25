/**
 * Theme Toggle System
 * Handles switching between 'dark' (TailwindCSS) and 'legacy' (Bootstrap) themes
 */

const THEME_KEY = 'leetcode-roadmap-theme';
const THEMES = {
  DARK: 'dark',
  LEGACY: 'legacy'
};

/**
 * Get the current theme from localStorage or default to dark
 */
function getCurrentTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored && Object.values(THEMES).includes(stored)) {
    return stored;
  }
  return THEMES.DARK;
}

/**
 * Set the theme on the document and persist to localStorage
 */
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);

  // Also set a cookie for server-side detection
  document.cookie = `theme=${theme};path=/;max-age=31536000;SameSite=Lax`;

  // Update toggle button state if it exists
  updateToggleButton(theme);

  // Dispatch custom event for components that need to react
  window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
}

/**
 * Toggle between dark and legacy themes
 */
function toggleTheme() {
  const current = getCurrentTheme();
  const next = current === THEMES.DARK ? THEMES.LEGACY : THEMES.DARK;
  setTheme(next);

  // If switching to legacy, we may need to reload for Bootstrap styles
  if (next === THEMES.LEGACY) {
    // Give time for the cookie to be set before reload
    setTimeout(() => {
      window.location.reload();
    }, 100);
  } else {
    // Switching to dark might also need a reload for Tailwind styles
    setTimeout(() => {
      window.location.reload();
    }, 100);
  }
}

/**
 * Update the toggle button UI based on current theme
 */
function updateToggleButton(theme) {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const sunIcon = document.getElementById('theme-icon-sun');
  const moonIcon = document.getElementById('theme-icon-moon');
  const themeLabel = document.getElementById('theme-label');

  if (!toggleBtn) return;

  if (theme === THEMES.LEGACY) {
    // Show sun icon for legacy (light-ish) theme
    if (sunIcon) sunIcon.classList.remove('hidden');
    if (moonIcon) moonIcon.classList.add('hidden');
    if (themeLabel) themeLabel.textContent = 'Dark Mode';
  } else {
    // Show moon icon for dark theme
    if (sunIcon) sunIcon.classList.add('hidden');
    if (moonIcon) moonIcon.classList.remove('hidden');
    if (themeLabel) themeLabel.textContent = 'Classic Mode';
  }
}

/**
 * Initialize theme on page load
 */
function initTheme() {
  const theme = getCurrentTheme();
  document.documentElement.setAttribute('data-theme', theme);
  updateToggleButton(theme);
}

// Initialize immediately to prevent flash
initTheme();

// Also run on DOMContentLoaded in case toggle button is added later
document.addEventListener('DOMContentLoaded', () => {
  initTheme();

  // Attach click handler to toggle button if it exists
  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', toggleTheme);
  }
});

// Export for use in other scripts
window.ThemeToggle = {
  getCurrentTheme,
  setTheme,
  toggleTheme,
  THEMES
};
