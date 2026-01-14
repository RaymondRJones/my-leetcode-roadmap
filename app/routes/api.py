"""
API routes blueprint.
"""
from flask import Blueprint, jsonify, request, current_app

from ..auth.decorators import ai_access_required

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
