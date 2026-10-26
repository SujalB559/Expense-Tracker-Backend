from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    TestSmtpDiagnosticView,
    CurrentUserView,
    LoginView,
    RegisterView,
    ResetUserDataView,
    VerifyEmailView,
    ResendVerificationView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('test-smtp/', TestSmtpDiagnosticView.as_view(), name='auth_test_smtp'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('verify-email/', VerifyEmailView.as_view(), name='auth_verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='auth_resend_verification'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
    path('reset-data/', ResetUserDataView.as_view(), name='auth_reset_data'),
]
