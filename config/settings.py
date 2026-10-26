"""
Django settings for the Expense Tracker backend.
"""

from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-expense-tracker-dev-key')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,.onrender.com,*').split(',')
    if host.strip()
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',

    # Modular local apps
    'accounts',
    'categories',
    'transactions',
    'budgets',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Needs to be as high as possible
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration
# PostgreSQL is the main database as requested.
# Configure credentials via environment variables.
DB_NAME = os.getenv('DATABASE_NAME', 'expense_tracker_db')
DB_USER = os.getenv('DATABASE_USER', 'postgres')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD', 'postgres')
DB_HOST = os.getenv('DATABASE_HOST', 'localhost')
DB_PORT = os.getenv('DATABASE_PORT', '5432')

# In local environments or Render free web service without a managed DB,
# automatically default to SQLite if no DATABASE_URL or DATABASE_HOST is provided.
has_postgres = bool(os.getenv('DATABASE_URL') or (os.getenv('DATABASE_HOST') and os.getenv('DATABASE_HOST') != 'localhost'))
USE_SQLITE = (
    os.getenv('USE_SQLITE', str(not has_postgres)).lower() in ('true', '1') or
    os.getenv('USE_SQLITE_FALLBACK', 'False').lower() in ('true', '1') or
    not has_postgres
)

if os.getenv('DATABASE_URL'):
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(default=os.getenv('DATABASE_URL'), conn_max_age=600)}
    except Exception:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
elif USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': None,  # Frontend handles array responses directly
}

# Simple JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True
cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174')
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in cors_origins.split(',')
    if origin.strip()
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.vercel\.app$',
]
if DEBUG or os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1'):
    CORS_ALLOW_ALL_ORIGINS = True

# Frontend URL for verification links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://expense-tracker-nu-six-83.vercel.app' if not DEBUG else 'http://localhost:5173').rstrip('/')

# Email Configuration (SMTP)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '').strip()
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 10))

# Sender identity
_configured_sender = os.getenv('DEFAULT_FROM_EMAIL', '').strip()
if _configured_sender:
    DEFAULT_FROM_EMAIL = _configured_sender
elif EMAIL_HOST_USER:
    DEFAULT_FROM_EMAIL = f'Expense Tracker <{EMAIL_HOST_USER}>'
else:
    DEFAULT_FROM_EMAIL = 'Expense Tracker <noreply@expensetracker.np>'

SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_VERIFICATION_TIMEOUT_HOURS = int(os.getenv('EMAIL_VERIFICATION_TIMEOUT_HOURS', 24))


# Resend HTTPS API Key
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '').strip()
