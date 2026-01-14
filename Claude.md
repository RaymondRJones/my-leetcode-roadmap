# Claude.md - LeetCode Roadmap Generator

> **IMPORTANT: Keep this file in sync with the codebase. After making significant changes to the project, update this file and push to GitHub.**
>
> ```bash
> git add Claude.md && git commit -m "Update Claude.md" && git push
> ```

## Project Overview

A web-based platform for learning programming through curated problem roadmaps and AI-powered tutoring. Designed to help users prepare for tech interviews at major companies with multiple learning paths:

- **Advanced Roadmap**: LeetCode problems organized by month and day
- **Intermediate Roadmap (Fortune500)**: Mid-tier company interview prep
- **Beginner Training**: AtCoder problems with AI-simplified explanations
- **System Design**: Architecture and design patterns
- **Assessments**: Python and Java skill evaluations
- **Guides**: Career resources including behavioral interviews

Implements a **tiered freemium model** with Clerk authentication and Stripe payments.

---

## Tech Stack

### Backend
- **Flask 3.0.0** - Web framework
- **Python 3.11+** - Runtime (tested on 3.13)
- **Gunicorn 21.2.0** - Production WSGI server
- **Stripe 8.0.0** - Payment processing
- **PyJWT 2.8.0** - Token handling

### Frontend
- **Bootstrap 5.1.3** - UI framework
- **Clerk.js 5.96.0** - Authentication widget
- **Material Design / Nord Theme** - Styling
- **Vite 7.1.7** - Frontend build tool

### Data Processing
- **pdfplumber 0.10.2** - PDF text extraction
- **pandas 2.2.0** - Data processing
- **BeautifulSoup4 4.12.2** - Web scraping
- **OpenAI 1.3.0** - ChatGPT integration

### Testing
- **pytest 8.0.0** - Test framework
- **pytest-cov** - Coverage reporting

---

## Architecture

The application uses a **modular architecture** with the following design patterns:

### Design Patterns

1. **Application Factory Pattern** - `create_app()` function for testability and configuration flexibility
2. **Blueprint Pattern** - Routes organized into logical blueprints (auth, main, api, system_design)
3. **Service Layer Pattern** - External API calls abstracted into service classes
4. **Repository Pattern** - `RoadmapService` acts as data repository for roadmap access

### Directory Structure

