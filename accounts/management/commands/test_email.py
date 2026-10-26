import sys
from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test SMTP configuration by sending an email to a recipient"

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Email address of recipient')

    def handle(self, *args, **options):
        recipient = options['recipient']
        self.stdout.write(self.style.NOTICE("Testing Email / SMTP Configuration..."))
        self.stdout.write(f"EMAIL_BACKEND:       {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST:          {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT:          {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS:       {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_USE_SSL:       {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"EMAIL_HOST_USER:     {settings.EMAIL_HOST_USER or '(not set)'}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(not set)'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL:  {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"FRONTEND_URL:        {settings.FRONTEND_URL}")

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            self.stdout.write(self.style.WARNING(
                "\nWARNING: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is not set in backend/.env!\n"
                "To deliver real emails to inboxes, add your SMTP credentials to backend/.env."
            ))

        self.stdout.write(f"\nAttempting connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        try:
            connection = get_connection(fail_silently=False)
            connection.open()
            self.stdout.write(self.style.SUCCESS("[OK] SMTP connection established successfully!"))

            self.stdout.write(f"Sending test email to {recipient}...")
            subject = "Expense Tracker - SMTP Delivery Test"
            body = (
                f"Namaste!\n\n"
                f"This is a test email sent from the Expense Tracker Django backend.\n"
                f"Your SMTP configuration is working correctly and real verification emails will be delivered.\n\n"
                f"From: {settings.DEFAULT_FROM_EMAIL}\n"
            )
            msg = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                connection=connection,
            )
            msg.send(fail_silently=False)
            connection.close()

            self.stdout.write(self.style.SUCCESS(f"\n[OK] Test email successfully sent to {recipient}!"))
            self.stdout.write(self.style.SUCCESS("Please check the inbox and spam folder of that email address."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n[FAIL] Failed to send email via SMTP: {type(e).__name__}: {e}"))
            import traceback
            traceback.print_exc()
            sys.exit(1)
