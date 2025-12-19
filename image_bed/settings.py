"""
Django settings for image_bed project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'simpleui',  # Django Admin UI theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'imagehost',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'image_bed.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'image_bed.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/i/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/data/images')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Image upload settings
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # 10MB default
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ENABLE_IMAGE_COMPRESSION = os.getenv('ENABLE_IMAGE_COMPRESSION', 'True') == 'True'
COMPRESSION_QUALITY = int(os.getenv('COMPRESSION_QUALITY', 85))
MAX_IMAGE_DIMENSION = int(os.getenv('MAX_IMAGE_DIMENSION', 4096))

# API Token settings
API_TOKEN = os.getenv('API_TOKEN', '')
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'True') == 'True'

# CSRF settings
# Support both HTTPS domains and HTTP IP addresses with ports
CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    # Skip localhost entries
    if host in ['localhost', '127.0.0.1']:
        continue
    # Add both HTTP and HTTPS for domains and IPs
    CSRF_TRUSTED_ORIGINS.append(f'http://{host}')
    CSRF_TRUSTED_ORIGINS.append(f'https://{host}')

# Security settings for production
# Allow disabling HTTPS redirect for IP-based deployments
FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'True') == 'True'

if not DEBUG and FORCE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Simpleui Configuration
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['图床管理', '认证和授权'],
    'dynamic': True,
    'menus': [{
        'name': '图床管理',
        'icon': 'fas fa-images',
        'models': [{
            'name': '图片',
            'icon': 'fas fa-image',
            'url': '/admin/imagehost/image/'
        }, {
            'name': 'API Token',
            'icon': 'fas fa-key',
            'url': '/admin/imagehost/uploadtoken/'
        }]
    }]
}

SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'