```
leetcode-roadmap-generator/
├── app/                                # Main application package
│   ├── __init__.py                     # App factory (create_app)
│   ├── config.py                       # Configuration classes
│   │
│   ├── auth/                           # Authentication module
│   │   ├── __init__.py
│   │   ├── access.py                   # Access checking functions
│   │   └── decorators.py               # Auth decorators
│   │
│   ├── models/                         # Data models
│   │   ├── __init__.py
│   │   └── course.py                   # Course dataclass & COURSES list
│   │
│   ├── routes/                         # Route blueprints
│   │   ├── __init__.py                 # Blueprint registration
│   │   ├── auth.py                     # Auth routes (/auth/*)
│   │   ├── main.py                     # Main routes (/, /beginner, etc.)
│   │   ├── api.py                      # API routes (/api/*)
│   │   ├── system_design.py            # System design routes
│   │   └── challenge.py                # 28-day challenge routes
│   │
│   ├── services/                       # Service layer
│   │   ├── __init__.py
│   │   ├── clerk_service.py            # Clerk API operations
│   │   ├── stripe_service.py           # Stripe operations
│   │   ├── openai_service.py           # OpenAI operations
│   │   ├── roadmap_service.py          # Roadmap data operations
│   │   └── challenge_service.py        # 28-day challenge logic
│   │
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       └── problem_utils.py            # URL generation, difficulty estimation
│
├── tests/                              # Test suite (178 tests)
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_access.py                  # Auth access tests
│   ├── test_routes.py                  # Route tests
│   ├── test_routes_authenticated.py    # Authenticated route tests
│   ├── test_services.py                # Service tests
│   ├── test_roadmap_service.py         # RoadmapService tests
│   ├── test_edge_cases.py              # Edge case tests
│   └── test_utils.py                   # Utility function tests
│
├── app.py                              # Entry point (minimal, ~23 lines)
├── pdf_analyzer.py                     # PDF parsing and roadmap generation
├── requirements.txt                    # Python dependencies
├── Procfile                            # Heroku deployment config
├── runtime.txt                         # Python version
├── run.sh                              # Startup script
├── .env.example                        # Environment template
│
├── scripts/
│   ├── atcoder_scraper.py              # AtCoder scraper + ChatGPT
│   └── run_scraper.sh                  # Scraper execution script
│
├── templates/                          # Jinja2 HTML templates
│   ├── base.html                       # Master template
│   ├── classroom.html                  # Homepage (9 course cards)
│   ├── index.html                      # Advanced roadmap
│   ├── intermediate.html               # Fortune500 roadmap
│   ├── beginner.html                   # AtCoder problems
│   ├── month.html                      # Individual month view
│   ├── complete_list.html              # Ray700 problem list
│   ├── behavioral_guide.html           # Behavioral prep + AI feedback
│   ├── system_design/                  # System design templates
│   ├── auth/                           # Auth templates
│   └── challenge/                      # 28-day challenge templates
│       ├── index.html                  # Challenge landing/enrollment
│       ├── day.html                    # Day view with Pyodide editor
│       ├── calendar.html               # 28-day calendar
│       ├── leaderboard.html            # Rankings
│       └── admin/                      # Admin templates
│           ├── dashboard.html          # Participant management
│           └── submissions.html        # Skool submission review
│
├── static/
│   └── clerk/
│       └── auth.js                     # Clerk frontend logic
│
├── data files (JSON):
│   ├── roadmap_data.json               # Advanced roadmap data
│   ├── intermediate_roadmap_data.json  # Fortune500 data
│   ├── atcoder_beginner_problems.json  # AtCoder problems
│   └── challenge_problems.json         # 28-day challenge problems
│
└── intermediate_roadmap_pdfs/          # PDF input directory
```

---

## Environment Variables

Create a `.env` file with:

```bash
# Required
FLASK_SECRET_KEY=your-super-secret-key
CLERK_PUBLISHABLE_KEY=pk_test_...

# Recommended
FLASK_ENV=development
CLERK_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PORT=5000
```

---

## Running Locally

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your keys

# 4. Run application
python app.py
# Or use: ./run.sh

# 5. Access at http://localhost:5002
```

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_routes.py -v

# Run specific test class
python -m pytest tests/test_access.py::TestHasPremiumAccess -v
```

**Current Test Coverage: 75% (178 tests passing)**

| Module | Coverage |
|--------|----------|
| app/auth/access.py | 97% |
| app/routes/auth.py | 100% |
| app/routes/main.py | 97% |
| app/routes/system_design.py | 100% |
| app/models/course.py | 100% |
| app/utils/problem_utils.py | 100% |
| app/services/roadmap_service.py | 97% |

---

## Routes and Endpoints

### Public Routes (No Auth)
| Route | Description |
|-------|-------------|
| `GET /` | Classroom homepage |
| `GET /landing` | Sales page |
| `GET /beginner` | AtCoder problems |
| `GET /intermediate` | Month 1 Fortune500 (free) |
| `GET /python-assessment` | Python quiz |
| `GET /java-assessment` | Java quiz |
| `GET /roadmap` | Career journey guide |

### Authentication Routes
| Route | Description |
|-------|-------------|
| `GET /auth/login` | Login page |
| `POST /auth/callback` | Clerk callback |
| `GET /auth/logout` | Logout |
| `GET /auth/status` | Auth status page |
| `GET /auth/debug` | Debug endpoint (JSON) |

### Premium Routes (requires `has_premium`)
| Route | Description |
|-------|-------------|
| `GET /advanced` | Advanced LeetCode roadmap |
| `GET /advanced/month/<name>` | Specific month view |
| `GET /intermediate/month/<name>` | Month 2 & 3 |
| `GET /complete-list` | Ray700 (700+ problems) |
| `GET /guides` | Career guides |

