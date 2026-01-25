/** @type {import('tailwindcss').Config} */
export default {
  content: [
    '../templates/**/*.html',
    '../static/**/*.js',
    './src/**/*.js'
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Background colors - Near black palette
        background: {
          DEFAULT: '#0A0A0B',
          secondary: '#111113',
          elevated: '#1A1A1D',
          hover: '#242428'
        },
        // Foreground/text colors
        foreground: {
          DEFAULT: '#FAFAFA',
          muted: '#A1A1AA',
          subtle: '#71717A'
        },
        // Border colors
        border: {
          DEFAULT: '#27272A',
          hover: '#3F3F46',
          focus: '#52525B'
        },
        // Accent colors
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          muted: '#1D4ED8'
        },
        success: {
          DEFAULT: '#22C55E',
          hover: '#16A34A',
          muted: '#15803D'
        },
        warning: {
          DEFAULT: '#F59E0B',
          hover: '#D97706',
          muted: '#B45309'
        },
        danger: {
          DEFAULT: '#EF4444',
          hover: '#DC2626',
          muted: '#B91C1C'
        },
        // Problem difficulty colors
        easy: '#22C55E',
        medium: '#F59E0B',
        hard: '#EF4444'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace']
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }]
      },
      boxShadow: {
        'glow': '0 0 20px rgba(59, 130, 246, 0.15)',
        'glow-success': '0 0 20px rgba(34, 197, 94, 0.15)',
        'glow-warning': '0 0 20px rgba(245, 158, 11, 0.15)',
        'glow-danger': '0 0 20px rgba(239, 68, 68, 0.15)',
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.4)'
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-card': 'linear-gradient(145deg, rgba(26, 26, 29, 0.8) 0%, rgba(17, 17, 19, 0.9) 100%)',
        'gradient-primary': 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
        'gradient-success': 'linear-gradient(135deg, #22C55E 0%, #15803D 100%)',
        'gradient-border': 'linear-gradient(135deg, #3F3F46 0%, #27272A 100%)'
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(59, 130, 246, 0.25)' }
        }
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem'
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      }
    }
  },
  plugins: []
}
