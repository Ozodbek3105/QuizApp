"""
Django settings for asosiy project.
(DigitalOcean App Platform uchun sozlangan)
"""
import os 
import dj_database_url 
from pathlib import Path
# from re import S (Keraksiz import)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ====================================================================
# XAVFSIZLIK SOZLAMALARI (PRODUCTION UCHUN)
# ====================================================================

# SECRET_KEY endi serverning o'zidan olinadi (xavfsiz)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-2b)bd1f90)hh=v2ksl-h378#y#e=i256&w+7100kii0_30o*vg')

# DEBUG serverda avtomatik 'False' bo'ladi, lokalda 'True'
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


# === ASOSIY O'ZGARISH SHU YERDA ===
# ALLOWED_HOSTS ni QO'LDA KIRITAMIZ (Eng ishonchli usul)
ALLOWED_HOSTS = ['quiz-app-rtyfi.ondigitalocean.app', '127.0.0.1','localhost','prodissolution-scripless-otha.ngrok-free.dev', # <-- Sizning ngrok
]


# CSRF himoyasi uchun ishonchli manbalar
CSRF_TRUSTED_ORIGINS = [
    'https://quiz-app-rtyfi.ondigitalocean.app', # <-- SIZNING ASOSIY MANZILINGIZ
    'https://prodissolution-scripless-otha.ngrok-free.dev',
]
# ====================================================================


# ====================================================================
# ILOVALAR VA MIDDLEWARE
# ====================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'question',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- QO'SHILDI (Statik fayllar uchun)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'asosiy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
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

WSGI_APPLICATION = 'asosiy.wsgi.application'


# ====================================================================
# MA'LUMOTLAR BAZASI (DATABASE)
# ====================================================================

# Bu sozlama serverda avtomatik 'DATABASE_URL' dan PostgreSQL ni oladi,
# lokal kompyuteringizda (agar 'DATABASE_URL' bo'lmasa) 'db.sqlite3' ni ishlatadi.

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=False # App Platform ichki tarmoq uchun SSL talab qilmaydi
        )
    }
else:
    # Lokal kompyuter uchun fallback (sqlite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # ... (o'zgarishsiz qoldirildi) ...
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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ====================================================================
# STATIK FAYLLAR (CSS, JS, RASMLAR)
# ====================================================================

STATIC_URL = 'static/'

# 'collectstatic' buyrug'i barcha statik fayllarni shu papkaga yig'adi
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise uchun maxsus saqlash ombori
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Sizda STATIC_ROOT ikki marta yozilgan edi, bittasi o'chirildi.

# ====================================================================
# BOSHQA SOZLAMALAR
# ====================================================================

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'