### System Design Routes (requires `has_system_design_access`)
| Route | Description |
|-------|-------------|
| `GET /system-design/` | System design home |
| `GET /system-design/real-life-problems` | Real-world problems |
| `GET /system-design/trivia` | Knowledge checks |
| `GET /system-design/low-level-design` | LLD patterns |

### API Endpoints
| Route | Description |
|-------|-------------|
| `GET /api/roadmap` | Roadmap JSON data |
| `GET /api/atcoder` | AtCoder JSON data |
| `POST /api/refresh` | Re-analyze PDFs |
| `POST /api/webhooks/stripe` | Stripe webhook handler |
| `POST /api/behavioral-feedback` | AI feedback endpoint |

---

## Authentication System

### Flow
1. **Frontend**: Clerk.js handles sign-in/sign-up
2. **Callback**: `POST /auth/callback` receives user data, stores in Flask session
3. **Protection**: Backend decorators validate access on each request

### Decorators (app/auth/decorators.py)
```python
@login_required           # Any authenticated user
@premium_required         # has_premium flag required
@ai_access_required       # has_ai_access flag required
@system_design_access_required  # has_system_design_access flag required
```

### Access Functions (app/auth/access.py)
```python
get_current_user() -> Optional[dict]
has_premium_access(user_data) -> bool
has_ai_access(user_data) -> bool
has_system_design_access(user_data) -> bool
is_allowed_user(user_data) -> bool
```

### User Metadata (Clerk)
```json
{
  "private_metadata": {
    "has_premium": true,
    "has_ai_access": false,
    "has_system_design_access": true
  },
  "public_metadata": {
    "has_premium": true,
    "specialAccess": false
  }
}
```

### Allowlist
Configured in `app/config.py` as `ALLOWED_EMAILS` list.

---

## Service Layer

### ClerkService (app/services/clerk_service.py)
```python
class ClerkService:
    def get_user_by_email(email: str) -> Optional[dict]
    def create_user(email: str, metadata: dict) -> Optional[dict]
    def update_user_metadata(user_id: str, private: dict, public: dict) -> Optional[dict]
    def provision_user(email: str, product_metadata: dict) -> bool
    def revoke_user_access(email: str) -> bool
```

### StripeService (app/services/stripe_service.py)
```python
class StripeService:
    def verify_webhook(payload, signature) -> dict
    def extract_customer_email(event: dict) -> Optional[str]
    def extract_product_id(event: dict) -> Optional[str]
    def get_product_metadata(product_id: str) -> dict
    def is_supported_event(event_type: str) -> bool
```

### OpenAIService (app/services/openai_service.py)
```python
class OpenAIService:
    def get_behavioral_feedback(question: str, story: str) -> str
```

### RoadmapService (app/services/roadmap_service.py)
```python
class RoadmapService:
    def get_ordered_roadmap_data() -> dict
    def get_ordered_intermediate_roadmap_data() -> dict
    def get_atcoder_problems() -> dict
    def get_all_problems() -> list
    def refresh_data() -> None
    def get_original_month_name(mapped_name: str) -> str
```

---

## Configuration (app/config.py)

### Configuration Classes
- `Config` - Base configuration
- `DevelopmentConfig` - Development settings (DEBUG=True)
- `ProductionConfig` - Production settings
- `TestingConfig` - Test settings (TESTING=True)

### Key Configuration Values
```python
MONTH_ORDER = ['April', 'May', 'June', 'July', 'August']
MONTH_MAPPING = {'April': 'Month 1', 'May': 'Month 2', ...}
INTERMEDIATE_MONTH_ORDER = ['Month 1', 'Month 2', 'Month 3']

STRIPE_PRODUCT_METADATA = {
    'prod_SvD9M0caNlgkfo': {'has_premium': True},
    'prod_SzSqbijjdXdg2a': {'has_premium': True, 'has_system_design_access': True},
    ...
}
```

---

## Stripe Integration

