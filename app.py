#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request, redirect, session, abort
import json
import os
import jwt
import requests
import stripe
import hmac
import hashlib
from functools import wraps
from pdf_analyzer import LeetCodeRoadmapAnalyzer
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Clerk configuration
CLERK_SECRET_KEY = os.environ.get('CLERK_SECRET_KEY')
CLERK_PUBLISHABLE_KEY = os.environ.get('CLERK_PUBLISHABLE_KEY')
if not CLERK_PUBLISHABLE_KEY:
    raise RuntimeError("❌ Please set the CLERK_PUBLISHABLE_KEY in your .env file.")

# Stripe configuration
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Stripe Product ID to Metadata Mapping
STRIPE_PRODUCT_METADATA = {
    'prod_SvD9M0caNlgkfo': {
        'has_premium': True,
        'has_ai_access': False,
        'has_system_design_access': False,
        'description': 'Premium Only'
    },
    'prod_SzSqbijjdXdg2a': {
        'has_premium': True,
        'has_ai_access': False,
        'has_system_design_access': True,
        'description': 'Premium + System Design'
    },
    'prod_SxymCQ9tLRKY3u': {
        'has_premium': True,
        'has_ai_access': False,
        'has_system_design_access': True,
        'description': 'Premium + System Design (Alternate)'
    }
}

# Initialize OpenAI client only if API key is available
def get_openai_client():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=api_key)

# Clerk API helper functions for Stripe webhook integration
def get_clerk_user_by_email(email):
    """Find Clerk user by email address"""
    if not CLERK_SECRET_KEY:
        return None

    headers = {
        'Authorization': f'Bearer {CLERK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        resp = requests.get(
            'https://api.clerk.com/v1/users',
            headers=headers,
            params={'email_address': email}
        )

        if resp.status_code != 200:
            return None

        response_data = resp.json()
        if isinstance(response_data, dict):
            data = response_data.get('data', [])
        else:
            data = response_data

        for user in data:
            for e in user.get('email_addresses', []):
                if e.get('email_address') == email:
                    return user
        return None
    except Exception as e:
        print(f"Error finding Clerk user {email}: {e}")
        return None


def create_clerk_user_with_metadata(email, metadata):
    """Create new Clerk user with both private and public metadata"""
    if not CLERK_SECRET_KEY:
        return None

    headers = {
        'Authorization': f'Bearer {CLERK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'email_address': [email],
        'private_metadata': metadata,
        'public_metadata': metadata,
        'skip_password_checks': True,
        'skip_password_requirement': True,
        'password': f'TempStripe{os.urandom(8).hex()}!',
    }

    try:
        resp = requests.post(
            'https://api.clerk.com/v1/users',
            headers=headers,
            json=payload
        )

        if resp.status_code != 200:
            print(f"Failed to create Clerk user {email}: {resp.text}")
            return None

        print(f"✅ Created Clerk user {email} from Stripe purchase")
        return resp.json()
    except Exception as e:
        print(f"Error creating Clerk user {email}: {e}")
        return None


def update_clerk_user_metadata_by_id(user_id, metadata):
    """Update Clerk user's private and public metadata"""
    if not CLERK_SECRET_KEY:
        return None

    headers = {
        'Authorization': f'Bearer {CLERK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'private_metadata': metadata,
        'public_metadata': metadata
    }

    try:
        resp = requests.patch(
            f'https://api.clerk.com/v1/users/{user_id}',
            headers=headers,
            json=payload
        )

        if resp.status_code != 200:
            print(f"Failed to update Clerk user {user_id}: {resp.text}")
            return None

        print(f"✅ Updated Clerk user {user_id} metadata")
        return resp.json()
    except Exception as e:
        print(f"Error updating Clerk user {user_id}: {e}")
        return None


def provision_user_from_stripe(email, product_id):
    """Provision or update Clerk user based on Stripe product purchase"""
    metadata = STRIPE_PRODUCT_METADATA.get(product_id)

    # Default configuration for unknown products - grant premium access
    if not metadata:
        print(f"⚠️ Unknown product ID: {product_id}, using default premium access")
        metadata = {
            'has_premium': True,
            'has_ai_access': False,
            'has_system_design_access': False,
            'description': 'Default Premium (Unknown Product)'
        }

    # Remove description from metadata before applying
    user_metadata = {k: v for k, v in metadata.items() if k != 'description'}

    # Check if user exists
    user = get_clerk_user_by_email(email)

    if user:
        # User exists - merge metadata
        user_id = user['id']
        current_metadata = user.get('private_metadata', {})

        # Merge: new metadata takes precedence
        merged_metadata = current_metadata.copy()
        for key, value in user_metadata.items():
            if value or key not in merged_metadata:
                merged_metadata[key] = value

        result = update_clerk_user_metadata_by_id(user_id, merged_metadata)
        return result is not None
    else:
        # Create new user
        result = create_clerk_user_with_metadata(email, user_metadata)
        return result is not None

# Simplified authentication - relying on frontend verification and session storage
def get_current_user():
    """Get current user from Flask session (set by frontend auth callback)"""
    return session.get('user')

