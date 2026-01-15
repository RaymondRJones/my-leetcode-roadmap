"""
Email service using Resend for transactional emails.
"""
import os
import resend
from flask import current_app


class EmailService:
    """Service for sending emails via Resend."""

    # Default sender - update this when you have a verified domain
    DEFAULT_FROM = "onboarding@resend.dev"

    @classmethod
    def _get_api_key(cls):
        """Get API key from app config or environment."""
        try:
            return current_app.config.get('RESEND_API_KEY') or os.environ.get('RESEND_API_KEY')
        except RuntimeError:
            # Outside of app context
            return os.environ.get('RESEND_API_KEY')

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
                "from": from_email or cls.DEFAULT_FROM,
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