### Product IDs
| Product ID | Access Level |
|------------|--------------|
| `prod_SvD9M0caNlgkfo` | Premium Only |
| `prod_SzSqbijjdXdg2a` | Premium + System Design |
| `prod_SxymCQ9tLRKY3u` | Premium + System Design (Alt) |

### Webhook Events Handled
- `checkout.session.completed` - New purchase
- `invoice.payment_succeeded` - Recurring payment
- `customer.subscription.updated` - Subscription change
- `customer.subscription.deleted` - Cancellation

---

## Data Models

### Course Model (app/models/course.py)
```python
@dataclass
class Course:
    title: str
    description: str
    route: str
    icon: str
    label: str
    is_premium: bool
    course_type: str
    duration: str
    problem_count: str
    level: str
    order: int
```

### Roadmap Data Structure (JSON)
```json
{
  "July": [
    {
      "day": 1,
      "problems": [
        {
          "name": "Problem Name",
          "status": "Accepted",
          "solved": true,
          "url": "https://leetcode.com/problems/problem-slug/"
        }
      ]
    }
  ]
}
```

### AtCoder Problem Structure (JSON)
```json
{
  "metadata": { "total_problems": 50 },
  "problems": [
    {
      "url": "https://atcoder.jp/...",
      "contest": "ABC 415",
      "title": "Problem Title",
      "problem_statement": "...",
      "difficulty": "Beginner",
      "tags": ["Basic Implementation"],
      "simplified": {
        "simplified_explanation": "...",
        "key_concepts": ["if-statements", "loops"]
      }
    }
  ]
}
```

---

## Key Patterns

### Month Mapping
- April → Month 1
- May → Month 2
- June → Month 3
- July → Month 4
- August → Month 5

### Problem URL Generation (app/utils/problem_utils.py)
```
"Two Sum" → https://leetcode.com/problems/two-sum/
```
Algorithm: lowercase → remove special chars → replace spaces with hyphens

### Daily Distribution
- Max 3 problems per day (days 1-29)
- Day 30 converted entirely to bonus section
- Overflow problems go to bonus

### Context Processor
Injects into all templates:
- `current_user`
- `is_authenticated`
- `has_premium`
- `has_ai_access`
- `has_system_design_access`
- `is_allowed`
- `clerk_publishable_key`

---

## Deployment (Heroku)

```bash
# Deploy
git push heroku main

# Set environment variables
heroku config:set FLASK_SECRET_KEY=...
heroku config:set CLERK_SECRET_KEY=...
heroku config:set STRIPE_SECRET_KEY=...
```

Procfile: `web: gunicorn app:app`

---

## 28-Day Challenge Feature

A gamified 28-day LeetCode challenge with built-in Python code editor, progress tracking, achievements, and leaderboard.

### Challenge Routes
| Route | Description |
|-------|-------------|
| `GET /challenge` | Challenge landing/enrollment page |
| `GET /challenge/day/<day>` | Day view with code editor (Pyodide) |
| `GET /challenge/calendar` | 28-day calendar showing progress |
| `GET /challenge/leaderboard` | Points-based leaderboard |
| `GET /challenge/admin` | Admin dashboard (requires `is_admin`) |
| `GET /challenge/admin/submissions` | Review Skool submissions |

### Challenge API Endpoints
| Route | Description |
|-------|-------------|
| `POST /api/challenge/enroll` | Enroll user in challenge |
| `POST /api/challenge/complete-problem` | Mark problem as completed |
| `GET /api/challenge/progress` | Get user's challenge progress |
| `POST /api/challenge/submit-skool` | Submit Skool post for review |
| `GET /api/challenge/leaderboard` | Get leaderboard data |
| `GET /api/challenge/admin/participants` | All participants (admin) |
| `POST /api/challenge/admin/approve-submission` | Approve/reject submission |

