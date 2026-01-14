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
- **Python 3.11** - Runtime
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

---

## Directory Structure

```
leetcode-roadmap-generator/
├── app.py                              # Main Flask application
├── pdf_analyzer.py                     # PDF parsing and roadmap generation
├── requirements.txt                    # Python dependencies
├── Procfile                            # Heroku deployment config
├── runtime.txt                         # Python version (3.11.0)
├── run.sh                              # Startup script
├── .env.example                        # Environment template
│
├── scripts/
│   ├── atcoder_scraper.py             # AtCoder scraper + ChatGPT
│   └── run_scraper.sh                 # Scraper execution script
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
│   └── auth/                           # Auth templates
│
├── static/
│   └── clerk/
│       └── auth.js                     # Clerk frontend logic
│
├── data files (JSON):
│   ├── roadmap_data.json               # Advanced roadmap data
│   ├── intermediate_roadmap_data.json  # Fortune500 data
│   └── atcoder_beginner_problems.json  # AtCoder problems
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
| `GET /auth/status` | Auth status |

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
| `GET /system-design` | System design home |
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

### Decorators
```python
@login_required           # Any authenticated user
@premium_required         # has_premium flag required
@ai_access_required       # has_ai_access flag required
@system_design_access_required  # has_system_design_access flag required
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

### Allowlist (Hardcoded)
- admin@example.com
- raymond@example.com

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

## Data Models (JSON-based)

### Roadmap Data Structure
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

### AtCoder Problem Structure
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

### Problem URL Generation
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

## Important Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Main Flask app | ~1,291 |
| `pdf_analyzer.py` | PDF parsing | ~263 |
| `templates/base.html` | Master template | ~350 |
| `static/clerk/auth.js` | Frontend auth | ~150 |

---

## Keeping This File Updated

**When to update Claude.md:**
1. Adding new routes or endpoints
2. Changing authentication logic
3. Adding new environment variables
4. Modifying data structures
5. Adding new features or templates
6. Changing deployment configuration

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
