import secrets
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model for the Expense Tracker.
    Stores personal preferences such as currency and theme,
    and tracks email verification status.
    """
    email = models.EmailField(unique=True)
    currency = models.CharField(max_length=10, default='$')
    theme = models.CharField(max_length=20, default='light')
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        if self.first_name:
            return self.first_name[:2].upper()
        return self.username[:2].upper()


class EmailVerificationToken(models.Model):
    """
    Secure, time-limited verification token generated upon registration or resend request.
    Does not expose sensitive user info in the URL token.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def create_token(cls, user, hours_valid=None):
        from django.conf import settings
        if hours_valid is None:
            hours_valid = getattr(settings, 'EMAIL_VERIFICATION_TIMEOUT_HOURS', 24)
        # Invalidate/delete any previous unused tokens for this user
        cls.objects.filter(user=user, is_used=False).delete()
        token_str = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=hours_valid)
        return cls.objects.create(
            user=user,
            token=token_str,
            expires_at=expires_at,
            is_used=False,
        )

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Token({self.user.username}, expired={self.is_expired}, used={self.is_used})"
