"""
API routes blueprint.
"""
import re
from datetime import datetime
from urllib.parse import urlparse

from flask import Blueprint, jsonify, request, current_app

from ..auth.decorators import ai_access_required, login_required, admin_required
from ..auth.access import get_current_user


def extract_leetcode_slug(url):
    """
    Extract problem slug from various LeetCode URL formats.

    Handles:
    - https://leetcode.com/problems/two-sum/
    - https://leetcode.com/problems/two-sum/description/
    - https://leetcode.com/problems/two-sum/?envType=daily-question&envId=2026-01-09
    - https://leetcode.com/problems/two-sum/description/?envType=daily-question

    Returns the slug (e.g., 'two-sum') or None if not found.
    """
    parsed = urlparse(url)
    path = parsed.path

    # Match pattern: /problems/{slug}/ - capture just the slug part
    match = re.search(r'/problems/([^/?]+)', path)
    if match:
        return match.group(1)
    return None

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/roadmap')
def roadmap():
    """API endpoint to get roadmap data."""
    roadmap_service = current_app.roadmap
    return jsonify(roadmap_service.get_ordered_roadmap_data())


@api_bp.route('/atcoder')
def atcoder():
    """API endpoint to get AtCoder beginner problems."""
    roadmap_service = current_app.roadmap
    return jsonify(roadmap_service.get_atcoder_problems())