def has_premium_access(user_data):
    """Check if user has premium access"""
    if not user_data:
        return False

    # Check private_metadata first (more secure), fallback to public_metadata
    private_metadata = user_data.get('private_metadata', {})
    if private_metadata and 'has_premium' in private_metadata:
        return private_metadata.get('has_premium', False)

    # Fallback to public_metadata for backwards compatibility
    public_metadata = user_data.get('public_metadata', {})
    return public_metadata.get('has_premium', False)

def has_ai_access(user_data):
    """Check if user has AI access"""
    if not user_data:
        return False

    # Check private_metadata first, fallback to public_metadata
    private_metadata = user_data.get('private_metadata', {})
    if private_metadata and 'has_ai_access' in private_metadata:
        return private_metadata.get('has_ai_access', False)

    # Fallback to public_metadata
    public_metadata = user_data.get('public_metadata', {})
    return public_metadata.get('has_ai_access', False)

def has_system_design_access(user_data):
    """Check if user has system design access"""
    if not user_data:
        return False

    # Check private_metadata first, fallback to public_metadata
    private_metadata = user_data.get('private_metadata', {})
    if private_metadata and 'has_system_design_access' in private_metadata:
        return private_metadata.get('has_system_design_access', False)

    # Fallback to public_metadata
    public_metadata = user_data.get('public_metadata', {})
    return public_metadata.get('has_system_design_access', False)

def is_allowed_user(user_data):
    """Check if user is in the special allowed list"""
    if not user_data:
        return False

    # List of allowed email addresses with special access
    allowed_emails = [
        'admin@example.com',
        'raymond@example.com',
        # Add more allowed emails here
    ]

    email_addresses = user_data.get('email_addresses', [])
    primary_email = ''
    if email_addresses:
        primary_email = email_addresses[0].get('email_address', '')

    public_metadata = user_data.get('public_metadata', {})

    return (
        primary_email in allowed_emails or
        public_metadata.get('specialAccess') is True
    )

