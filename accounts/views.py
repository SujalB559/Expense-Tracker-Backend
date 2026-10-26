from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .emails import send_verification_email, is_smtp_configured
from .models import EmailVerificationToken, User
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new user, creates a secure verification token,
    and sends the verification email. Account starts unverified.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Account starts unverified — generate token and dispatch verification email
            token_obj = EmailVerificationToken.create_token(user)
            email_sent = send_verification_email(user, token_obj)

            resp_data = {
                'message': (
                    'Registration successful! A verification email has been sent to your inbox.'
                    if email_sent
                    else "Registration successful! However, we couldn't send the verification email. Please click resend verification."
                ),
                'email': user.email,
                'is_email_verified': False,
                'email_sent': email_sent,
                'user': UserSerializer(user).data,
            }
            return Response(resp_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Logs in user with username/email and password.
    Blocks unverified accounts with HTTP 403 and provides a resend option.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Check email verification status
            if not user.is_email_verified:
                return Response(
                    {
                        'error': 'email_not_verified',
                        'message': 'Your email address is not verified yet. Please check your inbox or click below to resend the verification link.',
                        'email': user.email,
                        'is_email_verified': False,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': 'Login successful.',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    GET /api/auth/verify-email/?token=...
    POST /api/auth/verify-email/ with {"token": "..."}
    Validates verification token, marks user email as verified,
    and returns session tokens.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        token_str = request.query_params.get('token')
        return self._verify(token_str)

    def post(self, request):
        token_str = request.data.get('token')
        return self._verify(token_str)

    def _verify(self, token_str):
        if not token_str or not str(token_str).strip():
            return Response(
                {
                    'error': 'missing_token',
                    'message': 'Verification token is required.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_str = str(token_str).strip()
        try:
            token_obj = EmailVerificationToken.objects.select_related('user').get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {
                    'error': 'invalid_token',
                    'message': 'This verification link is invalid or has already expired. Please request a new verification email.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token_obj.user.is_email_verified:
            return Response(
                {
                    'message': 'Your email address is already verified. You can proceed to log in.',
                    'email': token_obj.user.email,
                    'already_verified': True,
                    'is_email_verified': True,
                },
                status=status.HTTP_200_OK,
            )

        if token_obj.is_used:
            return Response(
                {
                    'error': 'already_used',
                    'message': 'This verification link has already been used. Please log in or request a new verification email.',
                    'email': token_obj.user.email,
                    'already_verified': False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token_obj.is_expired:
            return Response(
                {
                    'error': 'token_expired',
                    'message': 'This verification link has expired. Please request a fresh verification link.',
                    'email': token_obj.user.email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark user as verified
        user = token_obj.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])

        # Mark token as used
        token_obj.is_used = True
        token_obj.save(update_fields=['is_used'])

        # Clear other unused tokens for this user
        EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

        # Provide tokens for automatic or one-click access
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'Your email address has been successfully verified! Welcome to Expense Tracker.',
                'email': user.email,
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationView(APIView):
    """
    POST /api/auth/resend-verification/
    Body: {"email": "user@example.com"} or {"username": "..."}
    Sends a new secure verification email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('email') or request.data.get('username')
        if not identifier or not str(identifier).strip():
            return Response(
                {
                    'error': 'missing_identifier',
                    'message': 'Please provide your email address or username.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        target = str(identifier).strip().lower()
        user = None
        if '@' in target:
            user = User.objects.filter(email__iexact=target).first()
        else:
            user = User.objects.filter(username__iexact=target).first()

        if not user:
            return Response(
                {
                    'error': 'user_not_found',
                    'message': 'No account was found matching that email address or username.',
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_email_verified:
            return Response(
                {
                    'message': 'This account is already verified. You can log in directly.',
                    'already_verified': True,
                    'email': user.email,
                },
                status=status.HTTP_200_OK,
            )



        # Generate fresh token & send verification email
        token_obj = EmailVerificationToken.create_token(user)
        email_sent = send_verification_email(user, token_obj)

        if not email_sent:
            return Response(
                {
                    'error': 'email_send_failed',
                    'message': "We couldn't send the verification email. Please try again.",
                    'email': user.email,
                    'email_sent': False,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                'message': 'Verification email sent. Please check your inbox and spam folder.',
                'email': user.email,
                'email_sent': True,
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):
    """
    GET /api/auth/me/
    PATCH /api/auth/me/
    Retrieves or updates the current authenticated user's profile and preferences.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class ResetUserDataView(APIView):
    """
    POST /api/auth/reset-data/
    Resets transactions, custom categories, category limits, budget, and savings goals
    for the current user back to clean defaults (matches frontend reset action).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Delete all transactions
        user.transactions.all().delete()

        # Delete custom categories & reset category limits on defaults
        user.categories.filter(is_default=False).delete()
        user.categories.filter(is_default=True).update(limit=None)

        # Reset budget to 2000
        if hasattr(user, 'budget'):
            user.budget.amount = 2000.00
            user.budget.save()

        # Clear savings goals
        user.savings_goals.all().delete()

        # Reset currency and theme to defaults
        user.currency = '$'
        user.theme = 'light'
        user.save()

        return Response(
            {
                'message': 'All user data has been successfully reset.',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