@api_bp.route('/refresh', methods=['POST'])
def refresh():
    """API endpoint to refresh roadmap data."""
    try:
        roadmap_service = current_app.roadmap
        roadmap_service.refresh_data()
        return jsonify({'status': 'success', 'message': 'Roadmap data refreshed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@api_bp.route('/test', methods=['GET'])
def test():
    """Simple test endpoint."""
    return jsonify({'status': 'API working', 'message': 'Test successful'})


@api_bp.route('/behavioral-feedback', methods=['POST'])
@ai_access_required
def behavioral_feedback():
    """API endpoint to get behavioral story feedback using OpenAI - AI Access Required."""
    try:
        print("Received behavioral feedback request")
        data = request.get_json()
        print(f"Request data: {data}")

        question = data.get('question', '')
        story = data.get('story', '')

        print(f"Question: {question[:50]}...")
        print(f"Story length: {len(story)}")

        if not question or not story:
            print("Missing question or story")
            return jsonify({'error': 'Question and story are required'}), 400

        # Get feedback from OpenAI service
        openai_service = current_app.openai
        feedback = openai_service.get_behavioral_feedback(question, story)

        return jsonify({
            'feedback': feedback,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': f'Failed to get feedback: {str(e)}',
            'status': 'error'
        }), 500


# =============================================================================
# Challenge API Endpoints
# =============================================================================

@api_bp.route('/challenge/enroll', methods=['POST'])
@login_required
def enroll_challenge():
    """Enroll the current user in the 28-day challenge."""
    user = get_current_user()
    user_id = user.get('id')

    # Initialize challenge data
    challenge_data = {
        'enrolled': True,
        'start_date': datetime.now().isoformat(),
        'days_completed': [],
        'problems_solved': {},
        'total_problems_solved': 0,
        'current_streak': 0,
        'best_streak': 0,
        'points': 0,
        'achievements': [],
        'last_activity_date': datetime.now().isoformat()
    }

    # Update Clerk metadata
    current_meta = user.get('public_metadata', {})
    current_meta['challenge'] = challenge_data

    clerk_service = current_app.clerk
    result = clerk_service.update_user_metadata(user_id, current_meta)

    if result:
        return jsonify({'status': 'success', 'challenge': challenge_data})
    return jsonify({'error': 'Failed to enroll'}), 500


@api_bp.route('/challenge/complete-problem', methods=['POST'])
@login_required
def complete_problem():
    """Mark a problem as completed."""
    data = request.get_json()
    day = data.get('day')
    problem_id = data.get('problem_id')

    if not day or not problem_id:
        return jsonify({'error': 'day and problem_id required'}), 400

    user = get_current_user()
    user_id = user.get('id')
    public_meta = user.get('public_metadata', {})
    challenge = public_meta.get('challenge', {})

    if not challenge.get('enrolled'):
        return jsonify({'error': 'Not enrolled in challenge'}), 400

    # Update problems_solved
    day_key = f'day_{day}'
    problems_solved = challenge.get('problems_solved', {})
    if day_key not in problems_solved:
        problems_solved[day_key] = []

    if problem_id not in problems_solved[day_key]:
        problems_solved[day_key].append(problem_id)
        challenge['problems_solved'] = problems_solved
        challenge['total_problems_solved'] = sum(len(p) for p in problems_solved.values())

        # Track activity in activity_log for heatmap
        today = datetime.now().date().isoformat()
        activity_log = challenge.get('activity_log', {})
        if today not in activity_log:
            activity_log[today] = {'count': 0, 'problems': []}
        activity_log[today]['count'] += 1
        activity_log[today]['problems'].append(problem_id)
        challenge['activity_log'] = activity_log

        # Check if day is complete
        service = current_app.challenge_service
        if service.is_day_complete(day, problems_solved):
            days_completed = challenge.get('days_completed', [])
            if day not in days_completed:
                days_completed.append(day)
                challenge['days_completed'] = days_completed

        # Update streak
        current_day = service.calculate_current_day(challenge.get('start_date', ''))
        challenge['current_streak'] = service.calculate_streak(
            challenge.get('days_completed', []), current_day
        )
        challenge['best_streak'] = max(
            challenge.get('best_streak', 0),
            challenge['current_streak']
        )

        # Calculate points
        challenge['points'] = service.calculate_points(challenge)

        # Check for new achievements
        new_achievements = service.check_achievements(challenge)
        if new_achievements:
            challenge['achievements'] = list(
                set(challenge.get('achievements', []) + new_achievements)
            )

        challenge['last_activity_date'] = datetime.now().isoformat()

        # Save to Clerk
        public_meta['challenge'] = challenge
        clerk_service = current_app.clerk
        clerk_service.update_user_metadata(user_id, public_meta)

        return jsonify({
            'status': 'success',
            'challenge': challenge,
            'new_achievements': new_achievements
        })

    return jsonify({'status': 'already_completed'})


@api_bp.route('/challenge/progress')
@login_required
def get_challenge_progress():
    """Get user's challenge progress."""
    user = get_current_user()
    challenge = user.get('public_metadata', {}).get('challenge', {})

    if not challenge.get('enrolled'):
        return jsonify({'enrolled': False})

    service = current_app.challenge_service
    current_day = service.calculate_current_day(challenge.get('start_date', ''))

    return jsonify({
        'enrolled': True,
        'current_day': current_day,
        'days_completed': challenge.get('days_completed', []),
        'problems_solved': challenge.get('problems_solved', {}),
        'total_problems_solved': challenge.get('total_problems_solved', 0),
        'current_streak': challenge.get('current_streak', 0),
        'best_streak': challenge.get('best_streak', 0),
        'points': challenge.get('points', 0),
        'achievements': challenge.get('achievements', [])
    })


@api_bp.route('/challenge/submit-skool', methods=['POST'])
@login_required
def submit_skool():
    """Submit a Skool post for admin review."""
    data = request.get_json()
    day = data.get('day')
    url = data.get('url')

    if not day or not url:
        return jsonify({'error': 'day and url required'}), 400

    if 'skool.com' not in url:
        return jsonify({'error': 'Invalid Skool URL'}), 400

    user = get_current_user()
    user_id = user.get('id')
    public_meta = user.get('public_metadata', {})

    submissions = public_meta.get('skool_submissions', [])
    submissions.append({
        'day': day,
        'url': url,
        'submitted_at': datetime.now().isoformat(),
        'status': 'pending'
    })

    public_meta['skool_submissions'] = submissions
    clerk_service = current_app.clerk
    clerk_service.update_user_metadata(user_id, public_meta)

    return jsonify({'status': 'success', 'message': 'Submission received'})


@api_bp.route('/challenge/bonus-problem', methods=['POST'])
@login_required
def submit_bonus_problem():
    """Submit a bonus LeetCode problem for extra points."""
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL required'}), 400

    if 'leetcode.com/problems/' not in url:
        return jsonify({'error': 'Invalid LeetCode problem URL'}), 400

    user = get_current_user()
    user_id = user.get('id')
    public_meta = user.get('public_metadata', {})
    challenge = public_meta.get('challenge', {})

    if not challenge.get('enrolled'):
        return jsonify({'error': 'Not enrolled in challenge'}), 400

    # Get existing bonus problems
    bonus_problems = challenge.get('bonus_problems', [])

    # Check if already added
    existing_urls = [p.get('url') for p in bonus_problems]
    # Normalize URL for comparison (remove trailing slash)
    normalized_url = url.rstrip('/')
    if any(existing.rstrip('/') == normalized_url for existing in existing_urls):
        return jsonify({'status': 'already_added'})

    # Extract problem slug from URL (handles /description/ and query params)
    problem_slug = extract_leetcode_slug(url)
    if not problem_slug:
        return jsonify({'error': 'Could not extract problem name from URL'}), 400
    problem_name = problem_slug.replace('-', ' ').title()

    # Add new bonus problem
    bonus_problems.append({
        'url': url,
        'name': problem_name,
        'added_at': datetime.now().isoformat()
    })

    challenge['bonus_problems'] = bonus_problems

    # Track activity in activity_log for heatmap
    today = datetime.now().date().isoformat()
    activity_log = challenge.get('activity_log', {})
    if today not in activity_log:
        activity_log[today] = {'count': 0, 'problems': []}
    activity_log[today]['count'] += 1
    activity_log[today]['problems'].append(f"bonus:{problem_slug}")
    challenge['activity_log'] = activity_log

    # Recalculate points (bonus problems are worth 5 points each)
    service = current_app.challenge_service
    challenge['points'] = service.calculate_points(challenge)

    # Save to Clerk
    public_meta['challenge'] = challenge
    clerk_service = current_app.clerk
    clerk_service.update_user_metadata(user_id, public_meta)

    return jsonify({
        'status': 'success',
        'bonus_problems': bonus_problems,
        'total_points': challenge['points']
    })


@api_bp.route('/challenge/leaderboard')
def get_challenge_leaderboard():
    """Get challenge leaderboard data."""
    # For now, return empty - would need Clerk API to list all users
    return jsonify({
        'leaderboard': [],
        'message': 'Leaderboard coming soon'
    })


@api_bp.route('/challenge/admin/participants')
@admin_required
def get_challenge_participants():
    """Get all challenge participants (admin only)."""
    # Would require Clerk API to list all users with challenge data
    return jsonify({
        'participants': [],
        'message': 'Admin participant list coming soon'
    })


@api_bp.route('/challenge/admin/approve-submission', methods=['POST'])
@admin_required
def approve_skool_submission():
    """Approve or reject a Skool submission (admin only)."""
    data = request.get_json()
    user_id = data.get('user_id')
    submission_index = data.get('submission_index')
    action = data.get('action')  # 'approve' or 'reject'

    if not user_id or submission_index is None or action not in ['approve', 'reject']:
        return jsonify({'error': 'user_id, submission_index, and action required'}), 400

    # Would need to fetch user by ID and update submission status
    # For now, return success placeholder
    return jsonify({
        'status': 'success',
        'message': f'Submission {action}d'
    })


@api_bp.route('/challenge/submit-skool-proof', methods=['POST'])
@login_required
def submit_skool_proof():
    """Submit Skool post URL for 28-day challenge refund verification."""
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL required'}), 400

    if 'skool.com' not in url:
        return jsonify({'error': 'Please provide a valid Skool URL'}), 400

    user = get_current_user()
    user_id = user.get('id')
    public_meta = user.get('public_metadata', {})
    challenge = public_meta.get('challenge', {})

    if not challenge.get('enrolled'):
        return jsonify({'error': 'Not enrolled in challenge'}), 400

    challenge['skool_proof_url'] = url
    challenge['skool_proof_submitted_at'] = datetime.now().isoformat()

    public_meta['challenge'] = challenge
    clerk_service = current_app.clerk
    clerk_service.update_user_metadata(user_id, public_meta)

    return jsonify({'status': 'success', 'message': 'Proof submitted successfully'})


# =============================================================================
# Stripe Webhook
# =============================================================================

@api_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook handler for subscription events.
    Auto-provisions users in Clerk when payments complete.
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    print("Received Stripe webhook")

    stripe_service = current_app.stripe
    clerk_service = current_app.clerk

    # Verify webhook signature
    if not stripe_service.is_webhook_configured():
        print("STRIPE_WEBHOOK_SECRET not configured")
        return jsonify({'error': 'Webhook secret not configured'}), 200

    event = stripe_service.verify_webhook(payload, sig_header)
    if not event:
        return jsonify({'error': 'Invalid payload or signature'}), 400

    # Get event type
    event_type = event.get('type')
    print(f"Processing event type: {event_type}")

    # Check if supported event
    if not stripe_service.is_supported_event(event_type):
        print(f"Ignoring event type: {event_type}")
        return jsonify({'status': 'ignored'}), 200

    # Extract customer email
    customer_email = stripe_service.extract_customer_email(event)
    if not customer_email:
        print("Could not extract customer email")
        return jsonify({'status': 'error', 'reason': 'no email'}), 200

    print(f"Customer email: {customer_email}")

    # Extract product ID
    product_id = stripe_service.extract_product_id(event)
    if not product_id:
        print("Could not extract product ID")
        return jsonify({'status': 'error', 'reason': 'no product'}), 200

    print(f"Product ID: {product_id}")

    # Handle subscription deletion (revoke access)
    if event_type == 'customer.subscription.deleted':
        print(f"Subscription deleted for {customer_email}")
        clerk_service.revoke_user_access(customer_email)
        return jsonify({'status': 'success', 'action': 'revoked'}), 200

    # Provision user
    try:
        product_metadata = stripe_service.get_product_metadata(product_id)
        success = clerk_service.provision_user(customer_email, product_metadata)

        if success:
            product_desc = stripe_service.get_product_description(product_id)
            print(f"Successfully provisioned {customer_email} with {product_desc}")

            # Send purchase confirmation email
            try:
                from ..services.email_service import EmailService
                email_result = EmailService.send_purchase_confirmation_email(
                    to=customer_email,
                    product_name=product_desc
                )
                if email_result['success']:
                    print(f"Purchase confirmation email sent to {customer_email}")
                else:
                    print(f"Failed to send email: {email_result.get('error')}")
            except Exception as email_error:
                print(f"Email sending error (non-fatal): {str(email_error)}")

            return jsonify({
                'status': 'success',
                'email': customer_email,
                'product': product_desc
            }), 200
        else:
            print(f"Failed to provision {customer_email}")
            return jsonify({'status': 'error', 'reason': 'provision failed'}), 200

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'reason': str(e)}), 200


