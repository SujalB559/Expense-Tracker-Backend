import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

def is_smtp_configured():
    host_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
    host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
    return bool(host_user and host_password)



def send_verification_email(user, token_obj):
    if not is_smtp_configured():
        logger.info('SMTP not configured, skipping send.')
        return False
    """
    Sends a professional, responsive HTML and plain-text email with a secure verification link.
    """
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    verification_link = f"{frontend_url}/verify-email?token={token_obj.token}"
    recipient_name = user.first_name or user.username
    timeout_hours = getattr(settings, 'EMAIL_VERIFICATION_TIMEOUT_HOURS', 24)

    subject = "Verify your email address - Expense Tracker"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Expense Tracker <noreply@expensetracker.np>')
    to_email = [user.email]

    # Plain text version
    text_content = f"""Namaste, {recipient_name}!

Thank you for registering with Expense Tracker.

Please verify your email address to activate your account and start tracking your income, expenses, and monthly budget in Nepali Rupees (Rs).

Click the link below to verify your email (Verify My Email):
{verification_link}

This link is secure, does not expose your private details, and will expire in {timeout_hours} hours.

If you did not sign up for Expense Tracker, you can safely ignore this email.

Warm regards,
Expense Tracker Team (Nepal · NPR)
"""

    # Rich responsive HTML version
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your email - Expense Tracker</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 560px; background-color: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
          <!-- Header -->
          <tr>
            <td style="padding: 32px 32px 24px 32px; text-align: center; border-bottom: 1px solid #f1f5f9;">
              <table role="presentation" align="center" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background-color: #059669; width: 44px; height: 44px; border-radius: 12px; text-align: center; vertical-align: middle;">
                    <span style="color: #ffffff; font-size: 22px; font-weight: bold; line-height: 44px; display: inline-block;">रू</span>
                  </td>
                  <td style="padding-left: 14px; text-align: left;">
                    <span style="font-size: 18px; font-weight: 700; color: #0f172a; display: block; letter-spacing: -0.02em;">Expense Tracker</span>
                    <span style="font-size: 12px; color: #64748b; font-weight: 500; display: block;">Nepal · NPR (Rs)</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 36px 32px;">
              <h1 style="margin: 0 0 16px 0; font-size: 20px; font-weight: 700; color: #0f172a;">
                Namaste, {recipient_name}! 👋
              </h1>
              <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 22px; color: #475569;">
                Thank you for creating an account with Expense Tracker. To complete your setup and begin managing your daily expenses, income, and monthly budget in Nepali Rupees (Rs), please confirm your email address.
              </p>

              <!-- CTA Button -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 28px 0;">
                <tr>
                  <td align="center">
                    <a href="{verification_link}" target="_blank" style="background-color: #059669; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-size: 15px; font-weight: 700; display: inline-block; box-shadow: 0 2px 4px rgba(5, 150, 105, 0.25); letter-spacing: 0.01em;">
                      Verify My Email
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Expiry Alert -->
              <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 14px; margin-bottom: 24px;">
                <p style="margin: 0; font-size: 12px; line-height: 18px; color: #166534;">
                  <strong>Security Note:</strong> This verification link will expire in <strong>{timeout_hours} hours</strong>. No sensitive personal data is stored in the link.
                </p>
              </div>

              <!-- Fallback Link -->
              <p style="margin: 0 0 8px 0; font-size: 12px; color: #64748b;">
                If the button above does not work, copy and paste this link into your browser:
              </p>
              <p style="margin: 0; font-size: 12px; line-height: 18px; word-break: break-all; background-color: #f1f5f9; padding: 10px; border-radius: 8px; color: #0f172a; font-family: monospace;">
                <a href="{verification_link}" style="color: #059669; text-decoration: underline;">{verification_link}</a>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 32px; background-color: #f8fafc; border-top: 1px solid #f1f5f9; text-align: center;">
              <p style="margin: 0 0 6px 0; font-size: 12px; color: #94a3b8;">
                If you did not sign up for Expense Tracker, please disregard this email. Your email address will not be activated.
              </p>
              <p style="margin: 0; font-size: 11px; color: #cbd5e1;">
                &copy; 2026 Expense Tracker · Built for Nepal
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Verification email successfully sent to {user.email}")
        return True
    except Exception as e:
        logger.exception(f"Failed to send verification email to {user.email}: {e}")
        return False