### Challenge Metadata (Clerk public_metadata)
```json
{
  "challenge": {
    "enrolled": true,
    "start_date": "2025-01-15T00:00:00",
    "days_completed": [1, 2, 3],
    "problems_solved": {"day_1": ["two-sum"], "day_2": ["valid-parentheses"]},
    "total_problems_solved": 2,
    "current_streak": 3,
    "best_streak": 3,
    "points": 50,
    "achievements": ["first_problem"],
    "last_activity_date": "2025-01-17T00:00:00"
  },
  "skool_submissions": [
    {"day": 1, "url": "https://skool.com/...", "status": "pending"}
  ]
}
```

### Points System
| Action | Points |
|--------|--------|
| Easy problem | 10 |
| Medium problem | 20 |
| Hard problem | 40 |
| 7-day streak bonus | +50 |
| 14-day streak bonus | +100 |
| 28-day completion bonus | +250 |
| Approved Skool post | +30 |

### Achievements
| ID | Name | Trigger |
|----|------|---------|
| `first_problem` | First Steps | Complete 1 problem |
| `streak_7` | Week Warrior | 7-day streak |
| `streak_14` | Fortnight Focus | 14-day streak |
| `streak_28` | Challenge Champion | Complete all 28 days |
| `hard_problem` | Hard Mode | Solve a hard problem |
| `community_star` | Community Star | 3 approved Skool posts |

### Challenge Service (app/services/challenge_service.py)
```python
class ChallengeService:
    def get_day_problems(day: int) -> List[Dict]
    def get_problem(day: int, problem_id: str) -> Optional[Dict]
    def calculate_current_day(start_date: str) -> int
    def calculate_streak(days_completed: List[int], current_day: int) -> int
    def calculate_points(challenge_data: Dict) -> int
    def check_achievements(challenge_data: Dict) -> List[str]
    def get_achievements_config() -> Dict
```

### Admin Access
- Uses `is_admin()` function in `app/auth/access.py`
- Checks `is_admin` flag in Clerk metadata
- Falls back to `is_allowed_user()` (config allowlist)
- `@admin_required` decorator in `app/auth/decorators.py`

### Code Execution (Pyodide)
- Python runs in browser via WebAssembly
- No server-side execution needed
- Loaded from CDN: `https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js`
- Test cases defined in `challenge_problems.json`

---

## Important Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `app/__init__.py` | App factory | ~120 |
| `app/config.py` | Configuration | ~100 |
| `app/routes/main.py` | Main routes | ~200 |
| `app/routes/api.py` | API routes | ~300 |
| `app/routes/challenge.py` | Challenge routes | ~140 |
| `app/services/roadmap_service.py` | Data service | ~180 |
| `app/services/challenge_service.py` | Challenge logic | ~200 |
| `app/auth/access.py` | Access checking | ~100 |
| `app/auth/decorators.py` | Auth decorators | ~90 |
| `app.py` | Entry point | ~23 |
| `pdf_analyzer.py` | PDF parsing | ~263 |
| `templates/base.html` | Master template | ~350 |
| `templates/challenge/day.html` | Code editor page | ~250 |
| `static/clerk/auth.js` | Frontend auth | ~150 |
| `challenge_problems.json` | Challenge data | ~200 |

---

## Test Fixtures (tests/conftest.py)

| Fixture | Description |
|---------|-------------|
| `app` | Flask app instance |
| `client` | Unauthenticated test client |
| `authenticated_client` | Premium user client |
| `non_premium_client` | Free user client |
| `allowed_user_client` | Admin/allowed user client |
| `full_access_client` | All access flags enabled |
| `mock_user_data` | Premium user data dict |
| `mock_non_premium_user_data` | Free user data dict |

---

## Keeping This File Updated

**When to update Claude.md:**
1. Adding new routes or endpoints
2. Changing authentication logic
3. Adding new environment variables
4. Modifying data structures
5. Adding new features or templates
6. Changing deployment configuration
7. Adding new services or modules
8. Updating test coverage

**Sync commands:**
```bash
# After making changes
git add Claude.md
git commit -m "Update Claude.md with [description of changes]"
git push origin $(git branch --show-current)
```

**Automated reminder:** Before merging any PR, ensure Claude.md reflects the changes.

---

*Last updated: January 2026*