# =============================================================================
# Daily Progress Trackers
# =============================================================================

@api_bp.route('/challenge/log-activity', methods=['POST'])
@login_required
def log_daily_activity():
    """Log daily progress tracker activity."""
    data = request.get_json()

    user = get_current_user()
    user_id = user.get('id')
    public_meta = user.get('public_metadata', {})
    challenge = public_meta.get('challenge', {})

    if not challenge.get('enrolled'):
        return jsonify({'error': 'Not enrolled in challenge'}), 400

    # Default tracker values
    default_trackers = {
        'new_problems': 0,
        'revised_problems': 0,
        'github_commits': 0,
        'skool_activity': 0,
        'comments_done': 0,
        'social_posts': 0,
        'mock_interviews': 0,
        'leetcode_rank': None
    }

    # Initialize trackers if needed
    trackers = challenge.get('trackers', default_trackers.copy())
    tracker_log = challenge.get('tracker_log', {})

    today = datetime.now().date().isoformat()

    # Get previous entry for today (if updating)
    previous_entry = tracker_log.get(today, {})

    # Cumulative tracker keys
    cumulative_keys = [
        'new_problems', 'revised_problems', 'github_commits',
        'skool_activity', 'comments_done', 'social_posts', 'mock_interviews'
    ]

    # Update cumulative totals (add delta from previous entry)
    for key in cumulative_keys:
        old_value = previous_entry.get(key, 0) or 0
        new_value = data.get(key, 0) or 0
        delta = new_value - old_value
        trackers[key] = (trackers.get(key, 0) or 0) + delta

    # LeetCode rank is just stored directly (not cumulative)
    if 'leetcode_rank' in data and data['leetcode_rank']:
        trackers['leetcode_rank'] = data['leetcode_rank']

    # Store today's log entry
    tracker_log[today] = {key: data.get(key, 0) for key in cumulative_keys}
    if data.get('leetcode_rank'):
        tracker_log[today]['leetcode_rank'] = data['leetcode_rank']

    # Save back to metadata
    challenge['trackers'] = trackers
    challenge['tracker_log'] = tracker_log

    # Update Clerk
    public_meta['challenge'] = challenge
    clerk_service = current_app.clerk
    clerk_service.update_user_metadata(user_id, public_meta)

    return jsonify({'status': 'success', 'trackers': trackers})
