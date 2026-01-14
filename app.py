#!/usr/bin/env python3
"""
LeetCode Roadmap Generator - Entry Point

This is the main entry point for the Flask application.
"""
import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Create templates directory if needed
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Get port from environment variable for Heroku, or use 5002 for local dev
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') != 'production'

    print(f"Starting server on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