# Authentication decorators
def login_required(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')
        return f(*args, **kwargs)
    return decorated_function

def premium_required(f):
    """Require user to have premium access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not has_premium_access(user) and not is_allowed_user(user):
            return redirect('/landing')

        return f(*args, **kwargs)
    return decorated_function

def ai_access_required(f):
    """Require user to have AI access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not has_ai_access(user) and not is_allowed_user(user):
            return redirect('/landing')

        return f(*args, **kwargs)
    return decorated_function

def system_design_access_required(f):
    """Require user to have system design access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/landing')

        if not has_system_design_access(user) and not is_allowed_user(user):
            return redirect('/landing')

        return f(*args, **kwargs)
    return decorated_function

# Stripe webhook event extraction helpers
def extract_customer_email_from_stripe_event(event):
    """Extract customer email from Stripe event"""
    data = event.get('data', {}).get('object', {})

    # Try customer_email field
    if 'customer_email' in data and data['customer_email']:
        return data['customer_email']

    # Try customer_details
    if 'customer_details' in data:
        email = data['customer_details'].get('email')
        if email:
            return email

    # Fetch customer object
    customer_id = data.get('customer')
    if customer_id and STRIPE_SECRET_KEY:
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer.email
        except Exception as e:
            print(f"Error fetching customer {customer_id}: {e}")
            return None

    return None


def extract_product_id_from_stripe_event(event):
    """Extract product ID from Stripe event"""
    event_type = event.get('type', '')
    data = event.get('data', {}).get('object', {})

    # For checkout.session.completed
    if event_type == 'checkout.session.completed':
        # Check if line_items are included in the event
        line_items = data.get('line_items', {}).get('data', [])

        # If line_items not in event, fetch the session with expanded line_items
        if not line_items and STRIPE_SECRET_KEY:
            session_id = data.get('id')
            if session_id:
                try:
                    print(f"📥 Fetching session {session_id} with line items...")
                    session = stripe.checkout.Session.retrieve(
                        session_id,
                        expand=['line_items']
                    )
                    line_items = session.get('line_items', {}).get('data', [])
                    print(f"✅ Retrieved {len(line_items)} line items")
                except Exception as e:
                    print(f"❌ Error fetching session: {e}")

        # Extract product from line items
        if line_items:
            price = line_items[0].get('price', {})
            product_id = price.get('product')
            print(f"🔍 Found product ID from line items: {product_id}")
            return product_id

    # For subscription/invoice events
    if 'subscription' in event_type or event_type == 'invoice.payment_succeeded':
        if 'items' in data:
            items = data['items'].get('data', [])
            if items:
                price = items[0].get('price', {})
                return price.get('product')

        if 'lines' in data:
            lines = data['lines'].get('data', [])
            if lines:
                price = lines[0].get('price', {})
                return price.get('product')

    return None

class RoadmapWebApp:
    def __init__(self):
        self.roadmap_data = {}
        self.intermediate_roadmap_data = {}
        self.atcoder_problems = {}
        # Define the order of months and their display names
        self.month_order = ['April', 'May', 'June', 'July', 'August']
        self.month_mapping = {
            'April': 'Month 1',
            'May': 'Month 2', 
            'June': 'Month 3',
            'July': 'Month 4',
            'August': 'Month 5'
        }
        # Define intermediate roadmap order
        self.intermediate_month_order = ['Month 1', 'Month 2', 'Month 3']
        self.load_roadmap_data()
        self.load_intermediate_roadmap_data()
        self.load_atcoder_problems()
    
    def load_roadmap_data(self):
        """Load roadmap data from JSON file"""
        if os.path.exists('roadmap_data.json'):
            with open('roadmap_data.json', 'r', encoding='utf-8') as f:
                self.roadmap_data = json.load(f)
        else:
            print("No roadmap data found. Run pdf_analyzer.py first.")
    
    def load_intermediate_roadmap_data(self):
        """Load intermediate roadmap data from JSON file"""
        if os.path.exists('intermediate_roadmap_data.json'):
            with open('intermediate_roadmap_data.json', 'r', encoding='utf-8') as f:
                self.intermediate_roadmap_data = json.load(f)
        else:
            print("No intermediate roadmap data found. Run pdf analyzer for intermediate PDFs first.")
    
    def load_atcoder_problems(self):
        """Load AtCoder beginner problems from JSON file"""
        if os.path.exists('atcoder_beginner_problems.json'):
            with open('atcoder_beginner_problems.json', 'r', encoding='utf-8') as f:
                self.atcoder_problems = json.load(f)
        else:
            print("No AtCoder problems found. Run scripts/atcoder_scraper.py first.")
    
    def get_ordered_roadmap_data(self):
        """Get roadmap data ordered properly and with renamed months, separating bonus problems"""
        ordered_data = {}
        for original_month in self.month_order:
            if original_month in self.roadmap_data:
                display_month = self.month_mapping.get(original_month, original_month)
                month_data = self.roadmap_data[original_month].copy()
                
                # Process the data to separate bonus problems
                processed_month = []
                bonus_problems = []
                
                for day in month_data:
                    if day['day'] == 30:
                        # Day 30 problems become bonus problems
                        bonus_problems.extend(day['problems'])
                    else:
                        # Regular days - limit to 3 problems, rest go to bonus
                        regular_problems = day['problems'][:3]
                        if len(day['problems']) > 3:
                            bonus_problems.extend(day['problems'][3:])
                        
                        processed_month.append({
                            'day': day['day'],
                            'problems': regular_problems
                        })
                
                # Add bonus section if there are bonus problems
                if bonus_problems:
                    processed_month.append({
                        'day': 'bonus',
                        'problems': bonus_problems
                    })
                
                ordered_data[display_month] = processed_month
        return ordered_data
    
    def get_ordered_intermediate_roadmap_data(self):
        """Get intermediate roadmap data ordered properly, separating bonus problems"""
        ordered_data = {}
        for month in self.intermediate_month_order:
            if month in self.intermediate_roadmap_data:
                month_data = self.intermediate_roadmap_data[month].copy()
                
                # Process the data to separate bonus problems (same logic as regular roadmap)
                processed_month = []
                bonus_problems = []
                
                for day in month_data:
                    if day['day'] == 30:
                        # Day 30 problems become bonus problems
                        bonus_problems.extend(day['problems'])
                    else:
                        # Regular days - limit to 3 problems, rest go to bonus
                        regular_problems = day['problems'][:3]
                        if len(day['problems']) > 3:
                            bonus_problems.extend(day['problems'][3:])
                        
                        processed_month.append({
                            'day': day['day'],
                            'problems': regular_problems
                        })
                
                # Add bonus section if there are bonus problems
                if bonus_problems:
                    processed_month.append({
                        'day': 'bonus',
                        'problems': bonus_problems
                    })
                
                ordered_data[month] = processed_month
        return ordered_data
    
    def get_original_month_name(self, display_month):
        """Get original month name from display name"""
        for original, display in self.month_mapping.items():
            if display == display_month:
                return original
        return display_month
    
    def refresh_data(self):
        """Refresh data by re-analyzing PDFs"""
        analyzer = LeetCodeRoadmapAnalyzer()
        # Regular roadmap
        monthly_problems = analyzer.analyze_all_pdfs()
        roadmap = analyzer.create_daily_roadmap(monthly_problems)
        analyzer.save_roadmap_json(roadmap)
        # Intermediate roadmap
        intermediate_problems = analyzer.analyze_intermediate_pdfs()
        intermediate_roadmap = analyzer.create_daily_roadmap(intermediate_problems)
        analyzer.save_intermediate_roadmap_json(intermediate_roadmap)
        
        self.load_roadmap_data()
        self.load_intermediate_roadmap_data()
        self.load_atcoder_problems()

web_app = RoadmapWebApp()

# Context processor to make auth data available in all templates
@app.context_processor
def inject_auth():
    user = get_current_user()
    return {
        'current_user': user,
        'is_authenticated': user is not None,
        'has_premium': has_premium_access(user) if user else False,
        'has_ai_access': has_ai_access(user) if user else False,
        'has_system_design_access': has_system_design_access(user) if user else False,
        'is_allowed': is_allowed_user(user) if user else False,
        'clerk_publishable_key': CLERK_PUBLISHABLE_KEY
    }

# Authentication routes
@app.route('/auth/login')
def auth_login():
    """Login page - handled by Clerk on frontend"""
    return render_template('auth/login.html')

@app.route('/auth/callback', methods=['POST'])
def auth_callback():
    """Handle Clerk auth callback"""
    try:
        data = request.get_json()
        user_data = data.get('user')

        if user_data:
            # Store user data in Flask session
            session['user'] = user_data
            return jsonify({'status': 'success'})

        return jsonify({'status': 'error', 'message': 'No user data provided'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/auth/logout')
def auth_logout():
    """Logout user"""
    session.pop('user', None)
    return redirect('/')

@app.route('/')
def index():
    """Classroom homepage - Central hub for all courses"""
    courses = [
        {
            'title': 'Complete Beginner Roadmap',
            'description': 'Master programming fundamentals with 200+ beginner-friendly problems. Perfect for absolute beginners starting from zero.',
            'route': '/beginner',
            'icon': 'school',
            'label': 'LEVEL 1',
            'image_url': '/static/images/course-beginner.jpg',
            'is_premium': False,
            'course_type': 'course-free',
            'duration': '4-8 weeks',
            'problem_count': '200+ problems',
            'level': 'Beginner',
            'order': 1
        },
        {
            'title': 'Fortune500 Roadmap',
            'description': 'Intermediate preparation for mid-tier companies. Month 1 is free, complete all 3 months to master mid-level interviews.',
            'route': '/intermediate',
            'icon': 'rocket_launch',
            'label': 'LEVEL 2',
            'image_url': '/static/images/course-intermediate.jpg',
            'is_premium': True,
            'course_type': 'course-premium',
            'duration': '3 months',
            'problem_count': '300+ problems',
            'level': 'Intermediate',
            'order': 2
        },
        {
            'title': 'The Software Engineering Journey',
            'description': 'Follow Raymond\'s complete path from bootcamp to Fortune 1 software engineer. Learn the strategies that work in 2025.',
            'route': '/roadmap',
            'icon': 'trending_up',
            'label': 'CAREER GUIDE',
            'image_url': '/static/images/course-journey.jpg',
            'is_premium': False,
            'course_type': 'course-free',
            'duration': '6-18 months',
            'problem_count': 'Career guide',
            'level': 'All Levels',
            'order': 3
        },
        {
            'title': 'FAANG+ Roadmap',
            'description': 'Raymond\'s exact path to top 2% on LeetCode. Advanced problems for FAANG and top-tier company preparation.',
            'route': '/advanced',
            'icon': 'star',
            'label': 'LEVEL 3',
            'image_url': '/static/images/course-advanced.jpg',
            'is_premium': True,
            'course_type': 'course-premium',
            'duration': '6+ months',
            'problem_count': '400+ problems',
            'level': 'Advanced',
            'order': 4
        },
        {
            'title': 'Ray700 Complete List',
            'description': 'Custom study plan generator with 700+ curated problems. Filter by difficulty, topics, and create your personalized roadmap.',
            'route': '/complete-list',
            'icon': 'tune',
            'label': 'MASTER COLLECTION',
            'image_url': '/static/images/course-ray700.jpg',
            'is_premium': True,
            'course_type': 'course-premium',
            'duration': 'Flexible',
            'problem_count': '700+ problems',
            'level': 'All Levels',
            'order': 5
        },
        {
            'title': 'Resume + LinkedIn Guide',
            'description': 'My exact resume and LinkedIn profile that landed me offers at Fortune 1 companies. Step-by-step templates and strategies.',
            'route': '/guides',
            'icon': 'description',
            'label': 'CAREER DOCS',
            'image_url': '/static/images/course-resume.jpg',
            'is_premium': True,
            'course_type': 'course-premium',
            'duration': '2-4 hours',
            'problem_count': 'Templates',
            'level': 'All Levels',
            'order': 6
        },
        {
            'title': 'System Design Guide',
            'description': 'Master system design interviews with real-world examples, architecture patterns, and scalability principles.',
            'route': '/guides',
            'icon': 'account_tree',
            'label': 'ARCHITECTURE',
            'image_url': '/static/images/course-system-design.jpg',
            'is_premium': True,
            'course_type': 'course-premium',
            'duration': '4-8 weeks',
            'problem_count': 'Design patterns',
            'level': 'Advanced',
            'order': 7
        },
        {
            'title': 'Python Assessment',
            'description': 'Test your Python knowledge with 20 multiple-choice questions. Evaluate your skills in syntax, data structures, and OOP concepts.',
            'route': '/python-assessment',
            'icon': 'quiz',
            'label': 'PYTHON TEST',
            'image_url': '/static/images/course-python.jpg',
            'is_premium': False,
            'course_type': 'course-free',
            'duration': '15-20 min',
            'problem_count': '20 questions',
            'level': 'All Levels',
            'order': 8
        },
        {
            'title': 'Java Assessment',
            'description': 'Evaluate your Java proficiency with 20 multiple-choice questions covering fundamentals, OOP, collections, and best practices.',
            'route': '/java-assessment',
            'icon': 'quiz',
            'label': 'JAVA TEST',
            'image_url': '/static/images/course-java.jpg',
            'is_premium': False,
            'course_type': 'course-free',
            'duration': '15-20 min',
            'problem_count': '20 questions',
            'level': 'All Levels',
            'order': 9
        }
    ]

    courses.sort(key=lambda x: x['order'])
    return render_template('classroom.html', courses=courses)

@app.route('/classroom')
def classroom():
    """Redirect to classroom homepage"""
    return redirect('/')

@app.route('/landing')
def sales_page():
    """Sales page showing all available premium roadmaps"""
    return render_template('sales_homepage.html')

@app.route('/intermediate')
def intermediate_view():
    """Intermediate roadmap (Fortune500) - Free for all users"""
    return render_template('intermediate.html', roadmap=web_app.get_ordered_intermediate_roadmap_data())

@app.route('/advanced')
@premium_required
def advanced_view():
    """Advanced roadmap page (formerly home page) - Premium content"""
    return render_template('index.html', roadmap=web_app.get_ordered_roadmap_data())

@app.route('/api/roadmap')
def api_roadmap():
    """API endpoint to get roadmap data"""
    return jsonify(web_app.get_ordered_roadmap_data())

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """API endpoint to refresh roadmap data"""
    try:
        web_app.refresh_data()
        return jsonify({'status': 'success', 'message': 'Roadmap data refreshed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/advanced/month/<month_name>')
@premium_required
def advanced_month_view(month_name):
    """View for a specific advanced month - Premium content"""
    # Convert display month name back to original month name
    original_month = web_app.get_original_month_name(month_name)
    month_data = web_app.roadmap_data.get(original_month, [])
    return render_template('month.html', month=month_name, days=month_data)


@app.route('/month/<month_name>')
def intermediate_month_redirect(month_name):
    """Redirect old intermediate month URLs to new structure"""
    return redirect(f'/intermediate/month/{month_name}')

@app.route('/intermediate/month/<month_name>')
def intermediate_month_view(month_name):
    """View for a specific intermediate month - Month 1 is free, Month 2+ requires premium"""
    # Allow Month 1 for everyone, require premium for Month 2 and 3
    if month_name != 'Month 1':
        # Check if user has premium access
        user = get_current_user()
        if not user:
            return redirect('/landing')
        if not has_premium_access(user) and not is_allowed_user(user):
            return redirect('https://raymond-site.vercel.app/leetcode-roadmap')

    ordered_data = web_app.get_ordered_intermediate_roadmap_data()
    month_data = ordered_data.get(month_name, [])
    return render_template('month.html', month=f"Intermediate {month_name}", days=month_data, is_intermediate=True)

@app.route('/beginner')
def beginner_view():
    """View for beginner AtCoder problems"""
    return render_template('beginner.html', atcoder_data=web_app.atcoder_problems)

@app.route('/api/atcoder')
def api_atcoder():
    """API endpoint to get AtCoder beginner problems"""
    return jsonify(web_app.atcoder_problems)

@app.route('/problem/<int:problem_id>')
def problem_detail(problem_id):
    """Detailed view for a specific beginner problem"""
    problems = web_app.atcoder_problems.get('problems', [])
    if 0 <= problem_id < len(problems):
        problem = problems[problem_id]
        return render_template('problem_detail.html', problem=problem, problem_id=problem_id)
    else:
        return "Problem not found", 404

@app.route('/roadmap')
def software_roadmap():
    """Raymond's Path to Software Engineer at Fortune 1"""
    return render_template('roadmap.html')

@app.route('/about')
def about():
    """About Raymond and his journey"""
    return render_template('about.html')

@app.route('/python-assessment')
def python_assessment():
    """Python programming assessment quiz"""
    return render_template('python_assessment.html')

@app.route('/java-assessment')
def java_assessment():
    """Java programming assessment quiz"""
    return render_template('java_assessment.html')

@app.route('/system-design')
@system_design_access_required
def system_design():
    """System Design Roadmap homepage - System Design Access Required"""
    return render_template('system_design/index.html')

@app.route('/system-design/real-life-problems')
@system_design_access_required
def system_design_real_life():
    """System Design Real Life Problems page - System Design Access Required"""
    return render_template('system_design/real_life_problems.html')

@app.route('/system-design/trivia')
@system_design_access_required
def system_design_trivia():
    """System Design Trivia and Knowledge Checks page - System Design Access Required"""
    return render_template('system_design/trivia.html')

@app.route('/system-design/low-level-design')
@system_design_access_required
def system_design_low_level():
    """System Design Low Level Design page - System Design Access Required"""
    return render_template('system_design/low_level_design.html')

@app.route('/guides')
@premium_required
def guides():
    """Guides landing page with all available guides"""
    return render_template('guides.html')

@app.route('/behavioral-guide')
@ai_access_required
def behavioral_guide():
    """Behavioral Interview Guide with AI Helper - AI Access Required"""
    # Amazon Leadership Principles questions
    behavioral_questions = {
        "General": [
            "Why do you want to work for [our company]? / Why are you leaving your job?",
            "What are your goals for the future?",
            "What are your strengths / weaknesses?",
            "Do you have experience working with cross-functional teams?",
            "Tell me about a project you're proud of"
        ],
        "Customer Obsession": [
            "Tell me about a time you went above and beyond for a customer.",
            "How do you prioritize customer needs in your work?"
        ],
        "Ownership": [
            "Describe a time when you took on a task beyond your responsibilities.",
            "Tell me about a time you made a mistake at work. How did you handle it?",
            "Tell me about a time you received feedback from your manager and what did you do?"
        ],
        "Invent and Simplify": [
            "Describe a time you created a simple solution to a complex problem.",
            "Tell me about a process you improved. What was your approach?"
        ],
        "Are Right, A Lot": [
            "Tell me about a decision you made that was wrong. What did you learn?",
            "Describe a time when you had to make a difficult judgment call."
        ],
        "Learn and Be Curious": [
            "Tell me about a time you picked up a new skill to solve a problem.",
            "What's the most recent thing you learned on your own?"
        ],
        "Think Big": [
            "Tell me about a time you proposed a bold idea. What happened?",
            "Describe a situation where you took a long-term view to solve a problem."
        ],
        "Bias for Action": [
            "Give me an example of a time when you made a decision quickly.",
            "Tell me about a time you took initiative to start a project."
        ],
        "Earn Trust": [
            "Tell me about a time you had a conflict with a colleague. How did you handle it?",
            "Describe how you build relationships in a team."
        ],
        "Dive Deep": [
            "Tell me about a technical problem you had to dig into to understand.",
            "How do you identify root causes when something goes wrong?"
        ],
        "Have Backbone; Disagree and Commit": [
            "Tell me about a time you strongly disagreed with your manager or team.",
            "Describe a situation where you advocated for a different approach."
        ],
        "Deliver Results": [
            "Tell me about a time you had to deliver a project under a tight deadline.",
            "Describe how you stay focused and productive."
        ]
    }

    return render_template('behavioral_guide.html', questions=behavioral_questions)

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint"""
    return jsonify({'status': 'API working', 'message': 'Test successful'})

@app.route('/debug/auth')
def debug_auth():
    """Debug authentication state"""
    user = get_current_user()
    return jsonify({
        'authenticated': user is not None,
        'user_data': user,
        'has_premium': has_premium_access(user),
        'has_ai_access': has_ai_access(user),
        'has_system_design_access': has_system_design_access(user),
        'is_allowed': is_allowed_user(user),
        'session_data': dict(session)
    })

@app.route('/auth/status')
def auth_status():
    """Show authentication status page"""
    return render_template('auth_status.html')

@app.route('/api/behavioral-feedback', methods=['POST'])
@ai_access_required
def behavioral_feedback():
    """API endpoint to get behavioral story feedback using OpenAI - AI Access Required"""
    try:
        print("Received behavioral feedback request")  # Debug log
        data = request.get_json()
        print(f"Request data: {data}")  # Debug log

        question = data.get('question', '')
        story = data.get('story', '')

        print(f"Question: {question[:50]}...")  # Debug log
        print(f"Story length: {len(story)}")  # Debug log

        if not question or not story:
            print("Missing question or story")  # Debug log
            return jsonify({'error': 'Question and story are required'}), 400

        # System prompt for behavioral interview feedback
        system_prompt = """You are an expert behavioral interview coach specializing in Amazon's Leadership Principles. Your role is to evaluate behavioral stories and provide constructive feedback.

CRITICAL RULES:
1. The candidate should NEVER use "we" in their stories - they must use "I" to show personal ownership and impact
2. Stories should follow the STAR method (Situation, Task, Action, Result)
3. Focus on specific, measurable results and personal contributions
4. Look for leadership principles demonstration

Provide feedback in this format:
- Score: X/10
- Strengths: (2-3 key strengths)
- Areas for Improvement: (2-3 specific suggestions)
- Leadership Principles Demonstrated: (which Amazon LP this shows)
- Suggested Improvements: (specific suggestions to make the story stronger)

Be constructive but direct. Focus on making the story more compelling and interview-ready."""

        user_prompt = f"""Question: {question}

Candidate's Story: {story}

Please evaluate this behavioral story and provide detailed feedback."""

        # Call OpenAI API
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        feedback = response.choices[0].message.content

        return jsonify({
            'feedback': feedback,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': f'Failed to get feedback: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook handler for subscription events.
    Auto-provisions users in Clerk when payments complete.
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    print(f"📬 Received Stripe webhook")

    # Verify webhook signature
    if not STRIPE_WEBHOOK_SECRET:
        print("⚠️ STRIPE_WEBHOOK_SECRET not configured")
        return jsonify({'error': 'Webhook secret not configured'}), 200

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"❌ Invalid webhook payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Invalid webhook signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Get event type
    event_type = event.get('type')
    print(f"📋 Processing event type: {event_type}")

    # Handle supported events
    supported_events = [
        'checkout.session.completed',
        'invoice.payment_succeeded',
        'customer.subscription.updated',
        'customer.subscription.deleted'
    ]

    if event_type not in supported_events:
        print(f"ℹ️ Ignoring event type: {event_type}")
        return jsonify({'status': 'ignored'}), 200

    # Extract customer email
    customer_email = extract_customer_email_from_stripe_event(event)
    if not customer_email:
        print(f"⚠️ Could not extract customer email")
        return jsonify({'status': 'error', 'reason': 'no email'}), 200

    print(f"👤 Customer email: {customer_email}")

    # Extract product ID
    product_id = extract_product_id_from_stripe_event(event)
    if not product_id:
        print(f"⚠️ Could not extract product ID")
        return jsonify({'status': 'error', 'reason': 'no product'}), 200

    print(f"📦 Product ID: {product_id}")

    # Note: Unknown products will use default premium access configuration

    # Handle subscription deletion (revoke access)
    if event_type == 'customer.subscription.deleted':
        print(f"🗑️ Subscription deleted for {customer_email}")
        user = get_clerk_user_by_email(customer_email)
        if user:
            revoked_metadata = {
                'has_premium': False,
                'has_ai_access': False,
                'has_system_design_access': False
            }
            update_clerk_user_metadata_by_id(user['id'], revoked_metadata)
            print(f"✅ Revoked access for {customer_email}")
        return jsonify({'status': 'success', 'action': 'revoked'}), 200

    # Provision user
    try:
        success = provision_user_from_stripe(customer_email, product_id)

        if success:
            # Get product description, with fallback for unknown products
            product_metadata = STRIPE_PRODUCT_METADATA.get(product_id, {
                'description': 'Default Premium (Unknown Product)'
            })
            product_desc = product_metadata.get('description', product_id)
            print(f"✅ Successfully provisioned {customer_email} with {product_desc}")
            return jsonify({
                'status': 'success',
                'email': customer_email,
                'product': product_desc
            }), 200
        else:
            print(f"❌ Failed to provision {customer_email}")
            return jsonify({'status': 'error', 'reason': 'provision failed'}), 200

    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'reason': str(e)}), 200

def estimate_difficulty_and_topics(problem_name):
    """Estimate difficulty and topics based on problem name"""
    name_lower = problem_name.lower()
    
    # Difficulty estimation based on common patterns
    difficulty = 'Medium'
    if any(keyword in name_lower for keyword in ['two sum', 'valid', 'merge', 'reverse', 'palindrome', 'anagram', 'binary search']):
        difficulty = 'Easy'
    elif any(keyword in name_lower for keyword in ['median', 'serialize', 'sliding window', 'minimum window', 'trapping', 'word ladder']):
        difficulty = 'Hard'
    
    # Topic estimation based on problem name patterns
    topics = []
    if any(keyword in name_lower for keyword in ['array', 'sum', 'product', 'subarray', 'rotate']):
        topics.append('Array')
    if any(keyword in name_lower for keyword in ['string', 'palindrome', 'anagram', 'word', 'character']):
        topics.append('String')
    if any(keyword in name_lower for keyword in ['tree', 'binary tree', 'bst', 'node']):
        topics.append('Binary Tree')
    if any(keyword in name_lower for keyword in ['linked list', 'list cycle', 'merge']):
        topics.append('Linked List')
    if any(keyword in name_lower for keyword in ['graph', 'dfs', 'bfs', 'island', 'clone']):
        topics.append('Graph')
    if any(keyword in name_lower for keyword in ['dynamic programming', 'dp', 'coin', 'climb', 'house robber']):
        topics.append('Dynamic Programming')
    if any(keyword in name_lower for keyword in ['binary search', 'search', 'find']):
        topics.append('Binary Search')
    if any(keyword in name_lower for keyword in ['stack', 'queue', 'parentheses', 'calculator']):
        topics.append('Stack')
    if any(keyword in name_lower for keyword in ['heap', 'priority', 'kth', 'median']):
        topics.append('Heap')
    if any(keyword in name_lower for keyword in ['hash', 'map', 'set']):
        topics.append('Hash Table')
    if any(keyword in name_lower for keyword in ['sort', 'merge']):
        topics.append('Sorting')
    if any(keyword in name_lower for keyword in ['matrix', 'grid', '2d']):
        topics.append('Matrix')
    if any(keyword in name_lower for keyword in ['backtrack', 'permutation', 'combination']):
        topics.append('Backtracking')
    if any(keyword in name_lower for keyword in ['trie', 'prefix']):
        topics.append('Trie')
    if any(keyword in name_lower for keyword in ['bit', 'xor', 'and', 'or']):
        topics.append('Bit Manipulation')
    
    # Default topics if none detected
    if not topics:
        topics = ['Algorithm']
    
    # Time estimation based on difficulty
    time_estimates = {'Easy': 20, 'Medium': 30, 'Hard': 45}
    time = time_estimates.get(difficulty, 30)
    
    return difficulty, topics, time

@app.route('/complete-list')
@premium_required
def complete_list():
    """Complete question list with customizable time sliders"""
    all_questions = []
    seen_urls = set()  # To avoid duplicates
    
    # Add questions from regular roadmap
    for month_name, month_data in web_app.roadmap_data.items():
        for day_data in month_data:
            for problem in day_data.get('problems', []):
                url = problem.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    problem_name = problem.get('name', 'Unknown Problem')
                    difficulty, topics, time = estimate_difficulty_and_topics(problem_name)
                    
                    all_questions.append({
                        'id': len(all_questions) + 1,
                        'title': problem_name,
                        'url': url,
                        'difficulty': difficulty,
                        'time': time,
                        'topics': topics,
                        'source': f'advanced-{month_name}'
                    })
    
    # Add questions from intermediate roadmap
    for month_name, month_data in web_app.intermediate_roadmap_data.items():
        for day_data in month_data:
            for problem in day_data.get('problems', []):
                url = problem.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    problem_name = problem.get('name', 'Unknown Problem')
                    difficulty, topics, time = estimate_difficulty_and_topics(problem_name)
                    
                    all_questions.append({
                        'id': len(all_questions) + 1,
                        'title': problem_name,
                        'url': url,
                        'difficulty': difficulty,
                        'time': time,
                        'topics': topics,
                        'source': f'intermediate-{month_name}'
                    })
    
    # Add questions from AtCoder beginner problems
    for problem in web_app.atcoder_problems.get('problems', []):
        url = problem.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            problem_name = problem.get('title', 'Unknown Problem')
            
            # AtCoder problems are generally easier
            all_questions.append({
                'id': len(all_questions) + 1,
                'title': problem_name,
                'url': url,
                'difficulty': 'Easy',
                'time': 15,
                'topics': ['Algorithm', 'Implementation'],
                'source': 'atcoder-beginner'
            })
    
    # Add some additional popular LeetCode problems to reach a comprehensive set
    additional_problems = [
        {'title': 'Two Sum', 'url': 'https://leetcode.com/problems/two-sum/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Hash Table']},
        {'title': 'Add Two Numbers', 'url': 'https://leetcode.com/problems/add-two-numbers/', 'difficulty': 'Medium', 'time': 25, 'topics': ['Linked List', 'Math']},
        {'title': 'Longest Substring Without Repeating Characters', 'url': 'https://leetcode.com/problems/longest-substring-without-repeating-characters/', 'difficulty': 'Medium', 'time': 30, 'topics': ['String', 'Sliding Window']},
        {'title': 'Median of Two Sorted Arrays', 'url': 'https://leetcode.com/problems/median-of-two-sorted-arrays/', 'difficulty': 'Hard', 'time': 45, 'topics': ['Array', 'Binary Search']},
        {'title': 'Valid Parentheses', 'url': 'https://leetcode.com/problems/valid-parentheses/', 'difficulty': 'Easy', 'time': 20, 'topics': ['String', 'Stack']},
        {'title': 'Merge Two Sorted Lists', 'url': 'https://leetcode.com/problems/merge-two-sorted-lists/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Linked List', 'Recursion']},
        {'title': 'Remove Duplicates from Sorted Array', 'url': 'https://leetcode.com/problems/remove-duplicates-from-sorted-array/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Two Pointers']},
        {'title': 'Best Time to Buy and Sell Stock', 'url': 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Array', 'Dynamic Programming']},
        {'title': 'Valid Palindrome', 'url': 'https://leetcode.com/problems/valid-palindrome/', 'difficulty': 'Easy', 'time': 15, 'topics': ['String', 'Two Pointers']},
        {'title': 'Invert Binary Tree', 'url': 'https://leetcode.com/problems/invert-binary-tree/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Binary Tree', 'DFS']},
        {'title': 'Maximum Subarray', 'url': 'https://leetcode.com/problems/maximum-subarray/', 'difficulty': 'Medium', 'time': 20, 'topics': ['Array', 'Dynamic Programming']},
        {'title': 'Climbing Stairs', 'url': 'https://leetcode.com/problems/climbing-stairs/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Math', 'Dynamic Programming']},
        {'title': 'Binary Search', 'url': 'https://leetcode.com/problems/binary-search/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Binary Search']},
        {'title': 'Flood Fill', 'url': 'https://leetcode.com/problems/flood-fill/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Array', 'DFS', 'BFS']},
        {'title': 'Number of Islands', 'url': 'https://leetcode.com/problems/number-of-islands/', 'difficulty': 'Medium', 'time': 25, 'topics': ['Array', 'DFS', 'BFS']},
    ]
    
    # Add additional problems if they're not already included
    for problem in additional_problems:
        if problem['url'] not in seen_urls:
            seen_urls.add(problem['url'])
            all_questions.append({
                'id': len(all_questions) + 1,
                'title': problem['title'],
                'url': problem['url'],
                'difficulty': problem['difficulty'],
                'time': problem['time'],
                'topics': problem['topics'],
                'source': 'popular'
            })
    
    return render_template('complete_list.html', questions_data=all_questions)

@app.route('/privacy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy_policy.html')

@app.route('/terms')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms_of_service.html')

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment variable for Heroku, or use 5000 for local dev
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Starting server on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
