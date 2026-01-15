"""
Email service using Resend for transactional emails.
"""
import os
import resend
from flask import current_app


class EmailService:
    """Service for sending emails via Resend."""

    @classmethod
    def _get_api_key(cls):
        """Get API key from app config or environment."""
        try:
            return current_app.config.get('RESEND_API_KEY') or os.environ.get('RESEND_API_KEY')
        except RuntimeError:
            # Outside of app context
            return os.environ.get('RESEND_API_KEY')

    @classmethod
    def _get_from_email(cls):
        """Get FROM email from app config or environment."""
        try:
            return current_app.config.get('RESEND_FROM_EMAIL') or os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
        except RuntimeError:
            # Outside of app context
            return os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')

    @classmethod
    def send_email(cls, to: str, subject: str, html: str, from_email: str = None) -> dict:
        """
        Send an email using Resend.

        Args:
            to: Recipient email address
            subject: Email subject line
            html: HTML content of the email
            from_email: Sender email (defaults to DEFAULT_FROM)

        Returns:
            dict with 'success' boolean and 'id' or 'error'
        """
        api_key = cls._get_api_key()
        if not api_key:
            return {'success': False, 'error': 'RESEND_API_KEY not configured'}

        resend.api_key = api_key

        try:
            result = resend.Emails.send({
                "from": from_email or cls._get_from_email(),
                "to": to,
                "subject": subject,
                "html": html
            })
            return {'success': True, 'id': result.get('id')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @classmethod
    def send_welcome_email(cls, to: str, name: str = None) -> dict:
        """
        Send a welcome email to a new user.

        Args:
            to: Recipient email address
            name: User's name (optional)

        Returns:
            dict with 'success' boolean and 'id' or 'error'
        """
        greeting = f"Hi {name}," if name else "Hi there,"

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #5E81AC;">Welcome to Ray's LeetCode Roadmap!</h1>

            <p>{greeting}</p>

            <p>Thank you for joining our platform! You now have access to:</p>

            <ul>
                <li><strong>Beginner Training</strong> - AtCoder problems with simplified explanations</li>
                <li><strong>28-Day Challenge</strong> - Gamified coding practice with achievements</li>
                <li><strong>Python & Java Assessments</strong> - Test your skills</li>
            </ul>

            <p>Ready to start your coding journey?</p>

            <p>
                <a href="https://your-domain.com/beginner"
                   style="background-color: #5E81AC; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Start Learning
                </a>
            </p>

            <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">

            <p style="color: #666; font-size: 14px;">
                Questions? Reply to this email or visit our coaching page for personalized help.
            </p>

            <p style="color: #888; font-size: 12px;">
                - Raymond Jones<br>
                Ray's LeetCode Roadmap
            </p>
        </div>
        """

        return cls.send_email(
            to=to,
            subject="Welcome to Ray's LeetCode Roadmap!",
            html=html
        )

    @classmethod
    def send_challenge_enrolled_email(cls, to: str, name: str = None) -> dict:
        """
        Send confirmation email when user enrolls in 28-day challenge.

        Args:
            to: Recipient email address
            name: User's name (optional)

        Returns:
            dict with 'success' boolean and 'id' or 'error'
        """
        greeting = f"Hi {name}," if name else "Hi there,"

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #5E81AC;">You're In! 28-Day Challenge</h1>

            <p>{greeting}</p>

            <p>You've successfully enrolled in the <strong>28-Day LeetCode Challenge</strong>!</p>

            <h3>What to expect:</h3>
            <ul>
                <li>1 problem per day for 28 days</li>
                <li>Built-in Python code editor</li>
                <li>Points and achievements to earn</li>
                <li>Leaderboard to track your progress</li>
            </ul>

            <h3>Tips for success:</h3>
            <ul>
                <li>Try to solve problems daily to build your streak</li>
                <li>Don't worry if you get stuck - the goal is learning</li>
                <li>Share your progress in the Skool community for bonus points</li>
            </ul>

            <p>
                <a href="https://your-domain.com/challenge/day/1"
                   style="background-color: #A3BE8C; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Start Day 1
                </a>
            </p>

            <p style="color: #888; font-size: 12px;">
                Good luck!<br>
                - Raymond Jones
            </p>
        </div>
        """

        return cls.send_email(
            to=to,
            subject="You're enrolled in the 28-Day Challenge!",
            html=html
        )

    @classmethod
    def send_purchase_confirmation_email(cls, to: str, product_name: str = None) -> dict:
        """
        Send purchase confirmation email after successful Stripe payment.

        Args:
            to: Recipient email address
            product_name: Name of the purchased product (optional)

        Returns:
            dict with 'success' boolean and 'id' or 'error'
        """
        product_info = f" ({product_name})" if product_name else ""

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #5E81AC; margin-bottom: 24px;">
                Welcome to Your Software Engineering Journey! 🎉
            </h1>

            <p style="font-size: 16px; line-height: 1.6; color: #2E3440;">
                Thank you for your purchase{product_info}! Your payment has been successfully processed,
                and your digital products are now available.
            </p>

            <div style="background-color: #ECEFF4; border-radius: 8px; padding: 24px; margin: 24px 0;">
                <h2 style="color: #5E81AC; margin-top: 0; font-size: 18px;">
                    📁 Access Your Products Immediately
                </h2>
                <p style="color: #4C566A; margin-bottom: 16px;">
                    Click the button below to access your digital products.
                    <strong>Create an account using the same email you used for purchase.</strong>
                </p>
                <a href="https://leet-roadmap-2b0ad46df54e.herokuapp.com/"
                   style="background-color: #5E81AC; color: white; padding: 14px 28px;
                          text-decoration: none; border-radius: 6px; display: inline-block;
                          font-weight: bold; font-size: 16px;">
                    👉 Access Your Digital Products
                </a>
            </div>

            <div style="background-color: #FFF8E1; border-left: 4px solid #FFC107; padding: 16px; margin: 24px 0;">
                <h3 style="color: #F57C00; margin-top: 0; font-size: 16px;">
                    🔒 Important: Secure Your Access
                </h3>
                <ul style="color: #5D4037; margin-bottom: 0; padding-left: 20px;">
                    <li style="margin-bottom: 8px;"><strong>Bookmark the site link</strong> - Save it to your browser favorites</li>
                    <li><strong>Save this email</strong> - Keep it in a dedicated folder for future reference</li>
                </ul>
            </div>

            <hr style="border: none; border-top: 1px solid #D8DEE9; margin: 32px 0;">

            <p style="color: #4C566A; font-size: 14px;">
                If you have any questions, just reply to this email. I'm here to help!
            </p>

            <p style="color: #2E3440; font-size: 16px;">
                Best,<br>
                <strong>Raymond</strong>
            </p>

            <p style="color: #8899A6; font-size: 12px; margin-top: 32px;">
                Ray's LeetCode Roadmap | Software Engineering Interview Prep
            </p>
        </div>
        """

        return cls.send_email(
            to=to,
            subject="Welcome to Your Software Engineering Journey! 🎉",
            html=html
        )


# Quick test function (run outside Flask context)
def test_send_email():
    """Test sending an email - run this directly to verify Resend is working."""
    from dotenv import load_dotenv
    load_dotenv()

    result = EmailService.send_email(
        to="raymond@raymondjones.dev",
        subject="Test Email from LeetCode Roadmap",
        html="<p>Congrats! Your <strong>Resend integration</strong> is working!</p>"
    )

    if result['success']:
        print(f"Email sent successfully! ID: {result['id']}")
    else:
        print(f"Failed to send email: {result['error']}")

    return result


if __name__ == "__main__":
    test_send_email()
